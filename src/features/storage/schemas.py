# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Dict, Optional


class PresignUploadRequest(BaseModel):
    filename: str = Field(..., description="Nome original do arquivo")
    module: str = Field(..., description="Módulo de destino (ex: consignments, dicom, contracts)")
    content_type: str = Field(..., description="MIME type do arquivo")


class PresignUploadResponse(BaseModel):
    upload_url: str
    key: str
    expires_in: int
    method: str
    headers: Dict[str, str]


class PresignDownloadResponse(BaseModel):
    download_url: str
    key: str
    expires_in: int


class DirectUploadResponse(BaseModel):
    model_config = {"extra": "allow"}
    status: str
    key: str
    url: str
    size_bytes: Optional[int] = 0
    content_type: Optional[str] = "application/octet-stream"
