# -*- coding: utf-8 -*-
"""
TDD for [TICKET-00] Async Stack Foundation & Frontend Workspace
Validates:
- SQLAlchemy 2.0 Async engine, sessionmaker, and async connection cycle
- Compatibility with existing synchronous DB functions
- Alembic configuration and migration environment
- Frontend package.json, tsconfig, tailwind tokens, and AppShell structure
"""

import os
import json
import asyncio
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine


def test_async_engine_and_session_cycle():
    """Valida ciclo assíncrono do SQLAlchemy 2.0 com get_async_session."""
    async def _run():
        from src.core.database import get_async_engine, get_async_session, AsyncSessionLocal

        engine = get_async_engine()
        assert isinstance(engine, AsyncEngine)

        async for session in get_async_session():
            assert isinstance(session, AsyncSession)
            result = await session.execute(text("SELECT 1 AS num;"))
            row = result.mappings().first()
            assert row["num"] == 1
            break

    asyncio.run(_run())


def test_async_database_schema_compatibility():
    """Garante que o banco assíncrono acessa as tabelas core existentes."""
    async def _run():
        from src.core.database import get_async_session, init_db

        # Garante inicialização do banco
        init_db()

        async for session in get_async_session():
            result = await session.execute(text("SELECT COUNT(*) AS total FROM accounts;"))
            row = result.mappings().first()
            assert row["total"] >= 1
            break

    asyncio.run(_run())


def test_alembic_configuration_exists():
    """Valida presença do alembic.ini e estrutura em migrations/."""
    assert os.path.isfile("alembic.ini"), "alembic.ini não encontrado"
    assert os.path.isdir("migrations"), "Diretório migrations/ não encontrado"
    assert os.path.isfile("migrations/env.py"), "migrations/env.py não encontrado"
    assert os.path.isfile("migrations/script.py.mako"), "migrations/script.py.mako não encontrado"


def test_frontend_workspace_configuration():
    """Valida arquivos essenciais do workspace frontend."""
    frontend_dir = os.path.abspath("frontend")
    pkg_json_path = os.path.join(frontend_dir, "package.json")
    tsconfig_path = os.path.join(frontend_dir, "tsconfig.json")
    tailwind_config_path = os.path.join(frontend_dir, "tailwind.config.ts")

    assert os.path.isfile(pkg_json_path), "frontend/package.json deve existir"
    assert os.path.isfile(tsconfig_path), "frontend/tsconfig.json deve existir"
    assert os.path.isfile(tailwind_config_path), "frontend/tailwind.config.ts deve existir"

    with open(pkg_json_path, "r", encoding="utf-8") as f:
        pkg = json.load(f)

    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    assert "react" in deps, "React obrigatório no frontend"
    assert "typescript" in deps, "TypeScript obrigatório no frontend"
    assert "tailwindcss" in deps, "Tailwind CSS obrigatório no frontend"
    assert "@tanstack/react-router" in deps or "@tanstack/react-query" in deps, "TanStack stack obrigatória"


def test_frontend_design_system_and_primitives_exist():
    """Garante existência dos 15 primitivos de UI e AppShell."""
    frontend_dir = os.path.abspath("frontend")
    primitives = [
        "Button", "Input", "Badge", "Card", "DataTable",
        "KanbanBoard", "Sheet", "Dialog", "Select", "Tabs",
        "Skeleton", "EmptyState", "ErrorBoundary", "Toast", "Avatar"
    ]
    ui_dir = os.path.join(frontend_dir, "src", "components", "ui")
    assert os.path.isdir(ui_dir), f"Diretório {ui_dir} deve existir"

    for p in primitives:
        file_path = os.path.join(ui_dir, f"{p}.tsx")
        assert os.path.isfile(file_path), f"Primitivo {p}.tsx deve existir em {ui_dir}"

    app_shell_path = os.path.join(frontend_dir, "src", "components", "layout", "AppShell.tsx")
    assert os.path.isfile(app_shell_path), "AppShell.tsx deve existir"
