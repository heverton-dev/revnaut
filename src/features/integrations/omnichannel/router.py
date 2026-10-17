# -*- coding: utf-8 -*-
"""
Router FastAPI para Gateway Unificado de Webhooks Omnichannel.
Valida assinatura HMAC SHA-256 e sincroniza dados em tempo real.
"""

import json
from typing import Optional
from fastapi import APIRouter, Request, Header, HTTPException, status
from src.features.integrations.omnichannel.schemas import OmnichannelWebhookResponse
from src.features.integrations.omnichannel import service

router = APIRouter(prefix="/api/v1/webhooks", tags=["Integrações • Omnichannel Webhooks"])


@router.post("/evolution", response_model=OmnichannelWebhookResponse, summary="Webhook Evolution API v2 (WhatsApp Inbound)")
async def evolution_webhook(
    request: Request,
    x_evolution_signature: Optional[str] = Header(None, alias="X-Evolution-Signature"),
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256")
):
    body_bytes = await request.body()
    sig = x_evolution_signature or x_hub_signature_256
    if not sig or not service.verify_hmac_signature(body_bytes, sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Assinatura HMAC inválida ou ausente para Evolution API."
        )

    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Payload JSON malformado.")

    return service.process_evolution_webhook(payload)


@router.post("/chatwoot", response_model=OmnichannelWebhookResponse, summary="Webhook Chatwoot (Live Chat & Omnichannel)")
async def chatwoot_webhook(
    request: Request,
    x_chatwoot_signature: Optional[str] = Header(None, alias="X-Chatwoot-Signature"),
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256")
):
    body_bytes = await request.body()
    sig = x_chatwoot_signature or x_hub_signature_256
    if not sig or not service.verify_hmac_signature(body_bytes, sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Assinatura HMAC inválida ou ausente para Chatwoot."
        )

    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Payload JSON malformado.")

    return service.process_chatwoot_webhook(payload)


@router.post("/mautic", response_model=OmnichannelWebhookResponse, summary="Webhook Mautic 5 (Lead Scoring & Points)")
async def mautic_webhook(
    request: Request,
    x_mautic_signature: Optional[str] = Header(None, alias="X-Mautic-Signature"),
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256")
):
    body_bytes = await request.body()
    sig = x_mautic_signature or x_hub_signature_256
    if not sig or not service.verify_hmac_signature(body_bytes, sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Assinatura HMAC inválida ou ausente para Mautic."
        )

    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Payload JSON malformado.")

    return service.process_mautic_webhook(payload)
