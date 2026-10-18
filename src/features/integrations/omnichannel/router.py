# -*- coding: utf-8 -*-
"""
Router FastAPI para Gateway Unificado de Webhooks Omnichannel.
Valida assinatura HMAC SHA-256 e sincroniza dados em tempo real.
"""

import json
from typing import List, Optional
from fastapi import APIRouter, Request, Header, HTTPException, status
from src.features.integrations.omnichannel.schemas import (
    OmnichannelWebhookResponse, WhatsappInstanceCreate,
    WhatsappInstanceOut, EvolutionWebhookResponse,
    Omnichannel360ContextOut, ChatwootSyncResponse
)
from src.features.integrations.omnichannel import service
from src.features.integrations.omnichannel import evolution_cluster
from src.features.integrations.omnichannel import evolution_webhook_router
from src.features.integrations.omnichannel import chatwoot_bridge

router = APIRouter(tags=["Integrações • Omnichannel & Webhooks"])


@router.post("/api/v1/webhooks/evolution", response_model=OmnichannelWebhookResponse, summary="Webhook Evolution API v2 (WhatsApp Inbound)")
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


@router.post("/api/v1/webhooks/chatwoot", response_model=OmnichannelWebhookResponse, summary="Webhook Chatwoot (Live Chat & Omnichannel)")
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


@router.post("/api/v1/webhooks/mautic", response_model=OmnichannelWebhookResponse, summary="Webhook Mautic 5 (Lead Scoring & Points)")
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


from src.features.integrations.omnichannel.schemas import MauticCampaignActionResponse
from src.features.campaigns.mautic_bridge import process_mautic_campaign_action


@router.post("/api/v1/webhooks/mautic/campaign-action", response_model=MauticCampaignActionResponse, summary="Despachante Determinístico de Ações de Campanha do Mautic")
async def mautic_campaign_action_endpoint(
    request: Request,
    x_mautic_signature: Optional[str] = Header(None, alias="X-Mautic-Signature"),
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256")
):
    body_bytes = await request.body()
    sig = x_mautic_signature or x_hub_signature_256
    if not sig or not service.verify_hmac_signature(body_bytes, sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Assinatura HMAC inválida ou ausente para Mautic Campaign Action."
        )

    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Payload JSON malformado.")

    result = process_mautic_campaign_action(payload)
    return MauticCampaignActionResponse(**result)


# --- Evolution API v2 Cluster Sharding & Inbound Event Endpoints ---

@router.post("/api/v1/omnichannel/whatsapp/instances", response_model=WhatsappInstanceOut, status_code=status.HTTP_201_CREATED, summary="Provisionar instância de WhatsApp balanceada no cluster")
def create_instance(payload: WhatsappInstanceCreate):
    return evolution_cluster.provision_whatsapp_instance(
        instance_name=payload.instance_name,
        consultant_user_id=payload.consultant_user_id,
        phone_number=payload.phone_number,
        account_id=payload.account_id or "0f14ffff"
    )


@router.get("/api/v1/omnichannel/whatsapp/instances", response_model=List[WhatsappInstanceOut], summary="Listar instâncias do cluster")
def list_whatsapp_instances(account_id: str = "0f14ffff"):
    return evolution_cluster.list_instances(account_id=account_id)


@router.get("/api/v1/omnichannel/whatsapp/instances/{instance_name}", response_model=WhatsappInstanceOut, summary="Obter detalhes da instância")
def get_whatsapp_instance(instance_name: str, account_id: str = "0f14ffff"):
    try:
        return evolution_cluster.get_instance(instance_name=instance_name, account_id=account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/api/v1/omnichannel/webhook/evolution", response_model=EvolutionWebhookResponse, summary="Webhook direto Evolution API (CALL_OFFER e mensagens)")
def evolution_direct_webhook(payload: dict):
    return evolution_webhook_router.handle_evolution_event(payload)


@router.get("/api/v1/omnichannel/context/{contact_identifier}", response_model=Omnichannel360ContextOut, summary="Agregador de Contexto 360° para Sidebar de Atendimento (KeyPartners + DENTGO)")
def get_omnichannel_context(contact_identifier: str, account_id: str = "0f14ffff"):
    return chatwoot_bridge.get_omnichannel_360_context(contact_identifier=contact_identifier, account_id=account_id)


@router.post("/api/v1/omnichannel/chatwoot/sync-contact/{contact_id}", response_model=ChatwootSyncResponse, summary="Sincronizar contato do CRM com o Chatwoot")
def sync_chatwoot_contact(contact_id: int, account_id: str = "0f14ffff"):
    try:
        return chatwoot_bridge.sync_contact_to_chatwoot(contact_id=contact_id, account_id=account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))



