# -*- coding: utf-8 -*-
"""
Motor de Transbordo Automático de Leads Hot (Tier A) & Gatilhos de Receita.
Identifica cirurgiões com alto volume/pontuação ICP e transfere com SLA de 15 min para o Closer territorial.
"""

from __future__ import annotations
import uuid
from typing import Dict, Any, Optional
from src.core.database import get_connection


def find_closer_for_territory(conn, territory_uf: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Localiza deterministicamente o Closer Regional responsável pelo território/UF."""
    cur = conn.cursor()
    uf_upper = (territory_uf or "SP").upper()

    # 1. Procura usuário com perfil de consultor/closer em equipe associada ao estado/UF
    cur.execute("""
        SELECT u.id, u.name, u.team_id, t.name as team_name
        FROM users u
        JOIN teams t ON u.team_id = t.id
        WHERE u.account_id = ? AND u.is_active = 1
        AND (t.name LIKE ? OR t.name LIKE ?)
        LIMIT 1
    """, (account_id, f"%{uf_upper}%", f"%Regional {uf_upper}%"))
    user = cur.fetchone()

    # 2. Se não encontrar equipe com nome do estado, busca qualquer consultor/closer ativo
    if not user:
        cur.execute("""
            SELECT u.id, u.name, u.team_id, COALESCE(t.name, 'Equipe de Vendas') as team_name
            FROM users u
            LEFT JOIN teams t ON u.team_id = t.id
            WHERE u.account_id = ? AND u.is_active = 1 AND u.is_superadmin = 0
            LIMIT 1
        """, (account_id,))
        user = cur.fetchone()

    # 3. Fallback seguro para o Super Admin caso ainda não haja equipes cadastradas
    if not user:
        cur.execute("SELECT id, name, team_id FROM users WHERE is_superadmin = 1 LIMIT 1")
        user = cur.fetchone()

    return {
        "id": user["id"] if user else "usr_closer_default",
        "name": user["name"] if user else "Closer Regional Responsável",
        "team_id": user["team_id"] if user and user["team_id"] else "tm_comercial_geral"
    }


def evaluate_hot_lead_and_overflow(
    contact_id: int, 
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Avalia se o cirurgião atingiu status Hot Lead (Tier A) e executa o transbordo automático:
    1. Localiza o Closer da região pelo estado/CRO_UF.
    2. Cria Deal prioritário no pipeline de Cirurgiões & Venda Direta.
    3. Gera Task com SLA de 15 minutos para primeiro contato.
    4. Grava nota de auditoria e alerta na timeline do contato.
    """
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, name, email, phone, company, score, cro, cro_uf, specialty, monthly_implants_volume, state
                FROM contacts WHERE id = ?
            """, (contact_id,))
            contact = cur.fetchone()

            if not contact:
                return {
                    "is_hot_lead": False,
                    "contact_id": contact_id,
                    "status": "not_found",
                    "message": "Contato não localizado"
                }

            score = contact["score"] or 0
            volume = (contact["monthly_implants_volume"] or "").lower()
            
            # Critério de Tier A (Hot Lead): score >= 80 OU volume >= 30 implantes/mês com score >= 60
            is_high_volume = (
                "> 50" in volume or "50/mês" in volume or "20-50" in volume or "30" in volume or "alto" in volume
            )
            is_hot = (score >= 80) or (is_high_volume and score >= 60)

            if not is_hot:
                return {
                    "is_hot_lead": False,
                    "contact_id": contact_id,
                    "status": "warm_or_nurturing",
                    "message": f"Lead com score {score} e volume '{volume}' ainda não qualifica para Tier A Hot."
                }

            # 1. Localiza o Closer do território
            uf = contact["cro_uf"] or contact["state"] or "SP"
            closer = find_closer_for_territory(conn, uf, account_id)
            closer_id = closer["id"]
            closer_name = closer["name"]
            team_id = closer["team_id"]

            # 2. Cria Deal prioritário
            deal_id = f"deal_hot_{uuid.uuid4().hex[:6]}"
            deal_title = f"Oportunidade Hot Tier A - Dr(a). {contact['name']} ({contact['cro'] or 'CRO ' + uf})"
            deal_value = 65000.0  # Ticket médio estimado de kit cirúrgico e implantes

            cur.execute("""
                INSERT INTO deals (id, account_id, pipeline_id, stage_id, title, value, company, contact_name, priority, owner_id, team_id)
                VALUES (?, ?, 1, 101, ?, ?, ?, ?, 'alta', ?, ?)
            """, (deal_id, account_id, deal_title, deal_value, contact["company"] or f"Clínica {contact['name']}", contact["name"], closer_id, team_id))

            # 3. Cria Task com SLA de 15 minutos
            task_id = f"task_hot_{uuid.uuid4().hex[:6]}"
            task_title = f"⚡ SLA 15min: Contatar Lead Hot Tier A - Dr(a). {contact['name']} ({uf})"
            cur.execute("""
                INSERT INTO tasks (id, account_id, title, due_date, assignee, priority, completed)
                VALUES (?, ?, ?, 'Em 15 minutos (SLA Hot Lead)', ?, 'alta', 0)
            """, (task_id, account_id, task_title, closer_name))

            # 4. Registra na timeline do contato
            cur.execute("""
                INSERT INTO contact_audit_logs (contact_id, author_name, action, new_value, comment)
                VALUES (?, 'Motor de Gatilhos de Receita', 'HOT_LEAD_OVERFLOW_TRANSBORDO', ?, ?)
            """, (
                contact_id,
                f"Atribuído a {closer_name} (SLA 15m)",
                f"Cirurgião classificado como Hot Lead (Score {score}). Deal {deal_id} e Task {task_id} criados com SLA 15min para o território {uf}."
            ))

            return {
                "is_hot_lead": True,
                "contact_id": contact_id,
                "closer_id": closer_id,
                "closer_name": closer_name,
                "team_id": team_id,
                "deal_id": deal_id,
                "task_id": task_id,
                "sla_minutes": 15,
                "status": "transferred",
                "message": f"Lead Hot transferido para o Closer {closer_name} com SLA de 15 minutos."
            }
    finally:
        conn.close()
