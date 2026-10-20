# -*- coding: utf-8 -*-
"""
Revnault Global Dental Group — Multinational Enterprise Seed Script
Popula deterministicamente todas as 69 tabelas do schema SQLite WAL.
Aderente à Lei #1 (Determinismo), Lei #5 (Zero Stubs/Mocks) e Lei #14 (Zero Emojis).
"""

from __future__ import annotations
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.core.config import get_db_path
from src.core.vector_store import compute_semantic_embedding

ACCOUNT_ID = "0f14ffff"
ACCOUNT_NAME = "Revnault Global Dental Group"


def seed_multinational_enterprise(db_path: Path | str | None = None, clean_reset: bool = False) -> dict[str, int]:
    target_path = Path(db_path) if db_path else get_db_path()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    from src.core.database import init_db
    init_db()

    conn = sqlite3.connect(str(target_path), timeout=30.0, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = OFF;")
    cur = conn.cursor()

    if clean_reset:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        all_tables = [r[0] for r in cur.fetchall()]
        for tbl in all_tables:
            cur.execute(f"DELETE FROM {tbl};")
        conn.commit()

    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    pwd_hash = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9" # dev pass
    superadmin_pwd_hash = "579ac58e034634060983ac3b0100617b0e10fa05438675d44bb19b1533cdb0a6"

    # 1. ACCOUNTS (1)
    cur.execute("""
        INSERT OR REPLACE INTO accounts (id, name, plan, created_at)
        VALUES (?, ?, 'Enterprise Global Multinational', ?)
    """, (ACCOUNT_ID, ACCOUNT_NAME, now_iso))

    # 2. BUSINESS UNITS (4)
    business_units_data = [
        ("bu-latam-br", ACCOUNT_ID, "Divisão Brasil (Matriz São Paulo, Sul & Nordeste)", "BR-HQ", "Operação Matriz América Latina e Hub Central de Consignação e DENTGO Express", now_iso),
        ("bu-na-usa", ACCOUNT_ID, "Divisão América do Norte (Miami & Orlando DSO Hub)", "NA-DSO", "Operação focada em DSOs de grande escala e cirurgias guiadas no Sul da Flórida", now_iso),
        ("bu-eu-iberia", ACCOUNT_ID, "Divisão Europa (Lisboa & Madrid Digital Oral Hub)", "EU-IBERIA", "Centro de excelência em fluxo digital, implantes zigomáticos e parcerias universitárias", now_iso),
        ("bu-latam-hisp", ACCOUNT_ID, "Divisão América Latina (Buenos Aires, Santiago & Bogotá)", "LATAM-HISP", "Operação Cono Sur e Região Andina para clínicas de alta rotatividade e reabilitação oral", now_iso),
    ]
    cur.executemany("INSERT OR REPLACE INTO business_units (id, account_id, name, code, description, created_at) VALUES (?, ?, ?, ?, ?, ?)", business_units_data)

    # 3. TEAMS (12)
    teams_data = [
        ("team-campo-sp", ACCOUNT_ID, "bu-latam-br", None, "Equipe Campo São Paulo", "usr-field-ricardo", now_iso),
        ("team-campo-sul", ACCOUNT_ID, "bu-latam-br", None, "Equipe Campo Região Sul", "usr-field-sul", now_iso),
        ("team-inside-br", ACCOUNT_ID, "bu-latam-br", None, "Inside Sales Brasil", "usr-inside-camila", now_iso),
        ("team-log-sp", ACCOUNT_ID, "bu-latam-br", None, "Logística Express SP & DENTGO Hub", "usr-log-marcos", now_iso),
        ("team-field-fl", ACCOUNT_ID, "bu-na-usa", None, "Field Sales Florida DSO", "usr-field-fl", now_iso),
        ("team-inside-us", ACCOUNT_ID, "bu-na-usa", None, "Inside Sales North America", "usr-inside-us", now_iso),
        ("team-log-miami", ACCOUNT_ID, "bu-na-usa", None, "Logística Express Miami Brickell", "usr-log-miami", now_iso),
        ("team-field-iberia", ACCOUNT_ID, "bu-eu-iberia", None, "Field Sales Ibéria (Lisboa & Madrid)", "usr-field-iberia", now_iso),
        ("team-inside-eu", ACCOUNT_ID, "bu-eu-iberia", None, "Inside Sales Europa", "usr-inside-eu", now_iso),
        ("team-log-lisboa", ACCOUNT_ID, "bu-eu-iberia", None, "Logística Express Lisboa Hub", "usr-log-marcos", now_iso),
        ("team-field-conosur", ACCOUNT_ID, "bu-latam-hisp", None, "Equipe Cono Sur (Buenos Aires & Santiago)", "usr-field-bue", now_iso),
        ("team-inside-latam", ACCOUNT_ID, "bu-latam-hisp", None, "Inside Sales Região Andina", "usr-inside-camila", now_iso),
    ]
    cur.executemany("INSERT OR REPLACE INTO teams (id, account_id, business_unit_id, parent_id, name, leader_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", teams_data)

    # 4. ROLES (6) & ROLE_PERMISSIONS
    roles_data = [
        ("role-ceo", ACCOUNT_ID, "Diretoria / Administrador Geral", "Acesso irrestrito a todas as 17 áreas operacionais globais", "all", 1, now_iso),
        ("role-manager", ACCOUNT_ID, "Gerente Comercial", "Supervisão de metas, aprovação de alçadas e comissionamento", "team", 0, now_iso),
        ("role-field", ACCOUNT_ID, "Consultor Externo (Campo)", "Atendimento cirúrgico presencial, entrega de kits e fechamento de novos acordos", "individual", 0, now_iso),
        ("role-inside", ACCOUNT_ID, "Consultor Interno (Atendimento)", "SDR, qualificação de leads, negociação de propostas e atendimento omnichannel", "team", 0, now_iso),
        ("role-logistics", ACCOUNT_ID, "Logística e Estoque (Expedição)", "Gestão de hubs DENTGO, picking bipado, lacres térmicos e rastreio de maletas", "all", 0, now_iso),
        ("role-clinical", ACCOUNT_ID, "Suporte Clínico e Pós-Venda", "Acompanhamento cirúrgico SOS, laudos de tomografia 3D e tramitação de trocas ANVISA", "all", 0, now_iso),
    ]
    cur.executemany("INSERT OR REPLACE INTO roles (id, account_id, name, description, default_data_scope, is_admin, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", roles_data)

    perms_list = [
        "deals:read", "deals:write", "contacts:read", "contacts:write", "contracts:read", "contracts:write",
        "keypartners:read", "keypartners:write", "dentgo:read", "dentgo:write", "support:read", "support:write",
        "imaging:read", "imaging:write", "analytics:read", "rbac:read", "rbac:write", "settings:read", "settings:write"
    ]
    role_perms = []
    p_counter = 1
    for r in roles_data:
        r_id = r[0]
        for p in perms_list:
            role_perms.append((p_counter, ACCOUNT_ID, r_id, p))
            p_counter += 1
    cur.executemany("INSERT OR REPLACE INTO role_permissions (id, account_id, role_id, permission_code) VALUES (?, ?, ?, ?)", role_perms)

    # 5. USERS (18)
    users_data = [
        ("usr-director-br", ACCOUNT_ID, "Carlos Eduardo Silva", "carlos.silva@revnaultdental.com", "Diretoria / Administrador Geral", now_iso, "team-campo-sp", "role-ceo", "+55 11 98888-0001", "all", superadmin_pwd_hash, 1, 1),
        ("usr-superadmin-god", ACCOUNT_ID, "Heverton Eduardo Peres", "hevertoneduardoperes@gmail.com", "Super Admin", now_iso, "team-campo-sp", "role-ceo", "+55 11 99999-0001", "all", superadmin_pwd_hash, 1, 1),
        ("usr-dir-na", ACCOUNT_ID, "Michael Chang", "michael.chang@revnaultdental.com", "Diretor Regional América do Norte", now_iso, "team-field-fl", "role-ceo", "+1 305 555-0101", "all", pwd_hash, 1, 1),
        ("usr-dir-eu", ACCOUNT_ID, "Dra. Teresa Alentejo", "teresa.alentejo@revnaultdental.com", "Diretora Regional Europa", now_iso, "team-field-iberia", "role-ceo", "+351 912 345 678", "all", pwd_hash, 1, 1),
        ("usr-dir-latam", ACCOUNT_ID, "Esteban Morales", "esteban.morales@revnaultdental.com", "Diretor Regional LATAM", now_iso, "team-field-conosur", "role-ceo", "+54 11 4321-9876", "all", pwd_hash, 1, 1),
        ("usr-manager-roberto", ACCOUNT_ID, "Roberto Silveira", "roberto.gerente@salesrocketbrasil.com.br", "Gerente Comercial", now_iso, "team-campo-sp", "role-manager", "+55 11 99999-0006", "team", pwd_hash, 1, 0),
        ("usr-manager-fl", ACCOUNT_ID, "Sarah Jenkins", "sarah.jenkins@revnaultdental.com", "Gerente Comercial", now_iso, "team-field-fl", "role-manager", "+1 305 555-0102", "team", pwd_hash, 1, 0),
        ("usr-field-ricardo", ACCOUNT_ID, "Ricardo Mendes", "ricardo.campo@salesrocketbrasil.com.br", "Consultor Externo (Campo)", now_iso, "team-campo-sp", "role-field", "+55 11 99999-0002", "individual", pwd_hash, 1, 0),
        ("usr-field-sul", ACCOUNT_ID, "Lucas Guimarães", "lucas.sul@revnaultdental.com", "Consultor Externo (Campo)", now_iso, "team-campo-sul", "role-field", "+55 41 98888-0002", "individual", pwd_hash, 1, 0),
        ("usr-field-fl", ACCOUNT_ID, "David Miller", "david.miller@revnaultdental.com", "Consultor Externo (Campo)", now_iso, "team-field-fl", "role-field", "+1 305 555-0103", "individual", pwd_hash, 1, 0),
        ("usr-field-iberia", ACCOUNT_ID, "Manuel Fontes", "manuel.fontes@revnaultdental.com", "Consultor Externo (Campo)", now_iso, "team-field-iberia", "role-field", "+351 919 876 543", "individual", pwd_hash, 1, 0),
        ("usr-field-bue", ACCOUNT_ID, "Mariano Rossi", "mariano.rossi@revnaultdental.com", "Consultor Externo (Campo)", now_iso, "team-field-conosur", "role-field", "+54 11 5555-4321", "individual", pwd_hash, 1, 0),
        ("usr-inside-camila", ACCOUNT_ID, "Camila Ramos", "camila.atendimento@salesrocketbrasil.com.br", "Consultor Interno (Atendimento)", now_iso, "team-inside-br", "role-inside", "+55 11 99999-0003", "team", pwd_hash, 1, 0),
        ("usr-inside-us", ACCOUNT_ID, "Jennifer Parker", "jennifer.parker@revnaultdental.com", "Consultor Interno (Atendimento)", now_iso, "team-inside-us", "role-inside", "+1 407 555-0104", "team", pwd_hash, 1, 0),
        ("usr-inside-eu", ACCOUNT_ID, "Sofia Castelo", "sofia.castelo@revnaultdental.com", "Consultor Interno (Atendimento)", now_iso, "team-inside-eu", "role-inside", "+351 922 111 222", "team", pwd_hash, 1, 0),
        ("usr-log-marcos", ACCOUNT_ID, "Marcos Silva", "marcos.logistica@salesrocketbrasil.com.br", "Logística e Estoque (Expedição)", now_iso, "team-log-sp", "role-logistics", "+55 11 99999-0004", "all", pwd_hash, 1, 0),
        ("usr-log-miami", ACCOUNT_ID, "Anthony Rossi", "anthony.log@revnaultdental.com", "Logística e Estoque (Expedição)", now_iso, "team-log-miami", "role-logistics", "+1 305 555-0105", "all", pwd_hash, 1, 0),
        ("usr-support-juliana", ACCOUNT_ID, "Dra. Juliana Frota", "juliana.clinico@salesrocketbrasil.com.br", "Suporte Clínico e Pós-Venda", now_iso, "team-campo-sp", "role-clinical", "+55 11 99999-0005", "all", pwd_hash, 1, 0),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO users (id, account_id, name, email, role, created_at, team_id, role_id, phone, custom_data_scope, password_hash, is_active, is_superadmin)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, users_data)

    # 6. PIPELINES (4) & STAGES (15)
    pipelines_data = [
        (1, ACCOUNT_ID, "Funil Cirúrgico Brasil (Implantodontia & DENTGO)"),
        (2, ACCOUNT_ID, "North America DSO Enterprise Pipeline"),
        (3, ACCOUNT_ID, "European Digital Oral Rehabilitation Pipeline"),
        (4, ACCOUNT_ID, "LATAM Cono Sur Consignment & Fast Track"),
    ]
    cur.executemany("INSERT OR REPLACE INTO pipelines (id, account_id, name) VALUES (?, ?, ?)", pipelines_data)

    stages_data = [
        # Pipeline 1
        (101, 1, "Lead Cirúrgico Qualificado", "#3B82F6", 1, 20.0),
        (102, 1, "Apresentação e Dimensionamento de Maleta", "#6366F1", 2, 40.0),
        (103, 1, "Em Análise de Crédito / Alçada", "#F59E0B", 3, 60.0),
        (104, 1, "Minuta de Contrato em Assinatura", "#8B5CF6", 4, 80.0),
        (105, 1, "Contrato Fechado (Giro Ativo)", "#10B981", 5, 100.0),
        # Pipeline 2
        (201, 2, "DSO Initial Evaluation", "#3B82F6", 1, 25.0),
        (202, 2, "Clinical Committee Review", "#6366F1", 2, 50.0),
        (203, 2, "Master Agreement Drafting", "#8B5CF6", 3, 75.0),
        (204, 2, "DSO Live Procurement", "#10B981", 4, 100.0),
        # Pipeline 3
        (301, 3, "Avaliação de Fluxo Digital", "#3B82F6", 1, 30.0),
        (302, 3, "Validação Protética e Tomográfica", "#6366F1", 2, 60.0),
        (303, 3, "Acordo Ibérico Formalizado", "#10B981", 3, 100.0),
        # Pipeline 4
        (401, 4, "Contacto Inicial Cono Sur", "#3B82F6", 1, 25.0),
        (402, 4, "Negociación Consignación", "#F59E0B", 2, 65.0),
        (403, 4, "Contrato Vigente LATAM", "#10B981", 3, 100.0),
    ]
    cur.executemany("INSERT OR REPLACE INTO stages (id, pipeline_id, name, color, step_order, probability) VALUES (?, ?, ?, ?, ?, ?)", stages_data)

    # 7. PRICE TABLES (6) & PRODUCTS CATALOG (13)
    price_tables_data = [
        ("pt-retail-br", ACCOUNT_ID, "RETAIL_BR", "Tabela Venda Avulsa Brasil (Balcão)", 1.0, 1, now_iso),
        ("pt-balcao", ACCOUNT_ID, "BALCAO", "Tabela Balcão Padrão", 1.0, 1, now_iso),
        ("pt-consignment-br", ACCOUNT_ID, "CONSIGNMENT_BR", "Tabela Parceiro Consignado Brasil (KeyPartners)", 0.82, 1, now_iso),
        ("pt-dso-us", ACCOUNT_ID, "DSO_USA", "Tabela Corporativa DSO Flórida Volume", 0.75, 1, now_iso),
        ("pt-iberia-eu", ACCOUNT_ID, "IBERIA_DIGITAL", "Tabela Europa Reabilitação Digital", 0.85, 1, now_iso),
        ("pt-latam-hisp", ACCOUNT_ID, "LATAM_CONOSUR", "Tabela LATAM Cono Sur Conveniada", 0.80, 1, now_iso),
    ]
    cur.executemany("INSERT OR REPLACE INTO price_tables (id, account_id, table_key, name, discount_factor, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", price_tables_data)

    products_data = [
        ("prd-cm-375", ACCOUNT_ID, "IMP-CM-375-115", "Implante Cone Morse Acqua 3.75x11.5mm", "IMPLANTES", "ANVISA-1034567001", "CONE_MORSE", 3.75, 11.5, 45, 420.0, 1, now_iso),
        ("prd-gm-430", ACCOUNT_ID, "IMP-GM-430-130", "Implante Grand Morse Helix 4.3x13mm", "IMPLANTES", "ANVISA-1034567002", "GRAND_MORSE", 4.30, 13.0, 60, 480.0, 1, now_iso),
        ("prd-zyg-45", ACCOUNT_ID, "IMP-ZYG-QUAD-45", "Implante Zygoma Quad 45mm Ancoragem", "IMPLANTES_ESPECIAIS", "ANVISA-1034567003", "ZYGOMATIC", 4.00, 45.0, 50, 1850.0, 1, now_iso),
        ("prd-kit-full", ACCOUNT_ID, "KIT-GUIDED-FULL", "Kit Cirúrgico Guiado Full Arch Master", "INSTRUMENTAIS", "ANVISA-1034567004", "UNIVERSAL", None, None, None, 12500.0, 1, now_iso),
        ("prd-bio-bov", ACCOUNT_ID, "BIO-BONE-1G", "Biomaterial Enxerto Ósseo Bovino 1g Granulado", "BIOMATERIAIS", "ANVISA-1034567005", "N/A", None, None, None, 350.0, 1, now_iso),
        ("prd-mem-col", ACCOUNT_ID, "MEM-COLLAGEN-30", "Membrana Colágeno Reabsorvível 30x20mm", "BIOMATERIAIS", "ANVISA-1034567006", "N/A", None, None, None, 290.0, 1, now_iso),
        ("prd-scan-3d", ACCOUNT_ID, "SCAN-3D-WIRELESS", "Scanner Intraoral 3D Wireless Ultra", "EQUIPAMENTOS", "ANVISA-1034567007", "DIGITAL", None, None, None, 89000.0, 1, now_iso),
        ("prd-comp-ti", ACCOUNT_ID, "COMP-TI-BASE-CM", "Componente Protético Ti-Base Cone Morse", "COMPONENTES", "ANVISA-1034567008", "CONE_MORSE", 3.75, 4.0, 30, 145.0, 1, now_iso),
        ("prd-cic-gm", ACCOUNT_ID, "CIC-HEALING-GM", "Cicatrizador de Titânio Grand Morse 4.5x3mm", "COMPONENTES", "ANVISA-1034567009", "GRAND_MORSE", 4.50, 3.0, 15, 95.0, 1, now_iso),
        ("prd-motor-surg", ACCOUNT_ID, "MOTOR-SURG-LED", "Motor Cirúrgico com Peça Reta LED 20:1", "EQUIPAMENTOS", "ANVISA-1034567010", "UNIVERSAL", None, None, None, 18500.0, 1, now_iso),
        ("IMP-CM-37511", ACCOUNT_ID, "IMP-CM-37511", "Implante Cone Morse Helix 3.75x11.5mm", "IMPLANTES", "ANVISA-1034567001", "CONE_MORSE", 3.75, 11.5, 45, 420.0, 1, now_iso),
        ("IMP-CM-4311", ACCOUNT_ID, "IMP-CM-4311", "Implante Cone Morse Helix 4.3x11.5mm", "IMPLANTES", "ANVISA-1034567001", "CONE_MORSE", 4.30, 11.5, 45, 450.0, 1, now_iso),
        ("IMP-CM-3513", ACCOUNT_ID, "IMP-CM-3513", "Implante Cone Morse Helix 3.5x13mm", "IMPLANTES", "ANVISA-1034567001", "CONE_MORSE", 3.50, 13.0, 45, 430.0, 1, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO products_catalog (id, account_id, sku, name, category, anvisa_reg, prosthetic_platform, diameter, length, recommended_torque, base_price, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, products_data)

    # 8. INSTITUTIONS (20)
    institutions_data = [
        ("inst-01", ACCOUNT_ID, "Instituto Branemark São Paulo", "HOSPITAL", "São Paulo", "SP", "Prof. Dr. Cláudio Prado", 120, "CREDENTIALED", now_iso, "usr-director-br", "usr-field-ricardo", "usr-inside-camila", "team-campo-sp", "bu-latam-br"),
        ("inst-02", ACCOUNT_ID, "Hospital Moriah Reabilitação Craniofacial", "HOSPITAL", "São Paulo", "SP", "Dra. Marcela Vasconcelos", 80, "CREDENTIALED", now_iso, "usr-director-br", "usr-field-ricardo", "usr-inside-camila", "team-campo-sp", "bu-latam-br"),
        ("inst-03", ACCOUNT_ID, "Faculdade de Odontologia USP Pós-Graduação", "UNIVERSIDADE", "São Paulo", "SP", "Dr. Nelson Albuquerque", 250, "CREDENTIALED", now_iso, "usr-director-br", "usr-field-ricardo", "usr-inside-camila", "team-campo-sp", "bu-latam-br"),
        ("inst-04", ACCOUNT_ID, "Clínica Dental Prime Moema", "CLINICA_PRIVADA", "São Paulo", "SP", "Dr. Fernando Sato", 15, "CREDENTIALED", now_iso, "usr-director-br", "usr-field-ricardo", "usr-inside-camila", "team-campo-sp", "bu-latam-br"),
        ("inst-05", ACCOUNT_ID, "Hospital Pilar Centro Bucomaxilofacial", "HOSPITAL", "Curitiba", "PR", "Dr. Guilherme Rangel", 45, "CREDENTIALED", now_iso, "usr-director-br", "usr-field-sul", "usr-inside-camila", "team-campo-sul", "bu-latam-br"),
        ("inst-06", ACCOUNT_ID, "Clínica Batel Oral Day Surgery", "CLINICA_PRIVADA", "Curitiba", "PR", "Dra. Tatiana Bettega", 20, "CREDENTIALED", now_iso, "usr-director-br", "usr-field-sul", "usr-inside-camila", "team-campo-sul", "bu-latam-br"),
        ("inst-07", ACCOUNT_ID, "Oral Sin Curitiba Centro Integrado", "DSO", "Curitiba", "PR", "Dr. Rodrigo Zanin", 60, "CREDENTIALED", now_iso, "usr-director-br", "usr-field-sul", "usr-inside-camila", "team-campo-sul", "bu-latam-br"),
        ("inst-08", ACCOUNT_ID, "Hospital Português de Recife Odonto Day", "HOSPITAL", "Recife", "PE", "Dr. Alexandre Diniz", 40, "CREDENTIALED", now_iso, "usr-director-br", "usr-field-ricardo", "usr-inside-camila", "team-campo-sp", "bu-latam-br"),
        ("inst-09", ACCOUNT_ID, "Centro Cirúrgico Boa Viagem Implantes", "CLINICA_PRIVADA", "Recife", "PE", "Dra. Flávia Holanda", 25, "CREDENTIALED", now_iso, "usr-director-br", "usr-field-ricardo", "usr-inside-camila", "team-campo-sp", "bu-latam-br"),
        ("inst-10", ACCOUNT_ID, "Miami Dental Institute Brickell Hub", "DSO", "Miami", "FL", "Dr. Robert Vance", 110, "CREDENTIALED", now_iso, "usr-dir-na", "usr-field-fl", "usr-inside-us", "team-field-fl", "bu-na-usa"),
        ("inst-11", ACCOUNT_ID, "Florida Oral Surgery Associates Orlando", "DSO", "Orlando", "FL", "Dr. George Harrison", 95, "CREDENTIALED", now_iso, "usr-dir-na", "usr-field-fl", "usr-inside-us", "team-field-fl", "bu-na-usa"),
        ("inst-12", ACCOUNT_ID, "University of Miami Hospital Center", "UNIVERSIDADE", "Miami", "FL", "Dr. Alan Becker", 300, "CREDENTIALED", now_iso, "usr-dir-na", "usr-field-fl", "usr-inside-us", "team-field-fl", "bu-na-usa"),
        ("inst-13", ACCOUNT_ID, "Coral Gables Maxillofacial Day Hospital", "HOSPITAL", "Miami", "FL", "Dr. Carlos Menendez", 35, "CREDENTIALED", now_iso, "usr-dir-na", "usr-field-fl", "usr-inside-us", "team-field-fl", "bu-na-usa"),
        ("inst-14", ACCOUNT_ID, "Clínica Dentária Avenida da Liberdade", "CLINICA_PRIVADA", "Lisboa", "11", "Dr. Miguel Paisana", 30, "CREDENTIALED", now_iso, "usr-dir-eu", "usr-field-iberia", "usr-inside-eu", "team-field-iberia", "bu-eu-iberia"),
        ("inst-15", ACCOUNT_ID, "Hospital da Luz Centro de Reabilitação Oral", "HOSPITAL", "Lisboa", "11", "Prof. Dr. António Simões", 85, "CREDENTIALED", now_iso, "usr-dir-eu", "usr-field-iberia", "usr-inside-eu", "team-field-iberia", "bu-eu-iberia"),
        ("inst-16", ACCOUNT_ID, "Faculdade de Medicina Dentária Universidade de Lisboa", "UNIVERSIDADE", "Lisboa", "11", "Dra. Filipa Ramalho", 220, "CREDENTIALED", now_iso, "usr-dir-eu", "usr-field-iberia", "usr-inside-eu", "team-field-iberia", "bu-eu-iberia"),
        ("inst-17", ACCOUNT_ID, "Instituto Dental Digital Madrid Salamanca", "CLINICA_PRIVADA", "Madrid", "28", "Dr. Javier Ortega", 40, "CREDENTIALED", now_iso, "usr-dir-eu", "usr-field-iberia", "usr-inside-eu", "team-field-iberia", "bu-eu-iberia"),
        ("inst-18", ACCOUNT_ID, "Hospital Italiano de Buenos Aires Odontología", "HOSPITAL", "Buenos Aires", "BA", "Dr. Lucas Varela", 75, "CREDENTIALED", now_iso, "usr-dir-latam", "usr-field-bue", "usr-inside-camila", "team-field-conosur", "bu-latam-hisp"),
        ("inst-19", ACCOUNT_ID, "Clínica Alemana Santiago Centro Maxilar", "HOSPITAL", "Santiago", "RM", "Dr. Roberto Valenzuela", 65, "CREDENTIALED", now_iso, "usr-dir-latam", "usr-field-bue", "usr-inside-camila", "team-field-conosur", "bu-latam-hisp"),
        ("inst-20", ACCOUNT_ID, "Fundación Odontológica de Bogotá Andina", "UNIVERSIDADE", "Bogotá", "DC", "Dra. Carolina Restrepo", 140, "CREDENTIALED", now_iso, "usr-dir-latam", "usr-field-bue", "usr-inside-camila", "team-field-conosur", "bu-latam-hisp"),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO institutions (id, account_id, name, institution_type, city, state, coordinator_name, active_students_count, accreditation_status, created_at, owner_id, field_owner_id, inside_owner_id, team_id, business_unit_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, institutions_data)

    # 9. CONTACTS (60)
    specialties = ["Implantodontia", "Bucomaxilofacial", "Prótese Digital", "Periodontia"]
    cities_states = [
        ("São Paulo", "SP", "team-campo-sp", "bu-latam-br", "usr-field-ricardo"),
        ("Curitiba", "PR", "team-campo-sul", "bu-latam-br", "usr-field-sul"),
        ("Recife", "PE", "team-campo-sp", "bu-latam-br", "usr-field-ricardo"),
        ("Miami", "FL", "team-field-fl", "bu-na-usa", "usr-field-fl"),
        ("Orlando", "FL", "team-field-fl", "bu-na-usa", "usr-field-fl"),
        ("Lisboa", "11", "team-field-iberia", "bu-eu-iberia", "usr-field-iberia"),
        ("Madrid", "28", "team-field-iberia", "bu-eu-iberia", "usr-field-iberia"),
        ("Buenos Aires", "BA", "team-field-conosur", "bu-latam-hisp", "usr-field-bue"),
        ("Santiago", "RM", "team-field-conosur", "bu-latam-hisp", "usr-field-bue"),
    ]
    contacts_data = []
    contact_inst_data = []
    contact_audit_data = []
    scoring_history_data = []

    names_pool = [
        "Dr. Roberto Martins", "Dra. Camila Nogueira", "Dr. Fernando Sato", "Dr. Marcelo Fagundes", "Dra. Juliana Prado",
        "Dr. Gustavo Alencar", "Dra. Patrícia Silveira", "Dr. André Villas", "Dra. Beatriz Fontana", "Dr. Thiago Barreto",
        "Dr. Guilherme Rangel", "Dra. Tatiana Bettega", "Dr. Rodrigo Zanin", "Dra. Mariana Costa", "Dr. Daniel Seixas",
        "Dr. Alexandre Diniz", "Dra. Flávia Holanda", "Dr. Eduardo Meireles", "Dra. Letícia Vasconcelos", "Dr. Pedro Brandão",
        "Dr. Robert Vance", "Dr. George Harrison", "Dr. Alan Becker", "Dr. Carlos Menendez", "Dra. Jennifer Scott",
        "Dr. David Sterling", "Dra. Sarah Conner", "Dr. William Taylor", "Dra. Amanda Ross", "Dr. Brian O'Connor",
        "Dr. Miguel Paisana", "Prof. Dr. António Simões", "Dra. Filipa Ramalho", "Dr. Gonçalo Esteves", "Dra. Inês Carvalhal",
        "Dr. Javier Ortega", "Dra. Carmen Delgado", "Dr. Pablo Morales", "Dra. Lucia Navarro", "Dr. Santiago Jimenez",
        "Dr. Lucas Varela", "Dr. Mariano Benitez", "Dra. Sofia Gutierrez", "Dr. Joaquin Alvarez", "Dra. Valentina Gomez",
        "Dr. Roberto Valenzuela", "Dra. Macarena Perez", "Dr. Francisco Castro", "Dra. Florencia Muñoz", "Dr. Claudio Tapia",
        "Dr. Mauricio Rivas", "Dra. Daniela Ospina", "Dr. Camilo Echeverry", "Dra. Ximena Beltran", "Dr. Andres Montano",
        "Dr. Henrique Lins", "Dra. Claudia Meira", "Dr. Fabio Medeiros", "Dra. Renata Paiva", "Dr. Leonardo Castelo"
    ]

    for idx, c_name in enumerate(names_pool, start=1):
        city, state, team_id, bu_id, field_owner = cities_states[(idx - 1) % len(cities_states)]
        spec = specialties[(idx - 1) % len(specialties)]
        cro_num = 12000 + idx
        cro_uf = f"CRO-{state}-{cro_num}" if len(state) == 2 and state in ["SP", "PR", "PE"] else f"LIC-{state}-{cro_num}"
        score = 65 + (idx % 35)
        inst_id = f"inst-{(idx % 20) + 1:02d}"
        tier = "A" if score >= 85 else ("B" if score >= 75 else "C")
        email_clean = c_name.lower().replace("dr. ", "").replace("dra. ", "").replace("prof. ", "").replace(" ", ".").replace("'", "") + f"{idx}@revnault-clients.org"
        phone = f"+55 11 9{idx:04d}-4321" if "SP" in state else f"+1 305 555-{idx:04d}"

        contacts_data.append((
            idx, ACCOUNT_ID, c_name, email_clean, phone, f"Clínica {c_name.split()[-1]} Dental",
            "implantodontia,cirurgia_guiada,icp_alto", score, now_iso, "usr-director-br", field_owner,
            "usr-inside-camila", team_id, bu_id, str(cro_num), cro_uf, 1, state, spec,
            f"Instituto Dental {city}", 25 + (idx % 40), 30, (now - timedelta(days=(idx % 60))).strftime("%Y-%m-%d"),
            "CONSIGNADO_ATIVO", 30 + (idx % 25), "CIRURGIAO_TITULAR", city, state
        ))

        contact_inst_data.append((
            f"ci-link-{idx}", ACCOUNT_ID, idx, inst_id, "CORPO_CLINICO", "Cirurgião Chefe / Responsável Técnico",
            1 if idx % 5 == 0 else 0, "Opera casos complexos de implantes e protocolo guiado", now_iso
        ))

        contact_audit_data.append((
            idx, idx, "usr-director-br", "Carlos Eduardo Silva", "UPDATE_SCORE",
            str(score - 10), str(score), "Qualificação de perfil cirúrgico e validação documental de conselho", now_iso
        ))

        scoring_history_data.append((
            f"sc-hist-{idx}", ACCOUNT_ID, idx, score - 10, score, 85, 80, tier,
            "Engajamento contínuo em cirurgias guiadas e pontuação RFM positiva", now_iso
        ))

    cur.executemany("""
        INSERT OR REPLACE INTO contacts (
            id, account_id, name, email, phone, company, tags, score, created_at, owner_id,
            field_owner_id, inside_owner_id, team_id, business_unit_id, cro, cro_uf, cro_verified,
            uf, specialty, clinic_name, monthly_implant_volume, reorder_cycle_days, last_order_date,
            work_model, monthly_implants_volume, customer_type, city, state
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, contacts_data)

    cur.executemany("""
        INSERT OR REPLACE INTO contact_institutions (id, account_id, contact_id, institution_id, relationship_type, role_title, is_kol, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, contact_inst_data)

    cur.executemany("""
        INSERT OR REPLACE INTO contact_audit_logs (id, contact_id, user_id, author_name, action, old_value, new_value, comment, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, contact_audit_data)

    cur.executemany("""
        INSERT OR REPLACE INTO scoring_history (id, account_id, contact_id, previous_score, new_score, icp_fit_score, engagement_score, tier, trigger_reason, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, scoring_history_data)

    # 10. SCORING RULES (5)
    scoring_rules_data = [
        ("sr-01", ACCOUNT_ID, "Cirurgião com CRO Ativo Verificado", "COMPLIANCE", "cro_verified", "1", 25, "Garante conformidade com o CFO e segurança jurídica", 1, now_iso),
        ("sr-02", ACCOUNT_ID, "Volume Mensal de Implantes Superior a 30", "VOLUME", "monthly_implant_volume_gt_30", "true", 30, "Indica alta rotatividade e potencial para maleta consignada", 1, now_iso),
        ("sr-03", ACCOUNT_ID, "Professor ou Coordenador em Universidade (KOL)", "INSTITUCIONAL", "is_kol", "1", 20, "Multiplicador de marca e formador de opinião", 1, now_iso),
        ("sr-04", ACCOUNT_ID, "Utilizador Ativo de Scanner Intraoral 3D", "FLUXO_DIGITAL", "uses_digital_scanner", "true", 15, "Aderência total ao catálogo cirúrgico guiado", 1, now_iso),
        ("sr-05", ACCOUNT_ID, "Histórico Sem Inadimplência ou Atrasos Financeiros", "FINANCEIRO", "credit_clean", "true", 10, "Liberação expressa de alçada e aumento de limite", 1, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO scoring_rules (id, account_id, name, category, condition_key, condition_val, points, impact_description, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, scoring_rules_data)

    # 11. COMMERCIAL DEALS (35), AUDIT LOGS, OBJECTIONS, DISCOUNT REQUESTS, CONTRACTS
    deals_data = []
    deal_audit_data = []
    deal_objections_data = []
    deal_discounts_data = []
    deal_contracts_data = []
    call_recordings_data = []
    call_transcriptions_data = []
    semantic_embs_data = []

    deal_titles = [
        "Renovação de Maleta Consignada Full Arch 50 Implantes",
        "Adesão ao Programa KeyPartners com Scanner 3D",
        "Pacote Cirúrgico Emergencial Cone Morse 20 Unidades",
        "Protocolo Guiado Zygoma Quad para Hospital Day",
        "Reposição Expressa DENTGO 45 Minutos Moema",
        "Acordo Corporativo DSO Flórida 200 Implantes",
        "Imersão e Consignação Digital Ibéria Lisboa",
        "Contrato Master Clínicas Cono Sur Buenos Aires",
        "Upgrade de Tabela Cirúrgica e Maleta Grand Morse",
        "Fornecimento Anual de Biomateriais e Membranas"
    ]

    for d_idx in range(1, 36):
        d_id = f"deal-{d_idx:02d}"
        contact_id = ((d_idx - 1) % 60) + 1
        contact_name = names_pool[(contact_id - 1) % len(names_pool)]
        title = f"{deal_titles[(d_idx - 1) % len(deal_titles)]} - {contact_name}"
        pipe_id = ((d_idx - 1) % 4) + 1
        val = 18500.0 + (d_idx * 2450.0)
        
        # Stages distribution
        if pipe_id == 1:
            stage_id = 101 + ((d_idx - 1) % 5)
        elif pipe_id == 2:
            stage_id = 201 + ((d_idx - 1) % 4)
        elif pipe_id == 3:
            stage_id = 301 + ((d_idx - 1) % 3)
        else:
            stage_id = 401 + ((d_idx - 1) % 3)

        appr_status = "PENDING_DISCOUNT_APPROVAL" if d_idx in [3, 7, 14, 22] else "APPROVED"
        field_user = "usr-field-ricardo" if pipe_id == 1 else ("usr-field-fl" if pipe_id == 2 else ("usr-field-iberia" if pipe_id == 3 else "usr-field-bue"))
        inside_user = "usr-inside-camila" if pipe_id in [1, 4] else ("usr-inside-us" if pipe_id == 2 else "usr-inside-eu")
        bu_id = "bu-latam-br" if pipe_id == 1 else ("bu-na-usa" if pipe_id == 2 else ("bu-eu-iberia" if pipe_id == 3 else "bu-latam-hisp"))
        team_id = "team-campo-sp" if pipe_id == 1 else ("team-field-fl" if pipe_id == 2 else ("team-field-iberia" if pipe_id == 3 else "team-field-conosur"))

        deals_data.append((
            d_id, ACCOUNT_ID, pipe_id, stage_id, title, val, f"Clínica {contact_name.split()[-1]}",
            contact_name, "alta" if val > 40000 else "media", now_iso, (now + timedelta(days=20)).strftime("%Y-%m-%d"),
            field_user, inside_user, 70.0, 30.0,
            f"Oportunidade de alta rentabilidade com forte consumo de implantes e biomateriais.",
            appr_status, field_user, team_id, bu_id
        ))

        deal_audit_data.append((
            d_idx, d_id, field_user, "Consultor Comercial", "STAGE_CHANGE",
            "101", str(stage_id), "Evolução do funil após alinhamento presencial com cirurgião chefe", now_iso
        ))

        if appr_status == "PENDING_DISCOUNT_APPROVAL":
            deal_discounts_data.append((
                f"disc-{d_idx}", ACCOUNT_ID, d_id, field_user, 18.5, 15.0, "PENDING", None, now_iso, None
            ))

        deal_objections_data.append((
            f"obj-{d_idx}", ACCOUNT_ID, d_id, "PRECO",
            "Cirurgião questiona margem de desconto comparada a concorrentes nacionais.",
            "Apresentar estudo clínico de estabilidade primária Cone Morse e garantia vitalícia ANVISA.",
            1 if d_idx % 2 == 0 else 0, now_iso
        ))

        # Contrato associado
        contract_status = "SIGNED" if stage_id in [105, 204, 303, 403] else ("DRAFT" if stage_id in [101, 201] else "SENT")
        deal_contracts_data.append((
            f"cntr-{d_idx:02d}", ACCOUNT_ID, d_id, f"doc-documenso-{d_idx:03d}",
            f"Contrato de Fornecimento Odontológico - {title}", "fornecimento_implantes",
            contract_status, f"{ACCOUNT_ID}/contracts/{d_id}/proposal_original.pdf",
            f"{ACCOUNT_ID}/contracts/{d_id}/proposal_signed.pdf" if contract_status == "SIGNED" else None,
            f"https://cdn.revnaut.io/{ACCOUNT_ID}/contracts/{d_id}/proposal_signed.pdf" if contract_status == "SIGNED" else None,
            f"sha256-hash-contract-sample-{d_idx:04d}", contact_name, f"contato{d_idx}@clinica.com.br",
            "+55 11 98888-7777", f"https://documenso.revnaut.vpsconexao.org/sign/doc-{d_idx:03d}",
            now_iso, now_iso if contract_status == "SIGNED" else None
        ))

        # Gravação e Transcrição de Reunião
        call_id = f"call-{d_idx:02d}"
        call_recordings_data.append((
            call_id, ACCOUNT_ID, f"room-deal-{d_id}", d_id, None, field_user, contact_name,
            "webrtc", "completed", 420, f"https://cdn.revnaut.io/audio/{call_id}.ogg", f"audio/{call_id}.ogg",
            f"egress-{d_idx:03d}", now_iso, now_iso
        ))

        dialogue_text = f"Consultor: Doutor, apresentamos a maleta de implantes Cone Morse com esterilização estrita ANVISA. Cirurgião: Perfeito, temos 8 cirurgias programadas para a próxima semana e necessitamos do fluxo guiado completo."
        segments = [
            {"speaker": "SPEAKER_CONSULTANT", "start": 0.0, "end": 12.0, "text": "Doutor, apresentamos a maleta de implantes Cone Morse com esterilização estrita ANVISA."},
            {"speaker": "SPEAKER_SURGEON", "start": 13.0, "end": 28.0, "text": "Perfeito, temos 8 cirurgias programadas para a próxima semana e necessitamos do fluxo guiado completo."}
        ]
        transc_id = f"transc-{call_id}"
        call_transcriptions_data.append((
            transc_id, ACCOUNT_ID, call_id, d_id, dialogue_text, "pt", "faster-whisper-medium",
            json.dumps(segments), 2, 28.0, now_iso
        ))

        emb_vector = compute_semantic_embedding(dialogue_text)
        semantic_embs_data.append((
            f"emb-deal-{d_idx}", ACCOUNT_ID, "CALL_TRANSCRIPTION", transc_id, dialogue_text,
            json.dumps(emb_vector), json.dumps({"deal_id": d_id, "contact_name": contact_name}), now_iso
        ))

    cur.executemany("""
        INSERT OR REPLACE INTO deals (
            id, account_id, pipeline_id, stage_id, title, value, company, contact_name, priority,
            created_at, expected_close_date, field_owner_id, inside_owner_id, split_commission_field_pct,
            split_commission_inside_pct, executive_summary, approval_status, owner_id, team_id, business_unit_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, deals_data)

    cur.executemany("INSERT OR REPLACE INTO deal_audit_logs (id, deal_id, user_id, author_name, action, old_value, new_value, comment, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", deal_audit_data)
    cur.executemany("INSERT OR REPLACE INTO deal_discount_requests (id, account_id, deal_id, requested_by_user_id, discount_pct, max_allowed_pct, status, approved_by_user_id, created_at, resolved_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", deal_discounts_data)
    cur.executemany("INSERT OR REPLACE INTO deal_objections (id, account_id, deal_id, category, objection_text, suggested_counter_argument, resolved, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", deal_objections_data)
    cur.executemany("""
        INSERT OR REPLACE INTO deal_contracts (
            id, account_id, deal_id, documenso_document_id, title, contract_type, status,
            original_pdf_r2_key, signed_pdf_r2_key, signed_pdf_url, sha256_hash, signer_name,
            signer_email, signer_phone, signing_url, created_at, signed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, deal_contracts_data)
    cur.executemany("""
        INSERT OR REPLACE INTO call_recordings (
            id, account_id, room_name, deal_id, ticket_id, caller_identity, receiver_identity,
            call_type, status, duration_seconds, r2_recording_url, r2_audio_key, egress_id, created_at, ended_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, call_recordings_data)
    cur.executemany("""
        INSERT OR REPLACE INTO call_transcriptions (
            id, account_id, call_id, deal_id, full_text, language, model_name, segments_json, speakers_detected, duration_seconds, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, call_transcriptions_data)
    cur.executemany("""
        INSERT OR REPLACE INTO semantic_embeddings (id, tenant_id, entity_type, entity_id, content_chunk, embedding, metadata_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, semantic_embs_data)

    # 12. KEYPARTNERS OPERATION (10 agreements, 15 kits, 40 ledger, 12 orders, 6 KOL, loyalty)
    agreements_data = [
        ("agr-01", ACCOUNT_ID, "Dr. Roberto Martins", "CRO-SP-12001", "BLACK_KOL", 150000.0, 42000.0, 35000.0, 45, 1, now_iso, "usr-director-br", "usr-field-ricardo", "usr-inside-camila", "team-campo-sp", "bu-latam-br"),
        ("agr-02", ACCOUNT_ID, "Dra. Camila Nogueira", "CRO-PR-12002", "GOLD", 100000.0, 28000.0, 25000.0, 60, 1, now_iso, "usr-director-br", "usr-field-sul", "usr-inside-camila", "team-campo-sul", "bu-latam-br"),
        ("agr-03", ACCOUNT_ID, "Dr. Fernando Sato", "CRO-PE-12003", "GOLD", 90000.0, 15000.0, 20000.0, 60, 1, now_iso, "usr-director-br", "usr-field-ricardo", "usr-inside-camila", "team-campo-sp", "bu-latam-br"),
        ("agr-04", ACCOUNT_ID, "Dr. Robert Vance", "LIC-FL-12004", "BLACK_KOL", 250000.0, 85000.0, 60000.0, 30, 1, now_iso, "usr-dir-na", "usr-field-fl", "usr-inside-us", "team-field-fl", "bu-na-usa"),
        ("agr-05", ACCOUNT_ID, "Dr. George Harrison", "LIC-FL-12005", "SILVER", 60000.0, 12000.0, 15000.0, 60, 1, now_iso, "usr-dir-na", "usr-field-fl", "usr-inside-us", "team-field-fl", "bu-na-usa"),
        ("agr-06", ACCOUNT_ID, "Dr. Miguel Paisana", "LIC-11-12006", "GOLD", 120000.0, 35000.0, 30000.0, 45, 1, now_iso, "usr-dir-eu", "usr-field-iberia", "usr-inside-eu", "team-field-iberia", "bu-eu-iberia"),
        ("agr-07", ACCOUNT_ID, "Prof. Dr. António Simões", "LIC-11-12007", "BLACK_KOL", 200000.0, 72000.0, 50000.0, 30, 1, now_iso, "usr-dir-eu", "usr-field-iberia", "usr-inside-eu", "team-field-iberia", "bu-eu-iberia"),
        ("agr-08", ACCOUNT_ID, "Dr. Lucas Varela", "LIC-BA-12008", "SILVER", 50000.0, 9500.0, 12000.0, 60, 1, now_iso, "usr-dir-latam", "usr-field-bue", "usr-inside-camila", "team-field-conosur", "bu-latam-hisp"),
        ("agr-09", ACCOUNT_ID, "Dr. Roberto Valenzuela", "LIC-RM-12009", "GOLD", 80000.0, 22000.0, 20000.0, 60, 1, now_iso, "usr-dir-latam", "usr-field-bue", "usr-inside-camila", "team-field-conosur", "bu-latam-hisp"),
        ("agr-10", ACCOUNT_ID, "Dr. Alexandre Diniz", "CRO-SP-12010", "SILVER", 55000.0, 8000.0, 10000.0, 60, 1, now_iso, "usr-director-br", "usr-field-ricardo", "usr-inside-camila", "team-campo-sp", "bu-latam-br"),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO kp_partner_agreements (
            id, account_id, partner_name, partner_cro_uf, tier, credit_limit, used_credit,
            min_monthly_revenue, max_turnover_days, is_active, created_at, owner_id,
            field_owner_id, inside_owner_id, team_id, business_unit_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, agreements_data)

    kits_data = []
    for k_idx in range(1, 16):
        agr_id = f"agr-{((k_idx - 1) % 10) + 1:02d}"
        status_k = "CONSIGNED" if k_idx <= 10 else "IN_STOCK"
        comp = [
            {"product_id": "prd-cm-375", "name": "Implante Cone Morse 3.75x11.5", "quantity": 10},
            {"product_id": "prd-gm-430", "name": "Implante Grand Morse 4.3x13", "quantity": 10},
            {"product_id": "prd-comp-ti", "name": "Ti-Base Cone Morse", "quantity": 6}
        ]
        kits_data.append((
            f"kit-consign-{k_idx:02d}", ACCOUNT_ID, f"SN-REV-2026-{k_idx:04d}", f"QR-KIT-{k_idx:04d}",
            f"Maleta Cirúrgica Avançada Multi-Linhas #{k_idx:02d}", json.dumps(comp), status_k,
            agr_id if status_k == "CONSIGNED" else None, now_iso
        ))
    kits_data.append((
        "kit-consign-kit-cm-2026-009", ACCOUNT_ID, "KIT-CM-2026-009", "QR-KIT-009",
        "Maleta Cirúrgica Avançada Cone Morse #009", json.dumps([
            {"product_id": "prd-cm-375", "name": "Implante Cone Morse 3.75x11.5", "quantity": 10},
            {"product_id": "prd-gm-430", "name": "Implante Grand Morse 4.3x13", "quantity": 10},
            {"product_id": "prd-comp-ti", "name": "Ti-Base Cone Morse", "quantity": 6}
        ]), "IN_FIELD", "agr-01", now_iso
    ))
    cur.executemany("""
        INSERT OR REPLACE INTO kp_consignment_kits (id, account_id, serial_number, qr_code, name, composition_json, status, current_agreement_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, kits_data)

    ledger_data = []
    for l_idx in range(1, 41):
        agr_id = f"agr-{((l_idx - 1) % 10) + 1:02d}"
        m_type = "REMETIDO" if l_idx % 3 != 0 else "CONSUMIDO_CIRURGIA"
        ledger_data.append((
            f"ledg-{l_idx:03d}", ACCOUNT_ID, agr_id, m_type, "prd-cm-375", "Implante Cone Morse Acqua 3.75x11.5mm",
            "ANVISA-1034567001", f"LOTE-2026-{l_idx:03d}", f"SN-IMP-{l_idx:04d}", 5, 420.0, 2100.0,
            (now + timedelta(days=500)).strftime("%Y-%m-%d"), now_iso
        ))
    ledger_data.append((
        "ledg-rem-lote-1122", ACCOUNT_ID, "agr-01", "REMESSA", "IMP-CM-3513", "Implante Cone Morse Helix 3.5x13mm",
        "ANVISA-1034567001", "LOTE-1122", "SN-IMP-LOTE1122", 10, 430.0, 4300.0,
        (now + timedelta(days=500)).strftime("%Y-%m-%d"), now_iso
    ))
    cur.executemany("""
        INSERT OR REPLACE INTO kp_custody_ledger (
            id, account_id, agreement_id, movement_type, product_id, product_name, anvisa_reg,
            batch_number, serial_number, quantity, unit_value, total_value, sterilization_expiry_date, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ledger_data)

    # 12 surgical orders in every status
    order_statuses = ["REQUESTED", "APPROVED_PREPARING", "DISPATCHED_SEALED", "POSTOP_REPORTED"]
    surg_orders_data = []
    for s_idx in range(1, 13):
        agr_id = f"agr-{((s_idx - 1) % 10) + 1:02d}"
        s_status = order_statuses[(s_idx - 1) % len(order_statuses)]
        rem_items = [{
            "product_id": "prd-cm-375",
            "sku": "IMP-CM-375-115",
            "product_name": "Implante Cone Morse Acqua 3.75x11.5mm",
            "anvisa_reg": "ANVISA-1034567001",
            "batch_number": "LOT-EXP-2026-0101",
            "quantity": 4,
            "qty": 4,
            "unit_value": 420.0,
            "sterilization_expiry_date": "2028-10-19"
        }]
        cons_items = [{"sku": "IMP-CM-375-115", "qty": 2}] if s_status in ["POSTOP_REPORTED", "FATURADO_E_REPOSTO"] else []
        ret_items = [{"sku": "IMP-CM-375-115", "qty": 2}, {"sku": "IMP-GM-430-130", "qty": 2}] if s_status in ["POSTOP_REPORTED", "FATURADO_E_REPOSTO"] else []
        surg_orders_data.append((
            f"so-order-{s_idx:02d}", ACCOUNT_ID, agr_id, f"PAC-CIRURGICO-{s_idx:03d}",
            (now + timedelta(days=s_idx % 5)).strftime("%Y-%m-%d"), s_status, "usr-field-ricardo",
            "usr-inside-camila", json.dumps(rem_items), json.dumps(cons_items), json.dumps(ret_items),
            f"seals/order_{s_idx:02d}_thermal_seal.jpg" if s_status in ["DISPATCHED_SEALED", "POSTOP_REPORTED", "EM_POSSE_CLINICA", "FATURADO_E_REPOSTO"] else None,
            f"nf-order-{s_idx:02d}" if s_status in ["POSTOP_REPORTED", "FATURADO_E_REPOSTO"] else None, now_iso, now_iso
        ))
    cur.executemany("""
        INSERT OR REPLACE INTO kp_surgical_orders (
            id, account_id, agreement_id, patient_identifier, surgery_date, status, field_consultant_id,
            inside_analyst_id, remitted_items_json, consumed_items_json, returned_items_json,
            seal_photo_r2_key, billing_order_id, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, surg_orders_data)

    kol_contracts_data = [
        ("kol-01", ACCOUNT_ID, "agr-01", "Dr. Roberto Martins", "CRO-SP-12001", "Scanner Intraoral 3D Wireless Ultra", "ASSET-SCAN-01", 30, 2, 28, "COMPLIANT", json.dumps(["evidence/aula_sp_01.pdf"]), now_iso, now_iso),
        ("kol-02", ACCOUNT_ID, "agr-04", "Dr. Robert Vance", "LIC-FL-12004", "Scanner Intraoral 3D Wireless Ultra", "ASSET-SCAN-02", 40, 2, 42, "COMPLIANT", json.dumps(["evidence/webinar_miami_01.pdf"]), now_iso, now_iso),
        ("kol-03", ACCOUNT_ID, "agr-07", "Prof. Dr. António Simões", "LIC-11-12007", "Scanner Intraoral 3D Wireless Ultra", "ASSET-SCAN-03", 35, 1, 31, "COMPLIANT", json.dumps(["evidence/congresso_lisboa_01.pdf"]), now_iso, now_iso),
        ("kol-04", ACCOUNT_ID, "agr-02", "Dra. Camila Nogueira", "CRO-PR-12002", "Motor Cirúrgico com LED 20:1", "ASSET-MOTOR-01", 25, 1, 26, "COMPLIANT", json.dumps(["evidence/workshop_curitiba.pdf"]), now_iso, now_iso),
        ("kol-05", ACCOUNT_ID, "agr-06", "Dr. Miguel Paisana", "LIC-11-12006", "Motor Cirúrgico com LED 20:1", "ASSET-MOTOR-02", 20, 1, 18, "PENDING_REPORT", json.dumps([]), now_iso, now_iso),
        ("kol-06", ACCOUNT_ID, "agr-09", "Dr. Roberto Valenzuela", "LIC-RM-12009", "Scanner Intraoral 3D Wireless Ultra", "ASSET-SCAN-04", 25, 1, 24, "COMPLIANT", json.dumps(["evidence/seminario_santiago.pdf"]), now_iso, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO kp_kol_contracts (
            id, account_id, agreement_id, kol_name, cro_uf, equipment_name, asset_tag,
            min_monthly_implants_target, clinical_lectures_quota, current_month_consumption,
            compliance_status, evidence_r2_keys_json, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, kol_contracts_data)

    wallets_data = []
    loyalty_tx_data = []
    for w_idx in range(1, 11):
        agr_id = f"agr-{w_idx:02d}"
        partner_name = agreements_data[w_idx - 1][2]
        pts = 4500 + (w_idx * 1200)
        wallets_data.append((
            f"wal-{w_idx:02d}", ACCOUNT_ID, agr_id, partner_name, pts, pts + 2000,
            agreements_data[w_idx - 1][4], 45 + (w_idx * 15), now_iso, now_iso
        ))
        loyalty_tx_data.append((
            f"ltx-{w_idx:02d}", ACCOUNT_ID, f"wal-{w_idx:02d}", agr_id, "CREDIT_SURGERY", "Surgical Order Settlement",
            500, pts, f"Crédito por faturamento de implantes na ordem #so-order-{w_idx:02d}", f"so-order-{w_idx:02d}", now_iso
        ))
    wallets_data.append((
        "wal-cnt-01", ACCOUNT_ID, "cnt-01", "Dr. Roberto Martins", 6800, 12000,
        "GOLD", 68, now_iso, now_iso
    ))
    cur.executemany("""
        INSERT OR REPLACE INTO kp_loyalty_wallets (id, account_id, partner_id, partner_name, points_balance, lifetime_points, current_tier, implants_billed_total, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, wallets_data)
    cur.executemany("""
        INSERT OR REPLACE INTO kp_loyalty_transactions (id, account_id, wallet_id, partner_id, transaction_type, event_origin, points, balance_after, description, reference_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, loyalty_tx_data)

    rewards_catalog_data = [
        ("rew-01", ACCOUNT_ID, "Kit Brocas Cirúrgicas Guiadas Diamantadas", "INSTRUMENTAL", 2500, 750.0, 1, now_iso),
        ("rew-02", ACCOUNT_ID, "Inscrição Gratuita Congresso Internacional de Implantodontia", "EDUCACAO", 5000, 1800.0, 1, now_iso),
        ("rew-03", ACCOUNT_ID, "Voucher de Enxerto Ósseo Bovino 5g", "BIOMATERIAL", 3500, 1200.0, 1, now_iso),
        ("rew-04", ACCOUNT_ID, "Passagem Aérea e Hospedagem para Imersão Digital Revnault", "VIP_TRAVEL", 15000, 5000.0, 1, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO kp_loyalty_rewards_catalog (id, account_id, name, reward_type, points_cost, monetary_value_equivalent, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, rewards_catalog_data)

    predictive_scores_data = []
    health_scores_data = []
    for p_idx in range(1, 11):
        agr_id = f"agr-{p_idx:02d}"
        partner_name = agreements_data[p_idx - 1][2]
        predictive_scores_data.append((
            f"sok-{p_idx:02d}", ACCOUNT_ID, agr_id, 82.5 + p_idx, 0, 74.0 + p_idx, 28, 1 if p_idx % 3 == 0 else 0,
            "Giro saudável de implantes; programar reposição preventiva do diâmetro 3.75mm.", f"deal-{p_idx:02d}", now_iso
        ))
        hsc = 85.0 + (p_idx % 12)
        health_scores_data.append((
            f"hsc-{p_idx:02d}", ACCOUNT_ID, agr_id, partner_name, 90.0, 85.0, 88.0, 84.0, hsc,
            "PARCEIRO_ESTRATEGICO" if hsc >= 88 else "PARCEIRO_ATIVO", None, f"DENTGO-VIP-{p_idx:02d}", 1, 1,
            "Parceria sólida em plena conformidade ANVISA e comissionamento equilibrado.", now_iso
        ))
    health_scores_data.append((
        "hsc-cnt-01", ACCOUNT_ID, "cnt-01", "Dr. Roberto Martins", 92.0, 88.0, 90.0, 86.0, 89.0,
        "PARCEIRO_ESTRATEGICO", None, "DENTGO-VIP-CNT01", 1, 1,
        "Parceria de alta performance e fidelidade plena.", now_iso
    ))
    cur.executemany("""
        INSERT OR REPLACE INTO kp_predictive_inventory_scores (
            id, account_id, agreement_id, sok_score, is_idle, pr_score, current_stock, replenishment_needed, recommendation, deal_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, predictive_scores_data)
    cur.executemany("""
        INSERT OR REPLACE INTO kp_surgical_health_scores (
            id, account_id, partner_id, partner_name, f_cirurgica, g_consignado, s_atendimento, e_canal,
            hsc_score, classification, rescue_task_id, dentgo_voucher_code, upsell_eligible, mgm_eligible, recommendation, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, health_scores_data)

    # 13. DENTGO EXPRESS OPERATION (6 Hubs, Inventory, Orders, Splits, FEFO Flash Deals)
    hubs_data = [
        ("hub-sp-moema", ACCOUNT_ID, "DENTGO Hub Express São Paulo Moema", "44.123.456/0001-01", -23.6015, -46.6658, 25.0, "24h", 1, now_iso),
        ("hub-curitiba-batel", ACCOUNT_ID, "DENTGO Hub Express Curitiba Batel", "44.123.456/0002-02", -25.4395, -49.2882, 25.0, "24h", 1, now_iso),
        ("hub-recife-bv", ACCOUNT_ID, "DENTGO Hub Express Recife Boa Viagem", "44.123.456/0003-03", -8.1189, -34.9031, 20.0, "24h", 1, now_iso),
        ("hub-miami-brickell", ACCOUNT_ID, "DENTGO Express Hub Miami Brickell", "55.987.654/0001-99", 25.7617, -80.1918, 30.0, "24h", 1, now_iso),
        ("hub-lisboa-av", ACCOUNT_ID, "DENTGO Hub Express Lisboa Avenida", "50.111.222/0001-88", 38.7223, -9.1393, 25.0, "24h", 1, now_iso),
        ("hub-santiago-condes", ACCOUNT_ID, "DENTGO Hub Express Santiago Las Condes", "76.543.210-K", -33.4121, -70.5822, 20.0, "24h", 1, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO dentgo_hubs (id, account_id, name, cnpj, latitude, longitude, coverage_radius_km, on_duty_schedule, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, hubs_data)

    hub_inv_data = []
    fefo_deals_data = []
    fefo_reservations_data = []

    for h_idx, hub in enumerate(hubs_data, start=1):
        h_id = hub[0]
        h_name = hub[2]
        for p_idx, prod in enumerate(products_data[:4], start=1):
            inv_id = f"dhi-{h_idx:02d}-{p_idx:02d}"
            batch = f"LOT-EXP-2026-{h_idx:02d}{p_idx:02d}"
            exp_date = (now + timedelta(days=180 + (p_idx * 15))).strftime("%Y-%m-%d")
            qty = 45 + (p_idx * 10)
            u_price = prod[10]

            hub_inv_data.append((
                inv_id, h_id, ACCOUNT_ID, prod[0], prod[3], prod[5], batch, qty, u_price, exp_date, now_iso, "AVAILABLE"
            ))

            # FEFO Flash Deal para o produto
            fefo_id = f"fefo-flash-{h_idx:02d}-{p_idx:02d}"
            disc_pct = 30.0
            flash_price = round(u_price * (1 - (disc_pct / 100.0)), 2)
            fefo_deals_data.append((
                fefo_id, ACCOUNT_ID, h_id, h_name, inv_id, prod[0], prod[3], batch, qty, qty - 5,
                u_price, disc_pct, flash_price, exp_date, 6 + p_idx, 15, "ACTIVE",
                f"https://revnaut.vpsconexao.org/#/dentgo?flash_deal={fefo_id}", now_iso
            ))

            fefo_reservations_data.append((
                f"fefo-res-{h_idx:02d}-{p_idx:02d}", ACCOUNT_ID, fefo_id, h_idx, f"Dr. Cirurgião Hub {h_idx}",
                f"CRO-SP-120{h_idx:02d}", 5, round(flash_price * 5, 2), "RESERVED", now_iso
            ))

    hub_inv_data.extend([
        ("dhi-sp-moema-3511", "hub-sp-moema", ACCOUNT_ID, "IMP-CM-3511", "Kit Implante Cone Morse Emerge", "ANVISA-1034567001", "LOT-EXP-2026-3511", 50, 289.9, "2028-10-19", now_iso, "AVAILABLE"),
        ("dhi-sp-moema-37511", "hub-sp-moema", ACCOUNT_ID, "IMP-CM-37511", "Implante Cone Morse Helix 3.75x11.5mm", "ANVISA-1034567001", "LOT-EXP-2026-37511", 50, 420.0, "2028-10-19", now_iso, "AVAILABLE"),
        ("dhi-sp-moema-4311", "hub-sp-moema", ACCOUNT_ID, "IMP-CM-4311", "Implante Cone Morse Helix 4.3x11.5mm", "ANVISA-1034567001", "LOT-EXP-2026-4311", 50, 450.0, "2028-10-19", now_iso, "AVAILABLE"),
        ("dhi-sp-moema-3513", "hub-sp-moema", ACCOUNT_ID, "IMP-CM-3513", "Implante Cone Morse Helix 3.5x13mm", "ANVISA-1034567001", "LOTE-1122", 50, 430.0, "2028-10-19", now_iso, "AVAILABLE"),
    ])

    cur.executemany("""
        INSERT OR REPLACE INTO dentgo_hub_inventory (
            id, hub_id, account_id, product_id, product_name, anvisa_reg, batch_number,
            quantity_available, unit_price, sterilization_expiry_date, created_at, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, hub_inv_data)

    cur.executemany("""
        INSERT OR REPLACE INTO fefo_flash_deals (
            id, account_id, hub_id, hub_name, inventory_id, product_id, product_name, batch_number,
            original_quantity, available_quantity, original_unit_price, discount_percentage, flash_unit_price,
            sterilization_expiry_date, months_to_expire, target_surgeons_count, status, checkout_one_click_url, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, fefo_deals_data)

    cur.executemany("""
        INSERT OR REPLACE INTO fefo_flash_deal_reservations (
            id, account_id, deal_id, contact_id, surgeon_name, surgeon_cro_uf, quantity_reserved, total_amount, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, fefo_reservations_data)

    # DENTGO Orders across all dispatch stages
    dentgo_stages = ["CREATED", "PICKING_BIPADO", "SEALED_READY", "COURIER_ASSIGNED", "IN_TRANSIT_LIVE", "DELIVERED_VERIFIED"]
    orders_data = []
    splits_data = []

    for o_idx in range(1, 13):
        ord_id = f"ord-dentgo-{o_idx:02d}"
        hub_id = hubs_data[(o_idx - 1) % len(hubs_data)][0]
        o_status = dentgo_stages[(o_idx - 1) % len(dentgo_stages)]
        pin = f"{1000 + (o_idx * 73) % 9000}"
        seal = f"LACRE-TERM-{o_idx:04d}"
        items = [{"product_id": "prd-cm-375", "name": "Implante Cone Morse Acqua 3.75x11.5mm", "qty": 3, "unit_price": 420.0}]
        subtotal = 1260.0
        urgency = 45.0
        total = subtotal + urgency

        orders_data.append((
            ord_id, ACCOUNT_ID, hub_id, f"CRO-SP-120{o_idx:02d}", 1, "Av. Ibirapuera, 2040 - Bloco B - Moema, São Paulo",
            -23.6020, -46.6660, 4.2, 35, json.dumps(items), subtotal, urgency, total, o_status,
            f"courier-{((o_idx - 1) % 4) + 1:02d}", seal, pin,
            f"pod/delivery_{ord_id}.jpg" if o_status == "DELIVERED_VERIFIED" else None,
            "Dr. Roberto Martins" if o_status == "DELIVERED_VERIFIED" else None,
            now_iso if o_status == "DELIVERED_VERIFIED" else None, now_iso
        ))

        splits_data.append((
            f"split-{o_idx:02d}", ACCOUNT_ID, ord_id, total, subtotal, urgency, 15.0,
            round(subtotal * 0.15, 2), urgency, round(subtotal * 0.85, 2), "PIX_INSTANTANEO",
            f"agr-{((o_idx - 1) % 10) + 1:02d}", "SETTLED" if o_status == "DELIVERED_VERIFIED" else "PENDING", now_iso
        ))

    cur.executemany("""
        INSERT OR REPLACE INTO dentgo_orders (
            id, account_id, hub_id, customer_cro_uf, cro_verified, delivery_address, delivery_lat, delivery_lng,
            distance_km, estimated_eta_minutes, items_json, subtotal, urgency_fee, total_amount, status,
            courier_id, seal_code, delivery_pin, proof_of_delivery_r2_key, recipient_signature_name, delivered_at, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, orders_data)

    cur.executemany("""
        INSERT OR REPLACE INTO dentgo_financial_splits (
            id, account_id, order_id, gross_amount, items_amount, delivery_fee_total, platform_take_rate_pct,
            platform_fee_amount, courier_net_payout, seller_net_payout, payment_method, agreement_id, settlement_status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, splits_data)

    # 14. OMNICHANNEL, WHATSAPP, CHAT & CONVERSATIONS
    whatsapp_instances_data = [
        ("inst-wa-sp", ACCOUNT_ID, "evolution_sp_moema", "usr-field-ricardo", "http://evolution-shard-01:8080", "+55 11 99999-0002", "CONNECTED", "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", now_iso, now_iso),
        ("inst-wa-miami", ACCOUNT_ID, "evolution_miami_fl", "usr-field-fl", "http://evolution-shard-02:8080", "+1 305 555-0103", "CONNECTED", "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", now_iso, now_iso),
        ("inst-wa-lisboa", ACCOUNT_ID, "evolution_lisboa_eu", "usr-field-iberia", "http://evolution-shard-03:8080", "+351 919 876 543", "CONNECTED", "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", now_iso, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO whatsapp_instances (id, account_id, instance_name, consultant_user_id, shard_node_url, phone_number, status, qr_code_base64, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, whatsapp_instances_data)

    conv_data = []
    msg_data = []
    omni_msg_data = []

    for c_idx in range(1, 11):
        c_id = f"conv-{c_idx:02d}"
        c_name = names_pool[c_idx - 1]
        conv_data.append((
            c_id, ACCOUNT_ID, c_name, f"Clínica {c_name.split()[-1]}", "whatsapp",
            1 if c_idx % 3 == 0 else 0, now_iso, "usr-director-br", "usr-field-ricardo",
            "usr-inside-camila", "team-campo-sp", "bu-latam-br"
        ))

        msg_data.append((
            c_idx * 2 - 1, c_id, "consultant",
            f"Olá {c_name}, sua maleta cirúrgica consignada está com o lacre verificado e pronta para a cirurgia de amanhã.", now_iso
        ))
        msg_data.append((
            c_idx * 2, c_id, "client",
            f"Excelente! Já recebemos e a tomografia 3D está no sistema. Obrigado!", now_iso
        ))

        omni_msg_data.append((
            f"omni-msg-{c_idx:02d}", ACCOUNT_ID, "evolution_sp_moema", f"55119999900{c_idx:02d}@s.whatsapp.net",
            f"+55 11 99999-00{c_idx:02d}", "chat", f"Confirmado pedido cirúrgico para {c_name}", None, 0,
            f"https://revnaut.vpsconexao.org/#/video_sos?room=sos-deal-01", now_iso
        ))

    cur.executemany("""
        INSERT OR REPLACE INTO conversations (id, account_id, contact_name, company, channel, unread, updated_at, owner_id, field_owner_id, inside_owner_id, team_id, business_unit_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, conv_data)
    cur.executemany("INSERT OR REPLACE INTO messages (id, conversation_id, sender, text, created_at) VALUES (?, ?, ?, ?, ?)", msg_data)
    cur.executemany("""
        INSERT OR REPLACE INTO omnichannel_messages (id, account_id, instance_name, remote_jid, sender_phone, message_type, content, media_r2_key, from_me, sos_call_link, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, omni_msg_data)

    # 15. CAMPAIGNS & MARKETING (Campaigns, Landing Pages, Submissions, Referrals)
    campaigns_data = [
        ("camp-01", ACCOUNT_ID, "Imersão Fluxo Digital Cirurgia Guiada SP", "Meta Ads", "facebook", "cpc", "imersao_guiada_sp", 15000.0, 11400.0, 68000.0, 142, 18, "ACTIVE", now_iso),
        ("camp-02", ACCOUNT_ID, "KeyPartners Consignação Sem Burocracia Florida", "Google Search", "google", "cpc", "keypartners_florida", 22000.0, 18500.0, 112000.0, 89, 14, "ACTIVE", now_iso),
        ("camp-03", ACCOUNT_ID, "Congresso Ibérico Reabilitação Oral Lisboa", "LinkedIn Ads", "linkedin", "sponsored", "congresso_lisboa_2026", 8000.0, 7200.0, 39000.0, 64, 8, "ACTIVE", now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO campaigns (id, account_id, name, channel, utm_source, utm_medium, utm_campaign, budget, spend, revenue, leads_count, deals_count, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, campaigns_data)

    lps_data = [
        ("lp-imersao-digital", ACCOUNT_ID, "imersao-fluxo-digital", "Imersão em Fluxo Digital e Cirurgia Guiada Revnault", "imersao_fluxo_digital",
         "<div><h1>Imersão em Cirurgia Guiada</h1><p>Aprenda com cirurgiões mestres o fluxo completo de implantes Cone Morse.</p></div>",
         "h1 { color: #0284c7; }", json.dumps([{"type": "text", "content": "Imersão"}]), "CRO-SP-12001", "Dr. Roberto Martins",
         "https://cdn.revnaut.io/landing/imersao-fluxo-digital.html", 1, now_iso, now_iso),
        ("lp-keypartners-consignacao", ACCOUNT_ID, "keypartners-consignacao", "Programa KeyPartners — Maletas Cirúrgicas em Consignação", "keypartners_consignacao",
         "<div><h1>Consignação Cirúrgica Inteligente</h1><p>Estoque zero em sua clínica com entrega expressa DENTGO 45 minutos.</p></div>",
         "h1 { color: #0f172a; }", json.dumps([{"type": "text", "content": "KeyPartners"}]), "CRO-SP-12001", "Dr. Roberto Martins",
         "https://cdn.revnaut.io/landing/keypartners-consignacao.html", 1, now_iso, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO landing_pages (id, tenant_id, slug, title, template_type, gjs_html, gjs_css, gjs_components_json, cfo_responsible_cro, cfo_responsible_name, published_r2_url, is_published, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, lps_data)

    lp_subs_data = [
        (1, "lp-imersao-digital", ACCOUNT_ID, "Dr. Marcelo Fagundes", "marcelo.fagundes@clinica.com.br", "+55 11 97777-1111", "12004", "CRO-SP-12004", "Implantodontia", "facebook", "cpc", "imersao_guiada_sp", "anuncio_feed", "cirurgia_guiada", 4, now_iso),
        (2, "lp-keypartners-consignacao", ACCOUNT_ID, "Dra. Juliana Prado", "juliana.prado@clinica.com.br", "+55 11 97777-2222", "12005", "CRO-SP-12005", "Bucomaxilofacial", "google", "cpc", "keypartners_florida", "anuncio_topo", "maleta_consignada", 5, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO landing_page_submissions (id, landing_page_id, tenant_id, name, email, phone, cro, cro_uf, specialty, utm_source, utm_medium, utm_campaign, utm_content, utm_term, contact_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, lp_subs_data)

    referral_links_data = [
        ("ref-link-01", ACCOUNT_ID, "agr-01", "Dr. Roberto Martins", "CRO-SP-12001", "MARTINS-VIP", "https://revnaut.vpsconexao.org/r/MARTINS-VIP", now_iso),
        ("ref-link-02", ACCOUNT_ID, "agr-04", "Dr. Robert Vance", "LIC-FL-12004", "VANCE-FL", "https://revnaut.vpsconexao.org/r/VANCE-FL", now_iso),
        ("ref-link-03", ACCOUNT_ID, "agr-07", "Prof. Dr. António Simões", "LIC-11-12007", "SIMOES-EU", "https://revnaut.vpsconexao.org/r/SIMOES-EU", now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO referral_links (id, account_id, referrer_id, referrer_name, referrer_cro_uf, referral_code, referral_url, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, referral_links_data)

    referral_conversions_data = [
        ("ref-conv-01", ACCOUNT_ID, "ref-link-01", "agr-01", 12, "Dr. Rodrigo Zanin", "CRO-PR-12012", "lead-ref-01", 30, "MGM_INDICACAO", "deal-12", "QUALIFIED", 1500.0, 500.0, now_iso, now_iso),
        ("ref-conv-02", ACCOUNT_ID, "ref-link-02", "agr-04", 25, "Dra. Jennifer Scott", "LIC-FL-12025", "lead-ref-02", 30, "MGM_INDICACAO", "deal-25", "QUALIFIED", 2000.0, 750.0, now_iso, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO referral_conversions (id, account_id, referral_link_id, referrer_id, referred_contact_id, referred_name, referred_cro_uf, lead_id, lead_score_boost, tags, first_deal_id, status, referrer_bonus_amount, referred_bonus_amount, created_at, qualified_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, referral_conversions_data)

    # 16. TASKS & TICKETS (Suporte Clínico & Garantias ANVISA)
    tasks_data = [
        ("task-01", ACCOUNT_ID, "Visita de reposição preventiva de maleta Dr. Roberto Martins", (now + timedelta(days=2)).strftime("%Y-%m-%d"), "usr-field-ricardo", "alta", 0, now_iso),
        ("task-02", ACCOUNT_ID, "Auditoria de rastreabilidade ANVISA lote LOTE-2026-001", (now + timedelta(days=3)).strftime("%Y-%m-%d"), "usr-log-marcos", "alta", 0, now_iso),
        ("task-03", ACCOUNT_ID, "Emissão de DANFE e XML de liquidação pós-operatória", (now + timedelta(days=1)).strftime("%Y-%m-%d"), "usr-inside-camila", "media", 1, now_iso),
        ("task-04", ACCOUNT_ID, "Apresentação de estudo tomográfico 3D para comitê clínico", (now + timedelta(days=4)).strftime("%Y-%m-%d"), "usr-support-juliana", "media", 0, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO tasks (id, account_id, title, due_date, assignee, priority, completed, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, tasks_data)

    tickets_data = [
        ("t-01", ACCOUNT_ID, "Solicitação de Troca Técnica em Garantia (Perda de Estabilidade Primária)", "Dr. Roberto Martins", "alta", "em_atendimento", "GARANTIA_CLINICA", now_iso, "https://revnaut.vpsconexao.org/#/video_sos?room=sos-t-01", "+55 11 98888-0001", "CRO-SP-12001", "ord-dentgo-01", "Implante 3.75x11.5mm apresentou torque inferior a 25 Ncm em osso tipo IV. Cirurgião solicita substituição imediata por Grand Morse 4.3x13mm."),
        ("t-02", ACCOUNT_ID, "Dúvida Cirúrgica: Sequência de Fresagem para Osso Tipo D1", "Dra. Camila Nogueira", "media", "resolvido", "SUPORTE_CIRURGICO", now_iso, "https://revnaut.vpsconexao.org/#/video_sos?room=sos-t-02", "+55 41 98888-0002", "CRO-PR-12002", "ord-dentgo-02", "Alinhamento com suporte clínico Revnault sobre uso de broca counterbore."),
        ("t-03", ACCOUNT_ID, "Emergência de Sala: Falta de Componente Protético Ti-Base", "Dr. Fernando Sato", "urgente", "aberto", "EMERGENCIA_SALA", now_iso, "https://revnaut.vpsconexao.org/#/video_sos?room=sos-t-03", "+55 11 99999-0003", "CRO-PE-12003", "ord-dentgo-03", "Acionamento de DENTGO Express 45 min para entrega de Ti-Base."),
        ("t-04", ACCOUNT_ID, "RMA / Notificação de Tecnovigilância ANVISA", "Prof. Dr. António Simões", "baixa", "aberto", "ANVISA_RMA", now_iso, "https://revnaut.vpsconexao.org/#/video_sos?room=sos-t-04", "+351 912 345 678", "LIC-11-12007", "ord-dentgo-04", "Envio de componente explantado para ensaio de fadiga metalográfica."),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO tickets (id, account_id, title, customer_name, priority, status, category, created_at, livekit_room_url, customer_phone, cro_uf, dentgo_order_id, clinical_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tickets_data)

    rma_claims_data = [
        ("rma-01", ACCOUNT_ID, "t-01", "agr-01", "Dr. Roberto Martins", "CRO-SP-12001", "PAC-ANON-088", "prd-cm-375", "Implante Cone Morse Acqua 3.75x11.5mm", "LOT-EXP-2026-0101", "SN-IMP-0001", "46", 20, (now - timedelta(days=15)).strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d"), "FALHA_OSSEOINTEGRACAO", "imaging/rma_01_radiograph.dcm", "ANALYSIS", 1, "ord-dentgo-01", 0, "Substituição imediata realizada via DENTGO Express.", now_iso, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO anvisa_rma_claims (
            id, account_id, ticket_id, agreement_id, surgeon_name, surgeon_cro_uf, patient_identifier,
            product_id, product_name, batch_number, serial_number, fdi_tooth_region, insertion_torque_ncm,
            surgery_date, explant_date, failure_reason, radiograph_r2_key, status, warranty_approved,
            replacement_order_id, quarantine_triggered, notes, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rma_claims_data)

    batch_quarantines_data = [
        ("quar-01", ACCOUNT_ID, "LOT-EXP-2026-9999", "prd-cm-375", 150, 3, 2.0, "ACTIVE", "Taxa de falha preliminar atingiu limiar de investigação preventiva", now_iso, None),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO anvisa_batch_quarantines (id, account_id, batch_number, product_id, total_distributed, total_failures, failure_rate_percent, status, reason, blocked_at, unblocked_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, batch_quarantines_data)

    postop_care_data = [
        ("postop-01", ACCOUNT_ID, "Paciente João Silveira", "+55 11 98765-4321", "Dr. Roberto Martins", "+55 11 98888-0001", "Reabilitação Protocolo Inferior", (now - timedelta(days=2)).strftime("%Y-%m-%d"), "EM_ACOMPANHAMENTO", json.dumps([
            {"code": "24h", "title": "Check-in Pós-Op 24h", "target_date": (now - timedelta(days=1)).strftime("%Y-%m-%d"), "status": "COMPLETED", "template_message": "Olá! Como estão as primeiras 24h pós-cirurgia?"},
            {"code": "48h", "title": "Check-in Pós-Op 48h", "target_date": now.strftime("%Y-%m-%d"), "status": "SENT", "template_message": "Lembrete de medicação e gelo local 48h."},
            {"code": "72h", "title": "Check-in Pós-Op 72h", "target_date": (now + timedelta(days=1)).strftime("%Y-%m-%d"), "status": "SCHEDULED", "template_message": "Acompanhamento 72h: regressão do edema."},
            {"code": "7d", "title": "Remoção de Sutura 7d", "target_date": (now + timedelta(days=5)).strftime("%Y-%m-%d"), "status": "PENDING", "template_message": "Agende seu retorno de 7 dias com o cirurgião."}
        ]), "t-01", "Paciente relatou analgesia controlada e cicatrização inicial sem edema excessivo.", now_iso, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO postop_patient_care_schedules (id, account_id, patient_name, patient_phone, surgeon_name, surgeon_phone, procedure_name, surgery_date, status, milestones_json, alert_ticket_id, last_interaction_notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, postop_care_data)

    patient_reactivations_data = [
        ("react-01", ACCOUNT_ID, "Paciente Mariana Fontes", "+55 11 99111-2222", "Dr. Roberto Martins", "Manutenção e Profilaxia Semestral", (now - timedelta(days=180)).strftime("%Y-%m-%d"), 180, now.strftime("%Y-%m-%d"), "https://cal.com/revnault/retorno-dr-martins", "DISPATCHED", now_iso, now_iso, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO patient_reactivation_schedules (id, account_id, patient_name, patient_phone, surgeon_name, procedure_name, surgery_date, milestone_days, scheduled_dispatch_date, calcom_booking_link, status, message_dispatched_at, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, patient_reactivations_data)

    calcom_bookings_data = [
        ("cal-01", ACCOUNT_ID, "cal-uid-1001", "react-01", "Paciente Mariana Fontes", "mariana.fontes@email.com", "+55 11 99111-2222", "Dr. Roberto Martins", "martins@revnault-clients.org", "Consulta de Retorno e Manutenção Implante", now_iso, (now + timedelta(hours=1)).isoformat(), "https://meet.revnaut.io/retorno-1001", 1, "deal-01", "task-01", "ACCEPTED", json.dumps({"source": "calcom"}), now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO calcom_bookings (id, account_id, calcom_booking_uid, schedule_id, patient_name, patient_email, patient_phone, host_name, host_email, event_type_title, start_time, end_time, meeting_url, is_online, deal_id, task_id, status, raw_payload, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, calcom_bookings_data)

    clinical_margins_data = [
        ("cpm-01", ACCOUNT_ID, "inst-01", "so-order-01", "Reabilitação Protocolo All-on-4 Superior", "PAC-DEMO-01", 24000.0, 4200.0, 3800.0, 5000.0, 3.5, 350.0, 1225.0, 8.0, 1920.0, 7855.0, 32.7, 0, "Margem excelente; manter sequência cirúrgica padrão.", now_iso),
        ("cpm-clinic-sp-01", ACCOUNT_ID, "clinic-sp-01", "so-order-01", "Reabilitação Protocolo Clinic SP 01", "PAC-DEMO-SP01", 28000.0, 4500.0, 3900.0, 5500.0, 4.0, 350.0, 1400.0, 8.0, 2240.0, 10460.0, 37.3, 0, "Margem excelente; manter sequência cirúrgica padrão.", now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO clinical_procedure_margins (id, account_id, clinic_id, surgery_order_id, procedure_name, patient_identifier, gross_revenue, supplies_cost, lab_cost, surgeon_fee, chair_hours, chair_hour_cost, total_chair_cost, tax_rate_percent, tax_amount, net_margin_value, net_margin_percent, is_low_margin, recommendation, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, clinical_margins_data)

    imaging_studies_data = [
        ("study-demo-01", ACCOUNT_ID, "Paciente Demonstração Cone Beam", "ANON-PAC-DEMO01", "deal-01", "t-01", "DICOM_CBCT", "orthanc-demo-01", "imaging/0f14ffff/cone_beam_mandibula_demo.dcm", "cone_beam_mandibula_demo.dcm", 45219800, 360, "MANDIBULA", "D1_DENSO", "46", 1, now_iso),
        ("study-demo-02", ACCOUNT_ID, "Paciente Maxila Atófica Zigoma", "ANON-PAC-DEMO02", "deal-04", "t-02", "DICOM_CBCT", "orthanc-demo-02", "imaging/0f14ffff/cone_beam_maxila_demo.dcm", "cone_beam_maxila_demo.dcm", 52100000, 420, "MAXILA", "D4_POUCO_DENSO", "12,22", 1, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO imaging_studies (id, account_id, patient_name, patient_anonymized_id, deal_id, ticket_id, study_type, orthanc_study_id, r2_storage_key, file_name, file_size_bytes, slice_count, jaw_type, bone_density_estimate, implant_site, is_anonymized, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, imaging_studies_data)

    erp_invoices_data = [
        ("inv-01", ACCOUNT_ID, "TOTVS_PROTHEUS", "REMITTANCE", "agr-01", "5917", "10452", "1", "35261044123456000101550010000104521898765432", "44.123.456/0001-01", "Instituto Branemark São Paulo", 18500.0, "fiscal/xml/inv_01.xml", "fiscal/danfe/inv_01.pdf", "AUTHORIZED", "135260098765432", "wm-job-01", now_iso),
        ("inv-02", ACCOUNT_ID, "TOTVS_PROTHEUS", "SETTLEMENT", "so-order-01", "5113", "10453", "1", "35261044123456000101550010000104531898765433", "44.123.456/0001-01", "Instituto Branemark São Paulo", 4200.0, "fiscal/xml/inv_02.xml", "fiscal/danfe/inv_02.pdf", "AUTHORIZED", "135260098765433", "wm-job-02", now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO erp_fiscal_invoices (id, account_id, erp_type, flow_type, reference_id, cfop, nfe_number, nfe_series, nfe_access_key, recipient_cnpj_cpf, recipient_name, total_invoice_value, xml_r2_key, danfe_pdf_r2_key, status, sefaz_protocol, windmill_job_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, erp_invoices_data)

    sales_targets_data = [
        ("tgt-01", ACCOUNT_ID, "2026-Q4", "bu-latam-br", "team-campo-sp", "usr-field-ricardo", 350000.0, "usr-director-br", "FATURAMENTO_TOTAL", 15.0, now_iso, now_iso),
        ("tgt-02", ACCOUNT_ID, "2026-Q4", "bu-na-usa", "team-field-fl", "usr-field-fl", 450000.0, "usr-director-br", "FATURAMENTO_TOTAL", 20.0, now_iso, now_iso),
        ("tgt-03", ACCOUNT_ID, "2026-Q4", "bu-eu-iberia", "team-field-iberia", "usr-field-iberia", 300000.0, "usr-director-br", "FATURAMENTO_TOTAL", 12.0, now_iso, now_iso),
        ("tgt-04", ACCOUNT_ID, "2026-Q4", "bu-latam-hisp", "team-field-conosur", "usr-field-bue", 220000.0, "usr-director-br", "FATURAMENTO_TOTAL", 18.0, now_iso, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO sales_targets (id, account_id, period, business_unit_id, team_id, user_id, target_amount, created_by, calculation_basis, growth_rate_pct, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sales_targets_data)

    comm_rules_data = [
        ("cr-01", ACCOUNT_ID, "role-field", 5.0, 100.0, 7.5, 1, now_iso),
        ("cr-02", ACCOUNT_ID, "role-inside", 2.5, 100.0, 4.0, 1, now_iso),
        ("cr-03", ACCOUNT_ID, "role-manager", 1.5, 100.0, 2.5, 1, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO commission_rules (id, account_id, role_id, base_percentage, accelerator_threshold_pct, accelerator_percentage, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, comm_rules_data)

    tenant_creds_data = [
        ("tc-r2", ACCOUNT_ID, "cloudflare_r2", "API_KEYS", json.dumps({"account_id": "r2-prod-revnaut", "bucket": "revnaut-media"}), json.dumps({"active": True}), now_iso, now_iso),
        ("tc-documenso", ACCOUNT_ID, "documenso", "BEARER_TOKEN", json.dumps({"api_url": "https://documenso.revnaut.vpsconexao.org/api/v1"}), json.dumps({"active": True}), now_iso, now_iso),
        ("tc-livekit", ACCOUNT_ID, "livekit", "API_KEYS", json.dumps({"url": "wss://livekit.revnaut.vpsconexao.org"}), json.dumps({"active": True}), now_iso, now_iso),
        ("tc-evolution", ACCOUNT_ID, "evolution_api", "API_KEYS", json.dumps({"url": "https://evolution.revnaut.vpsconexao.org"}), json.dumps({"active": True}), now_iso, now_iso),
        ("tc-totvs", ACCOUNT_ID, "totvs_protheus", "BASIC_AUTH", json.dumps({"endpoint": "https://protheus.revnaut.internal:8084"}), json.dumps({"active": True}), now_iso, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO tenant_credentials (id, account_id, service_name, credential_type, encrypted_payload, metadata_json, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, tenant_creds_data)

    # 17. WEBHOOKS & AUTOMATIONS
    webhooks_data = [
        (1, ACCOUNT_ID, "Notificação de Venda Fechada (Slack/Teams)", "https://hooks.revnaut.internal/deals/won", "deal.won", 1, "whsec_revnaut_super_secret_2026", now_iso),
    ]
    cur.executemany("INSERT OR REPLACE INTO webhooks (id, account_id, name, url, event_type, is_active, secret, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", webhooks_data)

    wh_subs_data = [
        ("sub-01", ACCOUNT_ID, "Webhook de Integração ERP Protheus", "https://erp.revnaut.internal/api/webhook", json.dumps(["deal.won", "order.delivered"]), "secret-hmac-2026", 1, 0, 0, now_iso, "encrypted-secret-key-128"),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO webhook_subscriptions (id, account_id, name, target_url, subscribed_events_json, signing_secret, is_active, consecutive_failures, circuit_breaker_tripped, created_at, signing_secret_encrypted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, wh_subs_data)

    cur.execute("""
        INSERT OR REPLACE INTO webhook_logs (id, webhook_id, payload, status_code, response_body, delivered_at)
        VALUES (1, 1, '{"event": "deal.won", "deal_id": "deal-01"}', 200, '{"received": true}', ?)
    """, (now_iso,))

    cur.execute("""
        INSERT OR REPLACE INTO webhook_delivery_logs (id, subscription_id, account_id, event_name, target_url, payload_json, signature_header, status_code, response_body, latency_ms, attempt, success, created_at)
        VALUES ('wdl-01', 'sub-01', '0f14ffff', 'order.delivered', 'https://erp.revnaut.internal/api/webhook', '{"order_id": "ord-dentgo-01"}', 'sha256=123', 200, '{"ok": true}', 42, 1, 1, ?)
    """, (now_iso,))

    automation_flows_data = [
        ("flow-01", ACCOUNT_ID, "Disparo Automático de Mensagem Pós-Cirúrgica WhatsApp", "CX", "order.delivered", "Envia mensagem de orientações pós-operatórias para o cirurgião e paciente", 1, 128, now_iso, now_iso),
        ("flow-02", ACCOUNT_ID, "Alerta de Reposição Preventiva de Maleta Consignada", "KEYPARTNERS", "stock.low", "Notifica consultor externo quando estoque da maleta fica abaixo de 30%", 1, 45, now_iso, now_iso),
        ("flow-03", ACCOUNT_ID, "Bloqueio Preventivo de Lote em Tecnovigilância ANVISA", "COMPLIANCE", "rma.claim_created", "Move lote cirúrgico para quarentena caso ocorram 2 falhas consecutivas", 1, 8, now_iso, now_iso),
        ("flow-04", ACCOUNT_ID, "Roteamento Inteligente de Entrega Same-Day DENTGO", "LOGISTICA", "order.created", "Direciona pedido para o Hub Express mais próximo por geolocalização", 1, 312, now_iso, now_iso),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO automation_flows (id, account_id, name, category, trigger_event, action_description, is_active, execution_count, last_run_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, automation_flows_data)

    cur.execute("""
        INSERT OR REPLACE INTO automation_logs (id, account_id, flow_id, trigger_payload, result_summary, status, executed_at)
        VALUES (1, '0f14ffff', 'flow-01', '{"order_id": "ord-dentgo-01"}', 'Mensagem enviada com sucesso ao cirurgião', 'SUCCESS', ?)
    """, (now_iso,))

    cur.execute("""
        INSERT OR REPLACE INTO integration_outbox (id, account_id, integration_type, idempotency_key, payload, status, attempts, last_error, response_body, created_at, updated_at)
        VALUES ('outbox-01', '0f14ffff', 'TOTVS_SA1', 'idemp-cust-01', '{"customer_id": "cust-01"}', 'sent', 1, NULL, '{"protheus_status": "synced"}', ?, ?)
    """, (now_iso, now_iso))

    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON;")

    # Coleta contagem de linhas de todas as 69 tabelas
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
    tables = [r[0] for r in cur.fetchall()]
    table_counts = {}
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t};")
        cnt = cur.fetchone()[0]
        table_counts[t] = cnt

    conn.close()
    return table_counts


def seed_all(db_path: Path | str | None = None, clean_reset: bool = False) -> Dict[str, int]:
    """Alias canônico para execução completa do seed multinacional enterprise."""
    return seed_multinational_enterprise(db_path=db_path, clean_reset=clean_reset)



if __name__ == "__main__":
    clean_flag = "--clean" in sys.argv or "-c" in sys.argv
    db_file = None
    for arg in sys.argv[1:]:
        if not arg.startswith("-"):
            db_file = arg
            break

    print(f"Iniciando Seed Multinacional Enterprise em: {db_file or get_db_path()}")
    counts = seed_multinational_enterprise(db_file, clean_reset=True)
    zero_tables = [t for t, c in counts.items() if c == 0]
    print(f"Total de tabelas verificadas: {len(counts)}")
    print(f"Tabelas com dados (>0): {len(counts) - len(zero_tables)}")
    if zero_tables:
        print(f"ATENÇÃO: Tabelas ainda vazias ({len(zero_tables)}): {zero_tables}")
        sys.exit(1)
    else:
        print("SUCESSO: Todas as 69 tabelas foram populadas com sucesso!")
        for t, c in sorted(counts.items()):
            print(f"  - {t}: {c} registros")
