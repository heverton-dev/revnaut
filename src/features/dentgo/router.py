# -*- coding: utf-8 -*-
"""
Vertical Slice: DENTGO Router
Endpoints REST OpenAPI 3.1 para Marketplace B2B, Hubs Urbanos e Entregas Cirúrgicas Expressas.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from src.features.dentgo.schemas import (
    HubCreate, HubOut,
    HubInventoryCreate, HubInventoryOut,
    EmergencySearchRequest, EmergencySearchResultOut,
    OrderCheckoutRequest, OrderOut,
    OrderPickingRequest, OrderSealRequest,
    OrderAssignCourierRequest, OrderDeliveryVerifyRequest
)
from src.features.dentgo import service
from src.features.dentgo import logistics_dispatch

router = APIRouter(prefix="/api/v1/dentgo", tags=["DENTGO • Marketplace B2B & Logística Express"])


@router.post("/hubs", response_model=HubOut, status_code=status.HTTP_201_CREATED, summary="Cadastrar novo Hub Logístico Urbano")
def create_hub(payload: HubCreate):
    return service.create_hub(
        name=payload.name,
        cnpj=payload.cnpj,
        latitude=payload.latitude,
        longitude=payload.longitude,
        coverage_radius_km=payload.coverage_radius_km,
        on_duty_schedule=payload.on_duty_schedule or "24h",
        account_id=payload.account_id or "0f14ffff"
    )


@router.get("/hubs", response_model=List[HubOut], summary="Listar Hubs parceiros ativos")
def list_hubs(account_id: str = "0f14ffff"):
    return service.list_hubs(account_id=account_id)


@router.post("/hubs/{hub_id}/inventory", response_model=HubInventoryOut, status_code=status.HTTP_201_CREATED, summary="Adicionar estoque de pronta-entrega ao Hub")
def add_inventory(hub_id: str, payload: HubInventoryCreate):
    try:
        return service.add_hub_inventory(
            hub_id=hub_id,
            product_id=payload.product_id,
            product_name=payload.product_name,
            anvisa_reg=payload.anvisa_reg,
            batch_number=payload.batch_number,
            quantity_available=payload.quantity_available,
            unit_price=payload.unit_price,
            sterilization_expiry_date=payload.sterilization_expiry_date,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/hubs/search-emergency", response_model=List[EmergencySearchResultOut], summary="Busca geolocalizada de emergência cirúrgica (Haversine & ETA)")
def search_emergency(payload: EmergencySearchRequest):
    return service.search_emergency_supply(
        delivery_lat=payload.delivery_lat,
        delivery_lng=payload.delivery_lng,
        product_id=payload.product_id,
        required_qty=payload.required_qty,
        account_id=payload.account_id or "0f14ffff"
    )


@router.post("/orders/checkout", response_model=OrderOut, status_code=status.HTTP_201_CREATED, summary="Checkout de pedido express com validação de CRO sanitário")
def checkout_order(payload: OrderCheckoutRequest):
    try:
        items_dict = [it.model_dump() for it in payload.items]
        return service.create_express_order(
            customer_cro_uf=payload.customer_cro_uf,
            delivery_address=payload.delivery_address,
            delivery_lat=payload.delivery_lat,
            delivery_lng=payload.delivery_lng,
            items=items_dict,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders/{order_id}", response_model=OrderOut, summary="Consultar dados do pedido express")
def get_order(order_id: str, account_id: str = "0f14ffff"):
    try:
        return service.get_order(order_id=order_id, account_id=account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/orders/{order_id}/picking", response_model=OrderOut, summary="Bipar DataMatrix/lote e iniciar separação")
def order_picking(order_id: str, payload: OrderPickingRequest):
    try:
        return logistics_dispatch.bip_picking(
            order_id=order_id,
            scanned_barcode=payload.scanned_barcode,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orders/{order_id}/seal", response_model=OrderOut, summary="Lacrar maleta térmica e gerar PIN de conferência")
def order_seal(order_id: str, payload: OrderSealRequest):
    try:
        return logistics_dispatch.seal_package(
            order_id=order_id,
            seal_code=payload.seal_code,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orders/{order_id}/assign-courier", response_model=OrderOut, summary="Atribuir entregador cirúrgico especializado")
def order_assign_courier(order_id: str, payload: OrderAssignCourierRequest):
    try:
        return logistics_dispatch.assign_courier(
            order_id=order_id,
            courier_id=payload.courier_id,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orders/{order_id}/start-transit", response_model=OrderOut, summary="Iniciar rota de entrega express em tempo real")
def order_start_transit(order_id: str, account_id: str = "0f14ffff"):
    try:
        return logistics_dispatch.start_transit(
            order_id=order_id,
            account_id=account_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orders/{order_id}/verify-delivery", response_model=OrderOut, summary="Validar PIN, anexar foto POD no R2 e concluir entrega")
def order_verify_delivery(order_id: str, payload: OrderDeliveryVerifyRequest):
    try:
        return logistics_dispatch.verify_and_complete_delivery(
            order_id=order_id,
            entered_pin=payload.entered_pin,
            proof_photo_r2_key=payload.proof_photo_r2_key,
            recipient_name=payload.recipient_name,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

