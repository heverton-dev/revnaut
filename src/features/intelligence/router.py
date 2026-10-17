# -*- coding: utf-8 -*-
"""
Vertical Slice: Intelligence Router (FastAPI)
Endpoints para Grafo Clínico KOL, Vínculos N:N e Radar Anti-Churn Odontológico.
"""

from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from src.features.intelligence import service
from src.features.intelligence.schemas import (
    ContactInstitutionCreate, ContactInstitutionOut,
    ClinicalGraphResponse, KOLSpeakerResponse,
    ChurnRiskResponse, IntelligenceOperationResponse
)

router = APIRouter(prefix="/api/v1/intelligence", tags=["Inteligência Clínica & Anti-Churn"])


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
