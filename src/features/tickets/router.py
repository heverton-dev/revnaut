# -*- coding: utf-8 -*-
"""
Vertical Slice: Tickets Router
"""

from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from src.features.tickets.schemas import (
    TicketCreate, TicketStatusUpdate, TicketOut,
    SurgicalSosTriggerRequest, SurgicalSosResponse,
    SurgicalSosDentgoDispatchRequest, SurgicalSosDentgoDispatchResponse,
    SurgicalSosTicketOut
)
from src.features.tickets import service
from src.features.tickets import surgical_sos

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


@router.post("/surgical-sos", response_model=SurgicalSosResponse, status_code=status.HTTP_201_CREATED, summary="Acionar SOS Mesa Cirúrgica com sala WebRTC LiveKit")
def trigger_sos(payload: SurgicalSosTriggerRequest):
    return surgical_sos.trigger_surgical_sos(
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        cro_uf=payload.cro_uf,
        procedure_details=payload.procedure_details,
        account_id=payload.account_id or "0f14ffff"
    )


@router.post("/surgical-sos/{ticket_id}/dispatch-dentgo", response_model=SurgicalSosDentgoDispatchResponse, summary="Despachar componente de emergência DENTGO durante chamada SOS")
def dispatch_dentgo_emergency(ticket_id: str, payload: SurgicalSosDentgoDispatchRequest):
    try:
        return surgical_sos.dispatch_emergency_dentgo_item(
            ticket_id=ticket_id,
            product_id=payload.product_id,
            quantity=payload.quantity,
            delivery_address=payload.delivery_address,
            delivery_lat=payload.delivery_lat,
            delivery_lng=payload.delivery_lng,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/surgical-sos/{ticket_id}", response_model=SurgicalSosTicketOut, summary="Consultar chamado de emergência cirúrgica")
def get_sos(ticket_id: str, account_id: str = "0f14ffff"):
    try:
        return surgical_sos.get_surgical_sos_ticket(ticket_id=ticket_id, account_id=account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

