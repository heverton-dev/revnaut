# -*- coding: utf-8 -*-
"""
Vertical Slice: Institutions Router (FastAPI)
"""

from __future__ import annotations
from typing import List
from fastapi import APIRouter, status
from src.features.institutions.schemas import InstitutionCreate, InstitutionOut
from src.features.institutions import service

router = APIRouter(prefix="/api/v1/institutions", tags=["Instituições de Ensino Odonto"])


@router.get("", response_model=List[InstitutionOut], summary="Listar polos de ensino e faculdades credenciadas (Mandic, ABO)")
def get_institutions():
    return service.list_institutions()


@router.post("", response_model=InstitutionOut, status_code=status.HTTP_201_CREATED, summary="Credenciar nova instituição ou polo de especialização")
def create_institution(data: InstitutionCreate):
    return service.create_institution(data)
