# -*- coding: utf-8 -*-
"""
Pydantic Schemas para o Motor DENTGO (Marketplace B2B & Logística Express)
"""

from typing import List, Optional
from pydantic import BaseModel, Field


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
    product_id: str = Field(..., description="ID do produto")
    quantity: int = Field(default=1, ge=1, description="Quantidade")


class OrderCheckoutRequest(BaseModel):
    customer_cro_uf: str = Field(..., description="CRO/UF do cirurgião solicitante")
    delivery_address: str = Field(..., description="Endereço completo da clínica/hospital")
    delivery_lat: float = Field(..., description="Latitude da entrega")
    delivery_lng: float = Field(..., description="Longitude da entrega")
    items: List[OrderItemIn] = Field(..., min_length=1, description="Lista de itens do pedido express")
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

