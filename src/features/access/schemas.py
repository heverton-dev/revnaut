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


class AccessCatalogRouteOut(BaseModel):
    route_id: str
    label: str
    journey_group: str
    default_facility: Optional[str] = None
    facilities: List[AccessFacilityOut] = Field(default_factory=list)


class AccessRoleGrantsOut(BaseModel):
    role_id: str
    role_name: str
    is_admin: bool = False
    editable: bool = False
    landing_route: Optional[str] = None
    landing_facility: Optional[str] = None
    allow_submenus: bool = False
    grants: List[AccessRouteOut] = Field(default_factory=list)


class AccessMatrixOut(BaseModel):
    source: str
    catalog: List[AccessCatalogRouteOut] = Field(default_factory=list)
    roles: List[AccessRoleGrantsOut] = Field(default_factory=list)
    editable_role_ids: List[str] = Field(default_factory=list)
    viewer_role_id: Optional[str] = None
    viewer_is_superadmin: bool = False


class AccessRouteGrantIn(BaseModel):
    route_id: str
    menu_priority: int = 999
    allow_submenus: bool = False
    facilities: List[str] = Field(default_factory=list)


class AccessSaveGrantsIn(BaseModel):
    routes: List[AccessRouteGrantIn] = Field(default_factory=list)


class AccessSaveGrantsOut(BaseModel):
    role_id: str
    route_count: int
    facility_count: int
    updated: bool = True


class AccessCreateRoleIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: Optional[str] = None
    default_data_scope: str = Field(default="team")
    # Grants iniciais opcionais (mesmo shape do PUT grants)
    routes: List[AccessRouteGrantIn] = Field(default_factory=list)


class AccessCreateRoleOut(BaseModel):
    role_id: str
    name: str
    is_admin: bool = False
    route_count: int = 0
    created: bool = True


class AccessAssignUserIn(BaseModel):
    user_id: str = Field(min_length=1)
    # opcional: também atualiza o label `users.role` para o nome do cargo
    sync_role_label: bool = True


class AccessAssignUserOut(BaseModel):
    user_id: str
    role_id: str
    role_name: str
    assigned: bool = True


class AccessUnassignUserOut(BaseModel):
    user_id: str
    role_id: str = ""
    role_name: str = "Sem cargo"
    unassigned: bool = True


class AccessRoleUserOut(BaseModel):
    user_id: str
    name: str
    email: str
    role_label: str
    role_id: Optional[str] = None
    is_active: bool = True
    is_superadmin: bool = False
