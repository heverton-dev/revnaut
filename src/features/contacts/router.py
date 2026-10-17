# -*- coding: utf-8 -*-
"""
Vertical Slice: Contacts Router
"""

from typing import Optional, List
from fastapi import APIRouter, Header, status, HTTPException
from src.features.contacts.schemas import (
    ContactCreate, ContactImportRequest, ContactImportResponse,
    ContactOut, ContactProfileResponse, ContactTimelineResponse,
    ContactTimelineCommentResponse
)
from src.features.contacts import service
from src.core.database import get_connection
from src.core.security import enforce_user_permission

router = APIRouter(tags=["Contatos & Leads"])


@router.get("/api/v1/contacts", response_model=List[ContactOut], summary="Buscar e Listar Contatos com Escopo Hierárquico")
def read_contacts(
    q: Optional[str] = None,
    account_id: str = "0f14ffff",
    x_user_id: Optional[str] = Header(None)
):
    return service.list_contacts(query=q, account_id=account_id, user_id=x_user_id)


@router.post("/api/v1/contacts", response_model=ContactOut, status_code=status.HTTP_201_CREATED, summary="Criar Contato com Validação RBAC")
def create_contact(
    payload: ContactCreate,
    account_id: str = "0f14ffff",
    x_user_id: Optional[str] = Header(None)
):
    conn = get_connection()
    try:
        enforce_user_permission(conn, x_user_id, account_id, "contacts:write")
    finally:
        conn.close()
    return service.create_contact(payload)


@router.post("/api/v1/contacts/import", response_model=ContactImportResponse, summary="Importação em Massa com Distribuição Territorial")
def import_contacts(
    payload: ContactImportRequest,
    account_id: str = "0f14ffff",
    x_user_id: Optional[str] = Header(None)
):
    conn = get_connection()
    try:
        enforce_user_permission(conn, x_user_id, account_id, "contacts:write")
    finally:
        conn.close()
    return service.import_contacts_batch(payload, account_id=account_id)


from pydantic import BaseModel
class ContactTimelineCommentCreate(BaseModel):
    comment: str
    author_name: Optional[str] = "Consultor Especialista"


@router.get("/api/v1/contacts/{contact_id}/profile", response_model=ContactProfileResponse, summary="Perfil Completo, Histórico & Oportunidades do Contato")
def get_contact_profile(contact_id: int):
    profile = service.get_contact_full_profile(contact_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Contato não localizado")
    return profile


@router.get("/api/v1/contacts/{contact_id}/timeline", response_model=ContactTimelineResponse, summary="Histórico e Linha do Tempo do Contato")
def get_contact_timeline(contact_id: int):
    return {"contact_id": contact_id, "timeline": service.get_contact_timeline(contact_id)}


@router.post("/api/v1/contacts/{contact_id}/timeline/comments", response_model=ContactTimelineCommentResponse, status_code=status.HTTP_201_CREATED, summary="Adicionar Nota de Auditoria na Timeline do Contato")
def add_timeline_comment(
    contact_id: int, 
    payload: ContactTimelineCommentCreate,
    x_user_id: Optional[str] = Header(None)
):
    return service.add_contact_timeline_comment(
        contact_id=contact_id, 
        comment=payload.comment, 
        user_id=x_user_id, 
        author_name=payload.author_name or "Consultor Especialista"
    )



