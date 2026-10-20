# -*- coding: utf-8 -*-
"""Schemas do permissionamento granular (fase 2)."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class AccessFacilityOut(BaseModel):
    facility_id: str
    label: str
    sort_order: int = 999


class AccessRouteOut(BaseModel):
    route_id: str
    label: str
    journey_group: str
    menu_priority: int = 999
    allow_submenus: bool = False
    facilities: List[AccessFacilityOut] = Field(default_factory=list)


class AccessMeOut(BaseModel):
    user_id: str
    account_id: str
    role_id: Optional[str] = None
    role_name: str
    display_name: str
    is_superadmin: bool = False
    can_manage_access: bool = False
    landing_route: str
    landing_facility: Optional[str] = None
    allow_submenus: bool = False
    source: str = Field(description="db | catalog_full | empty")
    routes: List[AccessRouteOut] = Field(default_factory=list)
