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


# ---------------------------------------------------------------------------
# Fase 4 — matriz de grants (Admin de Acesso / Super Admin)
# ---------------------------------------------------------------------------

_PROTECTED_ROLE_IDS = frozenset({"role-ceo", "role-access-admin"})


def _is_superadmin(user: Dict[str, Any]) -> bool:
    return bool(user.get("is_superadmin")) or (user.get("role_id") or "") == "role-ceo"


# Prefixo de path → rotas aceitas (qualquer uma) para autorização de API de domínio
_PATH_ROUTE_RULES: tuple = (
    ("/api/v1/deals", ("deals",)),
    ("/api/v1/pipelines", ("deals",)),
    ("/api/v1/contacts", ("contacts",)),
    ("/api/v1/omnichannel", ("omnichannel",)),
    ("/api/v1/dentgo", ("dentgo",)),
    ("/api/v1/keypartners", ("keypartners",)),
    ("/api/v1/scoring", ("scoring",)),
    ("/api/v1/campaigns", ("marketing",)),
    ("/api/v1/intelligence", ("intelligence",)),
    ("/api/v1/imaging", ("imaging",)),
    ("/api/v1/market-intel", ("market_intel",)),
    ("/api/v1/competitors", ("market_intel",)),
    ("/api/v1/tickets", ("support",)),
    ("/api/v1/hierarchy", ("rbac", "settings")),
    ("/api/v1/documenso", ("contracts",)),
    # Cal.com + pós-op + fluxos de receita (página de agenda/suporte/marketing)
    ("/api/v1/automations", ("scheduling", "support", "marketing")),
    # ERP TOTVS (config fiscal e emissão de pedido)
    ("/api/v1/integrations/totvs", ("settings", "deals", "dentgo")),
)

# Nunca passa por grant de navegação (auth, webhooks, infra…)
_PATH_EXEMPT_PREFIXES = (
    "/api/v1/auth",
    "/api/v1/access",
    "/api/v1/health",
    "/api/v1/webhooks",
    "/api/v1/storage",
    "/api/v1/quarteto",
    "/api/v1/tasks",
    "/api/v1/mcp",
)


def required_routes_for_path(path: str) -> Optional[tuple]:
    """Retorna tupla de route_ids exigidos (aceita qualquer uma) ou None se não há gate."""
    if any(path.startswith(p) for p in _PATH_EXEMPT_PREFIXES):
        return None
    for prefix, routes in _PATH_ROUTE_RULES:
        if path.startswith(prefix):
            return routes
    return None


def user_can_access_routes(
    user: Dict[str, Any],
    account_id: str,
    required: Optional[tuple],
) -> bool:
    """True se o usuário pode bater a API; superadmin sempre pode; required=None sem gate."""
    if required is None:
        return True
    if _is_superadmin(user):
        return True
    role_id = user.get("role_id") or None
    if not role_id:
        # fallback string → role_id
        resolved = resolve_role_id_from_name(user.get("role") or "")
        role_id = resolved
    if not role_id:
        # Legado/testes de escopo sem role_id canônico: o gate de grants
        # não se aplica (isolamento de dados continua no service de domínio).
        return True
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT route_id FROM role_route_grants "
            "WHERE account_id = ? AND role_id = ? AND is_visible_menu = 1",
            (account_id, role_id),
        ).fetchall()
        granted = {r[0] for r in rows}
        if not granted:
            # Sem grants no catálogo: role legado (r_cons, r_greg…) — gate de
            # navegação não cobre; autorização de linha continua no service de domínio.
            if role_id not in _FALLBACK_BY_ROLE_ID and role_id not in (
                "role-field",
                "role-inside",
                "role-logistics",
                "role-clinical",
                "role-manager",
                "role-ceo",
                "role-access-admin",
            ):
                return True
            fb = _FALLBACK_BY_ROLE_ID.get(role_id, [])
            if fb == "ALL":
                return True
            granted = {x[0] for x in fb} if fb else set()
            if not granted:
                return True
        return any(r in granted for r in required)
    finally:
        conn.close()


def resolve_role_id_from_name(role_name: str) -> Optional[str]:
    s = (role_name or "").lower()
    if "super admin" in s or "diretoria" in s or "administrador" in s:
        return "role-ceo"
    if "gerente" in s or "manager" in s:
        return "role-manager"
    if "campo" in s or "externo" in s:
        return "role-field"
    if "atendimento" in s or "interno" in s or "inside" in s:
        return "role-inside"
    if "logística" in s or "logistica" in s or "estoque" in s or "expedi" in s:
        return "role-logistics"
    if "clínico" in s or "clinico" in s or "pós" in s or "pos-venda" in s:
        return "role-clinical"
    if "acesso" in s and "admin" in s:
        return "role-access-admin"
    return None


def _editable_role_ids(conn, user: Dict[str, Any], account_id: str) -> List[str]:
    if _is_superadmin(user):
        rows = conn.execute(
            "SELECT id FROM roles WHERE account_id = ? ORDER BY id",
            (account_id,),
        ).fetchall()
        return [r[0] for r in rows if r[0] not in _PROTECTED_ROLE_IDS]
    if (user.get("role_id") or "") != "role-access-admin":
        return []
    rows = conn.execute(
        "SELECT editable_role_id FROM access_admin_scopes "
        "WHERE account_id = ? AND admin_role_id = 'role-access-admin'",
        (account_id,),
    ).fetchall()
    return [r[0] for r in rows]


def can_manage_role(
    user: Dict[str, Any],
    account_id: str,
    target_role_id: str,
) -> bool:
    if _is_superadmin(user):
        return True
    if target_role_id in _PROTECTED_ROLE_IDS:
        return False
    if (user.get("role_id") or "") != "role-access-admin":
        return False
    conn = get_connection()
    try:
        return target_role_id in _editable_role_ids(conn, user, account_id)
    finally:
        conn.close()


def list_access_matrix(user: Dict[str, Any], account_id: Optional[str] = None) -> Dict[str, Any]:
    account = account_id or user.get("account_id") or DEFAULT_ACCOUNT
    conn = get_connection()
    try:
        catalog_rows = _load_catalog_routes(conn)
        fac_map = _load_facilities(conn, [r["route_id"] for r in catalog_rows])
        catalog = []
        for r in catalog_rows:
            catalog.append(
                {
                    "route_id": r["route_id"],
                    "label": r["label"],
                    "journey_group": r["journey_group"],
                    "default_facility": r.get("default_facility"),
                    "facilities": [
                        f.model_dump() for f in fac_map.get(r["route_id"], [])
                    ],
                }
            )

        editable = set(_editable_role_ids(conn, user, account))
        role_rows = conn.execute(
            "SELECT id, name, is_admin FROM roles WHERE account_id = ? ORDER BY is_admin DESC, name ASC",
            (account,),
        ).fetchall()

        roles_out = []
        for rid, rname, is_admin in role_rows:
            grants = _load_role_grants(conn, account, rid)
            fac_grants = _load_role_facilities(conn, account, rid)
            meta = {c["route_id"]: c for c in catalog_rows}
            route_list = []
            for g in sorted(grants, key=lambda x: (x["menu_priority"], x["route_id"])):
                rid_r = g["route_id"]
                m = meta.get(rid_r, {})
                all_f = fac_map.get(rid_r, [])
                granted_ids = fac_grants.get(rid_r, [])
                if g["allow_submenus"] and not granted_ids:
                    granted_ids = [f.facility_id for f in all_f]
                route_list.append(
                    {
                        "route_id": rid_r,
                        "label": m.get("label", rid_r),
                        "journey_group": m.get("journey_group", "Outros"),
                        "menu_priority": g["menu_priority"],
                        "allow_submenus": g["allow_submenus"],
                        "facilities": [
                            {
                                "facility_id": fid,
                                "label": next(
                                    (f.label for f in all_f if f.facility_id == fid),
                                    fid,
                                ),
                                "sort_order": next(
                                    (f.sort_order for f in all_f if f.facility_id == fid),
                                    999,
                                ),
                            }
                            for fid in granted_ids
                        ],
                    }
                )
            landing = route_list[0]["route_id"] if route_list else None
            landing_fac = (
                route_list[0]["facilities"][0]["facility_id"]
                if route_list and route_list[0]["facilities"]
                else None
            )
            roles_out.append(
                {
                    "role_id": rid,
                    "role_name": rname,
                    "is_admin": bool(is_admin),
                    "editable": rid in editable or _is_superadmin(user),
                    "landing_route": landing,
                    "landing_facility": landing_fac,
                    "allow_submenus": any(x["allow_submenus"] for x in route_list),
                    "grants": route_list,
                }
            )

        return {
            "source": "db",
            "catalog": catalog,
            "roles": roles_out,
            "editable_role_ids": sorted(editable),
            "viewer_role_id": user.get("role_id"),
            "viewer_is_superadmin": _is_superadmin(user),
        }
    finally:
        conn.close()


def save_role_grants(
    user: Dict[str, Any],
    account_id: str,
    role_id: str,
    routes: List[Dict[str, Any]],
) -> Dict[str, Any]:
    if not can_manage_role(user, account_id, role_id):
        raise PermissionError(
            "Sem permissão para alterar este cargo (escopo do Admin de Acesso)."
        )

    conn = get_connection()
    try:
        with conn:
            # Zera grants antigos deste cargo (replace total)
            conn.execute(
                "DELETE FROM role_route_grants WHERE account_id = ? AND role_id = ?",
                (account_id, role_id),
            )
            conn.execute(
                "DELETE FROM role_facility_grants WHERE account_id = ? AND role_id = ?",
                (account_id, role_id),
            )

            priority = 0
            fac_count = 0
            for item in routes:
                priority += 1
                route_id = item["route_id"]
                menu_priority = int(item.get("menu_priority") or priority)
                allow_sub = 1 if item.get("allow_submenus") else 0
                facilities = list(item.get("facilities") or [])

                # Se marcou submenus sem lista, libera todas as facilities da rota
                if allow_sub and not facilities:
                    rows = conn.execute(
                        "SELECT facility_id FROM access_catalog_facilities WHERE route_id = ?",
                        (route_id,),
                    ).fetchall()
                    facilities = [r[0] for r in rows]
                if not allow_sub:
                    # sem submenus: só default facility (se houver)
                    drow = conn.execute(
                        "SELECT default_facility FROM access_catalog_routes WHERE route_id = ?",
                        (route_id,),
                    ).fetchone()
                    facilities = [drow[0]] if drow and drow[0] else []

                conn.execute(
                    "INSERT OR IGNORE INTO role_route_grants "
                    "(account_id, role_id, route_id, is_visible_menu, menu_priority, allow_submenus, created_at) "
                    "VALUES (?, ?, ?, 1, ?, ?, datetime('now'))",
                    (account_id, role_id, route_id, menu_priority, allow_sub),
                )
                for i, fac in enumerate(facilities, start=1):
                    conn.execute(
                        "INSERT OR IGNORE INTO role_facility_grants "
                        "(account_id, role_id, route_id, facility_id, sort_order, created_at) "
                        "VALUES (?, ?, ?, ?, ?, datetime('now'))",
                        (account_id, role_id, route_id, fac, i),
                    )
                    fac_count += 1

            conn.execute(
                "INSERT INTO access_audit_log "
                "(account_id, actor_user_id, action, target_role_id, payload_json, created_at) "
                "VALUES (?, ?, 'grants.replace', ?, ?, datetime('now'))",
                (
                    account_id,
                    user.get("id") or "",
                    role_id,
                    str(len(routes)),
                ),
            )

        return {
            "role_id": role_id,
            "route_count": len(routes),
            "facility_count": fac_count,
            "updated": True,
        }
    finally:
        conn.close()


def can_create_roles(user: Dict[str, Any]) -> bool:
    return _is_superadmin(user) or (user.get("role_id") or "") == "role-access-admin"


def create_operational_role(
    user: Dict[str, Any],
    account_id: str,
    name: str,
    description: Optional[str],
    default_data_scope: str,
    routes: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Cria cargo operacional (nunca admin de plataforma) + grants iniciais."""
    if not can_create_roles(user):
        raise PermissionError("Sem permissão para criar cargos.")

    import re
    import uuid

    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")[:40] or "cargo"
    role_id = f"role_{slug}_{uuid.uuid4().hex[:6]}"

    if role_id in _PROTECTED_ROLE_IDS:
        raise ValueError("Identificador reservado.")

    conn = get_connection()
    try:
        with conn:
            exists = conn.execute(
                "SELECT 1 FROM roles WHERE account_id = ? AND lower(name) = lower(?)",
                (account_id, name),
            ).fetchone()
            if exists:
                raise ValueError(f"Já existe um cargo com o nome “{name}”.")

            scope = default_data_scope if default_data_scope in (
                "self",
                "team",
                "all",
                "individual",
                "business_unit",
                "tenant_global",
            ) else "team"

            conn.execute(
                "INSERT INTO roles (id, account_id, name, description, default_data_scope, is_admin, created_at) "
                "VALUES (?, ?, ?, ?, ?, 0, datetime('now'))",
                (role_id, account_id, name, description or "", scope),
            )

            # Grants iniciais (usa mesmo caminho do PUT quando houver rotas)
            if routes:
                for i, item in enumerate(routes, start=1):
                    route_id = item.get("route_id")
                    if not route_id:
                        continue
                    allow_sub = 1 if item.get("allow_submenus") else 0
                    pri = int(item.get("menu_priority") or i)
                    conn.execute(
                        "INSERT OR IGNORE INTO role_route_grants "
                        "(account_id, role_id, route_id, is_visible_menu, menu_priority, allow_submenus, created_at) "
                        "VALUES (?, ?, ?, 1, ?, ?, datetime('now'))",
                        (account_id, role_id, route_id, pri, allow_sub),
                    )
                    facs = list(item.get("facilities") or [])
                    if allow_sub and not facs:
                        facs = [
                            r[0]
                            for r in conn.execute(
                                "SELECT facility_id FROM access_catalog_facilities WHERE route_id = ?",
                                (route_id,),
                            ).fetchall()
                        ]
                    if not allow_sub:
                        drow = conn.execute(
                            "SELECT default_facility FROM access_catalog_routes WHERE route_id = ?",
                            (route_id,),
                        ).fetchone()
                        facs = [drow[0]] if drow and drow[0] else []
                    for j, fac in enumerate(facs, start=1):
                        conn.execute(
                            "INSERT OR IGNORE INTO role_facility_grants "
                            "(account_id, role_id, route_id, facility_id, sort_order, created_at) "
                            "VALUES (?, ?, ?, ?, ?, datetime('now'))",
                            (account_id, role_id, route_id, fac, j),
                        )

            # Access-admin: novo cargo entra no escopo editável dele
            if (user.get("role_id") or "") == "role-access-admin" and not _is_superadmin(user):
                conn.execute(
                    "INSERT OR IGNORE INTO access_admin_scopes "
                    "(account_id, admin_role_id, editable_role_id, created_at) "
                    "VALUES (?, 'role-access-admin', ?, datetime('now'))",
                    (account_id, role_id),
                )

            conn.execute(
                "INSERT INTO access_audit_log "
                "(account_id, actor_user_id, action, target_role_id, payload_json, created_at) "
                "VALUES (?, ?, 'role.create', ?, ?, datetime('now'))",
                (account_id, user.get("id") or "", role_id, name),
            )

        n = conn.execute(
            "SELECT COUNT(*) FROM role_route_grants WHERE role_id = ?", (role_id,)
        ).fetchone()[0]
        return {
            "role_id": role_id,
            "name": name,
            "is_admin": False,
            "route_count": int(n),
            "created": True,
        }
    finally:
        conn.close()


def list_role_users(
    user: Dict[str, Any],
    account_id: str,
    role_id: str,
) -> List[Dict[str, Any]]:
    """Lista usuários do cargo (quem pode gerenciar o cargo)."""
    if not can_manage_role(user, account_id, role_id):
        raise PermissionError("Sem permissão para listar membros deste cargo.")

    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, name, email, role, role_id, COALESCE(is_active,1), COALESCE(is_superadmin,0) "
            "FROM users WHERE account_id = ? AND role_id = ? "
            "ORDER BY name ASC",
            (account_id, role_id),
        ).fetchall()
        return [
            {
                "user_id": r[0],
                "name": r[1],
                "email": r[2],
                "role_label": r[3],
                "role_id": r[4],
                "is_active": bool(r[5]),
                "is_superadmin": bool(r[6]),
            }
            for r in rows
        ]
    finally:
        conn.close()


def assign_user_to_role(
    admin: Dict[str, Any],
    account_id: str,
    role_id: str,
    target_user_id: str,
    sync_role_label: bool = True,
) -> Dict[str, Any]:
    """Atribui um usuário existente a um cargo (Super Admin / Admin de Acesso)."""
    if not can_manage_role(admin, account_id, role_id):
        raise PermissionError(
            "Sem permissão para alterar membros deste cargo."
        )

    conn = get_connection()
    try:
        with conn:
            target = conn.execute(
                "SELECT id, name, account_id, "
                "COALESCE(is_superadmin,0) AS is_superadmin, "
                "COALESCE(is_active,1) AS is_active "
                "FROM users WHERE id = ?",
                (target_user_id,),
            ).fetchone()
            if not target:
                raise ValueError("Usuário não encontrado.")
            if target["account_id"] != account_id:
                raise PermissionError("Usuário de outra conta.")
            if not target["is_active"]:
                raise ValueError("Usuário inativo não pode receber cargo.")

            # Não rebaixar superadmin de plataforma a cargo operacional sem superadmin
            if target["is_superadmin"] and not _is_superadmin(admin):
                raise PermissionError(
                    "Apenas Super Admin altera conta de superadministrador."
                )
            # Superadmin não pode se rebaixar por engano via mesmo fluxo se target==self e role não ceo
            if (
                target["is_superadmin"]
                and target_user_id == admin.get("id")
                and role_id != "role-ceo"
            ):
                raise PermissionError("Não é permitido rebaixar a própria conta Super Admin.")

            role = conn.execute(
                "SELECT name FROM roles WHERE id = ? AND account_id = ?",
                (role_id, account_id),
            ).fetchone()
            if not role:
                raise ValueError("Cargo não encontrado.")

            role_name = role["name"]
            is_admin_flag = 1 if role_id == "role-ceo" else 0

            conn.execute(
                "UPDATE users SET role_id = ?, is_superadmin = ? WHERE id = ?",
                (role_id, is_admin_flag if role_id == "role-ceo" else int(target["is_superadmin"]),
                 target_user_id),
            )
            if sync_role_label:
                conn.execute(
                    "UPDATE users SET role = ? WHERE id = ?",
                    (role_name, target_user_id),
                )

            conn.execute(
                "INSERT INTO access_audit_log "
                "(account_id, actor_user_id, action, target_role_id, payload_json, created_at) "
                "VALUES (?, ?, 'user.assign_role', ?, ?, datetime('now'))",
                (
                    account_id,
                    admin.get("id") or "",
                    role_id,
                    f"user={target_user_id}",
                ),
            )

        return {
            "user_id": target_user_id,
            "role_id": role_id,
            "role_name": role_name,
            "assigned": True,
        }
    finally:
        conn.close()


def unassign_user_from_role(
    admin: Dict[str, Any],
    account_id: str,
    role_id: str,
    target_user_id: str,
) -> Dict[str, Any]:
    """Desvincula usuário do cargo atual (role_id → NULL). Menos-privilege no menu."""
    if not can_manage_role(admin, account_id, role_id):
        raise PermissionError(
            "Sem permissão para alterar membros deste cargo."
        )

    conn = get_connection()
    try:
        with conn:
            target = conn.execute(
                "SELECT id, name, account_id, role_id, "
                "COALESCE(is_superadmin,0) AS is_superadmin, "
                "COALESCE(is_active,1) AS is_active "
                "FROM users WHERE id = ?",
                (target_user_id,),
            ).fetchone()
            if not target:
                raise ValueError("Usuário não encontrado.")
            if target["account_id"] != account_id:
                raise PermissionError("Usuário de outra conta.")

            # Só desvincula se o usuário está de fato neste cargo
            if (target["role_id"] or "") != role_id:
                raise ValueError("Usuário não está vinculado a este cargo.")

            # Nunca remove o Super Admin de plataforma do cargo de diretoria
            if target["is_superadmin"] and role_id == "role-ceo":
                if target_user_id == admin.get("id"):
                    raise PermissionError(
                        "Não é permitido remover a própria conta Super Admin da diretoria."
                    )
                if not _is_superadmin(admin):
                    raise PermissionError(
                        "Apenas Super Admin remove conta superadministradora da diretoria."
                    )
                # Superadmin removendo OUTRO superadmin do ceo — ainda bloqueado se for o último?
                # Permitimos só se não for o dono da sessão; último superadmin do sistema:
                others = conn.execute(
                    "SELECT COUNT(*) FROM users "
                    "WHERE account_id = ? AND COALESCE(is_superadmin,0) = 1 "
                    "AND id != ? AND COALESCE(is_active,1) = 1",
                    (account_id, target_user_id),
                ).fetchone()[0]
                if int(others) == 0:
                    raise PermissionError(
                        "Não é possível remover o último Super Admin ativo."
                    )

            conn.execute(
                "UPDATE users SET role_id = NULL, role = ? WHERE id = ?",
                ("Sem cargo", target_user_id),
            )
            # Superadmin flag permanece só se ainda for role-ceo — aqui saiu do ceo
            if target["is_superadmin"] and role_id == "role-ceo":
                conn.execute(
                    "UPDATE users SET is_superadmin = 0 WHERE id = ?",
                    (target_user_id,),
                )

            conn.execute(
                "INSERT INTO access_audit_log "
                "(account_id, actor_user_id, action, target_role_id, payload_json, created_at) "
                "VALUES (?, ?, 'user.unassign_role', ?, ?, datetime('now'))",
                (
                    account_id,
                    admin.get("id") or "",
                    role_id,
                    f"user={target_user_id}",
                ),
            )

        return {
            "user_id": target_user_id,
            "role_id": "",
            "role_name": "Sem cargo",
            "unassigned": True,
        }
    finally:
        conn.close()
