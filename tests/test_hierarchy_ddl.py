# -*- coding: utf-8 -*-
"""
Testes TDD - TICKET-01: Migração DDL e Modelagem Relacional no SQLite WAL
Valida a integridade das tabelas de hierarquia e escopo organizacional.
"""

from src.core.database import get_connection, init_db


def test_hierarchy_tables_exist():
    """Valida se as tabelas relacionais de hierarquia foram criadas."""
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    expected_tables = ["business_units", "teams", "roles", "role_permissions", "users"]
    for table in expected_tables:
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name = ?", 
            (table,)
        )
        row = cur.fetchone()
        assert row is not None, f"Tabela obrigatória '{table}' não foi encontrada no SQLite WAL"

    conn.close()


def test_entities_have_owner_and_team_id():
    """Valida se consignments, deals e contacts possuem owner_id e team_id."""
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    entities = ["consignments", "deals", "contacts"]
    for entity in entities:
        cur.execute(f"PRAGMA table_info({entity})")
        cols = [col[1] for col in cur.fetchall()]
        assert "owner_id" in cols, f"Coluna 'owner_id' ausente na tabela '{entity}'"
        assert "team_id" in cols, f"Coluna 'team_id' ausente na tabela '{entity}'"

    conn.close()


def test_superadmin_user_seed_exists():
    """Valida se o usuário Super Admin (User God) inicial está registrado."""
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name, is_superadmin FROM users WHERE is_superadmin = 1")
    superadmin = cur.fetchone()
    assert superadmin is not None, "Usuário Super Admin (User God) deve existir no banco"
    assert superadmin["is_superadmin"] == 1

    conn.close()
