# -*- coding: utf-8 -*-
"""
Database Module — SQLite WAL Engine (Lei #3 e Lei #11)
Garante persistência atômica, segura para concorrência e auditável.
"""

from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "rvops.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
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
            role TEXT NOT NULL DEFAULT 'Super Admin',
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
            event_type TEXT NOT NULL, -- 'deal.created', 'deal.stage_changed', 'contact.created'
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
        """)

        # Seed inicial determinístico se vazio
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM accounts WHERE id = '0f14ffff'")
        if cur.fetchone()[0] == 0:
            cur.execute(
                "INSERT INTO accounts (id, name, plan) VALUES ('0f14ffff', 'Sales Rocket', 'Enterprise Scale')"
            )
            cur.execute(
                "INSERT INTO users (id, account_id, name, email, role) VALUES "
                "('2b08046d-d5e2-4d83-8fd3-b76e184748d7', '0f14ffff', 'Thiago Hortolan', 'thiago@salesrocketbrasil.com.br', 'Super Admin')"
            )

            # Pipeline
            cur.execute("INSERT INTO pipelines (id, account_id, name) VALUES (1, '0f14ffff', 'Funil Enterprise B2B 2026')")
            stages_data = [
                (101, 1, "Qualificação & SDR", "hsl(208, 67%, 45%)", 1, 20),
                (102, 1, "Demonstração & Diagnóstico", "hsl(43, 95%, 45%)", 2, 40),
                (103, 1, "Proposta Comercial", "hsl(27, 100%, 50%)", 3, 60),
                (104, 1, "Negociação & Jurídico", "hsl(280, 60%, 50%)", 4, 80),
                (105, 1, "Fechado & Ganho", "hsl(148, 50%, 45%)", 5, 100)
            ]
            cur.executemany("INSERT INTO stages (id, pipeline_id, name, color, step_order, probability) VALUES (?, ?, ?, ?, ?, ?)", stages_data)

            # Deals
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

            # Contatos
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

            # Conversas & Mensagens
            cur.execute("INSERT INTO conversations (id, account_id, contact_name, company, channel, unread) VALUES ('chat-1', '0f14ffff', 'Rafael Bittencourt', 'Stark Payments', 'whatsapp', 1)")
            cur.execute("INSERT INTO messages (conversation_id, sender, text) VALUES ('chat-1', 'contact', 'Olá Thiago, recebemos a apresentação técnica. Muito sólida!')")
            cur.execute("INSERT INTO messages (conversation_id, sender, text) VALUES ('chat-1', 'user', 'Excelente Rafael! Podemos alinhar a homologação dos webhooks na sexta-feira?')")
            cur.execute("INSERT INTO messages (conversation_id, sender, text) VALUES ('chat-1', 'contact', 'Combinado, vou convidar nossa equipe de engenharia para o call.')")

            # Webhooks exemplo
            cur.execute("INSERT INTO webhooks (account_id, name, url, event_type, secret) VALUES ('0f14ffff', 'Webhook ERP SAP', 'https://api.empresa.com.br/hooks/rvops', 'deal.stage_changed', 'whsec_rvops_2026_x89a')")
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database SQLite WAL inicializado com sucesso em:", DB_PATH)
