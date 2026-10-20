# -*- coding: utf-8 -*-
"""Leitura de grants de navegação a partir do SQLite (fase 2)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core.database import get_connection
from src.features.access.schemas import (
    AccessFacilityOut,
    AccessMeOut,
    AccessRouteOut,
)

DEFAULT_ACCOUNT = "0f14ffff"

# Fallback espelhando navConfig quando a tabela de grants ainda não existe/está vazia
_FALLBACK_BY_ROLE_ID: Dict[str, List[tuple]] = {
    "role-field": [
        ("deals", 1, 0),
        ("dentgo", 2, 0),
        ("contacts", 3, 0),
        ("keypartners", 4, 0),
        ("video_sos", 5, 0),
        ("intelligence", 6, 0),
        ("market_intel", 7, 0),
    ],
    "role-inside": [
        ("omnichannel", 1, 0),
        ("scheduling", 2, 0),
        ("deals", 3, 0),
        ("scoring", 4, 0),
        ("contacts", 5, 0),
        ("contracts", 6, 0),
        ("market_intel", 7, 0),
    ],
    "role-logistics": [
        ("dentgo", 1, 1),
        ("keypartners", 2, 1),
        ("support", 3, 1),
        ("settings", 4, 1),
    ],
    "role-clinical": [
        ("support", 1, 1),
        ("video_sos", 2, 0),
        ("imaging", 3, 0),
        ("scheduling", 4, 0),
        ("omnichannel", 5, 0),
    ],
    "role-manager": [
        ("dashboard", 1, 0),
        ("deals", 2, 0),
        ("market_intel", 3, 1),
        ("contacts", 4, 1),
        ("keypartners", 5, 1),
        ("contracts", 6, 1),
        ("marketing", 7, 0),
        ("rbac", 8, 1),
    ],
    "role-access-admin": [
        ("dashboard", 1, 0),
        ("rbac", 2, 1),
        ("settings", 3, 1),
        ("analytics", 4, 1),
    ],
    "role-ceo": "ALL",
}


def _table_exists(conn, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return row is not None


def _load_catalog_routes(conn) -> List[Dict[str, Any]]:
    if not _table_exists(conn, "access_catalog_routes"):
        return []
    rows = conn.execute(
        """
        SELECT route_id, label, journey_group, default_facility
          FROM access_catalog_routes
         ORDER BY journey_group, route_id
        """
    ).fetchall()
    return [
        {
            "route_id": r[0],
            "label": r[1],
            "journey_group": r[2],
            "default_facility": r[3],
        }
        for r in rows
    ]


def _load_facilities(conn, route_ids: List[str]) -> Dict[str, List[AccessFacilityOut]]:
    if not route_ids or not _table_exists(conn, "access_catalog_facilities"):
        return {}
    placeholders = ",".join("?" for _ in route_ids)
    rows = conn.execute(
        f"""
        SELECT route_id, facility_id, label, sort_order
          FROM access_catalog_facilities
         WHERE route_id IN ({placeholders})
         ORDER BY route_id, sort_order, facility_id
        """,
        route_ids,
    ).fetchall()
    out: Dict[str, List[AccessFacilityOut]] = {}
    for route_id, facility_id, label, sort_order in rows:
        out.setdefault(route_id, []).append(
            AccessFacilityOut(
                facility_id=facility_id,
                label=label,
                sort_order=int(sort_order or 999),
            )
        )
    return out


def _load_role_grants(conn, account_id: str, role_id: str) -> List[Dict[str, Any]]:
    if not _table_exists(conn, "role_route_grants"):
        return []
    rows = conn.execute(
        """
        SELECT route_id, menu_priority, allow_submenus, is_visible_menu
          FROM role_route_grants
         WHERE account_id = ? AND role_id = ? AND is_visible_menu = 1
         ORDER BY menu_priority, route_id
        """,
        (account_id, role_id),
    ).fetchall()
    return [
        {
            "route_id": r[0],
            "menu_priority": int(r[1] or 999),
            "allow_submenus": bool(r[2]),
            "route_id_raw": r[0],
        }
        for r in rows
    ]


def _load_role_facilities(
    conn, account_id: str, role_id: str
) -> Dict[str, List[str]]:
    if not _table_exists(conn, "role_facility_grants"):
        return {}
    rows = conn.execute(
        """
        SELECT route_id, facility_id, sort_order
          FROM role_facility_grants
         WHERE account_id = ? AND role_id = ?
         ORDER BY route_id, sort_order, facility_id
        """,
        (account_id, role_id),
    ).fetchall()
    out: Dict[str, List[str]] = {}
    for route_id, facility_id, _sort in rows:
        out.setdefault(route_id, []).append(facility_id)
    return out


def _catalog_meta(conn) -> Dict[str, Dict[str, Any]]:
    return {r["route_id"]: r for r in _load_catalog_routes(conn)}


def _build_route_out(
    route_id: str,
    meta: Dict[str, Any],
    menu_priority: int,
    allow_submenus: bool,
    facility_ids: List[str],
    all_facilities: List[AccessFacilityOut],
) -> AccessRouteOut:
    if facility_ids:
        by_id = {f.facility_id: f for f in all_facilities}
        facilities = [by_id[fid] for fid in facility_ids if fid in by_id]
    else:
        facilities = []
    return AccessRouteOut(
        route_id=route_id,
        label=meta.get("label", route_id),
        journey_group=meta.get("journey_group", "Outros"),
        menu_priority=menu_priority,
        allow_submenus=allow_submenus,
        facilities=facilities,
    )


def get_access_me(
    user: Dict[str, Any],
    account_id: Optional[str] = None,
) -> AccessMeOut:
    """Resolve grants de navegação do usuário efetivo (com impersonation)."""
    account = account_id or user.get("account_id") or DEFAULT_ACCOUNT
    role_id = user.get("role_id") or None
    role_name = user.get("role") or ""
    is_super = bool(user.get("is_superadmin"))
    user_id = user.get("id") or ""

    # role-ceo canônico mesmo sem role_id em bases antigas
    if is_super or (role_id or "") == "role-ceo":
        role_id = role_id or "role-ceo"
        is_super = True

    can_manage = is_super or role_id == "role-access-admin"

    conn = get_connection()
    try:
        catalog = _catalog_meta(conn)
        route_ids = list(catalog.keys())
        fac_map = _load_facilities(conn, route_ids)

        grants = _load_role_grants(conn, account, role_id or "")
        fac_grants = _load_role_facilities(conn, account, role_id or "")

        source = "db"
        if not grants:
            fb = _FALLBACK_BY_ROLE_ID.get(role_id or "", [])
            if fb == "ALL" or (is_super and route_ids):
                source = "catalog_full"
                routes = []
                for i, rid in enumerate(route_ids, start=1):
                    meta = catalog[rid]
                    all_f = fac_map.get(rid, [])
                    routes.append(
                        _build_route_out(
                            rid,
                            meta,
                            menu_priority=i,
                            allow_submenus=True,
                            facility_ids=[f.facility_id for f in all_f],
                            all_facilities=all_f,
                        )
                    )
                landing = routes[0].route_id if routes else "dashboard"
                landing_fac = (
                    routes[0].facilities[0].facility_id
                    if routes and routes[0].facilities
                    else None
                )
                return AccessMeOut(
                    user_id=user_id,
                    account_id=account,
                    role_id=role_id,
                    role_name=role_name,
                    display_name=role_name,
                    is_superadmin=is_super,
                    can_manage_access=can_manage,
                    landing_route=landing,
                    landing_facility=landing_fac,
                    allow_submenus=True,
                    source=source,
                    routes=routes,
                )
            if fb:
                source = "empty"
                routes = []
                for rid, pri, allow_sub in fb:
                    meta = catalog.get(rid, {"label": rid, "journey_group": "Outros"})
                    all_f = fac_map.get(rid, [])
                    routes.append(
                        _build_route_out(
                            rid,
                            meta,
                            menu_priority=pri,
                            allow_submenus=bool(allow_sub),
                            facility_ids=[f.facility_id for f in all_f],
                            all_facilities=all_f,
                        )
                    )
            else:
                source = "empty"
                routes = []
        else:
            routes = []
            for g in grants:
                rid = g["route_id"]
                meta = catalog.get(rid, {"label": rid, "journey_group": "Outros"})
                all_f = fac_map.get(rid, [])
                routes.append(
                    _build_route_out(
                        rid,
                        meta,
                        menu_priority=g["menu_priority"],
                        allow_submenus=g["allow_submenus"],
                        facility_ids=fac_grants.get(rid, []),
                        all_facilities=all_f,
                    )
                )

        if not routes:
            # último recurso: nunca menu vazio no backend
            routes = [
                AccessRouteOut(
                    route_id="deals",
                    label="Funil de Negociações",
                    journey_group="Pipeline Comercial",
                    menu_priority=1,
                    allow_submenus=False,
                    facilities=[],
                )
            ]
            landing = "deals"
            landing_fac = None
            allow_sub = False
        else:
            landing = routes[0].route_id
            landing_fac = (
                routes[0].facilities[0].facility_id if routes[0].facilities else None
            )
            allow_sub = any(r.allow_submenus for r in routes)

        return AccessMeOut(
            user_id=user_id,
            account_id=account,
            role_id=role_id,
            role_name=role_name,
            display_name=role_name,
            is_superadmin=is_super,
            can_manage_access=can_manage,
            landing_route=landing,
            landing_facility=landing_fac,
            allow_submenus=allow_sub,
            source=source,
            routes=routes,
        )
    finally:
        conn.close()
