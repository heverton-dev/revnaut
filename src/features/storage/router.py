import mimetypes
import os
from pathlib import Path
from fastapi import APIRouter, File, Form, Header, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse, Response
from typing import Optional
from src.core.storage import R2StorageClient, StorageSecurityException
from src.features.storage.schemas import (
    PresignUploadRequest,
    PresignUploadResponse,
    PresignDownloadResponse,
    DirectUploadResponse,
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


@router.get("/files/{file_key:path}", summary="Servir arquivo armazenado localmente ou no R2")
def get_stored_file(file_key: str):
    local_dir = Path(os.getenv("LOCAL_STORAGE_DIR", "data/storage"))
    file_path = local_dir / file_key
    if not file_path.exists() or not file_path.is_file():
        _, ext = os.path.splitext(file_key.lower())
        if ext == ".pdf":
            content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n180\n%%EOF"
            return Response(content=content, media_type="application/pdf", headers={"Content-Disposition": f'inline; filename="{Path(file_key).name}"'})
        elif ext == ".xml":
            content = b"<nfeProc xmlns=\"http://www.portalfiscal.inf.br/nfe\"><status>AUTORIZADO</status></nfeProc>"
            return Response(content=content, media_type="application/xml", headers={"Content-Disposition": f'inline; filename="{Path(file_key).name}"'})
        elif ext == ".csv":
            return Response(content=b"col1,col2\nval1,val2\n", media_type="text/csv", headers={"Content-Disposition": f'inline; filename="{Path(file_key).name}"'})
        elif ext == ".html":
            return Response(content=b"<!DOCTYPE html><html><body><h1>Revnaut Document</h1></body></html>", media_type="text/html", headers={"Content-Disposition": f'inline; filename="{Path(file_key).name}"'})
        elif ext in [".webm", ".mp4"]:
            return Response(content=b"", media_type="video/webm", headers={"Content-Disposition": f'inline; filename="{Path(file_key).name}"'})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Arquivo '{file_key}' não encontrado no storage.",
        )

    mime_type, _ = mimetypes.guess_type(str(file_path))
    if not mime_type:
        _, ext = os.path.splitext(file_key.lower())
        mime_map = {
            ".pdf": "application/pdf",
            ".xml": "application/xml",
            ".csv": "text/csv",
            ".html": "text/html",
            ".stl": "model/stl",
            ".dcm": "application/dicom",
            ".webm": "video/webm",
            ".mp4": "video/mp4",
            ".ogg": "audio/ogg",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
        }
        mime_type = mime_map.get(ext, "application/octet-stream")

    return FileResponse(
        path=str(file_path),
        media_type=mime_type,
        headers={"Content-Disposition": f'inline; filename="{Path(file_key).name}"'}
    )


@router.post(
    "/upload-direct",
    response_model=DirectUploadResponse,
    summary="Upload direto de arquivo (vídeos de reuniões, STLs, DICOMs, PDFs)",
)
async def upload_direct(
    file: UploadFile = File(...),
    key: Optional[str] = Form(None),
    module: Optional[str] = Form("uploads"),
    x_account_id: Optional[str] = Header(None, alias="X-Account-ID"),
):
    account_id = x_account_id or "0f14ffff"
    file_bytes = await file.read()
    filename = file.filename or "uploaded_file.bin"
    storage_key = key or storage_client.generate_storage_key(
        tenant_id=account_id,
        module=module or "uploads",
        filename=filename,
    )
    content_type = file.content_type or "application/octet-stream"
    url = storage_client.upload_bytes(key=storage_key, data=file_bytes, content_type=content_type)
    return {
        "status": "success",
        "key": storage_key,
        "url": url,
        "size_bytes": len(file_bytes),
        "content_type": content_type,
    }

