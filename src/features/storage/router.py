# -*- coding: utf-8 -*-
"""
Storage Router — Presigned URLs para Cloudflare R2
Upload e download direto com isolamento multi-tenant.
"""

from fastapi import APIRouter, Header, HTTPException, Query, status
from typing import Optional
from src.core.storage import R2StorageClient, StorageSecurityException
from src.features.storage.schemas import (
    PresignUploadRequest,
    PresignUploadResponse,
    PresignDownloadResponse,
)

router = APIRouter(prefix="/api/v1/storage", tags=["Storage R2"])
storage_client = R2StorageClient()


@router.post("/presign-upload", response_model=PresignUploadResponse)
def presign_upload(
    payload: PresignUploadRequest,
    x_account_id: Optional[str] = Header(None, alias="X-Account-ID"),
):
    account_id = x_account_id or "0f14ffff"
    try:
        key = storage_client.generate_storage_key(
            tenant_id=account_id,
            module=payload.module,
            filename=payload.filename,
        )
        res = storage_client.generate_presigned_upload_url(
            key=key,
            content_type=payload.content_type,
            expires_in=900,
        )
        return PresignUploadResponse(**res)
    except StorageSecurityException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/presign-download", response_model=PresignDownloadResponse)
def presign_download(
    key: str = Query(..., description="Chave do objeto no R2"),
    x_account_id: Optional[str] = Header(None, alias="X-Account-ID"),
):
    account_id = x_account_id or "0f14ffff"
    try:
        storage_client.validate_tenant_access(tenant_id=account_id, key=key)
        res = storage_client.generate_presigned_download_url(key=key, expires_in=900)
        return PresignDownloadResponse(**res)
    except StorageSecurityException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("/presign-download/{file_id:path}", response_model=PresignDownloadResponse)
def presign_download_by_path(
    file_id: str,
    x_account_id: Optional[str] = Header(None, alias="X-Account-ID"),
):
    account_id = x_account_id or "0f14ffff"
    try:
        storage_client.validate_tenant_access(tenant_id=account_id, key=file_id)
        res = storage_client.generate_presigned_download_url(key=file_id, expires_in=900)
        return PresignDownloadResponse(**res)
    except StorageSecurityException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
