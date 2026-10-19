# -*- coding: utf-8 -*-
"""
Cloudflare R2 Object Storage Client — Revnaut Core (S3 API v4 compatible)
Particionamento multi-tenant determinístico, URLs pré-assinadas e blindagem de segurança.
"""

from __future__ import annotations
import datetime
import os
from pathlib import Path
import uuid
from typing import Any, Dict, Optional
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from src.core.config import (
    R2_ACCOUNT_ID,
    R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY,
    R2_BUCKET_NAME,
    R2_ENDPOINT_URL,
    R2_PUBLIC_DOMAIN,
)


LOCAL_STORAGE_ROOT = Path(os.getenv("LOCAL_STORAGE_DIR", "data/storage"))
try:
    LOCAL_STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
except Exception:
    pass


class StorageSecurityException(Exception):
    """Exceção levantada em caso de violação de segurança no storage (MIME ou cross-tenant)."""
    pass


PROHIBITED_EXTENSIONS = {
    ".exe", ".sh", ".bat", ".cmd", ".dll",
    ".msi", ".vbs", ".ps1", ".com", ".scr", ".pif",
}

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/dicom",
    "application/octet-stream",
    "application/vnd.apache.parquet",
    "application/xml",
    "text/xml",
    "text/csv",
    "text/html",
    "model/stl",
    "model/ply",
    "audio/ogg",
    "audio/mpeg",
    "audio/wav",
    "video/mp4",
    "video/webm",
    "image/png",
    "image/jpeg",
    "image/webp",
    "text/csv",
    "application/json",
}


class R2StorageClient:
    def __init__(
        self,
        account_id: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ) -> None:
        self.account_id = account_id or R2_ACCOUNT_ID
        self.access_key_id = access_key_id or R2_ACCESS_KEY_ID
        self.secret_access_key = secret_access_key or R2_SECRET_ACCESS_KEY
        self.bucket_name = bucket_name or R2_BUCKET_NAME
        self.endpoint_url = endpoint_url or R2_ENDPOINT_URL
        self.mock_mode = not self.access_key_id or self.access_key_id.startswith("mock-") or "internal" in str(self.endpoint_url)

        self._s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            config=Config(signature_version="s3v4", region_name="auto"),
        )

    def generate_storage_key(
        self,
        tenant_id: str,
        module: str,
        filename: str,
        custom_uuid: Optional[str] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
    ) -> str:
        """
        Gera chave particionada estrita: {tenant_id}/{module}/{yyyy}/{mm}/{uuid}.{ext}
        """
        if not tenant_id or not module or not filename:
            raise StorageSecurityException("tenant_id, module e filename são obrigatórios.")

        _, ext = os.path.splitext(filename.lower())
        if ext in PROHIBITED_EXTENSIONS:
            raise StorageSecurityException(f"Extensão proibida por política de segurança: {ext}")

        now = datetime.datetime.now(datetime.timezone.utc)
        y = year or now.year
        m = month or now.month
        file_uuid = custom_uuid or str(uuid.uuid4())

        clean_ext = ext if ext else ".bin"
        return f"{tenant_id}/{module}/{y}/{m:02d}/{file_uuid}{clean_ext}"

    def validate_tenant_access(self, tenant_id: str, key: str) -> None:
        """
        Verifica se a chave solicitada pertence ao tenant autenticado.
        Bloqueia acesso cruzado / IDOR.
        """
        parts = key.split("/")
        if not parts or parts[0] != tenant_id:
            raise StorageSecurityException(
                f"Acesso cruzado não autorizado: Chave '{key}' não pertence ao tenant '{tenant_id}'."
            )

    def generate_presigned_upload_url(
        self,
        key: Optional[str] = None,
        content_type: str = "application/octet-stream",
        expires_in: int = 900,
        filename: Optional[str] = None,
        module: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Gera URL pré-assinada para PUT direto no Cloudflare R2 ou endpoint local FastAPI.
        """
        effective_key = key
        if not effective_key:
            if filename and module and tenant_id:
                effective_key = self.generate_storage_key(tenant_id, module, filename)
            else:
                raise StorageSecurityException("Chave do objeto ou (filename, module, tenant_id) é obrigatório.")

        _, ext = os.path.splitext(effective_key.lower())
        if ext in PROHIBITED_EXTENSIONS:
            raise StorageSecurityException(f"Extensão proibida por política de segurança: {ext}")

        if content_type not in ALLOWED_MIME_TYPES:
            raise StorageSecurityException(f"MIME type não permitido por política de segurança: {content_type}")

        if self.mock_mode:
            return {
                "upload_url": f"/api/v1/storage/upload-direct/{effective_key}",
                "key": effective_key,
                "expires_in": expires_in,
                "method": "PUT",
                "headers": {"Content-Type": content_type},
            }

        try:
            url = self._s3_client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": effective_key,
                    "ContentType": content_type,
                },
                ExpiresIn=expires_in,
            )
            return {
                "upload_url": url,
                "key": effective_key,
                "expires_in": expires_in,
                "method": "PUT",
                "headers": {"Content-Type": content_type},
            }
        except ClientError as e:
            raise StorageSecurityException(f"Erro ao gerar presigned upload URL: {e}")

    def generate_presigned_download_url(
        self,
        key: str,
        expires_in: int = 900,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Gera URL temporária para leitura/download direto do Cloudflare R2 ou storage local.
        """
        if tenant_id:
            self.validate_tenant_access(tenant_id=tenant_id, key=key)

        if self.mock_mode:
            return {
                "download_url": f"/api/v1/storage/files/{key}",
                "key": key,
                "expires_in": expires_in,
            }
        try:
            url = self._s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": key,
                },
                ExpiresIn=expires_in,
            )
            return {
                "download_url": url,
                "key": key,
                "expires_in": expires_in,
            }
        except ClientError as e:
            raise StorageSecurityException(f"Erro ao gerar presigned download URL: {e}")

    def upload_bytes(
        self,
        key: str,
        data: Optional[bytes] = None,
        content_type: str = "application/octet-stream",
        *,
        data_bytes: Optional[bytes] = None,
    ) -> str:
        """Upload direto de bytes com persistência em disco local e R2."""
        payload = data if data is not None else (data_bytes or b"")
        _, ext = os.path.splitext(key.lower())
        if ext in PROHIBITED_EXTENSIONS:
            raise StorageSecurityException(f"Extensão proibida: {ext}")

        if content_type not in ALLOWED_MIME_TYPES:
            raise StorageSecurityException(f"MIME type não permitido por política de segurança: {content_type}")

        # Persistência em disco local (LOCAL_STORAGE_ROOT / key)
        local_file = LOCAL_STORAGE_ROOT / key
        try:
            local_file.parent.mkdir(parents=True, exist_ok=True)
            local_file.write_bytes(payload)
        except Exception:
            pass

        if not self.mock_mode:
            try:
                self._s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=payload,
                    ContentType=content_type,
                )
                if R2_PUBLIC_DOMAIN and "internal" not in R2_PUBLIC_DOMAIN:
                    return f"{R2_PUBLIC_DOMAIN.rstrip('/')}/{key}"
            except Exception:
                pass

        return f"/api/v1/storage/files/{key}"

