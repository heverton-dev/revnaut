# -*- coding: utf-8 -*-
"""
Vertical Slice: Intelligence Router (FastAPI)
Endpoints para Grafo Clínico KOL, Vínculos N:N e Radar Anti-Churn Odontológico.
"""

from __future__ import annotations
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.features.auth.router import get_current_user
from src.features.auth.schemas import UserProfileOut
from src.features.intelligence import service
from src.features.intelligence import transcription_worker
from src.features.intelligence import granola_copilot
from src.features.intelligence import surgical_rag
from src.features.intelligence import superset_embedded
from src.features.intelligence import text_to_sql_agent
from src.features.intelligence import predictive_inventory
from src.features.intelligence import clinical_margin
from src.features.intelligence import health_score_hsc
from src.features.intelligence.orthanc_dicom import OrthancDicomClient
from src.features.intelligence.schemas import (
    ContactInstitutionCreate, ContactInstitutionOut,
    ClinicalGraphResponse, KOLSpeakerResponse,
    ChurnRiskResponse, IntelligenceOperationResponse,
    TranscriptionProcessRequest, TranscriptionProcessResponse,
    TranscriptionItemOut,
    CopilotExtractAndApplyRequest, CopilotExtractAndApplyResponse,
    CatalogChunkIngestRequest, CatalogChunkIngestResponse,
    CatalogRagQueryRequest, CatalogRagQueryResponse,
    SupersetGuestTokenRequest, SupersetGuestTokenResponse,
    AnalyticsDatasetExportRequest, AnalyticsDatasetExportResponse,
    TextToSqlExecuteRequest, TextToSqlExecuteResponse,
    SokCalculationRequest, SokCalculationResponse,
    PrCalculationRequest, PrCalculationResponse,
    PredictiveInventoryReportResponse,
    ClinicalMarginCalculateRequest, ClinicalMarginCalculateResponse,
    ClinicalMarginSummaryReportResponse,
    HealthScoreCalculateRequest, HealthScoreCalculateResponse,
    HealthScoreSummaryResponse,
    ImagingStudyUploadPresignRequest, ImagingStudyUploadPresignResponse,
    ImagingStudyViewerTokenResponse, ImagingStudyOut,
    ImagingStudyListResponse
)


router = APIRouter(prefix="/api/v1/intelligence", tags=["Inteligência Clínica & STT"])
imaging_router = APIRouter(prefix="/api/v1/imaging", tags=["Imagiologia Médica Orthanc DICOM"])
orthanc_client = OrthancDicomClient()


@router.get("/churn-risk", response_model=ChurnRiskResponse, summary="Radar Anti-Churn & Inteligência de Carteira (RFM Odontológico)")
def get_churn_risk(
    current_user: UserProfileOut = Depends(get_current_user),
    days_threshold: Optional[int] = Query(None, description="Filtrar clientes com dias de atraso acima deste limite")
):
    """
    Algoritmo determinístico de RFM odontológico:
    Cruza o ciclo médio de recompra de implantes/componentes com a data da última compra/deal ganho.
    Identifica clientes em atraso crítico (> 30 dias quando ciclo <= 20) com risco de migrar para concorrentes.

    TICKET-DASH-04: o tenant é derivado exclusivamente do usuário autenticado.
    """
    return service.get_churn_risk_radar(account_id=current_user.account_id, days_threshold=days_threshold)


@router.get("/clinical-graph", response_model=ClinicalGraphResponse, summary="Grafo de Relacionamento Clínico KOL (Ecossistema do Implante)")
def get_clinical_graph(current_user: UserProfileOut = Depends(get_current_user)):
    """
    Retorna os nós (Cirurgiões, Clínicas, Laboratórios CAD/CAM, Universidades, Radiologias) e arestas
    do ecossistema odontológico, identificando Key Opinion Leaders (KOLs) e Speakers acadêmicos.

    TICKET-DASH-04: o tenant é derivado exclusivamente do usuário autenticado.
    """
    return service.get_clinical_graph(account_id=current_user.account_id)


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


_log = logging.getLogger(__name__)


def _resolve_bi_actor(
    payload_user_id: Optional[str],
    payload_account_id: Optional[str],
    current_user: UserProfileOut,
) -> tuple[str, str]:
    """
    DASH4-01/02: identidade e tenant do BI vêm da sessão assinada. user_id diferente do da sessão
    só é aceito para superadmin (impersonação); o tenant nunca é trocado pelo corpo da requisição.
    """
    if payload_account_id and payload_account_id != current_user.account_id:
        raise HTTPException(status_code=403, detail="Tenant diferente do tenant da sessão.")
    if payload_user_id and payload_user_id != current_user.id and not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Não é permitido agir em nome de outro usuário.")
    return payload_user_id or current_user.id, current_user.account_id


def _bi_http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, PermissionError):
        return HTTPException(status_code=403, detail=str(exc))
    if isinstance(exc, ValueError):
        return HTTPException(status_code=400, detail=str(exc))
    _log.exception("Falha no endpoint BI de inteligência")
    return HTTPException(status_code=500, detail="Erro interno ao processar a requisição BI.")


@router.post(
    "/bi/guest-token",
    response_model=SupersetGuestTokenResponse,
    summary="Gerar Guest Token JWT com Row-Level Security (RLS) para Apache Superset Embedded"
)
def get_superset_guest_token(
    payload: SupersetGuestTokenRequest,
    current_user: UserProfileOut = Depends(get_current_user)
):
    user_id, account_id = _resolve_bi_actor(payload.user_id, payload.account_id, current_user)
    try:
        return superset_embedded.generate_superset_guest_token(
            user_id=user_id,
            dashboard_id=payload.dashboard_id,
            dashboard_type=payload.dashboard_type or "industry_consignment",
            account_id=account_id
        )
    except Exception as e:
        raise _bi_http_error(e)


@router.post(
    "/bi/export-dataset",
    response_model=AnalyticsDatasetExportResponse,
    summary="Exportar dataset analítico para Cloudflare R2 com RLS"
)
def export_dataset(
    payload: AnalyticsDatasetExportRequest,
    current_user: UserProfileOut = Depends(get_current_user)
):
    user_id, account_id = _resolve_bi_actor(payload.user_id, payload.account_id, current_user)
    try:
        return superset_embedded.export_analytics_dataset(
            dataset_name=payload.dataset_name,
            user_id=user_id,
            format=payload.format or "csv",
            account_id=account_id
        )
    except Exception as e:
        raise _bi_http_error(e)


@router.post(
    "/bi/text-to-sql",
    response_model=TextToSqlExecuteResponse,
    summary="Executar consulta analítica Text-to-SQL com proteção AST e RLS"
)
def execute_text_to_sql(
    payload: TextToSqlExecuteRequest,
    current_user: UserProfileOut = Depends(get_current_user)
):
    user_id, account_id = _resolve_bi_actor(payload.user_id, payload.account_id, current_user)
    try:
        return text_to_sql_agent.execute_analytical_query(
            natural_language_query=payload.natural_language_query,
            raw_sql=payload.raw_sql,
            user_id=user_id,
            account_id=account_id
        )
    except Exception as e:
        raise _bi_http_error(e)


@router.post(
    "/inventory/sok",
    response_model=SokCalculationResponse,
    summary="Calcular Score de Ociosidade de Kit Consignado (SOK)"
)
def calculate_kit_idle_score(payload: SokCalculationRequest):
    """
    Equacao deterministica do Score de Ociosidade de Kit (SOK):
    SOK = (D_sem_cirurgia / D_limite_contratual) * 0.6 + (V_kit_imobilizado / V_faturamento_medio_mensal) * 0.4
    Quando SOK >= 1.0, sinaliza alerta de ociosidade e sugere ordem de coleta reversa DENTGO.
    """
    try:
        return predictive_inventory.calculate_kit_idle_score_sok(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/inventory/pr",
    response_model=PrCalculationResponse,
    summary="Calcular Ponto de Reposicao de Estoque Consignado (PR)"
)
def calculate_replenishment_point(payload: PrCalculationRequest):
    """
    Equacao deterministica do Ponto de Reposicao (PR):
    PR = (C_medio_diario * T_entrega_dentgo) + ES
    Quando o saldo atual <= PR, gera Deal de Recompra Ativa no funil e dispara mensagem WhatsApp.
    """
    try:
        return predictive_inventory.calculate_replenishment_point_pr(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/inventory/report/{agreement_id}",
    response_model=PredictiveInventoryReportResponse,
    summary="Obter historico de scores de estoque preditivo do parceiro"
)
def get_inventory_scores_report(
    agreement_id: str,
    account_id: str = Query("0f14ffff", description="ID do tenant")
):
    try:
        return predictive_inventory.get_predictive_inventory_report(
            agreement_id=agreement_id,
            account_id=account_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/margin/calculate",
    response_model=ClinicalMarginCalculateResponse,
    summary="Calcular Margem Liquida Real de Procedimento Clinico Cirurgico"
)
def calculate_clinical_margin(payload: ClinicalMarginCalculateRequest):
    """
    Motor financeiro para clinicas e franquias odontologicas:
    Margem Liquida = V_procedimento - (C_insumos + C_lab + C_honorario + C_hora_cadeira + C_imposto)
    Emite alerta no dashboard quando a margem liquida for inferior a 15.0%.
    """
    try:
        return clinical_margin.calculate_procedure_net_margin(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/margin/summary/{clinic_id}",
    response_model=ClinicalMarginSummaryReportResponse,
    summary="Obter relatorio consolidado de rentabilidade e margens da clinica"
)
def get_clinic_margin_summary_report(
    clinic_id: str,
    account_id: str = Query("0f14ffff", description="ID do tenant")
):
    try:
        return clinical_margin.get_clinic_margin_summary(
            clinic_id=clinic_id,
            account_id=account_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/health-score/calculate",
    response_model=HealthScoreCalculateResponse,
    summary="Calcular Health Score Cirurgico (HSC) e Disparar Playbook Anti-Churn"
)
def calculate_health_score(payload: HealthScoreCalculateRequest):
    """
    Motor deterministico de saude cirurgica da conta:
    HSC = 0.4 * F_cirurgica + 0.3 * G_consignado + 0.2 * S_atendimento + 0.1 * E_canal
    Dispara playbooks de resgate (HSC < 40) ou promocao/MGM (HSC > 75).
    """
    try:
        return health_score_hsc.calculate_surgical_health_score(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health-score/history/{partner_id}",
    response_model=HealthScoreSummaryResponse,
    summary="Consultar historico de avaliacoes HSC do parceiro"
)
def get_health_score_history(
    partner_id: str,
    account_id: str = Query("0f14ffff", description="ID do tenant")
):
    try:
        return health_score_hsc.get_health_score_history(
            partner_id=partner_id,
            account_id=account_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# Endpoints de Imagiologia Médica Orthanc DICOM & 3D (TICKET-39)
# Suportados tanto em /api/v1/imaging/studies quanto /api/v1/intelligence/imaging/studies
# ==============================================================================

@imaging_router.post(
    "/studies/upload-presign",
    response_model=ImagingStudyUploadPresignResponse,
    summary="Gerar URL pré-assinada para upload de Tomografia DICOM ou STL no Cloudflare R2"
)
@router.post(
    "/imaging/studies/upload-presign",
    response_model=ImagingStudyUploadPresignResponse,
    summary="Gerar URL pré-assinada para upload de Tomografia DICOM ou STL no Cloudflare R2 (alias)"
)
def create_imaging_upload_presign(
    payload: ImagingStudyUploadPresignRequest,
    account_id: str = Query("0f14ffff", description="ID do tenant")
):
    try:
        acc = payload.account_id or account_id
        return orthanc_client.create_upload_presign(
            file_name=payload.file_name,
            study_type=payload.study_type,
            jaw_type=payload.jaw_type,
            slice_count=payload.slice_count or 1,
            patient_name=payload.patient_name,
            deal_id=payload.deal_id,
            ticket_id=payload.ticket_id,
            implant_site=payload.implant_site,
            anonymize_lgpd=payload.anonymize_lgpd if payload.anonymize_lgpd is not None else True,
            account_id=acc,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@imaging_router.get(
    "/studies/{study_id}/viewer-token",
    response_model=ImagingStudyViewerTokenResponse,
    summary="Gerar token assinado e URLs de streaming 3D para visualização médica"
)
@router.get(
    "/imaging/studies/{study_id}/viewer-token",
    response_model=ImagingStudyViewerTokenResponse,
    summary="Gerar token assinado e URLs de streaming 3D para visualização médica (alias)"
)
def get_imaging_study_viewer_token(
    study_id: str,
    account_id: str = Query("0f14ffff", description="ID do tenant")
):
    return orthanc_client.generate_viewer_session(study_id=study_id, account_id=account_id)


@imaging_router.get(
    "/studies/{study_id}",
    response_model=ImagingStudyOut,
    summary="Consultar metadados anatômicos e técnicos do estudo de imagem"
)
@router.get(
    "/imaging/studies/{study_id}",
    response_model=ImagingStudyOut,
    summary="Consultar metadados anatômicos e técnicos do estudo de imagem (alias)"
)
def get_imaging_study_by_id(
    study_id: str,
    account_id: str = Query("0f14ffff", description="ID do tenant")
):
    return orthanc_client.get_study(study_id=study_id, account_id=account_id)


@imaging_router.get(
    "/studies",
    response_model=ImagingStudyListResponse,
    summary="Listar estudos tomográficos e escaneamentos 3D do tenant"
)
@router.get(
    "/imaging/studies",
    response_model=ImagingStudyListResponse,
    summary="Listar estudos tomográficos e escaneamentos 3D do tenant (alias)"
)
def list_imaging_studies(
    deal_id: Optional[str] = Query(None, description="Filtrar por Deal/Cirurgia Guiada"),
    study_type: Optional[str] = Query(None, description="Filtrar por tipo (DICOM_CBCT, INTRAORAL_STL)"),
    account_id: str = Query("0f14ffff", description="ID do tenant")
):
    items = orthanc_client.list_studies(account_id=account_id, deal_id=deal_id, study_type=study_type)
    return {
        "studies": items,
        "total": len(items)
    }



