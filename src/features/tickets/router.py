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
    SurgicalSosTicketOut,
    AnvisaRmaClaimCreate, AnvisaRmaClaimOut, AnvisaBatchQuarantineOut
)
from src.features.tickets import service
from src.features.tickets import surgical_sos
from src.features.tickets import anvisa_technovigilance


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


@router.post(
    "/anvisa-rma",
    response_model=AnvisaRmaClaimOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar queixa técnica e pedido de reposição em garantia ANVISA"
)
def create_anvisa_rma(payload: AnvisaRmaClaimCreate):
    try:
        return anvisa_technovigilance.submit_anvisa_rma_claim(
            surgeon_cro_uf=payload.surgeon_cro_uf,
            product_id=payload.product_id,
            product_name=payload.product_name,
            batch_number=payload.batch_number,
            fdi_tooth_region=payload.fdi_tooth_region,
            insertion_torque_ncm=payload.insertion_torque_ncm,
            surgery_date=payload.surgery_date,
            explant_date=payload.explant_date,
            failure_reason=payload.failure_reason,
            radiograph_r2_key=payload.radiograph_r2_key,
            surgeon_name=payload.surgeon_name,
            agreement_id=payload.agreement_id,
            patient_identifier=payload.patient_identifier,
            serial_number=payload.serial_number,
            notes=payload.notes,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/anvisa-rma",
    response_model=List[AnvisaRmaClaimOut],
    summary="Listar queixas técnicas regulatórias ANVISA"
)
def list_anvisa_rma(
    batch_number: Optional[str] = None,
    account_id: str = "0f14ffff"
):
    return anvisa_technovigilance.list_anvisa_rma_claims(
        account_id=account_id,
        batch_number=batch_number
    )


@router.get(
    "/anvisa-rma/quarantines",
    response_model=List[AnvisaBatchQuarantineOut],
    summary="Listar todos os lotes em quarentena sanitária ANVISA"
)
def list_batch_quarantines(account_id: str = "0f14ffff"):
    from src.core.database import get_connection
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM anvisa_batch_quarantines WHERE account_id = ? OR account_id = '0f14ffff' ORDER BY created_at DESC",
            (account_id,)
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


@router.get(
    "/anvisa-rma/quarantine/{batch_number}",
    response_model=Optional[AnvisaBatchQuarantineOut],
    summary="Verificar status sanitário e quarentena de lote fabril"
)
def get_quarantine_status(batch_number: str, account_id: str = "0f14ffff"):
    info = anvisa_technovigilance.get_batch_quarantine_info(
        batch_number=batch_number,
        account_id=account_id
    )
    if not info:
        raise HTTPException(status_code=404, detail=f"Lote {batch_number} não está em quarentena.")
    return info


@router.get(
    "/anvisa-rma/{claim_id}",
    response_model=AnvisaRmaClaimOut,
    summary="Obter detalhes de queixa técnica por ID"
)
def get_anvisa_rma(claim_id: str, account_id: str = "0f14ffff"):
    claim = anvisa_technovigilance.get_anvisa_rma_claim(
        claim_id=claim_id,
        account_id=account_id
    )
    if not claim:
        raise HTTPException(status_code=404, detail="Processo de RMA não encontrado.")
    return claim


