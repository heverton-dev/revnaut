# -*- coding: utf-8 -*-
"""
Database Module — SQLite WAL Engine (Lei #3 e Lei #11)
Persistência transacional com concorrência segura e isolamento.
"""

from __future__ import annotations
import sqlite3
from typing import Any, Dict, List, Optional
from src.core.config import DB_PATH


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
        """)

        # Migração idempotente para colunas complementares em deals
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(deals)")
        existing_cols = {row["name"] for row in cur.fetchall()}
        if "expected_close_date" not in existing_cols:
            cur.execute("ALTER TABLE deals ADD COLUMN expected_close_date TEXT DEFAULT NULL")


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
            (2, "0f14ffff", "Outbound & Pré-Vendas SDR"),
            (3, "0f14ffff", "Parcerias & Canais Indiretos"),
            (4, "0f14ffff", "CS, Expansão & Renovações")
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

        # Atualização canônica dos nomes dos pipelines para a Indústria Dental
        cur.execute("UPDATE pipelines SET name = 'Cirurgiões & Venda Direta' WHERE id = 1")
        cur.execute("UPDATE pipelines SET name = 'Instituições de Ensino & Kits Acadêmicos (Mandic)' WHERE id = 2")
        cur.execute("UPDATE pipelines SET name = 'Distribuidores & Contratos Atacado (Sell-In / Sell-Out)' WHERE id = 3")
        cur.execute("UPDATE pipelines SET name = 'Key Opinion Leaders (KOLs), Speakers & CIOSP' WHERE id = 4")

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

        # Migração de owner_id e team_id em entidades de dados
        for table in ["deals", "contacts", "institutions"]:
            cur.execute(f"PRAGMA table_info({table});")
            tbl_cols = {row[1] for row in cur.fetchall()}
            if "owner_id" not in tbl_cols:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN owner_id TEXT;")
            if "team_id" not in tbl_cols:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN team_id TEXT;")

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
