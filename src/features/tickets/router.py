# -*- coding: utf-8 -*-
"""
Vertical Slice: Tickets Router
"""

from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from src.features.tickets.schemas import TicketCreate, TicketStatusUpdate, TicketOut
from src.features.tickets import service

router = APIRouter(prefix="/api/v1/tickets", tags=["Tickets"])


@router.get("", response_model=List[TicketOut], summary="Listar chamados e tickets de suporte")
def get_tickets(status: Optional[str] = None):
    return service.list_tickets(status=status)


@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED, summary="Criar novo ticket")
def create_ticket(data: TicketCreate):
    return service.create_ticket(data)


@router.patch("/{ticket_id}/status", response_model=TicketOut, summary="Atualizar status do ticket")
def update_status(ticket_id: str, data: TicketStatusUpdate):
    ticket = service.update_ticket_status(ticket_id, data)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    return ticket
