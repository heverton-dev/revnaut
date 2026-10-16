# -*- coding: utf-8 -*-
"""
Vertical Slice: Consignments Schemas (Estoque Consignado e Caixas Cirúrgicas da Indústria Dental)
"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class ConsignmentItemOut(BaseModel):
    id: int
    consignment_id: str
    product_sku: str
    product_name: str
    batch_number: str
    quantity_allocated: int
    quantity_consumed: int
    unit_price: float


class ConsignmentOut(BaseModel):
    id: str
    account_id: str
    contact_id: int
    clinic_name: str
    box_code: str
    total_items: int
    consumed_items: int
    last_audit_date: Optional[str] = None
    status: str
    created_at: str
    items: List[ConsignmentItemOut] = []


class ConsignmentConsumptionCreate(BaseModel):
    product_sku: str = Field(..., min_length=2, description="SKU do implante ou componente consumido")
    quantity: int = Field(default=1, ge=1, description="Quantidade de envelopes estéreis abertos na cirurgia")
    patient_protocol: Optional[str] = Field(default=None, description="Prontuário ou protocolo cirúrgico")


class ConsignmentConsumptionOut(BaseModel):
    status: str
    consignment_id: str
    product_sku: str
    quantity_consumed: int
    remaining_quantity: int
    total_billed: float
    replacement_order_triggered: bool
