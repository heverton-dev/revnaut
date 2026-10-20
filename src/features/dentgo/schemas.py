# -*- coding: utf-8 -*-
"""
Pydantic Schemas para o Motor DENTGO (Marketplace B2B & Logística Express)
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator


class HubCreate(BaseModel):
    name: str = Field(..., description="Nome do Hub / Seller logístico urbano")
    cnpj: str = Field(..., description="CNPJ do Hub")
    latitude: float = Field(..., description="Latitude geográfica WGS84")
    longitude: float = Field(..., description="Longitude geográfica WGS84")
    coverage_radius_km: float = Field(default=30.0, ge=1.0, description="Raio de cobertura em km")
    on_duty_schedule: Optional[str] = Field(default="24h", description="Horário de plantão cirúrgico")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class HubOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    name: str
    cnpj: str
    latitude: float
    longitude: float
    coverage_radius_km: float
    on_duty_schedule: str
    is_active: int
    created_at: str


class HubInventoryCreate(BaseModel):
    product_id: str = Field(..., description="Código do produto implantável/instrumental")
    product_name: str = Field(..., description="Descrição técnica")
    anvisa_reg: str = Field(..., description="Registro ANVISA obrigatório")
    batch_number: str = Field(..., description="Lote de fabricação")
    quantity_available: int = Field(default=1, ge=1, description="Saldo disponível no Hub")
    unit_price: float = Field(..., ge=0.0, description="Preço unitário em R$")
    sterilization_expiry_date: str = Field(..., description="Data de validade da esterilização (YYYY-MM-DD)")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class HubInventoryOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    hub_id: str
    account_id: str
    product_id: str
    product_name: str
    anvisa_reg: str
    batch_number: str
    quantity_available: int
    unit_price: float
    sterilization_expiry_date: str
    created_at: str


class EmergencySearchRequest(BaseModel):
    delivery_lat: float = Field(..., description="Latitude do local de entrega / cirurgia")
    delivery_lng: float = Field(..., description="Longitude do local de entrega")
    product_id: str = Field(..., description="ID do implante ou componente de emergência")
    required_qty: int = Field(default=1, ge=1, description="Quantidade solicitada com urgência")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class EmergencySearchResultOut(BaseModel):
    model_config = {"extra": "allow"}
    hub_id: str
    hub_name: str
    distance_km: float
    estimated_eta_minutes: int
    urgency_fee: float
    product_id: str
    product_name: str
    anvisa_reg: str
    batch_number: str
    quantity_available: int
    unit_price: float


class OrderItemIn(BaseModel):
    product_id: Optional[str] = Field(default=None, description="ID do produto")
    sku: Optional[str] = Field(default=None, description="SKU do produto")
    product_name: Optional[str] = Field(default=None, description="Descrição do produto")
    quantity: int = Field(default=1, ge=1, description="Quantidade")
    unit_price: Optional[float] = Field(default=None, description="Preço unitário em R$")

    @model_validator(mode="before")
    @classmethod
    def _fill_product_id_or_sku(cls, values: Any) -> Any:
        if isinstance(values, dict):
            pid = values.get("product_id")
            sku = values.get("sku")
            if not pid and sku:
                values["product_id"] = sku
            elif not sku and pid:
                values["sku"] = pid
        return values


OrderItemRequest = OrderItemIn


class OrderCheckoutRequest(BaseModel):
    customer_cro_uf: str = Field(..., description="CRO/UF do cirurgião solicitante")
    customer_name: Optional[str] = Field(default=None, description="Nome do cliente/cirurgião solicitante")
    delivery_address: str = Field(..., description="Endereço completo da clínica/hospital")
    delivery_lat: float = Field(..., description="Latitude da entrega")
    delivery_lng: float = Field(..., description="Longitude da entrega")
    payment_method: Optional[str] = Field(default="CORPORATE_CREDIT", description="Método de pagamento corporativo ou PIX")
    items: List[OrderItemIn] = Field(..., min_length=1, description="Lista de itens do pedido express")
    voucher_code: Optional[str] = Field(default=None, description="Código de voucher para isenção da taxa de urgência")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class OrderOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    hub_id: str
    customer_cro_uf: str
    cro_verified: int
    delivery_address: str
    delivery_lat: float
    delivery_lng: float
    distance_km: float
    estimated_eta_minutes: int
    items_json: str
    subtotal: float
    urgency_fee: float
    total_amount: float
    status: str
    courier_id: Optional[str] = None
    seal_code: Optional[str] = None
    delivery_pin: Optional[str] = None
    proof_of_delivery_r2_key: Optional[str] = None
    recipient_signature_name: Optional[str] = None
    delivered_at: Optional[str] = None
    created_at: str


class OrderPickingRequest(BaseModel):
    scanned_barcode: str = Field(..., description="Código de barras ou DataMatrix bipado na separação")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class OrderSealRequest(BaseModel):
    seal_code: str = Field(..., description="Código do lacre inviolável da maleta térmica")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class OrderAssignCourierRequest(BaseModel):
    courier_id: str = Field(..., description="ID ou matrícula do entregador especializado")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class OrderDeliveryVerifyRequest(BaseModel):
    entered_pin: str = Field(..., min_length=4, max_length=4, description="PIN de 4 dígitos informado pelo cirurgião/recepcionista")
    proof_photo_r2_key: str = Field(..., description="Chave R2 da foto comprovante de entrega (POD)")
    recipient_name: str = Field(..., description="Nome do recebedor na clínica")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class TriggerDentgoPickupRequest(BaseModel):
    target_agreement_id: Optional[str] = Field(default=None, description="Acordo de parceria da clínica destino para realocação")
    pickup_address: Optional[str] = Field(default="Endereço da clínica de origem", description="Endereço de coleta")
    destination_address: Optional[str] = Field(default="Endereço da clínica de destino", description="Endereço de entrega após hub")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class TriggerDentgoPickupResponse(BaseModel):
    model_config = {"extra": "allow"}
    success: bool
    status: str
    pickup_order_id: str
    kit_serial: str
    origin_agreement_id: str
    target_agreement_id: Optional[str] = None


class ReplenishmentOrderResponse(BaseModel):
    model_config = {"extra": "allow"}
    status: str
    replenishment_order_id: str
    agreement_id: str
    hub_id: str
    items_count: int


class FinancialSplitRequest(BaseModel):
    platform_take_rate_pct: float = Field(default=5.0, ge=1.0, le=30.0, description="Percentual de comissão da plataforma RevNault (ex: 5.0%)")
    payment_method: str = Field(default="PIX_INSTANT", description="Método de pagamento: PIX_INSTANT ou CORPORATE_CREDIT")
    agreement_id: Optional[str] = Field(default=None, description="ID do acordo KeyPartners para faturamento corporativo quinzenal")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class FinancialSplitOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    order_id: str
    gross_amount: float
    items_amount: float
    delivery_fee_total: float
    platform_take_rate_pct: float
    platform_fee_amount: float
    courier_net_payout: float
    seller_net_payout: float
    payment_method: str
    agreement_id: Optional[str] = None
    settlement_status: str
    created_at: str


class FefoScanRequest(BaseModel):
    reference_date: Optional[str] = Field(default=None, description="Data de referência para varredura (YYYY-MM-DD)")
    discount_percentage: float = Field(default=35.0, ge=5.0, le=70.0, description="Percentual de desconto Flash Deal")
    max_target_surgeons: int = Field(default=50, ge=1, le=200, description="Limite máximo de cirurgiões segmentados")
    radius_km: float = Field(default=50.0, ge=5.0, le=200.0, description="Raio geográfico em km ao redor do Hub")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class FefoTargetSurgeonItem(BaseModel):
    model_config = {"extra": "allow"}
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    cro: Optional[str] = None
    cro_uf: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    monthly_implants_volume: Optional[int] = None


class FefoFlashDealItem(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    hub_id: str
    hub_name: str
    inventory_id: str
    product_id: str
    product_name: str
    batch_number: str
    original_quantity: int
    available_quantity: int
    original_unit_price: float
    discount_percentage: float
    flash_unit_price: float
    sterilization_expiry_date: str
    months_to_expire: float
    target_surgeons_count: int
    status: str
    checkout_one_click_url: str
    target_surgeons: Optional[List[FefoTargetSurgeonItem]] = None
    created_at: Optional[str] = None


class FefoScanResponse(BaseModel):
    model_config = {"extra": "allow"}
    scanned_batches: int
    created_deals_count: int
    reference_date: str
    created_deals: List[FefoFlashDealItem]


class FefoReserveRequest(BaseModel):
    surgeon_cro_uf: str = Field(..., description="CRO-UF do cirurgião (ex: 12345-SP)")
    surgeon_name: str = Field(..., min_length=2, description="Nome do cirurgião")
    quantity: int = Field(default=1, ge=1, description="Quantidade de unidades a reservar")
    contact_id: Optional[int] = Field(default=None, description="ID do contato cirurgião se cadastrado")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class FefoReserveResponse(BaseModel):
    model_config = {"extra": "allow"}
    reservation_id: str
    deal_id: str
    surgeon_name: str
    surgeon_cro_uf: str
    quantity_reserved: int
    total_amount: float
    remaining_available: int
    deal_status: str
    status: str



