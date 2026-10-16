# -*- coding: utf-8 -*-
"""
Service para Gestão de Hierarquia Organizacional, RBAC e Presets Odontológicos.
"""

from __future__ import annotations
import uuid
from typing import List, Dict, Any, Optional, Set
from src.core.database import get_connection
from src.features.hierarchy.schemas import (
    BusinessUnitCreate, TeamCreate, RoleCreate, DataScopeEnum
)


def list_business_units(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, account_id, name, code, description, created_at "
            "FROM business_units WHERE account_id = ? ORDER BY name ASC",
            (account_id,)
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def create_business_unit(data: BusinessUnitCreate, account_id: str = "0f14ffff") -> Dict[str, Any]:
    conn = get_connection()
    bu_id = f"bu_{data.code.lower()}_{uuid.uuid4().hex[:6]}"
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO business_units (id, account_id, name, code, description) "
                "VALUES (?, ?, ?, ?, ?)",
                (bu_id, account_id, data.name, data.code.upper(), data.description or "")
            )
            cur.execute(
                "SELECT id, account_id, name, code, description, created_at "
                "FROM business_units WHERE id = ?",
                (bu_id,)
            )
            return dict(cur.fetchone())
    finally:
        conn.close()


def list_teams(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, account_id, business_unit_id, parent_id, name, leader_id, created_at "
            "FROM teams WHERE account_id = ? ORDER BY name ASC",
            (account_id,)
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def _is_descendant(conn, candidate_descendant_id: str, potential_ancestor_id: str) -> bool:
    """Verifica recursivamente se candidate_descendant_id é descendente de potential_ancestor_id."""
    cur = conn.cursor()
    visited: Set[str] = set()
    current_id: Optional[str] = candidate_descendant_id

    while current_id:
        if current_id == potential_ancestor_id:
            return True
        if current_id in visited:
            break
        visited.add(current_id)
        cur.execute("SELECT parent_id FROM teams WHERE id = ?", (current_id,))
        row = cur.fetchone()
        current_id = row[0] if row and row[0] else None

    return False


def create_team(data: TeamCreate, account_id: str = "0f14ffff") -> Dict[str, Any]:
    conn = get_connection()
    team_id = f"tm_{uuid.uuid4().hex[:8]}"
    try:
        with conn:
            cur = conn.cursor()
            if data.parent_id:
                cur.execute("SELECT id FROM teams WHERE id = ? AND account_id = ?", (data.parent_id, account_id))
                if not cur.fetchone():
                    raise ValueError(f"Equipe pai '{data.parent_id}' não encontrada")

            cur.execute(
                "INSERT INTO teams (id, account_id, business_unit_id, parent_id, name, leader_id) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (team_id, account_id, data.business_unit_id, data.parent_id, data.name, data.leader_id)
            )
            cur.execute(
                "SELECT id, account_id, business_unit_id, parent_id, name, leader_id, created_at "
                "FROM teams WHERE id = ?",
                (team_id,)
            )
            return dict(cur.fetchone())
    finally:
        conn.close()


def update_team_parent(team_id: str, new_parent_id: Optional[str], account_id: str = "0f14ffff") -> Dict[str, Any]:
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM teams WHERE id = ? AND account_id = ?", (team_id, account_id))
            if not cur.fetchone():
                raise ValueError(f"Equipe '{team_id}' não encontrada")

            if new_parent_id:
                if new_parent_id == team_id:
                    raise ValueError("Uma equipe não pode ser pai de si mesma (relação circular)")
                if _is_descendant(conn, new_parent_id, team_id):
                    raise ValueError("Relação circular detectada na hierarquia: o novo pai já é descendente desta equipe")

            cur.execute("UPDATE teams SET parent_id = ? WHERE id = ?", (new_parent_id, team_id))
            cur.execute(
                "SELECT id, account_id, business_unit_id, parent_id, name, leader_id, created_at "
                "FROM teams WHERE id = ?",
                (team_id,)
            )
            return dict(cur.fetchone())
    finally:
        conn.close()


def list_roles(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, account_id, name, description, default_data_scope, is_admin, created_at "
            "FROM roles WHERE account_id = ? ORDER BY is_admin DESC, name ASC",
            (account_id,)
        )
        roles = [dict(row) for row in cur.fetchall()]
        for r in roles:
            cur.execute("SELECT permission_code FROM role_permissions WHERE role_id = ?", (r["id"],))
            r["permissions"] = [p[0] for p in cur.fetchall()]
        return roles
    finally:
        conn.close()


def create_role(data: RoleCreate, account_id: str = "0f14ffff") -> Dict[str, Any]:
    conn = get_connection()
    role_id = f"role_{uuid.uuid4().hex[:8]}"
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO roles (id, account_id, name, description, default_data_scope, is_admin) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (role_id, account_id, data.name, data.description or "", data.default_data_scope.value, data.is_admin)
            )
            for perm in data.permissions:
                cur.execute(
                    "INSERT INTO role_permissions (account_id, role_id, permission_code) VALUES (?, ?, ?)",
                    (account_id, role_id, perm)
                )
            cur.execute(
                "SELECT id, account_id, name, description, default_data_scope, is_admin, created_at "
                "FROM roles WHERE id = ?",
                (role_id,)
            )
            res = dict(cur.fetchone())
            res["permissions"] = data.permissions
            return res
    finally:
        conn.close()


def apply_hierarchy_preset(account_id: str, preset_name: str) -> Dict[str, Any]:
    """Aplica deterministicamente um dos 4 templates progressivos do setor odontológico."""
    valid_presets = ["fabrica_enxuta", "nacional_expansao", "multidivisao_produtos", "multinacional_enterprise"]
    if preset_name not in valid_presets:
        raise ValueError(f"Preset '{preset_name}' inválido. Opções válidas: {valid_presets}")

    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()

            if preset_name == "fabrica_enxuta":
                # BU única
                bu_id = f"bu_com_geral_{account_id[:4]}"
                cur.execute(
                    "INSERT OR IGNORE INTO business_units (id, account_id, name, code, description) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (bu_id, account_id, "Comercial & Vendas Odonto", "COM_GERAL", "Operação comercial unificada")
                )
                # Time único de campo
                tm_id = f"tm_campo_{account_id[:4]}"
                cur.execute(
                    "INSERT OR IGNORE INTO teams (id, account_id, business_unit_id, parent_id, name) "
                    "VALUES (?, ?, ?, NULL, ?)",
                    (tm_id, account_id, bu_id, "Consultores Cirúrgicos de Campo")
                )
                # Roles
                cur.execute(
                    "INSERT OR IGNORE INTO roles (id, account_id, name, description, default_data_scope, is_admin) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (f"role_dir_{account_id[:4]}", account_id, "Diretor Comercial", "Acesso total à empresa", "tenant_global", 1)
                )
                cur.execute(
                    "INSERT OR IGNORE INTO roles (id, account_id, name, description, default_data_scope, is_admin) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (f"role_cons_{account_id[:4]}", account_id, "Consultor de Campo", "Vê apenas seus cirurgiões e caixas", "self", 0)
                )

            elif preset_name == "nacional_expansao":
                # 2 BUs: Vendas Externa e Televendas
                bu_ext = f"bu_ext_{account_id[:4]}"
                bu_tel = f"bu_tel_{account_id[:4]}"
                cur.execute("INSERT OR IGNORE INTO business_units (id, account_id, name, code) VALUES (?, ?, ?, ?)",
                            (bu_ext, account_id, "Venda Direta & Consultores Externos", "VENDAS_EXT"))
                cur.execute("INSERT OR IGNORE INTO business_units (id, account_id, name, code) VALUES (?, ?, ?, ?)",
                            (bu_tel, account_id, "Inside Sales & Televendas", "TELEVENDAS"))

                # Árvore: Diretoria -> Regionais (SP, Sul, Nordeste)
                tm_dir = f"tm_dir_nac_{account_id[:4]}"
                cur.execute("INSERT OR IGNORE INTO teams (id, account_id, business_unit_id, parent_id, name) VALUES (?, ?, ?, NULL, ?)",
                            (tm_dir, account_id, bu_ext, "Diretoria Nacional de Vendas"))
                for reg_name, reg_code in [("Regional Interior SP", "sp"), ("Regional Sul", "sul"), ("Regional Nordeste", "ne")]:
                    cur.execute("INSERT OR IGNORE INTO teams (id, account_id, business_unit_id, parent_id, name) VALUES (?, ?, ?, ?, ?)",
                                (f"tm_{reg_code}_{account_id[:4]}", account_id, bu_ext, tm_dir, reg_name))

                # Roles
                cur.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES (?, ?, ?, ?, ?)",
                            (f"role_dir_{account_id[:4]}", account_id, "Diretor Nacional", "tenant_global", 1))
                cur.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES (?, ?, ?, ?, ?)",
                            (f"role_greg_{account_id[:4]}", account_id, "Gerente Regional", "team", 0))
                cur.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES (?, ?, ?, ?, ?)",
                            (f"role_cons_{account_id[:4]}", account_id, "Consultor Cirúrgico", "self", 0))

            elif preset_name == "multidivisao_produtos":
                # 3 BUs por linha de produto
                for b_name, b_code in [
                    ("Divisão Implantes Cirúrgicos", "BU_CIRURGICO"),
                    ("Divisão Biomateriais & Enxertos", "BU_BIOMATERIAIS"),
                    ("Divisão Prótese & CAD/CAM", "BU_PROTESE")
                ]:
                    b_id = f"bu_{b_code.lower()}_{account_id[:4]}"
                    cur.execute("INSERT OR IGNORE INTO business_units (id, account_id, name, code) VALUES (?, ?, ?, ?)",
                                (b_id, account_id, b_name, b_code))
                    tm_head = f"tm_head_{b_code.lower()}_{account_id[:4]}"
                    cur.execute("INSERT OR IGNORE INTO teams (id, account_id, business_unit_id, parent_id, name) VALUES (?, ?, ?, NULL, ?)",
                                (tm_head, account_id, b_id, f"Gestão Nacional {b_name}"))
                    cur.execute("INSERT OR IGNORE INTO teams (id, account_id, business_unit_id, parent_id, name) VALUES (?, ?, ?, ?, ?)",
                                (f"tm_reg_{b_code.lower()}_{account_id[:4]}", account_id, b_id, tm_head, f"Especialistas {b_name}"))

                # Roles
                cur.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES (?, ?, ?, ?, ?)",
                            (f"role_gdiv_{account_id[:4]}", account_id, "Gerente de Divisão", "business_unit", 1))
                cur.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES (?, ?, ?, ?, ?)",
                            (f"role_sup_{account_id[:4]}", account_id, "Supervisor Regional", "team", 0))
                cur.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES (?, ?, ?, ?, ?)",
                            (f"role_ast_{account_id[:4]}", account_id, "Assessor Técnico de Produto", "self", 0))

            elif preset_name == "multinacional_enterprise":
                # 4 BUs padrão Neodent / Straumann
                bus_multinacional = [
                    ("Força Cirúrgica Direta (Implantes)", "BU_CIRURGIA_DIRETA"),
                    ("Fluxo Digital & CAD/CAM", "BU_CADCAM"),
                    ("Instituições de Ensino & Universidades (Mandic)", "BU_ENSINO_MANDIC"),
                    ("Key Accounts & Redes Odontológicas (DSOs)", "BU_KEY_ACCOUNTS")
                ]
                for b_name, b_code in bus_multinacional:
                    b_id = f"bu_{b_code.lower()}_{account_id[:4]}"
                    cur.execute("INSERT OR IGNORE INTO business_units (id, account_id, name, code) VALUES (?, ?, ?, ?)",
                                (b_id, account_id, b_name, b_code))
                    # Nível 1: Diretoria de Divisão
                    tm_dir = f"tm_dir_{b_code.lower()}_{account_id[:4]}"
                    cur.execute("INSERT OR IGNORE INTO teams (id, account_id, business_unit_id, parent_id, name) VALUES (?, ?, ?, NULL, ?)",
                                (tm_dir, account_id, b_id, f"Diretoria {b_name}"))
                    # Nível 2: Distrito
                    tm_dist = f"tm_dist_{b_code.lower()}_{account_id[:4]}"
                    cur.execute("INSERT OR IGNORE INTO teams (id, account_id, business_unit_id, parent_id, name) VALUES (?, ?, ?, ?, ?)",
                                (tm_dist, account_id, b_id, tm_dir, f"Distrito Sudeste & Sul ({b_code})"))
                    # Nível 3: Regional
                    cur.execute("INSERT OR IGNORE INTO teams (id, account_id, business_unit_id, parent_id, name) VALUES (?, ?, ?, ?, ?)",
                                (f"tm_reg_{b_code.lower()}_{account_id[:4]}", account_id, b_id, tm_dist, f"Regional São Paulo / Interior ({b_code})"))

                # 5 Roles hierárquicas
                cur.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES (?, ?, ?, ?, ?)",
                            (f"role_clevel_{account_id[:4]}", account_id, "C-Level / Diretoria Executiva", "tenant_global", 1))
                cur.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES (?, ?, ?, ?, ?)",
                            (f"role_dirbu_{account_id[:4]}", account_id, "Diretor de Divisão (BU Head)", "business_unit", 1))
                cur.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES (?, ?, ?, ?, ?)",
                            (f"role_gdist_{account_id[:4]}", account_id, "Gerente Distrital", "subtree", 0))
                cur.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES (?, ?, ?, ?, ?)",
                            (f"role_greg_{account_id[:4]}", account_id, "Gerente Regional", "team", 0))
                cur.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES (?, ?, ?, ?, ?)",
                            (f"role_cons_{account_id[:4]}", account_id, "Consultor Cirúrgico de Campo", "self", 0))

            # Contagens finais
            cur.execute("SELECT COUNT(*) FROM business_units WHERE account_id = ?", (account_id,))
            bu_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM teams WHERE account_id = ?", (account_id,))
            team_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM roles WHERE account_id = ?", (account_id,))
            role_count = cur.fetchone()[0]

            return {
                "success": True,
                "preset": preset_name,
                "account_id": account_id,
                "business_units_count": bu_count,
                "teams_count": team_count,
                "roles_count": role_count,
                "message": f"Preset '{preset_name}' aplicado com sucesso no SQLite WAL"
            }
    finally:
        conn.close()


def get_permission_catalog() -> List[Dict[str, Any]]:
    """Catálogo determinístico de recursos e ações do setor odontológico."""
    return [
        {
            "resource": "deals",
            "resource_label": "Funil de Vendas & Oportunidades",
            "actions": [
                {"code": "deals:read", "label": "Visualizar Funis e Cards"},
                {"code": "deals:write", "label": "Criar e Mover Oportunidades"},
                {"code": "deals:delete", "label": "Excluir Oportunidades"},
                {"code": "deals:export", "label": "Exportar Relatórios de Vendas"}
            ]
        },
        {
            "resource": "contacts",
            "resource_label": "Base de Cirurgiões (CRO) & Decisores",
            "actions": [
                {"code": "contacts:read", "label": "Visualizar Cirurgiões e Especialidades"},
                {"code": "contacts:write", "label": "Cadastrar / Editar Cirurgiões"},
                {"code": "contacts:delete", "label": "Excluir Contatos"},
                {"code": "contacts:export_lgpd", "label": "Exportação em Massa (LGPD)"}
            ]
        },
        {
            "resource": "hierarchy",
            "resource_label": "Estrutura Corporativa & Organograma",
            "actions": [
                {"code": "hierarchy:read", "label": "Visualizar Árvore e BUs"},
                {"code": "hierarchy:manage_teams", "label": "Gerenciar Equipes na DAG"},
                {"code": "hierarchy:manage_roles", "label": "Editar Papéis e Permissões"}
            ]
        },
        {
            "resource": "campaigns",
            "resource_label": "Campanhas & Automações Cirúrgicas",
            "actions": [
                {"code": "campaigns:read", "label": "Visualizar Campanhas"},
                {"code": "campaigns:write", "label": "Criar e Editar Automações"},
                {"code": "campaigns:trigger", "label": "Disparar Reposição Imediata"}
            ]
        }
    ]


def list_roles(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    """Lista todas as funções da empresa com suas respectivas permissões."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, account_id, name, description, default_data_scope, is_admin, created_at "
            "FROM roles WHERE account_id = ? ORDER BY is_admin DESC, name ASC",
            (account_id,)
        )
        roles = [dict(row) for row in cur.fetchall()]

        for r in roles:
            cur.execute(
                "SELECT permission_code FROM role_permissions WHERE role_id = ?",
                (r["id"],)
            )
            r["permissions"] = [p[0] for p in cur.fetchall()]

        return roles
    finally:
        conn.close()


def create_role(data: RoleCreate, account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Cria uma nova função corporativa com permissões associadas."""
    conn = get_connection()
    role_id = f"role_{uuid.uuid4().hex[:8]}"
    raw_scope = data.default_data_scope.value if hasattr(data.default_data_scope, 'value') else str(data.default_data_scope)
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO roles (id, account_id, name, description, default_data_scope, is_admin) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (role_id, account_id, data.name, data.description or "", raw_scope, data.is_admin)
            )
            for perm in set(data.permissions):
                cur.execute(
                    "INSERT INTO role_permissions (account_id, role_id, permission_code) VALUES (?, ?, ?)",
                    (account_id, role_id, perm)
                )

            cur.execute(
                "SELECT id, account_id, name, description, default_data_scope, is_admin, created_at "
                "FROM roles WHERE id = ?",
                (role_id,)
            )
            r = dict(cur.fetchone())
            r["permissions"] = list(set(data.permissions))
            return r
    finally:
        conn.close()


def get_role_permissions(role_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Retorna dados de uma role com a lista de permissões ativas."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, account_id, name, description, default_data_scope, is_admin, created_at "
            "FROM roles WHERE id = ? AND account_id = ?",
            (role_id, account_id)
        )
        row = cur.fetchone()
        if not row:
            return {}

        role_data = dict(row)
        cur.execute(
            "SELECT permission_code FROM role_permissions WHERE role_id = ?",
            (role_id,)
        )
        role_data["permissions"] = [p[0] for p in cur.fetchall()]
        return role_data
    finally:
        conn.close()


def update_role_permissions(
    role_id: str, 
    permissions: List[str], 
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Atualiza atomicamente o conjunto de permissões atribuídas a uma role."""
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            # Valida existência da role no tenant
            cur.execute("SELECT id, name FROM roles WHERE id = ? AND account_id = ?", (role_id, account_id))
            role_row = cur.fetchone()
            if not role_row:
                raise ValueError("Função corporativa não encontrada.")

            # Remove permissões anteriores
            cur.execute("DELETE FROM role_permissions WHERE role_id = ?", (role_id,))

            # Insere as novas permissões de forma determinística
            for code in set(permissions):
                cur.execute(
                    "INSERT INTO role_permissions (account_id, role_id, permission_code) VALUES (?, ?, ?)",
                    (account_id, role_id, code)
                )

            return {
                "success": True,
                "role_id": role_id,
                "role_name": role_row["name"],
                "permissions_count": len(set(permissions)),
                "permissions": list(set(permissions))
            }
    finally:
        conn.close()


from src.features.hierarchy.schemas import SalesTargetCreate, CommissionRuleCreate


def _get_team_subtree_ids(conn, team_id: str) -> List[str]:
    """Retorna IDs do time e de todos os seus descendentes recursivos via CTE."""
    cur = conn.cursor()
    cur.execute("""
        WITH RECURSIVE subteams AS (
            SELECT id FROM teams WHERE id = ?
            UNION ALL
            SELECT t.id FROM teams t
            JOIN subteams s ON t.parent_id = s.id
        )
        SELECT id FROM subteams;
    """, (team_id,))
    return [r[0] for r in cur.fetchall()]


def _get_bu_team_ids(conn, bu_id: str) -> List[str]:
    """Retorna todos os time_ids vinculados a uma Business Unit."""
    cur = conn.cursor()
    cur.execute("SELECT id FROM teams WHERE business_unit_id = ?", (bu_id,))
    return [r[0] for r in cur.fetchall()]


def list_targets(
    account_id: str = "0f14ffff",
    period: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lista metas comerciais calculando o atingimento real em tempo real a partir dos deals ganhos."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = "SELECT * FROM sales_targets WHERE account_id = ?"
        params: List[Any] = [account_id]
        if period:
            query += " AND period = ?"
            params.append(period)
        query += " ORDER BY created_at DESC"
        cur.execute(query, tuple(params))
        targets = [dict(r) for r in cur.fetchall()]

        for t in targets:
            entity_name = "Meta Geral"
            achieved = 0.0

            if t.get("user_id"):
                cur.execute("SELECT name FROM users WHERE id = ?", (t["user_id"],))
                u = cur.fetchone()
                entity_name = u["name"] if u else t["user_id"]
                cur.execute(
                    "SELECT COALESCE(SUM(value), 0.0) FROM deals WHERE owner_id = ? AND stage_id = 105",
                    (t["user_id"],)
                )
                achieved = float(cur.fetchone()[0])
            elif t.get("team_id"):
                cur.execute("SELECT name FROM teams WHERE id = ?", (t["team_id"],))
                tm = cur.fetchone()
                entity_name = tm["name"] if tm else t["team_id"]
                team_ids = _get_team_subtree_ids(conn, t["team_id"])
                if team_ids:
                    placeholders = ",".join(["?"] * len(team_ids))
                    cur.execute(
                        f"SELECT COALESCE(SUM(value), 0.0) FROM deals WHERE team_id IN ({placeholders}) AND stage_id = 105",
                        tuple(team_ids)
                    )
                    achieved = float(cur.fetchone()[0])
            elif t.get("business_unit_id"):
                cur.execute("SELECT name FROM business_units WHERE id = ?", (t["business_unit_id"],))
                bu = cur.fetchone()
                entity_name = bu["name"] if bu else t["business_unit_id"]
                team_ids = _get_bu_team_ids(conn, t["business_unit_id"])
                if team_ids:
                    placeholders = ",".join(["?"] * len(team_ids))
                    cur.execute(
                        f"SELECT COALESCE(SUM(value), 0.0) FROM deals WHERE team_id IN ({placeholders}) AND stage_id = 105",
                        tuple(team_ids)
                    )
                    achieved = float(cur.fetchone()[0])

            target_val = float(t.get("target_amount") or 1.0)
            rate = round((achieved / target_val) * 100, 2) if target_val > 0 else 0.0

            t["entity_name"] = entity_name
            t["achieved_amount"] = achieved
            t["achievement_rate_pct"] = rate

        return targets
    finally:
        conn.close()


def create_target(
    data: SalesTargetCreate,
    account_id: str = "0f14ffff",
    created_by: Optional[str] = None
) -> Dict[str, Any]:
    """Cria uma nova meta comercial vinculada a consultor, equipe ou BU."""
    if not any([data.business_unit_id, data.team_id, data.user_id]):
        raise ValueError("Ao menos uma entidade (user_id, team_id ou business_unit_id) deve ser informada para a meta.")

    target_id = f"tgt-{uuid.uuid4().hex[:8]}"
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                "INSERT INTO sales_targets (id, account_id, period, business_unit_id, team_id, user_id, "
                "target_amount, created_by, calculation_basis, growth_rate_pct) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    target_id, account_id, data.period, data.business_unit_id, data.team_id, data.user_id,
                    data.target_amount, created_by, data.calculation_basis, data.growth_rate_pct
                )
            )
        targets = list_targets(account_id=account_id, period=data.period)
        return next((t for t in targets if t["id"] == target_id), {})
    finally:
        conn.close()


def get_target_suggestion(
    entity_type: str,
    entity_id: str,
    period: str = "2026-Q4",
    growth_rate_pct: float = 15.0,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Calcula deterministicamente a sugestão algorítmica de meta com taxa de evolução crescente."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        historical_base = 0.0
        entity_name = entity_id

        if entity_type == "user":
            cur.execute("SELECT name FROM users WHERE id = ?", (entity_id,))
            u = cur.fetchone()
            if u:
                entity_name = u["name"]
            cur.execute(
                "SELECT COALESCE(SUM(value), 0.0) FROM deals WHERE owner_id = ? AND stage_id = 105",
                (entity_id,)
            )
            historical_base = float(cur.fetchone()[0])
            if historical_base == 0.0:
                historical_base = 50000.0  # Baseline inicial de consultor odontológico

        elif entity_type == "team":
            cur.execute("SELECT name FROM teams WHERE id = ?", (entity_id,))
            tm = cur.fetchone()
            if tm:
                entity_name = tm["name"]
            team_ids = _get_team_subtree_ids(conn, entity_id)
            if team_ids:
                placeholders = ",".join(["?"] * len(team_ids))
                cur.execute(
                    f"SELECT COALESCE(SUM(value), 0.0) FROM deals WHERE team_id IN ({placeholders}) AND stage_id = 105",
                    tuple(team_ids)
                )
                historical_base = float(cur.fetchone()[0])
            if historical_base == 0.0:
                historical_base = 200000.0  # Baseline regional

        elif entity_type == "bu":
            cur.execute("SELECT name FROM business_units WHERE id = ?", (entity_id,))
            bu = cur.fetchone()
            if bu:
                entity_name = bu["name"]
            team_ids = _get_bu_team_ids(conn, entity_id)
            if team_ids:
                placeholders = ",".join(["?"] * len(team_ids))
                cur.execute(
                    f"SELECT COALESCE(SUM(value), 0.0) FROM deals WHERE team_id IN ({placeholders}) AND stage_id = 105",
                    tuple(team_ids)
                )
                historical_base = float(cur.fetchone()[0])
            if historical_base == 0.0:
                historical_base = 800000.0  # Baseline divisão de produtos

        suggested = round(historical_base * (1.0 + (growth_rate_pct / 100.0)), 2)
        explanation = (
            f"Base histórica realizada de R$ {historical_base:,.2f} com aplicação de fator "
            f"de aceleração de mercado de +{growth_rate_pct}% para o ciclo {period}."
        )

        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "entity_name": entity_name,
            "period": period,
            "historical_base": historical_base,
            "growth_rate_pct": growth_rate_pct,
            "suggested_target": suggested,
            "explanation": explanation
        }
    finally:
        conn.close()


def list_commission_rules(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    """Lista as regras de comissionamento por cargo ativas na empresa."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT cr.id, cr.account_id, cr.role_id, r.name as role_name,
                   cr.base_percentage, cr.accelerator_threshold_pct, cr.accelerator_percentage,
                   cr.is_active, cr.created_at
            FROM commission_rules cr
            JOIN roles r ON cr.role_id = r.id
            WHERE cr.account_id = ?
            ORDER BY cr.base_percentage DESC
        """, (account_id,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def create_commission_rule(
    data: CommissionRuleCreate,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Cria ou atualiza uma regra de comissionamento para uma função/cargo."""
    rule_id = f"crule-{uuid.uuid4().hex[:6]}"
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM roles WHERE id = ? AND account_id = ?", (data.role_id, account_id))
            if not cur.fetchone():
                raise ValueError(f"Cargo '{data.role_id}' não encontrado na conta.")

            # Remove regra prévia para manter 1 regra ativa por cargo
            cur.execute("DELETE FROM commission_rules WHERE role_id = ? AND account_id = ?", (data.role_id, account_id))
            cur.execute("""
                INSERT INTO commission_rules (id, account_id, role_id, base_percentage, accelerator_threshold_pct, accelerator_percentage)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (rule_id, account_id, data.role_id, data.base_percentage, data.accelerator_threshold_pct, data.accelerator_percentage))

        rules = list_commission_rules(account_id)
        return next((r for r in rules if r["role_id"] == data.role_id), {})
    finally:
        conn.close()


def get_commission_statement(
    user_id: str,
    period: str = "2026-Q4",
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Gera o extrato determinístico de comissões calculando atingimento, overrides e acelerador de meta."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        # 1. Obter usuário e cargo
        cur.execute("""
            SELECT u.id, u.name, u.team_id, u.role_id, r.name as role_name, r.default_data_scope
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.id = ? AND u.account_id = ?
        """, (user_id, account_id))
        user_row = cur.fetchone()
        if not user_row:
            raise ValueError(f"Usuário '{user_id}' não encontrado.")

        role_name = user_row["role_name"] or "Consultor"
        data_scope = user_row["default_data_scope"] or "self"

        # 2. Obter regra de comissão aplicável
        cur.execute("SELECT * FROM commission_rules WHERE role_id = ? AND account_id = ?", (user_row["role_id"], account_id))
        rule = cur.fetchone()
        if rule:
            base_pct = float(rule["base_percentage"])
            accel_thresh = float(rule["accelerator_threshold_pct"])
            accel_pct = float(rule["accelerator_percentage"])
        else:
            # Defaults de mercado se não houver regra configurada
            if "Gerente Regional" in role_name:
                base_pct, accel_thresh, accel_pct = 1.5, 100.0, 2.5
            elif "Gerente Distrital" in role_name:
                base_pct, accel_thresh, accel_pct = 0.8, 100.0, 1.5
            else:
                base_pct, accel_thresh, accel_pct = 5.0, 100.0, 7.5

        # 3. Obter meta do período
        cur.execute(
            "SELECT target_amount FROM sales_targets WHERE user_id = ? AND period = ? AND account_id = ?",
            (user_id, period, account_id)
        )
        target_row = cur.fetchone()
        target_amount = float(target_row["target_amount"]) if target_row else 100000.0

        # 4. Obter deals elegíveis conforme hierarquia do usuário
        deals_query = ""
        params: List[Any] = []
        payout_type = "direta"

        if data_scope == "self" or "Consultor" in role_name:
            deals_query = "SELECT id, title, value FROM deals WHERE owner_id = ? AND stage_id = 105"
            params = [user_id]
            payout_type = "direta"
        elif data_scope in ("team", "subtree") and user_row["team_id"]:
            team_ids = _get_team_subtree_ids(conn, user_row["team_id"])
            placeholders = ",".join(["?"] * len(team_ids))
            deals_query = f"SELECT id, title, value FROM deals WHERE team_id IN ({placeholders}) AND stage_id = 105"
            params = list(team_ids)
            payout_type = "override_regional" if data_scope == "team" else "override_distrital"
        else:
            deals_query = "SELECT id, title, value FROM deals WHERE stage_id = 105"
            params = []
            payout_type = "direta"

        cur.execute(deals_query, tuple(params))
        deals_won = [dict(d) for d in cur.fetchall()]

        achieved_amount = sum(float(d["value"]) for d in deals_won)
        achievement_rate = round((achieved_amount / target_amount) * 100, 2) if target_amount > 0 else 0.0
        is_accelerated = achievement_rate >= accel_thresh

        rate_applied = accel_pct if is_accelerated else base_pct

        items: List[Dict[str, Any]] = []
        total_commission = 0.0

        for d in deals_won:
            val = float(d["value"])
            comm = round(val * (rate_applied / 100.0), 2)
            total_commission += comm
            items.append({
                "deal_id": d["id"],
                "deal_title": d["title"],
                "deal_value": val,
                "commission_rate_pct": rate_applied,
                "commission_amount": comm,
                "payout_type": payout_type
            })

        return {
            "user_id": user_id,
            "user_name": user_row["name"],
            "role_id": user_row["role_id"] or "",
            "role_name": role_name,
            "period": period,
            "target_amount": target_amount,
            "achieved_amount": achieved_amount,
            "achievement_rate_pct": achievement_rate,
            "is_accelerated": is_accelerated,
            "total_commission": round(total_commission, 2),
            "items": items
        }
    finally:
        conn.close()

