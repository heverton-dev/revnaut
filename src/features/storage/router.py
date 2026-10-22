import mimetypes
import os
from pathlib import Path
from fastapi import APIRouter, File, Form, Header, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import FileResponse, Response
from typing import Optional
from src.core.storage import R2StorageClient, StorageSecurityException, LOCAL_STORAGE_ROOT
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


def _validate_safe_storage_path(file_key: str, account_id: Optional[str] = None) -> Path:
    if not file_key or ".." in file_key or file_key.startswith("/") or file_key.startswith("\\"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path traversal detectado: caminho invalido ou inseguro.",
        )
    p = Path(file_key)
    if p.is_absolute() or any(part == ".." for part in p.parts):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path traversal detectado: caminho invalido ou inseguro.",
        )
    resolved = (LOCAL_STORAGE_ROOT / file_key).resolve()
    if not resolved.is_relative_to(LOCAL_STORAGE_ROOT.resolve()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path traversal detectado: arquivo fora do diretorio permitido.",
        )

    if account_id:
        try:
            storage_client.validate_tenant_access(tenant_id=account_id, key=file_key)
        except StorageSecurityException as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )
    return resolved


@router.get("/presign-download/{file_id:path}", response_model=PresignDownloadResponse)
def presign_download_by_path(
    file_id: str,
    x_account_id: Optional[str] = Header(None, alias="X-Account-ID"),
):
    account_id = x_account_id or "0f14ffff"
    _validate_safe_storage_path(file_id, account_id=account_id)
    try:
        res = storage_client.generate_presigned_download_url(key=file_id, expires_in=900)
        return PresignDownloadResponse(**res)
    except StorageSecurityException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.put("/upload-direct/{file_key:path}", response_model=DirectUploadResponse, summary="Upload direto de arquivo via PUT")
@router.post("/upload-direct/{file_key:path}", response_model=DirectUploadResponse, summary="Upload direto de arquivo via POST")
async def upload_direct_by_key(
    file_key: str,
    request: Request,
    x_account_id: Optional[str] = Header(None, alias="X-Account-ID"),
):
    dest = _validate_safe_storage_path(file_key, account_id=x_account_id)
    body = await request.body()
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo em disco: {e}")

    return {
        "status": "uploaded",
        "key": file_key,
        "url": f"/api/v1/storage/files/{file_key}",
        "size_bytes": len(body),
        "content_type": request.headers.get("content-type") or "application/octet-stream",
    }


@router.get("/files/{file_key:path}", summary="Servir arquivo armazenado localmente ou no R2")
def get_stored_file(
    file_key: str,
    download: Optional[bool] = Query(False),
    x_account_id: Optional[str] = Header(None, alias="X-Account-ID"),
):
    file_path = _validate_safe_storage_path(file_key, account_id=x_account_id)
    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo nao encontrado no storage.",
        )

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
    mime_type = mime_map.get(ext)
    if not mime_type:
        mime_type, _ = mimetypes.guess_type(str(file_path))
    mime_type = mime_type or "application/octet-stream"

    is_attachment = download or ext in [".csv", ".parquet", ".zip", ".tar", ".gz", ".xlsx"]
    disp_type = "attachment" if is_attachment else "inline"
    return FileResponse(
        path=str(file_path),
        media_type=mime_type,
        headers={"Content-Disposition": f'{disp_type}; filename="{Path(file_key).name}"'}
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

