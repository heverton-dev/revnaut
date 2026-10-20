# -*- coding: utf-8 -*-
"""
Matriz RBAC Territorial da Inteligência de Mercado (Seção 5 da SPEC MARKET INTEL).

| Perfil              | Sinais              | Concorrentes             | Minuta de Campanha | Aprovação/Disparo |
| director            | Global              | Global + configuração    | Sim (Nacional)     | Sim               |
| regional_manager    | Regional + Global   | Somente leitura          | Sim (sua praça)    | Sim (sua praça)   |
| inside_sales        | Carteira + Global   | Somente leitura          | Sim (Draft)        | Não               |
| field_sales         | Carteira + Global   | Somente leitura (cards)  | Não                | Não               |
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import FrozenSet, Optional

from fastapi import Header, HTTPException, status

from src.core.database import get_connection

DIRECTOR = "director"
REGIONAL_MANAGER = "regional_manager"
INSIDE_SALES = "inside_sales"
FIELD_SALES = "field_sales"

CANONICAL_ROLES: FrozenSet[str] = frozenset({DIRECTOR, REGIONAL_MANAGER, INSIDE_SALES, FIELD_SALES})

DEFAULT_ACCOUNT_ID = "0f14ffff"
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


def _role_from_user_id(user_id: str, account_id: str) -> Optional[str]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT role, is_superadmin FROM users WHERE id = ? AND account_id = ?",
            (user_id, account_id),
        ).fetchone()
    except Exception:
        row = None
    finally:
        conn.close()
    if not row:
        return None
    if row["is_superadmin"]:
        return DIRECTOR
    return normalize_role(row["role"])


def resolve_principal(
    role: Optional[str] = None,
    user_id: Optional[str] = None,
    region: Optional[str] = None,
    account_id: Optional[str] = None,
) -> MarketIntelPrincipal:
    """
    Resolve o principal da requisição. Ordem: papel explícito -> papel do usuário cadastrado.
    Sem identificação válida aplica privilégio mínimo (field_sales).
    """
    acc = (account_id or DEFAULT_ACCOUNT_ID).strip()
    canonical = normalize_role(role)
    if role and canonical is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Papel desconhecido: '{role}'.")
    if canonical is None and user_id:
        canonical = _role_from_user_id(user_id, acc)
    if canonical is None:
        canonical = FIELD_SALES

    eff_region = (region or "").strip().upper() or (GLOBAL_SCOPE if canonical == DIRECTOR else DEFAULT_REGION)
    if eff_region not in VALID_REGIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Região inválida: '{eff_region}'.")
    return MarketIntelPrincipal(role=canonical, user_id=user_id, region=eff_region, account_id=acc)


def get_market_intel_principal(
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_user_region: Optional[str] = Header(None, alias="X-User-Region"),
    x_account_id: Optional[str] = Header(None, alias="X-Account-ID"),
) -> MarketIntelPrincipal:
    """Dependência FastAPI compartilhada pelos routers market_intel, competitors e campaigns."""
    return resolve_principal(role=x_user_role, user_id=x_user_id, region=x_user_region, account_id=x_account_id)


def forbidden(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
