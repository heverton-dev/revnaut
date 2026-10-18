# -*- coding: utf-8 -*-
"""
Vertical Slice: Intelligence Router (FastAPI)
Endpoints para Grafo Clínico KOL, Vínculos N:N e Radar Anti-Churn Odontológico.
"""

from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from src.features.intelligence import service
from src.features.intelligence import transcription_worker
from src.features.intelligence import granola_copilot
from src.features.intelligence import surgical_rag
from src.features.intelligence.schemas import (
    ContactInstitutionCreate, ContactInstitutionOut,
    ClinicalGraphResponse, KOLSpeakerResponse,
    ChurnRiskResponse, IntelligenceOperationResponse,
    TranscriptionProcessRequest, TranscriptionProcessResponse,
    TranscriptionItemOut,
    CopilotExtractAndApplyRequest, CopilotExtractAndApplyResponse,
    CatalogChunkIngestRequest, CatalogChunkIngestResponse,
    CatalogRagQueryRequest, CatalogRagQueryResponse
)


router = APIRouter(prefix="/api/v1/intelligence", tags=["Inteligência Clínica & STT"])


@router.get("/churn-risk", response_model=ChurnRiskResponse, summary="Radar Anti-Churn & Inteligência de Carteira (RFM Odontológico)")
def get_churn_risk(
    account_id: str = "0f14ffff",
    days_threshold: Optional[int] = Query(None, description="Filtrar clientes com dias de atraso acima deste limite")
):
    """
    Algoritmo determinístico de RFM odontológico:
    Cruza o ciclo médio de recompra de implantes/componentes com a data da última compra/deal ganho.
    Identifica clientes em atraso crítico (> 30 dias quando ciclo <= 20) com risco de migrar para concorrentes.
    """
    return service.get_churn_risk_radar(account_id=account_id, days_threshold=days_threshold)


@router.get("/clinical-graph", response_model=ClinicalGraphResponse, summary="Grafo de Relacionamento Clínico KOL (Ecossistema do Implante)")
def get_clinical_graph(account_id: str = "0f14ffff"):
    """
    Retorna os nós (Cirurgiões, Clínicas, Laboratórios CAD/CAM, Universidades, Radiologias) e arestas
    do ecossistema odontológico, identificando Key Opinion Leaders (KOLs) e Speakers acadêmicos.
    """
    return service.get_clinical_graph(account_id=account_id)


@router.get("/kol-speakers", response_model=KOLSpeakerResponse, summary="Listar Key Opinion Leaders (KOLs) e Speakers Oficiais")
def list_kol_speakers(account_id: str = "0f14ffff"):
    """Lista cirurgiões identificados como KOLs com suas redes de ensino, clínicas e laboratórios afiliados."""
    return service.list_kol_speakers(account_id=account_id)


@router.post("/links", response_model=ContactInstitutionOut, status_code=status.HTTP_201_CREATED, summary="Vincular Cirurgião a Clínica, Lab CAD/CAM ou Universidade")
def create_institution_link(data: ContactInstitutionCreate, account_id: str = "0f14ffff"):
    """Cria relacionamento N:N entre o Cirurgião e uma Instituição do ecossistema."""
    try:
        return service.link_contact_institution(data=data, account_id=account_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/links/contact/{contact_id}", response_model=List[ContactInstitutionOut], summary="Listar vínculos institucionais de um Cirurgião")
def get_contact_links(contact_id: int, account_id: str = "0f14ffff"):
    """Lista todas as clínicas onde opera, labs que utiliza e faculdades onde leciona."""
    return service.list_contact_institutions(contact_id=contact_id, account_id=account_id)


@router.delete("/links/{link_id}", response_model=IntelligenceOperationResponse, summary="Remover vínculo institucional")
def remove_institution_link(link_id: str, account_id: str = "0f14ffff"):
    """Exclui o vínculo N:N."""
    deleted = service.unlink_contact_institution(link_id=link_id, account_id=account_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vínculo não encontrado.")
    return {"success": True, "message": "Vínculo removido com sucesso."}


@router.post("/transcriptions/process", response_model=TranscriptionProcessResponse, summary="Processar e diarizar áudio de reunião/ligação")
def process_transcription(payload: TranscriptionProcessRequest):
    try:
        return transcription_worker.process_call_audio(
            call_id=payload.call_id,
            account_id=payload.account_id or "0f14ffff",
            dialogue_text=payload.dialogue_text,
            audio_url=payload.audio_url,
            duration_seconds=payload.duration_seconds or 0.0,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transcriptions/{transcription_id}", response_model=TranscriptionItemOut, summary="Obter transcrição e diarização por ID")
def get_transcription(transcription_id: str):
    item = transcription_worker.get_transcription_by_id(transcription_id)
    if not item:
        raise HTTPException(status_code=404, detail="Transcrição não encontrada")
    return item


@router.get("/transcriptions/deal/{deal_id}", response_model=List[TranscriptionItemOut], summary="Listar transcrições de reuniões do Deal")
def list_deal_transcriptions(deal_id: str, account_id: str = "0f14ffff"):
    return transcription_worker.list_transcriptions_for_deal(deal_id=deal_id, account_id=account_id)


@router.post("/copilot/extract-and-apply", response_model=CopilotExtractAndApplyResponse, summary="Copiloto Granola: Extrair notas da reunião e atualizar Deal com Zero-Touch")
def copilot_extract_and_apply(payload: CopilotExtractAndApplyRequest):
    try:
        extraction = granola_copilot.extract_meeting_intelligence(
            transcription_text=payload.transcription_text,
            deal_id=payload.deal_id,
            account_id=payload.account_id or "0f14ffff"
        )
        applied = granola_copilot.apply_copilot_intelligence_to_deal(
            deal_id=payload.deal_id,
            extraction=extraction,
            account_id=payload.account_id or "0f14ffff"
        )
        return {
            "success": True,
            "deal_id": payload.deal_id,
            "extraction": extraction,
            "objections_count": applied["objections_count"],
            "tasks_count": applied["tasks_count"],
            "updated_value": applied["updated_value"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/catalog-rag/ingest",
    response_model=CatalogChunkIngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingestar fragmento de catálogo cirúrgico com embedding vetorial"
)
def ingest_catalog_chunk(payload: CatalogChunkIngestRequest):
    try:
        return surgical_rag.ingest_catalog_chunk(
            source_manual=payload.source_manual,
            page_number=payload.page_number,
            implant_line=payload.implant_line,
            bone_type=payload.bone_type,
            content_chunk=payload.content_chunk,
            drill_sequence=payload.drill_sequence,
            recommended_implant_torque_ncm=payload.recommended_implant_torque_ncm,
            recommended_prosthetic_torque_ncm=payload.recommended_prosthetic_torque_ncm,
            account_id=payload.account_id or "0f14ffff"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/catalog-rag/query",
    response_model=CatalogRagQueryResponse,
    summary="Consultar copiloto RAG de torques e sequência de fresagem"
)
def query_catalog_rag(payload: CatalogRagQueryRequest):
    try:
        return surgical_rag.query_surgical_catalog(
            query=payload.query,
            bone_type=payload.bone_type,
            min_similarity=payload.min_similarity if payload.min_similarity is not None else 0.65,
            account_id=payload.account_id or "0f14ffff"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



