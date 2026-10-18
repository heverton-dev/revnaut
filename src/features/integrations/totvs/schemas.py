# -*- coding: utf-8 -*-
"""
Schemas OpenAPI 3.1 & Pydantic para Conector TOTVS Protheus (SA1 / SC5 / SC6).
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TotvsCustomerSA1(BaseModel):
    A1_COD: Optional[str] = Field(None, description="Código do cliente no Protheus")
    A1_LOJA: str = Field(default="01", description="Loja do cliente")
    A1_NOME: str = Field(..., description="Razão Social ou Nome do Cirurgião/Clínica")
    A1_CGC: str = Field(..., description="CPF ou CNPJ (apenas dígitos ou formatado)")
    A1_X_CRO: Optional[str] = Field(None, description="Número de registro no CRO e UF (ex: SP-89450)")
    A1_LC: float = Field(default=0.0, description="Limite de crédito liberado no ERP em R$")
    A1_END: Optional[str] = Field(None, description="Endereço comercial da clínica")
    A1_MUN: Optional[str] = Field(None, description="Município / Cidade")
    A1_EST: Optional[str] = Field(None, description="UF / Estado (ex: SP, PR)")


class TotvsOrderItemSC6(BaseModel):
    C6_ITEM: str = Field(default="01", description="Número sequencial do item")
    C6_PRODUTO: str = Field(..., description="Código do produto/implante no ERP (B1_COD)")
    C6_QTD: float = Field(..., gt=0, description="Quantidade vendida ou consumida")
    C6_PRCVEN: float = Field(..., gt=0, description="Preço unitário de venda")
    C6_VALOR: float = Field(..., gt=0, description="Valor total do item (QTD * PRCVEN)")


class TotvsOrderSC5(BaseModel):
    C5_NUM: Optional[str] = Field(None, description="Número gerado do pedido de venda Protheus")
    C5_CLIENTE: str = Field(..., description="Código do cliente (SA1 A1_COD)")
    C5_LOJACLI: str = Field(default="01", description="Loja do cliente")
    C5_CONDPAG: str = Field(default="001", description="Condição de pagamento no ERP")
    C5_VEND1: Optional[str] = Field(None, description="Código do consultor/vendedor responsável")
    C5_TOTAL: float = Field(..., gt=0, description="Valor total do pedido em R$")
    deal_id: Optional[str] = Field(None, description="ID do negócio de origem no Revnaut")
    idempotency_key: str = Field(..., description="Chave única de idempotência para evitar duplicidade")
    items: List[TotvsOrderItemSC6] = Field(..., min_length=1, description="Lista de itens do pedido (SC6)")


class TotvsSyncResponse(BaseModel):
    success: bool
    action: str
    entity: str
    idempotency_key: str
    status: str
    data: Dict[str, Any]


class OutboxItemOut(BaseModel):
    id: str
    account_id: str
    integration_type: str
    idempotency_key: str
    status: str
    attempts: int
    last_error: Optional[str] = None
    created_at: str
    updated_at: str


class ErpConsignmentItem(BaseModel):
    product_id: str = Field(..., description="Código do produto no ERP")
    product_name: str = Field(..., description="Descrição técnica do produto")
    ncm: str = Field(default="90211010", description="NCM fiscal do produto")
    batch_number: str = Field(..., description="Lote rastreável de fabricação")
    quantity: int = Field(default=1, ge=1, description="Quantidade de itens")
    unit_price: float = Field(..., ge=0.0, description="Preço unitário em R$")


class ErpRemittanceRequest(BaseModel):
    erp_type: str = Field(default="totvs_protheus", description="ERP de destino: totvs_protheus | sap_b1 | sankhya")
    agreement_id: str = Field(..., description="ID do termo/acordo KeyPartners")
    emitter_uf: str = Field(default="SP", description="UF de origem da indústria/distribuidor")
    recipient_uf: str = Field(default="SP", description="UF de destino da clínica/cirurgião")
    recipient_cnpj: str = Field(..., description="CNPJ ou CPF do destinatário")
    recipient_name: str = Field(..., description="Razão social ou nome do destinatário")
    items: List[ErpConsignmentItem] = Field(..., min_length=1, description="Itens da remessa consignada")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class ErpSettlementRequest(BaseModel):
    erp_type: str = Field(default="totvs_protheus", description="ERP de destino: totvs_protheus | sap_b1 | sankhya")
    agreement_id: str = Field(..., description="ID do termo de consignação")
    surgical_report_id: Optional[str] = Field(None, description="ID do reporte cirúrgico de consumo")
    emitter_uf: str = Field(default="SP", description="UF de origem do emitente")
    recipient_uf: str = Field(default="SP", description="UF de destino do destinatário")
    recipient_cnpj: str = Field(..., description="CNPJ ou CPF do destinatário")
    recipient_name: str = Field(..., description="Razão social ou nome do destinatário")
    consumed_items: List[ErpConsignmentItem] = Field(..., min_length=1, description="Itens implantados no paciente")
    returned_unconsumed_items: Optional[List[ErpConsignmentItem]] = Field(default=None, description="Itens devolvidos intactos")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class ErpFiscalInvoiceOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    erp_type: str
    flow_type: str
    reference_id: Optional[str] = None
    cfop: str
    nfe_number: str
    nfe_series: str = "1"
    nfe_access_key: str
    recipient_cnpj_cpf: Optional[str] = None
    recipient_name: str
    total_invoice_value: float
    xml_r2_key: str
    danfe_pdf_r2_key: str
    xml_url: Optional[str] = None
    danfe_pdf_url: Optional[str] = None
    status: str
    sefaz_protocol: Optional[str] = None
    windmill_job_id: Optional[str] = None
    created_at: Optional[str] = None


class ErpSettlementResponse(BaseModel):
    model_config = {"extra": "allow"}
    success: bool
    settlement_job_id: str
    symbolic_return_invoice: Dict[str, Any]
    sale_invoice: Dict[str, Any]

