# -*- coding: utf-8 -*-
"""
Vertical Slice: Contacts Router
"""

from typing import Optional
from fastapi import APIRouter, Header, status
from src.features.contacts.schemas import ContactCreate
from src.features.contacts import service

router = APIRouter(tags=["Contatos & Leads"])


@router.get("/api/v1/contacts", summary="Buscar e Listar Contatos com Escopo Hierárquico")
def read_contacts(
    q: Optional[str] = None,
    account_id: str = "0f14ffff",
    x_user_id: Optional[str] = Header(None)
):
    return service.list_contacts(query=q, account_id=account_id, user_id=x_user_id)


@router.post("/api/v1/contacts", status_code=status.HTTP_201_CREATED, summary="Criar Contato")
def create_contact(payload: ContactCreate):
    return service.create_contact(payload)
