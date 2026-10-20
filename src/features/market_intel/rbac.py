# -*- coding: utf-8 -*-
"""
Matriz RBAC Territorial da Inteligência de Mercado (Seção 5 da SPEC MARKET INTEL).

| Perfil              | Sinais              | Concorrentes             | Minuta de Campanha | Aprovação/Disparo |
| director            | Global              | Global + configuração    | Sim (Nacional)     | Sim               |
| regional_manager    | Regional + Global   | Somente leitura          | Sim (sua praça)    | Sim (sua praça)   |
| inside_sales        | Carteira + Global   | Somente leitura          | Sim (Draft)        | Não               |
| field_sales         | Carteira + Global   | Somente leitura (cards)  | Não                | Não               |

Autenticação: o principal é derivado do token Bearer de sessão (HMAC) e do cadastro do usuário
(users.role, users.is_superadmin, users.region_code, users.account_id).
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import FrozenSet, Optional

from fastapi import Header, HTTPException, status

from src.core.database import get_connection
from src.features.auth.service import verify_session_token

DIRECTOR = "director"
REGIONAL_MANAGER = "regional_manager"
INSIDE_SALES = "inside_sales"
FIELD_SALES = "field_sales"

CANONICAL_ROLES: FrozenSet[str] = frozenset({DIRECTOR, REGIONAL_MANAGER, INSIDE_SALES, FIELD_SALES})

DEFAULT_REGION = "BR-SP"
GLOBAL_SCOPE = "GLOBAL"

VALID_REGIONS: FrozenSet[str] = frozenset({"GLOBAL", "BR-SP", "BR-PR", "BR-PE", "BR-RJ", "BR-MG", "BR-RS", "BR-SC", "US-FL", "LATAM"})

_ROLE_ALIASES = {
    "director": DIRECTOR,
    "diretor": DIRECTOR,
    "diretoria": DIRECTOR,
    "admin": DIRECTOR,
    "administrador": DIRECTOR,
    "superadmin": DIRECTOR,
    "super admin": DIRECTOR,
    "manager": REGIONAL_MANAGER,
    "regional_manager": REGIONAL_MANAGER,
    "gerente": REGIONAL_MANAGER,
    "gerente regional": REGIONAL_MANAGER,
    "gerente comercial": REGIONAL_MANAGER,
    "sales_manager": REGIONAL_MANAGER,
    "inside_sales": INSIDE_SALES,
    "sdr": INSIDE_SALES,
    "consultor interno": INSIDE_SALES,
    "field_sales": FIELD_SALES,
    "consultor externo": FIELD_SALES,
    "campo": FIELD_SALES,
}


class MarketIntelForbidden(Exception):
    """Ação negada pela matriz RBAC territorial (mapeada para HTTP 403)."""


@dataclass(frozen=True)
class MarketIntelPrincipal:
    role: str
    user_id: Optional[str]
    region: str
    account_id: str
    actual_role: str = FIELD_SALES

    @property
    def can_simulate(self) -> bool:
        return self.actual_role == DIRECTOR

    @property
    def visible_scopes(self) -> Optional[FrozenSet[str]]:
        """None significa acesso irrestrito (todas as praças)."""
        if self.role == DIRECTOR:
            return None
        return frozenset({GLOBAL_SCOPE, self.region})

    @property
    def can_manage_competitors(self) -> bool:
        return self.role == DIRECTOR

    @property
    def can_generate_draft(self) -> bool:
        return self.role in (DIRECTOR, REGIONAL_MANAGER, INSIDE_SALES)

    @property
    def can_dispatch(self) -> bool:
        return self.role in (DIRECTOR, REGIONAL_MANAGER)

    def can_see_scope(self, scope: str) -> bool:
        scopes = self.visible_scopes
        return scopes is None or scope in scopes

    def can_operate_region(self, region: str) -> bool:
        """Criação/disparo de campanha: diretoria em qualquer praça, demais apenas na própria praça."""
        return self.role == DIRECTOR or region == self.region


def _strip_accents(value: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", value) if not unicodedata.combining(c))


def normalize_role(raw_role: Optional[str]) -> Optional[str]:
    """Converte papéis livres (ex: 'Consultor Externo (Campo)') no papel canônico da matriz."""
    if not raw_role:
        return None
    s = _strip_accents(raw_role).strip().lower()
    if s in _ROLE_ALIASES:
        return _ROLE_ALIASES[s]
    if "extern" in s or "campo" in s or "field" in s:
        return FIELD_SALES
    if "intern" in s or "inside" in s or "sdr" in s or "atendimento" in s:
        return INSIDE_SALES
    if "gerente" in s or "manager" in s:
        return REGIONAL_MANAGER
    if "diretor" in s or "director" in s or "admin" in s:
        return DIRECTOR
    return None


_ROLE_RANK = {FIELD_SALES: 0, INSIDE_SALES: 1, REGIONAL_MANAGER: 2, DIRECTOR: 3}


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _load_active_user(user_id: str) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT id, account_id, role, COALESCE(is_superadmin, 0) AS is_superadmin,
                   COALESCE(is_active, 1) AS is_active, region_code
            FROM users WHERE id = ?
            """,
            (user_id,),
        ).fetchone()
    finally:
        conn.close()
    return dict(row) if row else None


def resolve_authenticated_principal(
    authorization: Optional[str],
    simulated_role: Optional[str] = None,
    simulated_region: Optional[str] = None,
) -> MarketIntelPrincipal:
    """
    Papel, praça e tenant vêm do usuário autenticado pelo token Bearer assinado (HMAC),
    nunca de headers livres. O header X-User-Role só rebaixa o papel (simulação de perfis
    menores); X-User-Region só é aceito quando o usuário real é Diretoria.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise _unauthorized("Não autenticado. Envie Authorization: Bearer <token de sessão>.")
    user_id = verify_session_token(authorization.split("Bearer ", 1)[1].strip())
    if not user_id:
        raise _unauthorized("Token de sessão inválido.")
    user = _load_active_user(user_id)
    if not user or not user["is_active"]:
        raise _unauthorized("Sessão inválida ou usuário inativo.")

    actual_role = DIRECTOR if user["is_superadmin"] else (normalize_role(user["role"]) or FIELD_SALES)
    actual_region = GLOBAL_SCOPE if actual_role == DIRECTOR else (str(user["region_code"] or DEFAULT_REGION).upper())

    role = actual_role
    if simulated_role:
        sim = normalize_role(simulated_role)
        if sim is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Papel desconhecido: '{simulated_role}'.")
        if _ROLE_RANK[sim] <= _ROLE_RANK[actual_role]:
            role = sim

    region = actual_region
    if actual_role == DIRECTOR:
        requested = (simulated_region or "").strip().upper()
        if requested:
            region = requested
        elif role != DIRECTOR:
            region = DEFAULT_REGION
    if region not in VALID_REGIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Região inválida: '{region}'.")
    return MarketIntelPrincipal(role=role, user_id=user_id, region=region, account_id=user["account_id"], actual_role=actual_role)


def get_market_intel_principal(
    authorization: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    x_user_region: Optional[str] = Header(None, alias="X-User-Region"),
) -> MarketIntelPrincipal:
    """Dependência FastAPI compartilhada pelos routers market_intel, competitors e campaigns."""
    return resolve_authenticated_principal(authorization, x_user_role, x_user_region)
