# -*- coding: utf-8 -*-
"""Granular RBAC: route/facility catalog, role grants, access-admin scopes, audit.

Revision ID: 0005_granular_rbac
Revises: 0004_add_market_intel_batch_ticks
Create Date: 2026-10-20 19:00:00
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005_granular_rbac"
down_revision: Union[str, None] = "0004_add_market_intel_batch_ticks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ---------------------------------------------------------------------------
# Catalog — must stay aligned with frontend navConfig.ts (docs/permissionamento-granular.md)
# ---------------------------------------------------------------------------

ACCOUNT_ID = "0f14ffff"
CREATED_AT = "2026-10-20T19:00:00Z"

ROUTES = [
    # route_id, label, journey_group, default_facility
    ("dashboard", "Visão do Dia", "Operação do Dia", None),
    ("omnichannel", "Atendimento", "Operação do Dia", "chats"),
    ("scheduling", "Agenda e Retornos", "Operação do Dia", None),
    ("scoring", "Qualificação (ICP)", "Pipeline Comercial", None),
    ("contacts", "Dentistas e Clínicas", "Pipeline Comercial", "crm_surgeons"),
    ("deals", "Funil de Negociações", "Pipeline Comercial", None),
    ("contracts", "Propostas e Contratos", "Pipeline Comercial", "documenso_lifecycle"),
    ("imaging", "Exames e Diagnóstico 3D", "Pipeline Comercial", None),
    ("marketing", "Campanhas e Indicações", "Pipeline Comercial", None),
    ("dentgo", "Entregas Expressas", "Entrega e Pós-Venda", "orders"),
    ("keypartners", "Consignação (Maletas)", "Entrega e Pós-Venda", "board"),
    ("video_sos", "Chamadas e Vídeo", "Entrega e Pós-Venda", None),
    ("support", "Suporte e Garantias", "Entrega e Pós-Venda", "anvisa_rma"),
    ("intelligence", "Assistente Comercial", "Inteligência e Gestão", "copilot"),
    ("market_intel", "Radar de Mercado", "Inteligência e Gestão", "signals"),
    ("analytics", "Relatórios e Metas", "Inteligência e Gestão", "rls_studio"),
    ("rbac", "Equipes e Acessos", "Inteligência e Gestão", "tree"),
    ("settings", "Configurações", "Inteligência e Gestão", "vault"),
]

FACILITIES = [
    # facility_id, route_id, label, sort_order
    ("chats", "omnichannel", "Fila de Chats", 1),
    ("contacts", "omnichannel", "Contatos", 2),
    ("instances", "omnichannel", "Instâncias", 3),
    ("crm_surgeons", "contacts", "Base de Cirurgiões", 1),
    ("institutions_links", "contacts", "Clínicas e Vínculos", 2),
    ("cfo_compliance", "contacts", "Auditor CFO 196", 3),
    ("icp_scoring", "contacts", "Score ICP", 4),
    ("documenso_lifecycle", "contracts", "Assinaturas Documenso", 1),
    ("anvisa_catalog_pricing", "contracts", "Catálogo e Preços", 2),
    ("r2_custody", "contracts", "Custódia R2", 3),
    ("orders", "dentgo", "Despacho 45 min", 1),
    ("hubs", "dentgo", "Hubs de Estoque", 2),
    ("fefo", "dentgo", "Ofertas FEFO", 3),
    ("split", "dentgo", "Repasses e Custos", 4),
    ("board", "keypartners", "Board Cirúrgico", 1),
    ("agreements", "keypartners", "Acordos", 2),
    ("kol", "keypartners", "KOL e Speakers", 3),
    ("loyalty", "keypartners", "Fidelidade", 4),
    ("anvisa_rma", "support", "ANVISA e RMA", 1),
    ("surgical_sos", "support", "SOS Mesa Cirúrgica", 2),
    ("postop_b2c", "support", "Pós-operatório B2C", 3),
    ("copilot", "intelligence", "Resumo de Reuniões", 1),
    ("rag", "intelligence", "Assistente Cirúrgico", 2),
    ("inventory", "intelligence", "Maletas Paradas", 3),
    ("margin", "intelligence", "Margem Clínica", 4),
    ("health_score", "intelligence", "Health Score", 5),
    ("signals", "market_intel", "Sinais", 1),
    ("competitors", "market_intel", "Concorrentes", 2),
    ("opportunities", "market_intel", "Oportunidades", 3),
    ("campaigns", "market_intel", "Disparos", 4),
    ("rls_studio", "analytics", "Studio BI e RLS", 1),
    ("text_to_sql", "analytics", "Text-to-SQL", 2),
    ("tree", "rbac", "Estrutura de Equipes", 1),
    ("permissions", "rbac", "Permissões", 2),
    ("targets", "rbac", "Metas Comerciais", 3),
    ("commissions", "rbac", "Comissionamento", 4),
    ("vault", "settings", "Cofre Cifrado", 1),
    ("erp", "settings", "ERP e Fiscal", 2),
    ("webhooks", "settings", "Webhooks", 3),
    ("users", "settings", "Usuários e Quarteto", 4),
]

# role_id -> list of (route_id, menu_priority, allow_submenus, facilities|None)
# facilities None means: all catalog facilities for that route are granted when route has any;
# empty list means: route only, no facility deep-links (or default facility only on backend).
ROLE_ROUTE_DEFAULTS = {
    "role-field": [
        ("deals", 1, 0, []),
        ("dentgo", 2, 0, []),
        ("contacts", 3, 0, []),
        ("keypartners", 4, 0, []),
        ("video_sos", 5, 0, []),
        ("intelligence", 6, 0, []),
        ("market_intel", 7, 0, []),
    ],
    "role-inside": [
        ("omnichannel", 1, 0, ["chats", "contacts", "instances"]),
        ("scheduling", 2, 0, []),
        ("deals", 3, 0, []),
        ("scoring", 4, 0, []),
        ("contacts", 5, 0, []),
        ("contracts", 6, 0, []),
        ("market_intel", 7, 0, []),
    ],
    "role-logistics": [
        ("dentgo", 1, 1, ["orders", "hubs", "fefo", "split"]),
        ("keypartners", 2, 1, ["board", "agreements", "kol", "loyalty"]),
        ("support", 3, 1, ["anvisa_rma", "surgical_sos", "postop_b2c"]),
        ("settings", 4, 1, ["vault", "erp", "webhooks", "users"]),
    ],
    "role-clinical": [
        ("support", 1, 1, ["anvisa_rma", "surgical_sos", "postop_b2c"]),
        ("video_sos", 2, 0, []),
        ("imaging", 3, 0, []),
        ("scheduling", 4, 0, []),
        ("omnichannel", 5, 0, ["chats", "contacts", "instances"]),
    ],
    "role-manager": [
        ("dashboard", 1, 0, []),
        ("deals", 2, 0, []),
        ("market_intel", 3, 1, ["signals", "competitors", "opportunities", "campaigns"]),
        ("contacts", 4, 1, ["crm_surgeons", "institutions_links", "cfo_compliance", "icp_scoring"]),
        ("keypartners", 5, 1, ["board", "agreements", "kol", "loyalty"]),
        ("contracts", 6, 1, ["documenso_lifecycle", "anvisa_catalog_pricing", "r2_custody"]),
        ("marketing", 7, 0, []),
        ("rbac", 8, 1, ["tree", "permissions", "targets", "commissions"]),
    ],
    "role-ceo": [
        ("dashboard", 1, 0, []),
        ("omnichannel", 2, 1, ["chats", "contacts", "instances"]),
        ("scheduling", 3, 0, []),
        ("scoring", 4, 0, []),
        ("contacts", 5, 1, ["crm_surgeons", "institutions_links", "cfo_compliance", "icp_scoring"]),
        ("deals", 6, 0, []),
        ("contracts", 7, 1, ["documenso_lifecycle", "anvisa_catalog_pricing", "r2_custody"]),
        ("imaging", 8, 0, []),
        ("marketing", 9, 0, []),
        ("dentgo", 10, 1, ["orders", "hubs", "fefo", "split"]),
        ("keypartners", 11, 1, ["board", "agreements", "kol", "loyalty"]),
        ("video_sos", 12, 0, []),
        ("support", 13, 1, ["anvisa_rma", "surgical_sos", "postop_b2c"]),
        ("intelligence", 14, 1, ["copilot", "rag", "inventory", "margin", "health_score"]),
        ("market_intel", 15, 1, ["signals", "competitors", "opportunities", "campaigns"]),
        ("analytics", 16, 1, ["rls_studio", "text_to_sql"]),
        ("rbac", 17, 1, ["tree", "permissions", "targets", "commissions"]),
        ("settings", 18, 1, ["vault", "erp", "webhooks", "users"]),
    ],
    "role-access-admin": [
        ("dashboard", 1, 0, []),
        ("rbac", 2, 1, ["tree", "permissions", "targets", "commissions"]),
        ("settings", 3, 1, ["users"]),
        ("analytics", 4, 1, ["rls_studio"]),
    ],
}

ACCESS_ADMIN_EDITABLE = [
    "role-field",
    "role-inside",
    "role-logistics",
    "role-clinical",
    "role-manager",
]


def upgrade() -> None:
    op.create_table(
        "access_catalog_routes",
        sa.Column("route_id", sa.String(), primary_key=True),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("journey_group", sa.String(), nullable=False),
        sa.Column("default_facility", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "access_catalog_facilities",
        sa.Column("facility_id", sa.String(), primary_key=True),
        sa.Column("route_id", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="999"),
        sa.ForeignKeyConstraint(["route_id"], ["access_catalog_routes.route_id"]),
        if_not_exists=True,
    )

    op.create_table(
        "role_route_grants",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("account_id", sa.String(), nullable=False),
        sa.Column("role_id", sa.String(), nullable=False),
        sa.Column("route_id", sa.String(), nullable=False),
        sa.Column("is_visible_menu", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("menu_priority", sa.Integer(), nullable=False, server_default="999"),
        sa.Column("allow_submenus", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["route_id"], ["access_catalog_routes.route_id"]),
        sa.UniqueConstraint("account_id", "role_id", "route_id", name="uq_role_route_grant"),
        if_not_exists=True,
    )

    op.create_table(
        "role_facility_grants",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("account_id", sa.String(), nullable=False),
        sa.Column("role_id", sa.String(), nullable=False),
        sa.Column("route_id", sa.String(), nullable=False),
        sa.Column("facility_id", sa.String(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="999"),
        sa.Column("created_at", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["facility_id"], ["access_catalog_facilities.facility_id"]),
        sa.UniqueConstraint(
            "account_id", "role_id", "route_id", "facility_id", name="uq_role_facility_grant"
        ),
        if_not_exists=True,
    )

    op.create_table(
        "access_admin_scopes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("account_id", sa.String(), nullable=False),
        sa.Column("admin_role_id", sa.String(), nullable=False),
        sa.Column("editable_role_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["admin_role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["editable_role_id"], ["roles.id"]),
        sa.UniqueConstraint(
            "account_id", "admin_role_id", "editable_role_id", name="uq_access_admin_scope"
        ),
        if_not_exists=True,
    )

    op.create_table(
        "access_audit_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("account_id", sa.String(), nullable=False),
        sa.Column("actor_user_id", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("target_role_id", sa.String(), nullable=True),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=False),
        if_not_exists=True,
    )

    # --- role-access-admin (day 1) ---
    op.execute(
        """
        INSERT OR IGNORE INTO roles
          (id, account_id, name, description, default_data_scope, is_admin, created_at)
        VALUES
          ('role-access-admin', :acc,
           'Admin de Acesso (Permissões)',
           'Edita grants de cargos operacionais; nao altera Super Admin nem outro Admin de Acesso',
           'team', 1, :ts)
        """,
        {"acc": ACCOUNT_ID, "ts": CREATED_AT},
    )

    # --- catalog ---
    for route_id, label, group, default_fac in ROUTES:
        op.execute(
            """
            INSERT OR IGNORE INTO access_catalog_routes
              (route_id, label, journey_group, default_facility)
            VALUES (:rid, :label, :grp, :dfac)
            """,
            {"rid": route_id, "label": label, "grp": group, "dfac": default_fac},
        )

    for fac_id, route_id, label, order in FACILITIES:
        op.execute(
            """
            INSERT OR IGNORE INTO access_catalog_facilities
              (facility_id, route_id, label, sort_order)
            VALUES (:fid, :rid, :label, :ord)
            """,
            {"fid": fac_id, "rid": route_id, "label": label, "ord": order},
        )

    # --- role grants ---
    for role_id, grants in ROLE_ROUTE_DEFAULTS.items():
        # Ensure role row exists for non-ceo operational ids (seed may create later)
        op.execute(
            """
            INSERT OR IGNORE INTO roles
              (id, account_id, name, description, default_data_scope, is_admin, created_at)
            VALUES (:rid, :acc, :rid, 'Seed catalog role', 'team', 0, :ts)
            """,
            {"rid": role_id, "acc": ACCOUNT_ID, "ts": CREATED_AT},
        )
        for route_id, priority, allow_sub, facilities in grants:
            op.execute(
                """
                INSERT OR IGNORE INTO role_route_grants
                  (account_id, role_id, route_id, is_visible_menu, menu_priority, allow_submenus, created_at)
                VALUES (:acc, :rid, :route, 1, :pri, :sub, :ts)
                """,
                {
                    "acc": ACCOUNT_ID,
                    "rid": role_id,
                    "route": route_id,
                    "pri": priority,
                    "sub": allow_sub,
                    "ts": CREATED_AT,
                },
            )
            for fac in facilities:
                op.execute(
                    """
                    INSERT OR IGNORE INTO role_facility_grants
                      (account_id, role_id, route_id, facility_id, sort_order, created_at)
                    SELECT :acc, :rid, :route, facility_id, sort_order, :ts
                      FROM access_catalog_facilities
                     WHERE facility_id = :fac AND route_id = :route
                    """,
                    {
                        "acc": ACCOUNT_ID,
                        "rid": role_id,
                        "route": route_id,
                        "fac": fac,
                        "ts": CREATED_AT,
                    },
                )

    for editable in ACCESS_ADMIN_EDITABLE:
        op.execute(
            """
            INSERT OR IGNORE INTO access_admin_scopes
              (account_id, admin_role_id, editable_role_id, created_at)
            VALUES (:acc, 'role-access-admin', :editable, :ts)
            """,
            {"acc": ACCOUNT_ID, "editable": editable, "ts": CREATED_AT},
        )


def downgrade() -> None:
    op.drop_table("access_audit_log")
    op.drop_table("access_admin_scopes")
    op.drop_table("role_facility_grants")
    op.drop_table("role_route_grants")
    op.drop_table("access_catalog_facilities")
    op.drop_table("access_catalog_routes")
    op.execute("DELETE FROM roles WHERE id = 'role-access-admin'")
