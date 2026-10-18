# -*- coding: utf-8 -*-
"""
Vertical Slice: KeyPartners Router
Endpoints REST OpenAPI 3.1 para Consignação Cirúrgica, Gestão de Kits e Razão de Custódia.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header, status
from src.features.keypartners.schemas import (
    PartnerAgreementCreate, PartnerAgreementOut,
    ConsignmentKitCreate, ConsignmentKitOut,
    CustodyDispatchRequest, CustodyDispatchResponse,
    CustodySummaryResponse,
    SurgicalOrderCreate, SurgicalOrderApproveRequest,
    SurgicalPostopReportRequest, SurgicalPostopReportResponse,
    SurgicalOrderOut,
    KolContractCreate, KolConsumptionRecordRequest,
    KolConsumptionRecordResponse, KolEvidenceSubmitRequest,
    KolEvidenceSubmitResponse, KolContractOut,
    LoyaltyPointsCreditRequest, LoyaltyPointsCreditResponse,
    LoyaltyRedemptionRequest, LoyaltyRedemptionResponse,
    LoyaltyWalletResponse, LoyaltyRewardItem
)
from src.features.dentgo.schemas import TriggerDentgoPickupRequest, TriggerDentgoPickupResponse
from src.features.dentgo import keypartners_synergy
from src.features.keypartners import service
from src.features.keypartners import surgical_cycle
from src.features.keypartners import kol_management
from src.features.keypartners import loyalty_engine

router = APIRouter(prefix="/api/v1/keypartners", tags=["KeyPartners • Consignação Cirúrgica"])


@router.post("/agreements", response_model=PartnerAgreementOut, status_code=status.HTTP_201_CREATED, summary="Criar novo acordo de consignação e parceria")
def create_agreement(payload: PartnerAgreementCreate):
    return service.create_partner_agreement(
        partner_name=payload.partner_name,
        partner_cro_uf=payload.partner_cro_uf,
        tier=payload.tier,
        credit_limit=payload.credit_limit,
        min_monthly_revenue=payload.min_monthly_revenue,
        max_turnover_days=payload.max_turnover_days,
        account_id=payload.account_id or "0f14ffff"
    )


@router.get("/agreements", response_model=List[PartnerAgreementOut], summary="Listar acordos de parceria do tenant")
def list_agreements(account_id: str = "0f14ffff"):
    return service.list_partner_agreements(account_id=account_id)


@router.post("/kits", response_model=ConsignmentKitOut, status_code=status.HTTP_201_CREATED, summary="Cadastrar novo kit cirúrgico/protético seriadocom QR Code")
def register_kit(payload: ConsignmentKitCreate):
    return service.register_consignment_kit(
        serial_number=payload.serial_number,
        name=payload.name,
        composition_json=payload.composition_json,
        account_id=payload.account_id or "0f14ffff"
    )


@router.post("/agreements/{agreement_id}/dispatch", response_model=CustodyDispatchResponse, summary="Efetuar remessa de custódia com auditoria de limite e validade ANVISA")
def dispatch_custody(agreement_id: str, payload: CustodyDispatchRequest):
    try:
        items_dict = [it.model_dump() for it in payload.items]
        return service.dispatch_consignment_custody(
            agreement_id=agreement_id,
            items=items_dict,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/agreements/{agreement_id}/custody-summary", response_model=CustodySummaryResponse, summary="Obter extrato e saldo de itens em posse da clínica parceira")
def get_custody_summary(agreement_id: str, account_id: str = "0f14ffff"):
    try:
        return service.get_partner_custody_summary(
            agreement_id=agreement_id,
            account_id=account_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/surgical-orders", response_model=SurgicalOrderOut, status_code=status.HTTP_201_CREATED, summary="Solicitar remessa para cirurgia agendada (SOLICITADO_FIELD)")
def create_surgical_order(payload: SurgicalOrderCreate):
    try:
        items_dict = [it.model_dump() for it in payload.items]
        return surgical_cycle.create_surgical_request(
            agreement_id=payload.agreement_id,
            patient_identifier=payload.patient_identifier,
            surgery_date=payload.surgery_date,
            items=items_dict,
            field_consultant_id=payload.field_consultant_id,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/surgical-orders/{order_id}/approve", response_model=SurgicalOrderOut, summary="Analista interno aprova a remessa cirúrgica")
def approve_surgical_order(order_id: str, payload: SurgicalOrderApproveRequest):
    try:
        return surgical_cycle.approve_surgical_request(
            order_id=order_id,
            inside_analyst_id=payload.inside_analyst_id or "usr-inside-01",
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/surgical-orders/{order_id}/dispatch", response_model=SurgicalOrderOut, summary="Efetuar despacho da maleta e termo de custódia")
def dispatch_surgical_order(order_id: str, account_id: str = "0f14ffff"):
    try:
        return surgical_cycle.dispatch_surgical_order(order_id=order_id, account_id=account_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/surgical-orders/{order_id}/postop-report", response_model=SurgicalPostopReportResponse, summary="Reporte pós-operatório e faturamento automático CFOP 5.113")
def report_postop(order_id: str, payload: SurgicalPostopReportRequest):
    try:
        consumed_dict = [it.model_dump() for it in payload.consumed_items]
        return surgical_cycle.report_surgical_postop(
            order_id=order_id,
            consumed_items=consumed_dict,
            seal_photo_r2_key=payload.seal_photo_r2_key,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/surgical-orders/{order_id}", response_model=SurgicalOrderOut, summary="Consultar detalhes da ordem cirúrgica")
def get_surgical_order(order_id: str, account_id: str = "0f14ffff"):
    try:
        return surgical_cycle.get_surgical_order(order_id=order_id, account_id=account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/kol-contracts", response_model=KolContractOut, status_code=status.HTTP_201_CREATED, summary="Cadastrar novo contrato de KOL e ativo em comodato")
def create_kol(payload: KolContractCreate):
    try:
        return kol_management.create_kol_contract(
            kol_name=payload.kol_name,
            cro_uf=payload.cro_uf,
            equipment_name=payload.equipment_name,
            asset_tag=payload.asset_tag,
            min_monthly_implants_target=payload.min_monthly_implants_target,
            clinical_lectures_quota=payload.clinical_lectures_quota,
            agreement_id=payload.agreement_id,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/kol-contracts", response_model=List[KolContractOut], summary="Listar contratos de KOL e ativos em comodato")
def list_kols(account_id: str = "0f14ffff"):
    return kol_management.list_kol_contracts(account_id=account_id)


@router.post("/kol-contracts/{contract_id}/record-consumption", response_model=KolConsumptionRecordResponse, summary="Registrar consumo mensal e auditar metas de comodato")
def record_kol_consumption(contract_id: str, payload: KolConsumptionRecordRequest):
    try:
        return kol_management.record_monthly_consumption(
            contract_id=contract_id,
            consumed_implants_count=payload.consumed_implants_count,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/kol-contracts/{contract_id}/evidence", response_model=KolEvidenceSubmitResponse, summary="Submeter caso clínico ou vídeo no Cloudflare R2")
def submit_kol_evidence(contract_id: str, payload: KolEvidenceSubmitRequest):
    try:
        return kol_management.submit_clinical_evidence(
            contract_id=contract_id,
            r2_key=payload.r2_key,
            title=payload.title,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/kol-contracts/{contract_id}", response_model=KolContractOut, summary="Obter detalhes do contrato de comodato do KOL")
def get_kol(contract_id: str, account_id: str = "0f14ffff"):
    try:
        return kol_management.get_kol_contract(contract_id=contract_id, account_id=account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/consignments/{kit_serial}/trigger-dentgo-pickup", response_model=TriggerDentgoPickupResponse, summary="Acionar resgate/coleta reversa express via DENTGO")
def trigger_dentgo_pickup(kit_serial: str, payload: TriggerDentgoPickupRequest):
    try:
        return keypartners_synergy.trigger_dentgo_reverse_pickup(
            kit_serial=kit_serial,
            target_agreement_id=payload.target_agreement_id,
            pickup_address=payload.pickup_address,
            destination_address=payload.destination_address,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/loyalty/credit", response_model=LoyaltyPointsCreditResponse, summary="Creditar Moedas Cirurgicas por implantes faturados")
def credit_loyalty(payload: LoyaltyPointsCreditRequest):
    try:
        return loyalty_engine.credit_loyalty_points(
            partner_id=payload.partner_id,
            partner_name=payload.partner_name,
            implants_count=payload.implants_count,
            event_origin=payload.event_origin or "deal.won",
            reference_id=payload.reference_id,
            account_id=payload.account_id or "0f14ffff"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/loyalty/redeem", response_model=LoyaltyRedemptionResponse, summary="Resgatar recompensa ou voucher com Moedas Cirurgicas")
def redeem_loyalty(payload: LoyaltyRedemptionRequest):
    try:
        return loyalty_engine.redeem_loyalty_reward(
            partner_id=payload.partner_id,
            reward_type_or_id=payload.reward_type_or_id,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/loyalty/wallet/{partner_id}", response_model=LoyaltyWalletResponse, summary="Consultar saldo e extrato da carteira de Moedas Cirurgicas")
def get_loyalty_wallet(partner_id: str, account_id: str = "0f14ffff"):
    try:
        return loyalty_engine.get_partner_loyalty_wallet(partner_id=partner_id, account_id=account_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/loyalty/rewards", response_model=List[LoyaltyRewardItem], summary="Listar catalogo de recompensas da Moeda Cirurgica")
def list_rewards(account_id: str = "0f14ffff"):
    try:
        return loyalty_engine.list_rewards_catalog(account_id=account_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



