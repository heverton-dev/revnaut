# -*- coding: utf-8 -*-
"""
Módulo de Imagiologia Médica Odontológica Orthanc DICOM & Cloudflare R2 3D.
Gerencia upload seguro presigned para R2, anonimização LGPD e tokens de visualização 3D.
"""

from __future__ import annotations
import os
import uuid
import hashlib
import hmac
import time
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from src.core.database import get_connection, init_db
from src.core.storage import R2StorageClient
from src.core.events import EventBus, StreamName


class OrthancDicomClient:
    """
    Cliente de integração com o servidor PACS Orthanc DICOM (porta 4242 / HTTP 8042)
    e armazenamento de alta escala de tomografias Cone Beam e escaneamentos STL no Cloudflare R2.
    """

    def __init__(
        self,
        orthanc_url: Optional[str] = None,
        r2_client: Optional[R2StorageClient] = None,
        mock_mode: Optional[bool] = None,
    ):
        self.orthanc_url = orthanc_url or os.getenv("ORTHANC_HTTP_URL", "http://orthanc:8042")
        self.orthanc_dicom_port = int(os.getenv("ORTHANC_DICOM_PORT", "4242"))
        app_env = os.getenv("APP_ENV", "local")
        self.mock_mode = mock_mode if mock_mode is not None else (app_env in ("local", "test", "development"))
        self.storage = r2_client or R2StorageClient()
        self.secret_salt = os.getenv("DICOM_ANONYMIZATION_SALT", "revnaut_lgpd_salt_2026")

    def anonymize_patient_identity(self, patient_name: Optional[str], account_id: str) -> str:
        """
        Anonimiza deterministicamente o identificador do paciente em conformidade com a LGPD,
        utilizando hash HMAC-SHA256 truncado para exibição clínica sem exposição de dados pessoais.
        """
        raw = f"{account_id}:{patient_name or 'PACIENTE_DESCONHECIDO'}"
        sig = hmac.new(self.secret_salt.encode(), raw.encode(), hashlib.sha256).hexdigest()
        return f"ANON-PAC-{sig[:10].upper()}"

    def estimate_bone_metrics(self, jaw_type: str, implant_site: Optional[str] = None) -> Dict[str, Any]:
        """
        Simula a medição tomográfica de densidade de Hounsfield (HU) e espessura óssea em mm,
        calculando o diâmetro e comprimento sugeridos para o implante dentário.
        """
        jaw_clean = (jaw_type or "AMBAS").upper()
        if jaw_clean == "MANDIBULA":
            bone_density = "D1_DENSO"
            thickness_mm = 8.8
            rec_diameter = 4.3
            rec_length = 10.0
        elif jaw_clean == "MAXILA":
            bone_density = "D3_POROSO"
            thickness_mm = 6.5
            rec_diameter = 3.75
            rec_length = 11.5
        elif jaw_clean == "PERIAPICAL":
            bone_density = "D2_NORMAL"
            thickness_mm = 5.2
            rec_diameter = 3.5
            rec_length = 10.0
        else:
            bone_density = "D2_NORMAL"
            thickness_mm = 7.4
            rec_diameter = 4.0
            rec_length = 10.0

        # Se houver dente incisivo estético definido (ex: 11, 21), calibrar diâmetro para perfil estético
        if implant_site in ("11", "12", "21", "22", "31", "32", "41", "42"):
            rec_diameter = 3.5

        return {
            "bone_density_estimate": bone_density,
            "bone_thickness_mm": thickness_mm,
            "recommended_implant_diameter_mm": rec_diameter,
            "recommended_implant_length_mm": rec_length,
        }

    def create_upload_presign(
        self,
        file_name: str,
        study_type: str = "DICOM_CBCT",
        jaw_type: str = "AMBAS",
        slice_count: int = 1,
        patient_name: Optional[str] = None,
        deal_id: Optional[str] = None,
        ticket_id: Optional[str] = None,
        implant_site: Optional[str] = None,
        anonymize_lgpd: bool = True,
        account_id: str = "0f14ffff",
    ) -> Dict[str, Any]:
        """
        Gera uma URL de upload pré-assinada no Cloudflare R2 para envio direto do arquivo
        DICOM ou STL (evitando gargalo no servidor FastAPI) e cadastra o registro prévio na base.
        """
        init_db()
        study_id = f"study-{uuid.uuid4().hex[:10]}"
        anon_id = self.anonymize_patient_identity(patient_name, account_id) if anonymize_lgpd else (patient_name or "ANON")

        clean_ext = ".dcm" if "DICOM" in study_type.upper() else ".stl"
        if not file_name.lower().endswith(clean_ext):
            file_name = f"{file_name}{clean_ext}"

        # Armazenamento particionado por tenant e estudo no R2
        storage_key = self.storage.generate_storage_key(
            tenant_id=account_id,
            module=f"imaging/{study_type.lower()}",
            filename=f"{study_id}_{file_name}"
        )

        content_type = "application/dicom" if "DICOM" in study_type.upper() else "model/stl"
        presigned_res = self.storage.generate_presigned_upload_url(
            key=storage_key,
            content_type=content_type,
            expires_in=3600
        )
        presigned_url = presigned_res["upload_url"]

        orthanc_study_uid = f"orthanc-{uuid.uuid4().hex[:12]}"
        metrics = self.estimate_bone_metrics(jaw_type, implant_site)

        # Salva registro do estudo no SQLite WAL
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO imaging_studies (
                    id, account_id, patient_name, patient_anonymized_id,
                    deal_id, ticket_id, study_type, orthanc_study_id,
                    r2_storage_key, file_name, file_size_bytes, slice_count,
                    jaw_type, bone_density_estimate, implant_site, is_anonymized
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                study_id, account_id, (None if anonymize_lgpd else patient_name), anon_id,
                deal_id, ticket_id, study_type, orthanc_study_uid,
                storage_key, file_name, 0, slice_count,
                jaw_type, metrics["bone_density_estimate"], implant_site, 1 if anonymize_lgpd else 0
            ))
            conn.commit()
        finally:
            conn.close()

        # Telemetria no EventBus
        try:
            EventBus.publish_sync(
                StreamName.AUDIT,
                {
                    "event": "imaging.study_upload_presigned",
                    "study_id": study_id,
                    "account_id": account_id,
                    "study_type": study_type,
                    "deal_id": deal_id,
                }
            )
        except Exception:
            pass

        return {
            "study_id": study_id,
            "upload_presigned_url": presigned_url,
            "r2_storage_key": storage_key,
            "patient_anonymized_id": anon_id,
            "study_type": study_type,
            "anonymized": anonymize_lgpd,
            "expires_in_seconds": 3600,
            "orthanc_dicom_port": self.orthanc_dicom_port,
            "orthanc_http_endpoint": f"{self.orthanc_url}/studies/{orthanc_study_uid}",
        }

    def generate_viewer_session(self, study_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
        """
        Gera um token de visualização assinado com HMAC-SHA256 e URLs de streaming 3D autenticado
        para o visualizador no navegador, respeitando isolamento multi-tenant restrito.
        """
        init_db()
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, account_id, patient_name, patient_anonymized_id,
                       deal_id, ticket_id, study_type, orthanc_study_id,
                       r2_storage_key, file_name, file_size_bytes, slice_count,
                       jaw_type, bone_density_estimate, implant_site, is_anonymized,
                       created_at
                FROM imaging_studies
                WHERE id = ?
            """, (study_id,))
            row = cur.fetchone()
        finally:
            conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Estudo de imagem não encontrado")

        # Invariante de Segurança e Isolamento Multi-tenant
        if row["account_id"] != account_id:
            raise HTTPException(status_code=403, detail="Acesso não autorizado a estudo de outro tenant")

        # Gera token assinado com validade de 2 horas
        expires_at = int(time.time()) + 7200
        token_payload = f"{study_id}:{account_id}:{expires_at}"
        token_sig = hmac.new(self.secret_salt.encode(), token_payload.encode(), hashlib.sha256).hexdigest()
        viewer_token = f"vt_{token_sig[:24]}_{expires_at}"

        r2_domain = os.getenv("R2_PUBLIC_URL", "https://r2.revnaut.internal")
        stream_url = f"{self.orthanc_url}/studies/{row['orthanc_study_id']}/stream"
        r2_url = f"{r2_domain}/{row['r2_storage_key']}?token={viewer_token}"

        metrics = self.estimate_bone_metrics(row["jaw_type"], row["implant_site"])

        return {
            "study_id": study_id,
            "viewer_token": viewer_token,
            "viewer_stream_url": stream_url,
            "r2_public_url": r2_url,
            "study_type": row["study_type"],
            "patient_anonymized_id": row["patient_anonymized_id"],
            "jaw_type": row["jaw_type"],
            "bone_density_estimate": row["bone_density_estimate"],
            "implant_site": row["implant_site"],
            "slice_count": row["slice_count"],
            "recommended_implant_diameter_mm": metrics["recommended_implant_diameter_mm"],
            "recommended_implant_length_mm": metrics["recommended_implant_length_mm"],
            "bone_thickness_mm": metrics["bone_thickness_mm"],
            "expires_in_seconds": 7200,
        }

    def get_study(self, study_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
        """Obtém detalhes do estudo de imagem validando titularidade do tenant."""
        init_db()
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, account_id, patient_name, patient_anonymized_id,
                       deal_id, ticket_id, study_type, orthanc_study_id,
                       r2_storage_key, file_name, file_size_bytes, slice_count,
                       jaw_type, bone_density_estimate, implant_site, is_anonymized,
                       created_at
                FROM imaging_studies
                WHERE id = ?
            """, (study_id,))
            row = cur.fetchone()
        finally:
            conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Estudo de imagem não encontrado")

        if row["account_id"] != account_id:
            raise HTTPException(status_code=403, detail="Acesso não autorizado a estudo de outro tenant")

        d = dict(row)
        d["is_anonymized"] = bool(d["is_anonymized"])
        return d

    def list_studies(
        self,
        account_id: str = "0f14ffff",
        deal_id: Optional[str] = None,
        study_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Lista estudos de imagiologia odontológica do tenant com filtros opcionais."""
        init_db()
        conn = get_connection()
        try:
            cur = conn.cursor()
            query = """
                SELECT id, account_id, patient_name, patient_anonymized_id,
                       deal_id, ticket_id, study_type, orthanc_study_id,
                       r2_storage_key, file_name, file_size_bytes, slice_count,
                       jaw_type, bone_density_estimate, implant_site, is_anonymized,
                       created_at
                FROM imaging_studies
                WHERE account_id = ?
            """
            params: List[Any] = [account_id]
            if deal_id:
                query += " AND deal_id = ?"
                params.append(deal_id)
            if study_type:
                query += " AND study_type = ?"
                params.append(study_type)

            query += " ORDER BY created_at DESC"
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
            result = []
            for r in rows:
                item = dict(r)
                item["is_anonymized"] = bool(item["is_anonymized"])
                result.append(item)
            return result
        finally:
            conn.close()
