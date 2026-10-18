# -*- coding: utf-8 -*-
"""
Database Module — SQLite WAL Engine (Lei #3 e Lei #11)
Persistência transacional com concorrência segura e isolamento.
"""

from __future__ import annotations
import os
import sqlite3
from typing import Any, AsyncGenerator, Dict, List, Optional
from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    event,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from src.core.config import DB_PATH


class Base(DeclarativeBase):
    pass


metadata: MetaData = Base.metadata

# Definição declarativa do schema core e de domínio no MetaData para o Alembic
Table(
    "accounts",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("plan", String, nullable=False, default="Enterprise Scale"),
    Column("created_at", String),
)
Table(
    "users",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("name", String, nullable=False),
    Column("email", String, nullable=False, unique=True),
    Column("role", String, nullable=False, default="Consultor"),
    Column("team_id", String),
    Column("role_id", String),
    Column("custom_data_scope", String),
    Column("is_superadmin", Integer, default=0),
    Column("created_at", String),
)
Table(
    "teams",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("business_unit_id", String, nullable=False),
    Column("parent_id", String, ForeignKey("teams.id")),
    Column("name", String, nullable=False),
    Column("leader_id", String),
    Column("created_at", String),
)
Table(
    "contacts",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("name", String, nullable=False),
    Column("email", String, nullable=False),
    Column("phone", String),
    Column("company", String),
    Column("tags", Text),
    Column("score", Integer, default=50),
    Column("owner_id", String),
    Column("field_owner_id", String),
    Column("inside_owner_id", String),
    Column("team_id", String),
    Column("cro", String),
    Column("cro_uf", String),
    Column("cro_verified", Integer, default=0),
    Column("created_at", String),
)
Table(
    "deals",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("pipeline_id", Integer, nullable=False),
    Column("stage_id", Integer, nullable=False),
    Column("title", String, nullable=False),
    Column("value", Float, nullable=False, default=0.0),
    Column("company", String, nullable=False),
    Column("contact_name", String, nullable=False),
    Column("priority", String, nullable=False, default="media"),
    Column("owner_id", String),
    Column("field_owner_id", String),
    Column("inside_owner_id", String),
    Column("team_id", String),
    Column("split_commission_field_pct", Float, default=70.0),
    Column("split_commission_inside_pct", Float, default=30.0),
    Column("executive_summary", Text),
    Column("created_at", String),
)
Table(
    "kp_partner_agreements",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("partner_name", String, nullable=False),
    Column("partner_cro_uf", String),
    Column("tier", String, nullable=False, default="SILVER"),
    Column("credit_limit", Float, nullable=False, default=0.0),
    Column("used_credit", Float, nullable=False, default=0.0),
    Column("min_monthly_revenue", Float, nullable=False, default=0.0),
    Column("max_turnover_days", Integer, nullable=False, default=60),
    Column("field_owner_id", String),
    Column("inside_owner_id", String),
    Column("is_active", Integer, nullable=False, default=1),
    Column("created_at", String),
)
Table(
    "kp_consignment_kits",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("serial_number", String, unique=True, nullable=False),
    Column("qr_code", String, nullable=False),
    Column("name", String, nullable=False),
    Column("composition_json", Text),
    Column("status", String, nullable=False, default="IN_STOCK"),
    Column("current_agreement_id", String, ForeignKey("kp_partner_agreements.id")),
    Column("created_at", String),
)
Table(
    "kp_custody_ledger",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("agreement_id", String, ForeignKey("kp_partner_agreements.id"), nullable=False),
    Column("movement_type", String, nullable=False),
    Column("product_id", String, nullable=False),
    Column("product_name", String, nullable=False),
    Column("anvisa_reg", String, nullable=False),
    Column("batch_number", String, nullable=False),
    Column("serial_number", String),
    Column("quantity", Integer, nullable=False, default=1),
    Column("unit_value", Float, nullable=False, default=0.0),
    Column("total_value", Float, nullable=False, default=0.0),
    Column("sterilization_expiry_date", String, nullable=False),
    Column("created_at", String),
)
Table(
    "kp_surgical_orders",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("agreement_id", String, ForeignKey("kp_partner_agreements.id"), nullable=False),
    Column("patient_identifier", String),
    Column("surgery_date", String, nullable=False),
    Column("status", String, nullable=False, default="SOLICITADO_FIELD"),
    Column("field_consultant_id", String),
    Column("inside_analyst_id", String),
    Column("remitted_items_json", Text),
    Column("consumed_items_json", Text),
    Column("returned_items_json", Text),
    Column("seal_photo_r2_key", String),
    Column("billing_order_id", String),
    Column("created_at", String),
    Column("updated_at", String),
)
Table(
    "kp_kol_contracts",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("agreement_id", String, ForeignKey("kp_partner_agreements.id")),
    Column("kol_name", String, nullable=False),
    Column("cro_uf", String, nullable=False),
    Column("equipment_name", String, nullable=False),
    Column("asset_tag", String, unique=True, nullable=False),
    Column("min_monthly_implants_target", Integer, nullable=False, default=20),
    Column("clinical_lectures_quota", Integer, nullable=False, default=1),
    Column("current_month_consumption", Integer, nullable=False, default=0),
    Column("compliance_status", String, nullable=False, default="COMPLIANT"),
    Column("evidence_r2_keys_json", Text),
    Column("created_at", String),
    Column("updated_at", String),
)
Table(
    "kp_loyalty_wallets",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("partner_id", String, unique=True, nullable=False),
    Column("partner_name", String, nullable=False),
    Column("points_balance", Integer, nullable=False, default=0),
    Column("lifetime_points", Integer, nullable=False, default=0),
    Column("current_tier", String, nullable=False, default="SILVER"),
    Column("implants_billed_total", Integer, nullable=False, default=0),
    Column("created_at", String),
    Column("updated_at", String),
)
Table(
    "dentgo_hubs",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("name", String, nullable=False),
    Column("cnpj", String, nullable=False),
    Column("latitude", Float, nullable=False),
    Column("longitude", Float, nullable=False),
    Column("coverage_radius_km", Float, nullable=False, default=30.0),
    Column("on_duty_schedule", String, default="24h"),
    Column("is_active", Integer, nullable=False, default=1),
    Column("created_at", String),
)
Table(
    "dentgo_hub_inventory",
    metadata,
    Column("id", String, primary_key=True),
    Column("hub_id", String, ForeignKey("dentgo_hubs.id"), nullable=False),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("product_id", String, nullable=False),
    Column("product_name", String, nullable=False),
    Column("anvisa_reg", String, nullable=False),
    Column("batch_number", String, nullable=False),
    Column("quantity_available", Integer, nullable=False, default=0),
    Column("unit_price", Float, nullable=False, default=0.0),
    Column("sterilization_expiry_date", String, nullable=False),
    Column("status", String, nullable=False, default="AVAILABLE"),
    Column("created_at", String),
)
Table(
    "dentgo_orders",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("hub_id", String, ForeignKey("dentgo_hubs.id"), nullable=False),
    Column("customer_cro_uf", String, nullable=False),
    Column("cro_verified", Integer, nullable=False, default=0),
    Column("delivery_address", String, nullable=False),
    Column("delivery_lat", Float, nullable=False),
    Column("delivery_lng", Float, nullable=False),
    Column("distance_km", Float, nullable=False, default=0.0),
    Column("estimated_eta_minutes", Integer, nullable=False, default=60),
    Column("items_json", Text, nullable=False),
    Column("subtotal", Float, nullable=False, default=0.0),
    Column("urgency_fee", Float, nullable=False, default=0.0),
    Column("total_amount", Float, nullable=False, default=0.0),
    Column("status", String, nullable=False, default="ORDER_PLACED"),
    Column("courier_id", String),
    Column("seal_code", String),
    Column("delivery_pin", String),
    Column("proof_of_delivery_r2_key", String),
    Column("recipient_signature_name", String),
    Column("delivered_at", String),
    Column("created_at", String),
)
Table(
    "dentgo_financial_splits",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("order_id", String, ForeignKey("dentgo_orders.id"), nullable=False),
    Column("gross_amount", Float, nullable=False),
    Column("items_amount", Float, nullable=False),
    Column("delivery_fee_total", Float, nullable=False),
    Column("platform_take_rate_pct", Float, nullable=False, default=5.0),
    Column("platform_fee_amount", Float, nullable=False),
    Column("courier_net_payout", Float, nullable=False),
    Column("seller_net_payout", Float, nullable=False),
    Column("payment_method", String, nullable=False, default="PIX_INSTANT"),
    Column("agreement_id", String),
    Column("settlement_status", String, nullable=False, default="SETTLED"),
    Column("created_at", String),
)
Table(
    "anvisa_rma_claims",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("ticket_id", String, nullable=False),
    Column("agreement_id", String),
    Column("surgeon_name", String),
    Column("surgeon_cro_uf", String, nullable=False),
    Column("patient_identifier", String),
    Column("product_id", String, nullable=False),
    Column("product_name", String, nullable=False),
    Column("batch_number", String, nullable=False),
    Column("serial_number", String),
    Column("fdi_tooth_region", String, nullable=False),
    Column("insertion_torque_ncm", Float, nullable=False),
    Column("surgery_date", String, nullable=False),
    Column("explant_date", String, nullable=False),
    Column("failure_reason", String, nullable=False),
    Column("radiograph_r2_key", String, nullable=False),
    Column("status", String, nullable=False, default="SUBMITTED"),
    Column("warranty_approved", Integer, nullable=False, default=0),
    Column("replacement_order_id", String),
    Column("quarantine_triggered", Integer, nullable=False, default=0),
    Column("notes", Text),
    Column("created_at", String),
    Column("updated_at", String),
)
Table(
    "anvisa_batch_quarantines",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("batch_number", String, nullable=False),
    Column("product_id", String),
    Column("total_distributed", Integer, nullable=False, default=0),
    Column("total_failures", Integer, nullable=False, default=0),
    Column("failure_rate_percent", Float, nullable=False, default=0.0),
    Column("status", String, nullable=False, default="QUARANTINE_BLOCKED"),
    Column("reason", Text, nullable=False),
    Column("blocked_at", String),
    Column("unblocked_at", String),
)
Table(
    "semantic_embeddings",
    metadata,
    Column("id", String, primary_key=True),
    Column("tenant_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("entity_type", String, nullable=False),
    Column("entity_id", String, nullable=False),
    Column("content_chunk", Text, nullable=False),
    Column("embedding", Text, nullable=False),
    Column("metadata_json", Text),
    Column("created_at", String),
)
Table(
    "scoring_history",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("contact_id", Integer, nullable=False),
    Column("previous_score", Integer, nullable=False, default=0),
    Column("new_score", Integer, nullable=False, default=0),
    Column("icp_fit_score", Integer, nullable=False, default=0),
    Column("engagement_score", Integer, nullable=False, default=0),
    Column("tier", String, nullable=False, default="C"),
    Column("trigger_reason", String),
    Column("created_at", String),
)
Table(
    "tenant_credentials",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("service_name", String, nullable=False),
    Column("credential_type", String, nullable=False),
    Column("encrypted_payload", Text, nullable=False),
    Column("metadata_json", Text),
    Column("created_at", String),
    Column("updated_at", String),
)
Table(
    "webhook_subscriptions",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("name", String, nullable=False),
    Column("target_url", String, nullable=False),
    Column("subscribed_events_json", Text, nullable=False),
    Column("signing_secret", String, nullable=False),
    Column("signing_secret_encrypted", Text),
    Column("is_active", Integer, nullable=False, default=1),
    Column("consecutive_failures", Integer, nullable=False, default=0),
    Column("circuit_breaker_tripped", Integer, nullable=False, default=0),
    Column("created_at", String),
)
Table(
    "erp_fiscal_invoices",
    metadata,
    Column("id", String, primary_key=True),
    Column("account_id", String, ForeignKey("accounts.id"), nullable=False),
    Column("erp_type", String, nullable=False, default="totvs_protheus"),
    Column("flow_type", String, nullable=False),
    Column("reference_id", String, nullable=False),
    Column("cfop", String, nullable=False),
    Column("nfe_number", String, nullable=False),
    Column("nfe_series", String, nullable=False, default="1"),
    Column("nfe_access_key", String, unique=True, nullable=False),
    Column("recipient_cnpj_cpf", String, nullable=False),
    Column("recipient_name", String, nullable=False),
    Column("total_invoice_value", Float, nullable=False, default=0.0),
    Column("xml_r2_key", String, nullable=False),
    Column("danfe_pdf_r2_key", String, nullable=False),
    Column("status", String, nullable=False, default="AUTORIZADA"),
    Column("sefaz_protocol", String),
    Column("windmill_job_id", String),
    Column("created_at", String),
)

_write_engine: Optional[AsyncEngine] = None
_read_engine: Optional[AsyncEngine] = None
_WriteSessionLocal: Optional[async_sessionmaker[AsyncSession]] = None
_ReadSessionLocal: Optional[async_sessionmaker[AsyncSession]] = None


def _normalize_async_db_url(raw_url: str) -> str:
    url = raw_url.strip()
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url[len("postgresql://"):]
    if url.startswith("sqlite:///") and not url.startswith("sqlite+aiosqlite:///"):
        return "sqlite+aiosqlite:///" + url[len("sqlite:///"):]
    return url


def get_async_database_url(read_only: bool = False) -> str:
    env_url = (
        (os.getenv("READ_DATABASE_URL") or os.getenv("DATABASE_URL"))
        if read_only
        else os.getenv("DATABASE_URL")
    )
    if env_url:
        return _normalize_async_db_url(env_url)
    db_str = str(DB_PATH).replace("\\", "/")
    return f"sqlite+aiosqlite:///{db_str}"


def _build_async_engine(url: str) -> AsyncEngine:
    is_sqlite = url.startswith("sqlite")
    kwargs: Dict[str, Any] = {
        "echo": False,
        "future": True,
    }
    if is_sqlite:
        kwargs["connect_args"] = {"timeout": 10.0}

    engine = create_async_engine(url, **kwargs)

    if is_sqlite:
        @event.listens_for(engine.sync_engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.execute("PRAGMA busy_timeout=5000;")
            cursor.close()

    return engine


def get_write_engine() -> AsyncEngine:
    global _write_engine
    target_url = get_async_database_url(read_only=False)
    if _write_engine is None or str(_write_engine.url) != target_url:
        _write_engine = _build_async_engine(target_url)
    return _write_engine


def get_read_engine() -> AsyncEngine:
    global _read_engine
    target_url = get_async_database_url(read_only=True)
    if _read_engine is None or str(_read_engine.url) != target_url:
        _read_engine = _build_async_engine(target_url)
    return _read_engine


def get_async_engine() -> AsyncEngine:
    return get_write_engine()


def get_async_session_maker(read_only: bool = False) -> async_sessionmaker[AsyncSession]:
    global _WriteSessionLocal, _ReadSessionLocal
    if read_only:
        engine = get_read_engine()
        if _ReadSessionLocal is None or _ReadSessionLocal.kw.get("bind") is not engine:
            _ReadSessionLocal = async_sessionmaker(
                bind=engine,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
                class_=AsyncSession,
            )
        return _ReadSessionLocal

    engine = get_write_engine()
    if _WriteSessionLocal is None or _WriteSessionLocal.kw.get("bind") is not engine:
        _WriteSessionLocal = async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
            class_=AsyncSession,
        )
    return _WriteSessionLocal


def AsyncSessionLocal() -> AsyncSession:
    return get_async_session_maker(read_only=False)()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = get_async_session_maker(read_only=False)
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_write_db() -> AsyncGenerator[AsyncSession, None]:
    """Sessão assíncrona dedicada a operações de escrita (Primary OLTP — DATABASE_URL)."""
    async_session = get_async_session_maker(read_only=False)
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_read_db() -> AsyncGenerator[AsyncSession, None]:
    """Sessão assíncrona dedicada a consultas de leitura analítica (Replica OLAP — READ_DATABASE_URL)."""
    async_session = get_async_session_maker(read_only=True)
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA temp_store=MEMORY;")
    conn.execute("PRAGMA cache_size=-32000;")
    return conn



def init_db() -> None:
    conn = get_connection()
    with conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            plan TEXT NOT NULL DEFAULT 'Enterprise Scale',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL DEFAULT 'Consultor',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS pipelines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS stages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pipeline_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            color TEXT NOT NULL,
            step_order INTEGER NOT NULL,
            probability INTEGER NOT NULL DEFAULT 50,
            FOREIGN KEY (pipeline_id) REFERENCES pipelines(id)
        );

        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            company TEXT,
            tags TEXT, -- JSON array
            score INTEGER DEFAULT 50,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS deals (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            pipeline_id INTEGER NOT NULL,
            stage_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            value REAL NOT NULL DEFAULT 0.0,
            company TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'media',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (pipeline_id) REFERENCES pipelines(id),
            FOREIGN KEY (stage_id) REFERENCES stages(id)
        );

        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            company TEXT NOT NULL,
            channel TEXT NOT NULL DEFAULT 'whatsapp',
            unread INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            sender TEXT NOT NULL, -- 'user' | 'contact'
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        );

        CREATE TABLE IF NOT EXISTS webhooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT NOT NULL,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            event_type TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            secret TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS webhook_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            webhook_id INTEGER NOT NULL,
            payload TEXT NOT NULL,
            status_code INTEGER,
            response_body TEXT,
            delivered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (webhook_id) REFERENCES webhooks(id)
        );

        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            title TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'media',
            status TEXT NOT NULL DEFAULT 'aberto',
            category TEXT NOT NULL DEFAULT 'Suporte Técnico',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            title TEXT NOT NULL,
            due_date TEXT NOT NULL,
            assignee TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'media',
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS campaigns (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            name TEXT NOT NULL,
            channel TEXT NOT NULL,
            utm_source TEXT NOT NULL,
            utm_medium TEXT NOT NULL,
            utm_campaign TEXT NOT NULL,
            budget REAL NOT NULL DEFAULT 0.0,
            spend REAL NOT NULL DEFAULT 0.0,
            revenue REAL NOT NULL DEFAULT 0.0,
            leads_count INTEGER NOT NULL DEFAULT 0,
            deals_count INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'ativa',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS scoring_rules (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            condition_key TEXT NOT NULL,
            condition_val TEXT NOT NULL,
            points INTEGER NOT NULL DEFAULT 10,
            impact_description TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS institutions (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            name TEXT NOT NULL,
            institution_type TEXT NOT NULL DEFAULT 'Faculdade',
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            coordinator_name TEXT NOT NULL,
            active_students_count INTEGER DEFAULT 0,
            accreditation_status TEXT DEFAULT 'credenciada',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        DROP TABLE IF EXISTS surgery_replacements;
        DROP TABLE IF EXISTS consignment_items;
        DROP TABLE IF EXISTS consignments;

        CREATE TABLE IF NOT EXISTS business_units (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            name TEXT NOT NULL,
            code TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS teams (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            business_unit_id TEXT NOT NULL,
            parent_id TEXT,
            name TEXT NOT NULL,
            leader_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (business_unit_id) REFERENCES business_units(id),
            FOREIGN KEY (parent_id) REFERENCES teams(id)
        );

        CREATE TABLE IF NOT EXISTS roles (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            default_data_scope TEXT NOT NULL DEFAULT 'self',
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS role_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT NOT NULL,
            role_id TEXT NOT NULL,
            permission_code TEXT NOT NULL,
            FOREIGN KEY (role_id) REFERENCES roles(id)
        );

        CREATE TABLE IF NOT EXISTS sales_targets (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            period TEXT NOT NULL,
            business_unit_id TEXT,
            team_id TEXT,
            user_id TEXT,
            target_amount REAL NOT NULL,
            created_by TEXT,
            calculation_basis TEXT DEFAULT 'manual',
            growth_rate_pct REAL DEFAULT 15.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (business_unit_id) REFERENCES business_units(id),
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS commission_rules (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            role_id TEXT NOT NULL,
            base_percentage REAL NOT NULL,
            accelerator_threshold_pct REAL DEFAULT 100.0,
            accelerator_percentage REAL DEFAULT 7.5,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (role_id) REFERENCES roles(id)
        );

        CREATE TABLE IF NOT EXISTS deal_audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deal_id TEXT NOT NULL,
            user_id TEXT,
            author_name TEXT NOT NULL,
            action TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (deal_id) REFERENCES deals(id)
        );

        CREATE TABLE IF NOT EXISTS contact_audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            user_id TEXT,
            author_name TEXT NOT NULL,
            action TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        );

        CREATE TABLE IF NOT EXISTS integration_outbox (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            integration_type TEXT NOT NULL,
            idempotency_key TEXT NOT NULL UNIQUE,
            payload TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            attempts INTEGER NOT NULL DEFAULT 0,
            last_error TEXT,
            response_body TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE INDEX IF NOT EXISTS idx_outbox_idempotency ON integration_outbox(idempotency_key);
        CREATE INDEX IF NOT EXISTS idx_outbox_status ON integration_outbox(status);

        CREATE TABLE IF NOT EXISTS contact_institutions (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            contact_id INTEGER NOT NULL,
            institution_id TEXT NOT NULL,
            relationship_type TEXT NOT NULL DEFAULT 'operates_at',
            role_title TEXT,
            is_kol INTEGER NOT NULL DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (contact_id) REFERENCES contacts(id),
            FOREIGN KEY (institution_id) REFERENCES institutions(id)
        );

        CREATE INDEX IF NOT EXISTS idx_contact_institutions_contact ON contact_institutions(contact_id);
        CREATE INDEX IF NOT EXISTS idx_contact_institutions_inst ON contact_institutions(institution_id);

        CREATE TABLE IF NOT EXISTS automation_flows (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            trigger_event TEXT NOT NULL,
            action_description TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            execution_count INTEGER NOT NULL DEFAULT 0,
            last_run_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS automation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT NOT NULL,
            flow_id TEXT NOT NULL,
            trigger_payload TEXT,
            result_summary TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'success',
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (flow_id) REFERENCES automation_flows(id)
        );

        CREATE TABLE IF NOT EXISTS semantic_embeddings (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            content_chunk TEXT NOT NULL,
            embedding TEXT NOT NULL,
            metadata_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES accounts(id)
        );

        CREATE INDEX IF NOT EXISTS idx_embeddings_tenant ON semantic_embeddings(tenant_id, entity_type);

        CREATE TABLE IF NOT EXISTS tenant_credentials (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            service_name TEXT NOT NULL,
            credential_type TEXT NOT NULL,
            encrypted_payload TEXT NOT NULL,
            metadata_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE INDEX IF NOT EXISTS idx_creds_account ON tenant_credentials(account_id, service_name);

        CREATE TABLE IF NOT EXISTS landing_pages (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            template_type TEXT NOT NULL DEFAULT 'imersao_fluxo_digital',
            gjs_html TEXT,
            gjs_css TEXT,
            gjs_components_json TEXT,
            cfo_responsible_cro TEXT,
            cfo_responsible_name TEXT,
            published_r2_url TEXT,
            is_published INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES accounts(id)
        );

        CREATE INDEX IF NOT EXISTS idx_lp_tenant_slug ON landing_pages(tenant_id, slug);

        CREATE TABLE IF NOT EXISTS landing_page_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            landing_page_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            cro TEXT,
            cro_uf TEXT,
            specialty TEXT,
            utm_source TEXT,
            utm_medium TEXT,
            utm_campaign TEXT,
            utm_content TEXT,
            utm_term TEXT,
            contact_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (landing_page_id) REFERENCES landing_pages(id),
            FOREIGN KEY (tenant_id) REFERENCES accounts(id)
        );

        CREATE INDEX IF NOT EXISTS idx_lp_subs_lp ON landing_page_submissions(landing_page_id);

        CREATE TABLE IF NOT EXISTS call_recordings (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            room_name TEXT NOT NULL,
            deal_id TEXT,
            ticket_id TEXT,
            caller_identity TEXT NOT NULL,
            receiver_identity TEXT,
            call_type TEXT NOT NULL DEFAULT 'webrtc',
            status TEXT NOT NULL DEFAULT 'initiated',
            duration_seconds INTEGER DEFAULT 0,
            r2_recording_url TEXT,
            r2_audio_key TEXT,
            egress_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (deal_id) REFERENCES deals(id)
        );

        CREATE INDEX IF NOT EXISTS idx_call_rec_deal ON call_recordings(deal_id);
        CREATE INDEX IF NOT EXISTS idx_call_rec_room ON call_recordings(room_name);

        CREATE TABLE IF NOT EXISTS call_transcriptions (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            call_id TEXT NOT NULL,
            deal_id TEXT,
            full_text TEXT NOT NULL,
            language TEXT NOT NULL DEFAULT 'pt',
            model_name TEXT NOT NULL DEFAULT 'faster-whisper-medium',
            segments_json TEXT NOT NULL,
            speakers_detected INTEGER DEFAULT 2,
            duration_seconds REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (call_id) REFERENCES call_recordings(id),
            FOREIGN KEY (deal_id) REFERENCES deals(id)
        );

        CREATE INDEX IF NOT EXISTS idx_transc_call ON call_transcriptions(call_id);
        CREATE INDEX IF NOT EXISTS idx_transc_deal ON call_transcriptions(deal_id);

        CREATE TABLE IF NOT EXISTS deal_objections (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            deal_id TEXT NOT NULL,
            category TEXT NOT NULL,
            objection_text TEXT NOT NULL,
            suggested_counter_argument TEXT,
            resolved INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (deal_id) REFERENCES deals(id)
        );

        CREATE INDEX IF NOT EXISTS idx_objections_deal ON deal_objections(deal_id);

        CREATE TABLE IF NOT EXISTS products_catalog (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            sku TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            anvisa_reg TEXT,
            prosthetic_platform TEXT,
            diameter REAL,
            length REAL,
            recommended_torque INTEGER DEFAULT 35,
            base_price REAL NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE INDEX IF NOT EXISTS idx_prod_cat_sku ON products_catalog(sku);

        CREATE TABLE IF NOT EXISTS price_tables (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            table_key TEXT NOT NULL,
            name TEXT NOT NULL,
            discount_factor REAL NOT NULL DEFAULT 1.0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE INDEX IF NOT EXISTS idx_price_tables_key ON price_tables(account_id, table_key);

        CREATE TABLE IF NOT EXISTS deal_discount_requests (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            deal_id TEXT NOT NULL,
            requested_by_user_id TEXT NOT NULL,
            discount_pct REAL NOT NULL,
            max_allowed_pct REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'PENDING_APPROVAL',
            approved_by_user_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (deal_id) REFERENCES deals(id)
        );

        CREATE INDEX IF NOT EXISTS idx_disc_req_deal ON deal_discount_requests(deal_id);

        CREATE TABLE IF NOT EXISTS deal_contracts (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            deal_id TEXT NOT NULL,
            documenso_document_id TEXT,
            title TEXT NOT NULL,
            contract_type TEXT NOT NULL DEFAULT 'fornecimento_implantes',
            status TEXT NOT NULL DEFAULT 'PENDING_SIGNATURE',
            original_pdf_r2_key TEXT,
            signed_pdf_r2_key TEXT,
            signed_pdf_url TEXT,
            sha256_hash TEXT,
            signer_name TEXT,
            signer_email TEXT,
            signer_phone TEXT,
            signing_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            signed_at TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (deal_id) REFERENCES deals(id)
        );

        CREATE INDEX IF NOT EXISTS idx_contracts_deal ON deal_contracts(deal_id);
        CREATE INDEX IF NOT EXISTS idx_contracts_doc_id ON deal_contracts(documenso_document_id);

        CREATE TABLE IF NOT EXISTS kp_partner_agreements (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            partner_name TEXT NOT NULL,
            partner_cro_uf TEXT,
            tier TEXT NOT NULL DEFAULT 'SILVER',
            credit_limit REAL NOT NULL DEFAULT 0.0,
            used_credit REAL NOT NULL DEFAULT 0.0,
            min_monthly_revenue REAL NOT NULL DEFAULT 0.0,
            max_turnover_days INTEGER NOT NULL DEFAULT 60,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS kp_consignment_kits (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            serial_number TEXT UNIQUE NOT NULL,
            qr_code TEXT NOT NULL,
            name TEXT NOT NULL,
            composition_json TEXT,
            status TEXT NOT NULL DEFAULT 'IN_STOCK',
            current_agreement_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (current_agreement_id) REFERENCES kp_partner_agreements(id)
        );

        CREATE TABLE IF NOT EXISTS kp_custody_ledger (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            agreement_id TEXT NOT NULL,
            movement_type TEXT NOT NULL,
            product_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            anvisa_reg TEXT NOT NULL,
            batch_number TEXT NOT NULL,
            serial_number TEXT,
            quantity INTEGER NOT NULL DEFAULT 1,
            unit_value REAL NOT NULL DEFAULT 0.0,
            total_value REAL NOT NULL DEFAULT 0.0,
            sterilization_expiry_date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (agreement_id) REFERENCES kp_partner_agreements(id)
        );

        CREATE TABLE IF NOT EXISTS kp_surgical_orders (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            agreement_id TEXT NOT NULL,
            patient_identifier TEXT,
            surgery_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'SOLICITADO_FIELD',
            field_consultant_id TEXT,
            inside_analyst_id TEXT,
            remitted_items_json TEXT DEFAULT '[]',
            consumed_items_json TEXT DEFAULT '[]',
            returned_items_json TEXT DEFAULT '[]',
            seal_photo_r2_key TEXT,
            billing_order_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (agreement_id) REFERENCES kp_partner_agreements(id)
        );

        CREATE INDEX IF NOT EXISTS idx_kp_agr_acc ON kp_partner_agreements(account_id);
        CREATE INDEX IF NOT EXISTS idx_kp_kits_agr ON kp_consignment_kits(current_agreement_id);
        CREATE INDEX IF NOT EXISTS idx_kp_ledger_agr ON kp_custody_ledger(agreement_id);
        CREATE INDEX IF NOT EXISTS idx_kp_ledger_batch ON kp_custody_ledger(batch_number);
        CREATE INDEX IF NOT EXISTS idx_kp_surg_agr ON kp_surgical_orders(agreement_id);
        CREATE INDEX IF NOT EXISTS idx_kp_surg_status ON kp_surgical_orders(status);

        CREATE TABLE IF NOT EXISTS kp_kol_contracts (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            agreement_id TEXT,
            kol_name TEXT NOT NULL,
            cro_uf TEXT NOT NULL,
            equipment_name TEXT NOT NULL,
            asset_tag TEXT UNIQUE NOT NULL,
            min_monthly_implants_target INTEGER NOT NULL DEFAULT 20,
            clinical_lectures_quota INTEGER NOT NULL DEFAULT 1,
            current_month_consumption INTEGER NOT NULL DEFAULT 0,
            compliance_status TEXT NOT NULL DEFAULT 'COMPLIANT',
            evidence_r2_keys_json TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (agreement_id) REFERENCES kp_partner_agreements(id)
        );

        CREATE INDEX IF NOT EXISTS idx_kp_kol_acc ON kp_kol_contracts(account_id);
        CREATE INDEX IF NOT EXISTS idx_kp_kol_status ON kp_kol_contracts(compliance_status);
        CREATE INDEX IF NOT EXISTS idx_kp_kol_asset ON kp_kol_contracts(asset_tag);

        CREATE TABLE IF NOT EXISTS dentgo_hubs (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            name TEXT NOT NULL,
            cnpj TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            coverage_radius_km REAL NOT NULL DEFAULT 30.0,
            on_duty_schedule TEXT DEFAULT '24h',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS dentgo_hub_inventory (
            id TEXT PRIMARY KEY,
            hub_id TEXT NOT NULL,
            account_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            anvisa_reg TEXT NOT NULL,
            batch_number TEXT NOT NULL,
            quantity_available INTEGER NOT NULL DEFAULT 0,
            unit_price REAL NOT NULL DEFAULT 0.0,
            sterilization_expiry_date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hub_id) REFERENCES dentgo_hubs(id),
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS dentgo_orders (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            hub_id TEXT NOT NULL,
            customer_cro_uf TEXT NOT NULL,
            cro_verified INTEGER NOT NULL DEFAULT 0,
            delivery_address TEXT NOT NULL,
            delivery_lat REAL NOT NULL,
            delivery_lng REAL NOT NULL,
            distance_km REAL NOT NULL DEFAULT 0.0,
            estimated_eta_minutes INTEGER NOT NULL DEFAULT 60,
            items_json TEXT NOT NULL DEFAULT '[]',
            subtotal REAL NOT NULL DEFAULT 0.0,
            urgency_fee REAL NOT NULL DEFAULT 0.0,
            total_amount REAL NOT NULL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'ORDER_PLACED',
            courier_id TEXT,
            seal_code TEXT,
            delivery_pin TEXT,
            proof_of_delivery_r2_key TEXT,
            recipient_signature_name TEXT,
            delivered_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hub_id) REFERENCES dentgo_hubs(id),
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE INDEX IF NOT EXISTS idx_dentgo_hubs_acc ON dentgo_hubs(account_id);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_dentgo_hub_cnpj ON dentgo_hubs(cnpj);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_dentgo_inv_hub_batch ON dentgo_hub_inventory(hub_id, product_id, batch_number);
        CREATE INDEX IF NOT EXISTS idx_dentgo_orders_hub ON dentgo_orders(hub_id);
        CREATE INDEX IF NOT EXISTS idx_dentgo_orders_status ON dentgo_orders(status);

        CREATE TABLE IF NOT EXISTS dentgo_financial_splits (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            order_id TEXT NOT NULL,
            gross_amount REAL NOT NULL,
            items_amount REAL NOT NULL,
            delivery_fee_total REAL NOT NULL,
            platform_take_rate_pct REAL NOT NULL DEFAULT 5.0,
            platform_fee_amount REAL NOT NULL,
            courier_net_payout REAL NOT NULL,
            seller_net_payout REAL NOT NULL,
            payment_method TEXT NOT NULL DEFAULT 'PIX_INSTANT',
            agreement_id TEXT,
            settlement_status TEXT NOT NULL DEFAULT 'SETTLED',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES dentgo_orders(id) ON DELETE CASCADE,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE INDEX IF NOT EXISTS idx_dentgo_splits_order ON dentgo_financial_splits(order_id);
        CREATE INDEX IF NOT EXISTS idx_dentgo_splits_acc ON dentgo_financial_splits(account_id);

        CREATE TABLE IF NOT EXISTS anvisa_rma_claims (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            ticket_id TEXT NOT NULL,
            agreement_id TEXT,
            surgeon_name TEXT,
            surgeon_cro_uf TEXT NOT NULL,
            patient_identifier TEXT,
            product_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            batch_number TEXT NOT NULL,
            serial_number TEXT,
            fdi_tooth_region TEXT NOT NULL,
            insertion_torque_ncm REAL NOT NULL,
            surgery_date TEXT NOT NULL,
            explant_date TEXT NOT NULL,
            failure_reason TEXT NOT NULL,
            radiograph_r2_key TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'SUBMITTED',
            warranty_approved INTEGER NOT NULL DEFAULT 0,
            replacement_order_id TEXT,
            quarantine_triggered INTEGER NOT NULL DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_anvisa_rma_batch ON anvisa_rma_claims(batch_number);
        CREATE INDEX IF NOT EXISTS idx_anvisa_rma_ticket ON anvisa_rma_claims(ticket_id);
        CREATE INDEX IF NOT EXISTS idx_anvisa_rma_status ON anvisa_rma_claims(status);

        CREATE TABLE IF NOT EXISTS anvisa_batch_quarantines (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            batch_number TEXT NOT NULL,
            product_id TEXT,
            total_distributed INTEGER NOT NULL DEFAULT 0,
            total_failures INTEGER NOT NULL DEFAULT 0,
            failure_rate_percent REAL NOT NULL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'QUARANTINE_BLOCKED',
            reason TEXT NOT NULL,
            blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            unblocked_at TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_anvisa_quar_acc_batch ON anvisa_batch_quarantines(account_id, batch_number);

        CREATE TABLE IF NOT EXISTS postop_patient_care_schedules (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            patient_name TEXT NOT NULL,
            patient_phone TEXT NOT NULL,
            surgeon_name TEXT NOT NULL,
            surgeon_phone TEXT NOT NULL,
            procedure_name TEXT NOT NULL,
            surgery_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVE',
            milestones_json TEXT NOT NULL,
            alert_ticket_id TEXT,
            last_interaction_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE INDEX IF NOT EXISTS idx_postop_patient_phone ON postop_patient_care_schedules(patient_phone);
        CREATE INDEX IF NOT EXISTS idx_postop_status ON postop_patient_care_schedules(status);

        CREATE TABLE IF NOT EXISTS kp_predictive_inventory_scores (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            agreement_id TEXT NOT NULL,
            sok_score REAL NOT NULL,
            is_idle INTEGER NOT NULL DEFAULT 0,
            pr_score REAL NOT NULL,
            current_stock INTEGER NOT NULL,
            replenishment_needed INTEGER NOT NULL DEFAULT 0,
            recommendation TEXT,
            deal_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
            FOREIGN KEY (agreement_id) REFERENCES kp_partner_agreements(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_pred_inv_agr ON kp_predictive_inventory_scores(agreement_id);

        CREATE TABLE IF NOT EXISTS clinical_procedure_margins (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            clinic_id TEXT,
            surgery_order_id TEXT,
            procedure_name TEXT NOT NULL,
            patient_identifier TEXT,
            gross_revenue REAL NOT NULL,
            supplies_cost REAL NOT NULL,
            lab_cost REAL NOT NULL DEFAULT 0.0,
            surgeon_fee REAL NOT NULL,
            chair_hours REAL NOT NULL,
            chair_hour_cost REAL NOT NULL,
            total_chair_cost REAL NOT NULL,
            tax_rate_percent REAL NOT NULL,
            tax_amount REAL NOT NULL,
            net_margin_value REAL NOT NULL,
            net_margin_percent REAL NOT NULL,
            is_low_margin INTEGER NOT NULL DEFAULT 0,
            recommendation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_clin_margin_acc ON clinical_procedure_margins(account_id);
        CREATE INDEX IF NOT EXISTS idx_clin_margin_clinic ON clinical_procedure_margins(clinic_id);

        CREATE TABLE IF NOT EXISTS kp_surgical_health_scores (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            partner_id TEXT NOT NULL,
            partner_name TEXT NOT NULL,
            f_cirurgica REAL NOT NULL,
            g_consignado REAL NOT NULL,
            s_atendimento REAL NOT NULL,
            e_canal REAL NOT NULL,
            hsc_score REAL NOT NULL,
            classification TEXT NOT NULL,
            rescue_task_id TEXT,
            dentgo_voucher_code TEXT,
            upsell_eligible INTEGER NOT NULL DEFAULT 0,
            mgm_eligible INTEGER NOT NULL DEFAULT 0,
            recommendation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_kp_hsc_acc ON kp_surgical_health_scores(account_id);
        CREATE INDEX IF NOT EXISTS idx_kp_hsc_partner ON kp_surgical_health_scores(partner_id);

        CREATE TABLE IF NOT EXISTS kp_loyalty_wallets (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            partner_id TEXT NOT NULL UNIQUE,
            partner_name TEXT NOT NULL,
            points_balance INTEGER NOT NULL DEFAULT 0,
            lifetime_points INTEGER NOT NULL DEFAULT 0,
            current_tier TEXT NOT NULL DEFAULT 'SILVER',
            implants_billed_total INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_kp_loyalty_acc ON kp_loyalty_wallets(account_id);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_kp_loyalty_partner ON kp_loyalty_wallets(partner_id);

        CREATE TABLE IF NOT EXISTS kp_loyalty_transactions (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            wallet_id TEXT NOT NULL,
            partner_id TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            event_origin TEXT NOT NULL,
            points INTEGER NOT NULL,
            balance_after INTEGER NOT NULL,
            description TEXT NOT NULL,
            reference_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
            FOREIGN KEY (wallet_id) REFERENCES kp_loyalty_wallets(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_kp_trans_wallet ON kp_loyalty_transactions(wallet_id);
        CREATE INDEX IF NOT EXISTS idx_kp_trans_partner ON kp_loyalty_transactions(partner_id);

        CREATE TABLE IF NOT EXISTS kp_loyalty_rewards_catalog (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            name TEXT NOT NULL,
            reward_type TEXT NOT NULL,
            points_cost INTEGER NOT NULL,
            monetary_value_equivalent REAL NOT NULL DEFAULT 0.0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_kp_rewards_acc ON kp_loyalty_rewards_catalog(account_id);

        CREATE TABLE IF NOT EXISTS referral_links (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            referrer_id TEXT NOT NULL,
            referrer_name TEXT NOT NULL,
            referrer_cro_uf TEXT NOT NULL,
            referral_code TEXT NOT NULL UNIQUE,
            referral_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_ref_links_acc ON referral_links(account_id);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_ref_links_code ON referral_links(referral_code);

        CREATE TABLE IF NOT EXISTS referral_conversions (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            referral_link_id TEXT NOT NULL,
            referrer_id TEXT NOT NULL,
            referred_contact_id TEXT NOT NULL,
            referred_name TEXT NOT NULL,
            referred_cro_uf TEXT NOT NULL,
            lead_id TEXT,
            lead_score_boost INTEGER NOT NULL DEFAULT 40,
            tags TEXT DEFAULT '["origem_indicacao_kol"]',
            first_deal_id TEXT,
            status TEXT NOT NULL DEFAULT 'LEAD_CAPTURED',
            referrer_bonus_amount REAL NOT NULL DEFAULT 600.0,
            referred_bonus_amount REAL NOT NULL DEFAULT 600.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            qualified_at TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
            FOREIGN KEY (referral_link_id) REFERENCES referral_links(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_ref_conv_link ON referral_conversions(referral_link_id);
        CREATE INDEX IF NOT EXISTS idx_ref_conv_referrer ON referral_conversions(referrer_id);
        CREATE INDEX IF NOT EXISTS idx_ref_conv_referred ON referral_conversions(referred_contact_id);

        CREATE TABLE IF NOT EXISTS whatsapp_instances (



            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            instance_name TEXT NOT NULL UNIQUE,
            consultant_user_id TEXT,
            shard_node_url TEXT NOT NULL,
            phone_number TEXT,
            status TEXT NOT NULL DEFAULT 'DISCONNECTED',
            qr_code_base64 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE INDEX IF NOT EXISTS idx_whatsapp_inst_acc ON whatsapp_instances(account_id);
        CREATE INDEX IF NOT EXISTS idx_whatsapp_inst_consultant ON whatsapp_instances(consultant_user_id);

        CREATE TABLE IF NOT EXISTS omnichannel_messages (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            instance_name TEXT NOT NULL,
            remote_jid TEXT NOT NULL,
            sender_phone TEXT NOT NULL,
            message_type TEXT NOT NULL DEFAULT 'text',
            content TEXT,
            media_r2_key TEXT,
            from_me INTEGER NOT NULL DEFAULT 0,
            sos_call_link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE INDEX IF NOT EXISTS idx_omni_msg_acc ON omnichannel_messages(account_id);
        CREATE INDEX IF NOT EXISTS idx_omni_msg_instance ON omnichannel_messages(instance_name);

        CREATE TABLE IF NOT EXISTS patient_reactivation_schedules (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            patient_name TEXT NOT NULL,
            patient_phone TEXT NOT NULL,
            surgeon_name TEXT NOT NULL,
            procedure_name TEXT NOT NULL,
            surgery_date TEXT NOT NULL,
            milestone_days INTEGER NOT NULL,
            scheduled_dispatch_date TEXT NOT NULL,
            calcom_booking_link TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PENDING',
            message_dispatched_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_reactiv_acc ON patient_reactivation_schedules(account_id);
        CREATE INDEX IF NOT EXISTS idx_reactiv_dispatch ON patient_reactivation_schedules(scheduled_dispatch_date, status);
        CREATE INDEX IF NOT EXISTS idx_reactiv_phone ON patient_reactivation_schedules(patient_phone);

        CREATE TABLE IF NOT EXISTS calcom_bookings (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            calcom_booking_uid TEXT NOT NULL UNIQUE,
            schedule_id TEXT,
            patient_name TEXT NOT NULL,
            patient_email TEXT,
            patient_phone TEXT,
            host_name TEXT,
            host_email TEXT,
            event_type_title TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            meeting_url TEXT,
            is_online INTEGER NOT NULL DEFAULT 0,
            deal_id TEXT,
            task_id TEXT,
            status TEXT NOT NULL DEFAULT 'CONFIRMED',
            raw_payload TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
            FOREIGN KEY (schedule_id) REFERENCES patient_reactivation_schedules(id) ON DELETE SET NULL,
            FOREIGN KEY (deal_id) REFERENCES deals(id) ON DELETE SET NULL,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_calcom_acc ON calcom_bookings(account_id);
        CREATE INDEX IF NOT EXISTS idx_calcom_uid ON calcom_bookings(calcom_booking_uid);

        CREATE TABLE IF NOT EXISTS fefo_flash_deals (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            hub_id TEXT NOT NULL,
            hub_name TEXT NOT NULL,
            inventory_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            batch_number TEXT NOT NULL,
            original_quantity INTEGER NOT NULL,
            available_quantity INTEGER NOT NULL,
            original_unit_price REAL NOT NULL,
            discount_percentage REAL NOT NULL DEFAULT 35.0,
            flash_unit_price REAL NOT NULL,
            sterilization_expiry_date TEXT NOT NULL,
            months_to_expire REAL NOT NULL,
            target_surgeons_count INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'ACTIVE',
            checkout_one_click_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
            FOREIGN KEY (hub_id) REFERENCES dentgo_hubs(id) ON DELETE CASCADE,
            FOREIGN KEY (inventory_id) REFERENCES dentgo_hub_inventory(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_fefo_deals_acc ON fefo_flash_deals(account_id);
        CREATE INDEX IF NOT EXISTS idx_fefo_deals_status ON fefo_flash_deals(status);
        CREATE INDEX IF NOT EXISTS idx_fefo_deals_hub ON fefo_flash_deals(hub_id);

        CREATE TABLE IF NOT EXISTS fefo_flash_deal_reservations (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            deal_id TEXT NOT NULL,
            contact_id INTEGER,
            surgeon_name TEXT NOT NULL,
            surgeon_cro_uf TEXT NOT NULL,
            quantity_reserved INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'RESERVED',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
            FOREIGN KEY (deal_id) REFERENCES fefo_flash_deals(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_fefo_res_deal ON fefo_flash_deal_reservations(deal_id);
        CREATE INDEX IF NOT EXISTS idx_fefo_res_acc ON fefo_flash_deal_reservations(account_id);

        CREATE TABLE IF NOT EXISTS erp_fiscal_invoices (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            erp_type TEXT NOT NULL DEFAULT 'totvs_protheus',
            flow_type TEXT NOT NULL,
            reference_id TEXT NOT NULL,
            cfop TEXT NOT NULL,
            nfe_number TEXT NOT NULL,
            nfe_series TEXT NOT NULL DEFAULT '1',
            nfe_access_key TEXT NOT NULL UNIQUE,
            recipient_cnpj_cpf TEXT NOT NULL,
            recipient_name TEXT NOT NULL,
            total_invoice_value REAL NOT NULL DEFAULT 0.0,
            xml_r2_key TEXT NOT NULL,
            danfe_pdf_r2_key TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'AUTORIZADA',
            sefaz_protocol TEXT,
            windmill_job_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_erp_inv_acc ON erp_fiscal_invoices(account_id);
        CREATE INDEX IF NOT EXISTS idx_erp_inv_key ON erp_fiscal_invoices(nfe_access_key);
        CREATE INDEX IF NOT EXISTS idx_erp_inv_flow ON erp_fiscal_invoices(flow_type);

        CREATE TABLE IF NOT EXISTS imaging_studies (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            patient_name TEXT,
            patient_anonymized_id TEXT NOT NULL,
            deal_id TEXT,
            ticket_id TEXT,
            study_type TEXT NOT NULL DEFAULT 'DICOM_CBCT',
            orthanc_study_id TEXT,
            r2_storage_key TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_size_bytes INTEGER NOT NULL DEFAULT 0,
            slice_count INTEGER NOT NULL DEFAULT 1,
            jaw_type TEXT NOT NULL DEFAULT 'AMBAS',
            bone_density_estimate TEXT NOT NULL DEFAULT 'D2_NORMAL',
            implant_site TEXT,
            is_anonymized INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_img_studies_acc ON imaging_studies(account_id);
        CREATE INDEX IF NOT EXISTS idx_img_studies_deal ON imaging_studies(deal_id);
        CREATE INDEX IF NOT EXISTS idx_img_studies_ticket ON imaging_studies(ticket_id);
        CREATE INDEX IF NOT EXISTS idx_img_studies_orthanc ON imaging_studies(orthanc_study_id);

        CREATE TABLE IF NOT EXISTS webhook_subscriptions (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            name TEXT NOT NULL,
            target_url TEXT NOT NULL,
            subscribed_events_json TEXT NOT NULL DEFAULT '["*"]',
            signing_secret TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            consecutive_failures INTEGER NOT NULL DEFAULT 0,
            circuit_breaker_tripped INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_wh_sub_acc ON webhook_subscriptions(account_id);
        CREATE INDEX IF NOT EXISTS idx_wh_sub_active ON webhook_subscriptions(is_active);

        CREATE TABLE IF NOT EXISTS webhook_delivery_logs (
            id TEXT PRIMARY KEY,
            subscription_id TEXT NOT NULL,
            account_id TEXT NOT NULL,
            event_name TEXT NOT NULL,
            target_url TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            signature_header TEXT NOT NULL,
            status_code INTEGER,
            response_body TEXT,
            latency_ms REAL NOT NULL DEFAULT 0.0,
            attempt INTEGER NOT NULL DEFAULT 1,
            success INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subscription_id) REFERENCES webhook_subscriptions(id) ON DELETE CASCADE,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_wh_log_sub ON webhook_delivery_logs(subscription_id);
        CREATE INDEX IF NOT EXISTS idx_wh_log_acc ON webhook_delivery_logs(account_id);
        CREATE INDEX IF NOT EXISTS idx_wh_log_evt ON webhook_delivery_logs(event_name);
        """)


        # Migração idempotente para colunas complementares em deals e contacts
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(deals)")
        existing_cols = {row["name"] for row in cur.fetchall()}
        for col_name, col_def in [
            ("expected_close_date", "TEXT DEFAULT NULL"),
            ("field_owner_id", "TEXT DEFAULT NULL"),
            ("inside_owner_id", "TEXT DEFAULT NULL"),
            ("split_commission_field_pct", "REAL DEFAULT 70.0"),
            ("split_commission_inside_pct", "REAL DEFAULT 30.0"),
            ("executive_summary", "TEXT DEFAULT NULL"),
            ("approval_status", "TEXT DEFAULT 'APPROVED'"),
        ]:
            if col_name not in existing_cols:
                cur.execute(f"ALTER TABLE deals ADD COLUMN {col_name} {col_def}")



        cur.execute("PRAGMA table_info(contacts)")
        contact_cols = {row["name"] for row in cur.fetchall()}
        for col_name, col_def in [
            ("owner_id", "TEXT DEFAULT NULL"),
            ("field_owner_id", "TEXT DEFAULT NULL"),
            ("inside_owner_id", "TEXT DEFAULT NULL"),
            ("team_id", "TEXT DEFAULT NULL"),
            ("business_unit_id", "TEXT DEFAULT NULL"),
            ("cro", "TEXT DEFAULT NULL"),
            ("cro_uf", "TEXT DEFAULT NULL"),
            ("cro_verified", "INTEGER DEFAULT 0"),
            ("uf", "TEXT DEFAULT NULL"),
            ("specialty", "TEXT DEFAULT NULL"),
            ("clinic_name", "TEXT DEFAULT NULL"),
            ("monthly_implant_volume", "INTEGER DEFAULT 0"),
            ("reorder_cycle_days", "INTEGER DEFAULT 20"),
            ("last_order_date", "TEXT DEFAULT NULL")
        ]:
            if col_name not in contact_cols:
                cur.execute(f"ALTER TABLE contacts ADD COLUMN {col_name} {col_def}")

        cur.execute("PRAGMA table_info(dentgo_orders)")
        order_cols = {row["name"] for row in cur.fetchall()}
        for col_name, col_def in [
            ("courier_id", "TEXT DEFAULT NULL"),
            ("seal_code", "TEXT DEFAULT NULL"),
            ("delivery_pin", "TEXT DEFAULT NULL"),
            ("proof_of_delivery_r2_key", "TEXT DEFAULT NULL"),
            ("recipient_signature_name", "TEXT DEFAULT NULL"),
            ("delivered_at", "TIMESTAMP DEFAULT NULL")
        ]:
            if col_name not in order_cols:
                cur.execute(f"ALTER TABLE dentgo_orders ADD COLUMN {col_name} {col_def}")

        cur.execute("CREATE INDEX IF NOT EXISTS idx_dentgo_orders_courier ON dentgo_orders(courier_id);")

        cur.execute("PRAGMA table_info(tickets)")
        ticket_cols = {row["name"] for row in cur.fetchall()}
        for col_name, col_def in [
            ("livekit_room_url", "TEXT DEFAULT NULL"),
            ("customer_phone", "TEXT DEFAULT NULL"),
            ("cro_uf", "TEXT DEFAULT NULL"),
            ("dentgo_order_id", "TEXT DEFAULT NULL"),
            ("clinical_notes", "TEXT DEFAULT NULL"),
        ]:
            if col_name not in ticket_cols:
                cur.execute(f"ALTER TABLE tickets ADD COLUMN {col_name} {col_def}")




        # Seed determinístico inicial se conta padrão não existir
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM accounts WHERE id = '0f14ffff'")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO accounts (id, name, plan) VALUES ('0f14ffff', 'Sales Rocket', 'Enterprise Scale')")
            cur.execute(
                "INSERT INTO users (id, account_id, name, email, role) VALUES "
                "('2b08046d-d5e2-4d83-8fd3-b76e184748d7', '0f14ffff', 'Thiago Hortolan', 'thiago@salesrocketbrasil.com.br', 'Super Admin')"
            )
            cur.execute("INSERT INTO pipelines (id, account_id, name) VALUES (1, '0f14ffff', 'Funil Enterprise B2B 2026')")
            stages_data = [
                (101, 1, "Qualificação & SDR", "#38bdf8", 1, 20),
                (102, 1, "Demonstração & Diagnóstico", "#facc15", 2, 40),
                (103, 1, "Proposta Comercial", "#ff7300", 3, 60),
                (104, 1, "Negociação & Jurídico", "#c084fc", 4, 80),
                (105, 1, "Fechado & Ganho", "#34d399", 5, 100)
            ]
            cur.executemany("INSERT INTO stages (id, pipeline_id, name, color, step_order, probability) VALUES (?, ?, ?, ?, ?, ?)", stages_data)

            deals_data = [
                ("d-1", "0f14ffff", 1, 101, "Contrato Anual - AgroTech Global", 36000.0, "AgroTech Brasil", "Carlos Mendonça", "alta"),
                ("d-2", "0f14ffff", 1, 101, "Expansão CRM - Logística Express", 18500.0, "LogExpress S/A", "Mariana Alencar", "media"),
                ("d-3", "0f14ffff", 1, 102, "Implementação RevOps - Fintech Stark", 74000.0, "Stark Payments", "Rafael Bittencourt", "alta"),
                ("d-4", "0f14ffff", 1, 102, "Migração Hubspot - Rede Varejo Mais", 42000.0, "Varejo Mais", "Juliana Frota", "baixa"),
                ("d-5", "0f14ffff", 1, 103, "Plataforma Omnichannel - Grupo Alfa", 120000.0, "Grupo Alfa Hospitalar", "Dr. Roberto Silveira", "alta"),
                ("d-6", "0f14ffff", 1, 103, "Licenciamento 50 Seats - EducarTech", 39000.0, "EducarTech Online", "Patrícia Diniz", "media"),
                ("d-7", "0f14ffff", 1, 104, "Rollout Nacional - Banco Nexus", 165000.0, "Nexus Soluções Financeiras", "Fernando Campos", "alta"),
                ("d-8", "0f14ffff", 1, 105, "Onboarding Enterprise - Logística Total", 85000.0, "Logística Total", "Carla Pires", "alta")
            ]
            cur.executemany("INSERT INTO deals (id, account_id, pipeline_id, stage_id, title, value, company, contact_name, priority) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", deals_data)

            contacts_data = [
                ("0f14ffff", "Carlos Mendonça", "carlos@agrotech.com.br", "+55 11 98455-1200", "AgroTech Brasil", '["Decisor", "Enterprise", "Inbound"]', 92),
                ("0f14ffff", "Mariana Alencar", "mariana.alencar@logexpress.com.br", "+55 19 99123-4567", "LogExpress S/A", '["Diretoria", "Follow-up"]', 78),
                ("0f14ffff", "Rafael Bittencourt", "rafael@starkpay.io", "+55 11 97788-9900", "Stark Payments", '["CTO", "Fintech", "Demo"]', 96),
                ("0f14ffff", "Juliana Frota", "jfrota@varejomais.com.br", "+55 21 98877-3322", "Varejo Mais", '["Varejo", "Migração"]', 64),
                ("0f14ffff", "Dr. Roberto Silveira", "roberto@grupoalfa.med.br", "+55 31 99654-7890", "Grupo Alfa Hospitalar", '["VIP", "Proposta"]', 98),
                ("0f14ffff", "Patrícia Diniz", "patricia@educartech.com", "+55 41 99234-5678", "EducarTech Online", '["EdTech", "Trial Ativo"]', 70),
                ("0f14ffff", "Fernando Campos", "fernando.campos@nexusbank.com", "+55 11 98111-2233", "Nexus Soluções Financeiras", '["Enterprise", "Jurídico"]', 95)
            ]
            cur.executemany("INSERT INTO contacts (account_id, name, email, phone, company, tags, score) VALUES (?, ?, ?, ?, ?, ?, ?)", contacts_data)

            cur.execute("INSERT INTO conversations (id, account_id, contact_name, company, channel, unread) VALUES ('chat-1', '0f14ffff', 'Rafael Bittencourt', 'Stark Payments', 'whatsapp', 1)")
            cur.execute("INSERT INTO messages (conversation_id, sender, text) VALUES ('chat-1', 'contact', 'Olá Thiago, recebemos a apresentação técnica. Muito sólida!')")
            cur.execute("INSERT INTO messages (conversation_id, sender, text) VALUES ('chat-1', 'user', 'Excelente Rafael! Podemos alinhar a homologação dos webhooks na sexta-feira?')")
            cur.execute("INSERT INTO messages (conversation_id, sender, text) VALUES ('chat-1', 'contact', 'Combinado, vou convidar nossa equipe de engenharia para o call.')")

            cur.execute("INSERT INTO webhooks (account_id, name, url, event_type, secret) VALUES ('0f14ffff', 'Webhook ERP SAP', 'https://api.empresa.com.br/hooks/rvops', 'deal.stage_changed', 'whsec_rvops_2026_x89a')")

        # Seed de Tickets se vazia
        cur.execute("SELECT COUNT(*) FROM tickets")
        if cur.fetchone()[0] == 0:
            tickets_data = [
                ("t-1", "0f14ffff", "Integração Webhook Falhando no ERP SAP", "Rafael Bittencourt (Stark Payments)", "alta", "em_andamento", "Engenharia"),
                ("t-2", "0f14ffff", "Dúvida no Cálculo de MRR Ponderado", "Mariana Alencar (LogExpress)", "media", "aberto", "Atendimento"),
                ("t-3", "0f14ffff", "Solicitação de Aumento de Seats Enterprise", "Dr. Roberto Silveira (Grupo Alfa)", "alta", "resolvido", "Comercial"),
                ("t-4", "0f14ffff", "Renovação e SSL Domínio Customizado", "Carlos Mendonça (AgroTech)", "media", "aberto", "DevOps")
            ]
            cur.executemany("INSERT INTO tickets (id, account_id, title, customer_name, priority, status, category) VALUES (?, ?, ?, ?, ?, ?, ?)", tickets_data)

        # Seed de Tarefas se vazia
        cur.execute("SELECT COUNT(*) FROM tasks")
        if cur.fetchone()[0] == 0:
            tasks_data = [
                ("task-1", "0f14ffff", "Enviar minuta contratual revisada pelo jurídico", "Hoje, 17:00", "Thiago Hortolan", "alta", 0),
                ("task-2", "0f14ffff", "Apresentar demonstração técnica de Webhooks e MCP", "Amanhã, 10:30", "Thiago Hortolan", "alta", 0),
                ("task-3", "0f14ffff", "Configurar automação de lead scoring no Mautic", "18/Out, 15:00", "Carlos Mendonça", "media", 1),
                ("task-4", "0f14ffff", "Reunião de alinhamento trimestral com equipe de CS", "19/Out, 09:00", "Mariana Alencar", "baixa", 0)
            ]
            cur.executemany("INSERT INTO tasks (id, account_id, title, due_date, assignee, priority, completed) VALUES (?, ?, ?, ?, ?, ?, ?)", tasks_data)

        # Seed idempotente de múltiplos pipelines enterprise (Pipelines 2, 3 e 4)
        extra_pipelines = [
            (2, "0f14ffff", "Prospecção & SDR Outbound (Instituições & Clínicas)"),
            (3, "0f14ffff", "Distribuidores & Contratos de Atacado"),
            (4, "0f14ffff", "CS, Expansão & KOLs (Pós-Venda Cirúrgica)")
        ]
        cur.executemany("INSERT OR IGNORE INTO pipelines (id, account_id, name) VALUES (?, ?, ?)", extra_pipelines)

        extra_stages = [
            (201, 2, "Prospecção Ativa", "#94a3b8", 1, 10),
            (202, 2, "Primeiro Contato Feito", "#38bdf8", 2, 25),
            (203, 2, "Diagnóstico Agendado", "#facc15", 3, 50),
            (204, 2, "Qualificado (MQL -> SQL)", "#34d399", 4, 100),
            (301, 3, "Mapeamento de Parcerias", "#c084fc", 1, 20),
            (302, 3, "Acordo de Co-Selling", "#38bdf8", 2, 50),
            (303, 3, "Contrato de Canal Fechado", "#34d399", 3, 100),
            (401, 4, "Onboarding Inicial (30d)", "#38bdf8", 1, 25),
            (402, 4, "Adoção Plena & Saúde Verde", "#34d399", 2, 75),
            (403, 4, "Upsell / Expansão Contratada", "#ff7300", 3, 100)
        ]
        cur.executemany("INSERT OR IGNORE INTO stages (id, pipeline_id, name, color, step_order, probability) VALUES (?, ?, ?, ?, ?, ?)", extra_stages)

        extra_deals = [
            ("d-ob-1", "0f14ffff", 2, 201, "Outbound - TechCorp Indústria", 24000.0, "TechCorp", "Marcos Viana", "alta"),
            ("d-ob-2", "0f14ffff", 2, 202, "Prospecção - BioFarma Sul", 32000.0, "BioFarma", "Luciana Prado", "media"),
            ("d-ob-3", "0f14ffff", 2, 203, "Call Marcada - Supermercados Real", 55000.0, "Rede Real", "Renato Souza", "alta"),
            ("d-ob-4", "0f14ffff", 2, 204, "MQL Validado - Construtora Moura", 48000.0, "Moura Engenharia", "Claudio Moura", "alta"),
            ("d-ch-1", "0f14ffff", 3, 301, "Canal Integradores TI", 80000.0, "Soluções Cloud", "Bruno Esteves", "alta"),
            ("d-ch-2", "0f14ffff", 3, 302, "Aliança Estratégica ERP", 150000.0, "TotalERP", "Sandra Gomes", "alta"),
            ("d-cs-1", "0f14ffff", 4, 401, "Onboarding - StartSeguros", 28000.0, "StartSeguros", "Vinicius Lima", "media"),
            ("d-cs-2", "0f14ffff", 4, 402, "Expansão de 20 licenças - Stark Payments", 35000.0, "Stark Payments", "Rafael Bittencourt", "alta")
        ]
        cur.executemany("INSERT OR IGNORE INTO deals (id, account_id, pipeline_id, stage_id, title, value, company, contact_name, priority) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", extra_deals)

        # Seed idempotente de Campanhas de Marketing & Atribuição de Mídia
        cur.execute("SELECT COUNT(*) FROM campaigns")
        if cur.fetchone()[0] == 0:
            campaigns_data = [
                ("camp-1", "0f14ffff", "RevOps Scaling Q4", "Google Ads Search (GCLID)", "google", "cpc", "revops-q4", 15000.0, 12400.0, 86000.0, 428, 34, "ativa"),
                ("camp-2", "0f14ffff", "Outbound Enterprise Tech", "LinkedIn InMail & Cold Mail", "linkedin", "inmail", "outbound-enterprise", 8000.0, 7500.0, 54000.0, 182, 21, "ativa"),
                ("camp-3", "0f14ffff", "Webinar Omnichannel 2026", "Meta CAPI / Instagram", "meta", "cpc", "webinar-omnichannel", 6000.0, 6000.0, 22000.0, 614, 18, "concluida")
            ]
            cur.executemany(
                "INSERT INTO campaigns (id, account_id, name, channel, utm_source, utm_medium, utm_campaign, budget, spend, revenue, leads_count, deals_count, status) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                campaigns_data
            )

        # Seed idempotente de Regras de Lead Scoring ICP
        cur.execute("SELECT COUNT(*) FROM scoring_rules")
        if cur.fetchone()[0] == 0:
            scoring_rules_data = [
                ("sr-1", "0f14ffff", "Porte da Organização (Enterprise)", "Firmográfico", "tag", "Enterprise", 30, "Avanço imediato para SDR", 1),
                ("sr-2", "0f14ffff", "Nível Hierárquico / Decisor C-Level", "Demográfico", "tag", "Decisor,CTO,VIP,Diretoria", 25, "Atribuição a Closer Senior", 1),
                ("sr-3", "0f14ffff", "Segmento Prioritário (Agro, Logística, Fintech)", "Firmográfico", "company", "AgroTech,LogExpress,Stark,Nexus,Varejo", 20, "Material de apresentação setorial", 1),
                ("sr-4", "0f14ffff", "Interação Omnichannel Ativa", "Comportamental", "interaction", "has_conversation", 15, "Alerta push no painel", 1),
                ("sr-5", "0f14ffff", "Canal de Entrada de Alta Intenção", "Comportamental", "tag", "Inbound,GCLID,InMail,Trial", 10, "Gatilho de contato prioritário", 1)
            ]
            cur.executemany(
                "INSERT INTO scoring_rules (id, account_id, name, category, condition_key, condition_val, points, impact_description, is_active) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                scoring_rules_data
            )

        # Migração idempotente de atributos da Indústria Odontológica em contacts
        cur.execute("PRAGMA table_info(contacts);")
        existing_cols = {row[1] for row in cur.fetchall()}
        dental_cols = [
            ("cro", "TEXT"),
            ("cro_uf", "TEXT"),
            ("specialty", "TEXT DEFAULT 'Implantodontia'"),
            ("work_model", "TEXT DEFAULT 'Clínica Própria'"),
            ("monthly_implants_volume", "TEXT DEFAULT '20-50/mês'"),
            ("customer_type", "TEXT DEFAULT 'Cirurgião'"),
            ("city", "TEXT"),
            ("state", "TEXT")
        ]
        for col_name, col_type in dental_cols:
            if col_name not in existing_cols:
                cur.execute(f"ALTER TABLE contacts ADD COLUMN {col_name} {col_type};")

        # Atualização determinística de campos odontológicos nos contatos iniciais
        cur.execute("UPDATE contacts SET cro='SP-89450', cro_uf='SP', specialty='Implantodontia', work_model='Clínica Própria', monthly_implants_volume='> 50/mês', customer_type='Cirurgião' WHERE id=1 AND (cro IS NULL OR cro = '')")
        cur.execute("UPDATE contacts SET cro='PR-67210', cro_uf='PR', specialty='Cirurgia Bucomaxilofacial', work_model='Hospital Dia', monthly_implants_volume='> 50/mês', customer_type='Cirurgião' WHERE id=2 AND (cro IS NULL OR cro = '')")
        cur.execute("UPDATE contacts SET cro='SP-45120', cro_uf='SP', specialty='Implantodontia', work_model='Docente Universitário', monthly_implants_volume='20-50/mês', customer_type='Professor/KOL' WHERE id=3 AND (cro IS NULL OR cro = '')")
        cur.execute("UPDATE contacts SET cro='RJ-78900', cro_uf='RJ', specialty='Periodontia & Implante', work_model='Clínica Multidisciplinar', monthly_implants_volume='20-50/mês', customer_type='Cirurgião' WHERE id=4 AND (cro IS NULL OR cro = '')")
        cur.execute("UPDATE contacts SET cro='MG-54200', cro_uf='MG', specialty='Prótese & Reabilitação', work_model='Instituto Odontológico', monthly_implants_volume='5-20/mês', customer_type='Aluno Especialização' WHERE id=5 AND (cro IS NULL OR cro = '')")

        # Seed idempotente de Instituições de Ensino Odontológico (Mandic, ABO, APCD)
        cur.execute("SELECT COUNT(*) FROM institutions")
        if cur.fetchone()[0] == 0:
            insts_data = [
                ("inst-1", "0f14ffff", "Faculdade São Leopoldo Mandic (Campinas)", "Faculdade / Pós-Graduação", "Campinas", "SP", "Prof. Dr. Marcelo Lucchesi", 48, "credenciada"),
                ("inst-2", "0f14ffff", "Faculdade São Leopoldo Mandic (Araras)", "Faculdade / Pós-Graduação", "Araras", "SP", "Prof. Dr. Fernando Cordeiro", 24, "credenciada"),
                ("inst-3", "0f14ffff", "ABO - Associação Brasileira de Odontologia (SP)", "Entidade de Classe / Especialização", "São Paulo", "SP", "Dra. Renata Vasconcelos", 36, "credenciada"),
                ("inst-4", "0f14ffff", "APCD Central - Cirurgiões-Dentistas", "Associação / Cursos de Imersão", "São Paulo", "SP", "Dr. Guilherme Fontes", 30, "em_negociacao")
            ]
            cur.executemany(
                "INSERT INTO institutions (id, account_id, name, institution_type, city, state, coordinator_name, active_students_count, accreditation_status) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                insts_data
            )

        # Seed idempotente de Fluxos de Automação Cirúrgica
        cur.execute("SELECT COUNT(*) FROM automation_flows")
        if cur.fetchone()[0] == 0:
            flows_data = [
                (
                    "flow-brocas", "0f14ffff",
                    "Alerta de Reposição de Brocas Cirúrgicas",
                    "Consignação",
                    "Caixa consignada > 15 dias sem consumo",
                    "Notificação WhatsApp via Evolution API para reposição de kit cirúrgico",
                    1, 14, "2026-10-15 14:30:00"
                ),
                (
                    "flow-transbordo-tier-a", "0f14ffff",
                    "Transbordo Automático de Leads Hot (Tier A)",
                    "Receita",
                    "Cirurgião atinge pontuação Tier A (>= 75 pts + CRO ativo)",
                    "Alocação do Closer regional pelo território/UF e geração de Task com SLA de 15 min",
                    1, 28, "2026-10-16 09:15:00"
                ),
                (
                    "flow-totvs-sc5", "0f14ffff",
                    "Faturamento Automático no TOTVS Protheus",
                    "ERP",
                    "Negócio movido para o estágio Fechado & Ganho",
                    "Emissão de pedido de venda SC5 com itens SC6 na fila de saída idempotente",
                    1, 9, "2026-10-16 17:45:00"
                ),
                (
                    "flow-anti-churn", "0f14ffff",
                    "Radar Anti-Churn & Recompra de Implantes",
                    "Retenção",
                    "Dias sem compras > 1.5x ciclo médio de consumo da clínica",
                    "Alerta visual no Kanban e agendamento automático de visita técnica preventiva",
                    1, 6, "2026-10-17 08:00:00"
                )
            ]
            cur.executemany(
                "INSERT INTO automation_flows (id, account_id, name, category, trigger_event, action_description, is_active, execution_count, last_run_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                flows_data
            )

        # Seed idempotente de Tabelas de Preço Odontológicas
        cur.execute("SELECT COUNT(*) FROM price_tables")
        if cur.fetchone()[0] == 0:
            price_tables_data = [
                ("pt-1", "0f14ffff", "BALCAO", "Tabela Balcão Padrão", 1.0, 1),
                ("pt-2", "0f14ffff", "FRANQUIA", "Tabela Franquias Odontológicas", 0.85, 1),
                ("pt-3", "0f14ffff", "DISTRIBUIDOR", "Tabela Distribuidores e Atacado", 0.70, 1),
                ("pt-4", "0f14ffff", "UNIVERSIDADE_ENSINO", "Tabela Universidades & Pós-Graduação", 0.60, 1),
                ("pt-5", "0f14ffff", "KOL_PARCEIRO", "Tabela Parceiros KOL & Speakers", 0.50, 1),
            ]
            cur.executemany(
                "INSERT INTO price_tables (id, account_id, table_key, name, discount_factor, is_active) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                price_tables_data
            )

        # Seed idempotente do Catálogo de Produtos Odontológicos
        cur.execute("SELECT COUNT(*) FROM products_catalog")
        if cur.fetchone()[0] == 0:
            catalog_products_data = [
                ("prod-1", "0f14ffff", "IMP-CM-37511", "Implante Cone Morse 3.75x11mm", "Implantes", "ANVISA-80123456789", "Cone Morse", 3.75, 11.0, 45, 450.0, 1),
                ("prod-2", "0f14ffff", "IMP-CM-4313", "Implante Cone Morse 4.3x13mm", "Implantes", "ANVISA-80123456789", "Cone Morse", 4.30, 13.0, 45, 480.0, 1),
                ("prod-3", "0f14ffff", "KIT-CIR-PRO", "Kit Cirúrgico Guiado Titanium Pro", "Kits Cirúrgicos", "ANVISA-80987654321", "Universal", None, None, None, 6500.0, 1),
                ("prod-4", "0f14ffff", "BIO-OS-05G", "Biomaterial Ósseo Particulado 0.5g", "Biomateriais", "ANVISA-80112233445", "Universal", None, None, None, 320.0, 1),
            ]
            cur.executemany(
                "INSERT INTO products_catalog (id, account_id, sku, name, category, anvisa_reg, prosthetic_platform, diameter, length, recommended_torque, base_price, is_active) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                catalog_products_data
            )


        # Atualização canônica dos nomes dos pipelines para a Indústria Dental (RevOps Puro)
        cur.execute("UPDATE pipelines SET name = 'Cirurgiões & Venda Direta / Consignação de Caixas' WHERE id = 1")
        cur.execute("UPDATE pipelines SET name = 'Prospecção & SDR Outbound (Instituições & Clínicas)' WHERE id = 2")
        cur.execute("UPDATE pipelines SET name = 'Distribuidores & Contratos de Atacado' WHERE id = 3")
        cur.execute("UPDATE pipelines SET name = 'CS, Expansão & KOLs (Pós-Venda Cirúrgica)' WHERE id = 4")

        # Migração de colunas de hierarquia e escopo em users
        cur.execute("PRAGMA table_info(users);")
        user_cols = {row[1] for row in cur.fetchall()}
        for col, col_t in [
            ("team_id", "TEXT"),
            ("role_id", "TEXT"),
            ("phone", "TEXT"),
            ("custom_data_scope", "TEXT"),
            ("password_hash", "TEXT"),
            ("is_active", "INTEGER DEFAULT 1"),
            ("is_superadmin", "INTEGER DEFAULT 0")
        ]:
            if col not in user_cols:
                cur.execute(f"ALTER TABLE users ADD COLUMN {col} {col_t};")

        # Migração de owner_id, field_owner_id, inside_owner_id, team_id e business_unit_id em entidades de dados
        for table in ["deals", "contacts", "conversations", "institutions", "kp_partner_agreements"]:
            cur.execute(f"PRAGMA table_info({table});")
            tbl_cols = {row[1] for row in cur.fetchall()}
            if "owner_id" not in tbl_cols:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN owner_id TEXT;")
            if "field_owner_id" not in tbl_cols:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN field_owner_id TEXT;")
            if "inside_owner_id" not in tbl_cols:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN inside_owner_id TEXT;")
            if "team_id" not in tbl_cols:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN team_id TEXT;")
            if "business_unit_id" not in tbl_cols:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN business_unit_id TEXT;")

        cur.execute("PRAGMA table_info(webhook_subscriptions);")
        wh_cols = {row[1] for row in cur.fetchall()}
        if "signing_secret_encrypted" not in wh_cols:
            cur.execute("ALTER TABLE webhook_subscriptions ADD COLUMN signing_secret_encrypted TEXT;")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS scoring_history (
                id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                contact_id INTEGER NOT NULL,
                previous_score INTEGER NOT NULL DEFAULT 0,
                new_score INTEGER NOT NULL DEFAULT 0,
                icp_fit_score INTEGER NOT NULL DEFAULT 0,
                engagement_score INTEGER NOT NULL DEFAULT 0,
                tier TEXT NOT NULL DEFAULT 'C',
                trigger_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
            );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_scoring_hist_contact ON scoring_history(account_id, contact_id);")

        # Migração de status em dentgo_hub_inventory
        cur.execute("PRAGMA table_info(dentgo_hub_inventory);")
        dhi_cols = {row[1] for row in cur.fetchall()}
        if "status" not in dhi_cols:
            cur.execute("ALTER TABLE dentgo_hub_inventory ADD COLUMN status TEXT NOT NULL DEFAULT 'AVAILABLE';")

        # Índices compostos obrigatórios de alta performance (SPEC_RBAC_DATA_SCOPING_HIERARQUICO)

        cur.execute("CREATE INDEX IF NOT EXISTS idx_teams_hierarchy ON teams(account_id, parent_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_deals_scope ON deals(account_id, team_id, owner_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_contacts_scope ON contacts(account_id, team_id, owner_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_conversations_scope ON conversations(account_id, team_id, owner_id);")

        # Garantia determinística do Super Admin (User God único - Heverton Eduardo Peres)
        # Regra Inegociável: Nenhum outro usuário no sistema pode possuir is_superadmin = 1
        superadmin_email = "hevertoneduardoperes@gmail.com"
        superadmin_id = "usr-superadmin-god"
        superadmin_name = "Heverton Eduardo Peres (Super Admin)"
        superadmin_pwd_hash = "579ac58e034634060983ac3b0100617b0e10fa05438675d44bb19b1533cdb0a6"

        cur.execute("UPDATE users SET is_superadmin = 0 WHERE email != ? AND id != ?", (superadmin_email, superadmin_id))
        cur.execute("SELECT id FROM users WHERE email = ? OR id = ?", (superadmin_email, superadmin_id))
        existing_god = cur.fetchone()
        if existing_god:
            cur.execute(
                "UPDATE users SET name = ?, email = ?, role = 'Super Admin', is_superadmin = 1, password_hash = ? WHERE id = ?",
                (superadmin_name, superadmin_email, superadmin_pwd_hash, existing_god[0])
            )
        else:
            cur.execute(
                "INSERT INTO users (id, account_id, name, email, role, is_superadmin, password_hash) VALUES "
                "(?, '0f14ffff', ?, ?, 'Super Admin', 1, ?)",
                (superadmin_id, superadmin_name, superadmin_email, superadmin_pwd_hash)
            )
        cur.execute("UPDATE users SET is_superadmin = 0 WHERE email != ?", (superadmin_email,))
        cur.execute("UPDATE users SET role = 'Consultor Comercial' WHERE email != ? AND role = 'Super Admin'", (superadmin_email,))

    conn.close()



if __name__ == "__main__":
    init_db()
    print("Database SQLite WAL inicializado com sucesso em:", DB_PATH)
