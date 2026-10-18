# -*- coding: utf-8 -*-
"""
Vertical Slice: Predictive Inventory & Consignment Intelligence
Implementação dos motores matemáticos de Score de Ociosidade de Kit (SOK) e Ponto de Reposição (PR).
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from src.core.database import get_connection, init_db
from src.features.intelligence.schemas import (
    SokCalculationRequest,
    SokCalculationResponse,
    PrCalculationRequest,
    PrCalculationResponse,
    PredictiveInventoryReportResponse
)


def calculate_kit_idle_score_sok(data: SokCalculationRequest) -> Dict[str, Any]:
    """
    Calcula o Score de Ociosidade de Kit Consignado (SOK):
    SOK = (D_sem_cirurgia / D_limite_contratual) * 0.6 + (V_kit_imobilizado / V_faturamento_medio_mensal) * 0.4

    Quando SOK >= 1.0:
    Sinaliza status IDLE_WARNING e sugere ordem de coleta reversa no DENTGO.
    """
    init_db()

    # Validações de limites e zero division
    limit_days = data.contract_limit_days if data.contract_limit_days > 0 else 30
    monthly_rev = data.avg_monthly_revenue if data.avg_monthly_revenue > 0 else 1.0

    term_days = (data.days_without_surgery / limit_days) * 0.6
    term_val = (data.kit_immobilized_value / monthly_rev) * 0.4
    raw_sok = term_days + term_val
    sok_score = round(raw_sok, 4)

    is_idle = sok_score >= 1.0
    dentgo_reverse_suggested = is_idle
    dentgo_order_id = None

    if is_idle:
        status_code = "IDLE_WARNING"
        recommendation = "Abrir tarefa critica para o consultor externo e sugerir ordem de coleta reversa no DENTGO."
    else:
        status_code = "REGULAR_FLOW"
        recommendation = "Kit em giro regular dentro do limite contratual."

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        cur = conn.cursor()

        # Se kit ocioso, cria ordem de coleta reversa DENTGO caso exista acordo
        if is_idle:
            dentgo_order_id = f"dentgo-rev-{uuid.uuid4().hex[:8]}"

            # Localiza ou inicializa hub para a conta
            cur.execute("SELECT id FROM dentgo_hubs WHERE account_id = ? AND is_active = 1 LIMIT 1", (data.account_id,))
            hub_row = cur.fetchone()
            if hub_row:
                hub_id = hub_row["id"]
            else:
                hub_id = f"hub-dentgo-{uuid.uuid4().hex[:6]}"
                cur.execute("""
                    INSERT OR IGNORE INTO dentgo_hubs (
                        id, account_id, name, cnpj, latitude, longitude
                    ) VALUES (?, ?, 'Hub Central DENTGO', '00.111.222/0001-99', -23.55052, -46.633308)
                """, (hub_id, data.account_id))

            # Busca cro do parceiro se houver
            cur.execute("SELECT partner_cro_uf FROM kp_partner_agreements WHERE id = ?", (data.agreement_id,))
            agr_row = cur.fetchone()
            cro_uf = agr_row["partner_cro_uf"] if (agr_row and agr_row["partner_cro_uf"]) else "CRO-SP-00000"

            cur.execute("""
                INSERT INTO dentgo_orders (
                    id, account_id, hub_id, customer_cro_uf, cro_verified,
                    delivery_address, delivery_lat, delivery_lng, items_json,
                    status, created_at
                ) VALUES (?, ?, ?, ?, 1, 'Consultorio do Parceiro (Coleta Reversa)', -23.55052, -46.633308, '[]', 'REVERSE_PICKUP_REQUESTED', ?)
            """, (dentgo_order_id, data.account_id, hub_id, cro_uf, now_str))

            # Cria tarefa crítica na tabela tasks para o consultor de campo recolher/realocar o kit ocioso
            task_id = f"tsk-sok-{uuid.uuid4().hex[:8]}"
            cur.execute("""
                INSERT INTO tasks (
                    id, account_id, title, due_date, assignee, priority, completed
                ) VALUES (?, ?, ?, ?, 'Consultor Externo Regional', 'alta', 0)
            """, (
                task_id,
                data.account_id,
                f"[SOK {sok_score}] Recolher Kit Consignado Ocioso (Acordo {data.agreement_id})",
                now_str[:10],
            ))

        record_id = f"pred_sok_{uuid.uuid4().hex[:10]}"
        cur.execute("""
            INSERT INTO kp_predictive_inventory_scores (
                id, account_id, agreement_id, sok_score, is_idle, pr_score, current_stock,
                replenishment_needed, recommendation, deal_id, created_at
            ) VALUES (?, ?, ?, ?, ?, 0.0, 0, 0, ?, ?, ?)
        """, (
            record_id,
            data.account_id,
            data.agreement_id,
            sok_score,
            1 if is_idle else 0,
            recommendation,
            dentgo_order_id,
            now_str
        ))
        conn.commit()

        return {
            "agreement_id": data.agreement_id,
            "sok_score": sok_score,
            "is_idle": is_idle,
            "days_without_surgery": data.days_without_surgery,
            "contract_limit_days": limit_days,
            "kit_immobilized_value": data.kit_immobilized_value,
            "avg_monthly_revenue": data.avg_monthly_revenue,
            "status": status_code,
            "recommendation": recommendation,
            "dentgo_reverse_pickup_suggested": dentgo_reverse_suggested,
            "dentgo_order_id": dentgo_order_id,
            "calculated_at": now_str
        }
    finally:
        conn.close()


def calculate_replenishment_point_pr(data: PrCalculationRequest) -> Dict[str, Any]:
    """
    Calcula o Ponto de Reposicao (PR):
    PR = (C_medio_diario * T_entrega_dentgo) + ES

    Quando o estoque atual <= PR:
    Gera Deal automatico no funil de Recompra Ativa e envia mensagem com link de aprovacao em 1 clique via WhatsApp.
    """
    init_db()

    raw_pr = (data.avg_daily_consumption * data.delivery_lead_time_days) + data.safety_stock
    pr_score = round(raw_pr, 2)

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        cur = conn.cursor()

        # Determina saldo líquido em estoque (passado explicitamente ou consultado no kp_custody_ledger)
        if data.current_stock is not None:
            current_stock = data.current_stock
        else:
            cur.execute("""
                SELECT
                    COALESCE(SUM(CASE WHEN movement_type = 'REMESSA' THEN quantity ELSE 0 END), 0) -
                    COALESCE(SUM(CASE WHEN movement_type IN ('CONSUMO_CIRURGICO', 'DEVOLUCAO_INTACTA', 'EXTRAVIO') THEN quantity ELSE 0 END), 0)
                FROM kp_custody_ledger
                WHERE agreement_id = ? AND account_id = ?
            """, (data.agreement_id, data.account_id))
            row = cur.fetchone()
            current_stock = max(0, int(row[0])) if row else 0

        replenishment_needed = current_stock <= pr_score
        deal_id = None
        deal_title = None
        whatsapp_sent = False
        whatsapp_message_id = None
        approval_link = None

        if replenishment_needed:
            cur.execute("SELECT partner_name FROM kp_partner_agreements WHERE id = ?", (data.agreement_id,))
            ag_row = cur.fetchone()
            partner_name = ag_row["partner_name"] if ag_row else "Clinica Parceira"

            if data.trigger_deal:
                deal_id = f"deal-rep-{uuid.uuid4().hex[:8]}"
                deal_title = f"Recompra Ativa Consignado - {partner_name}"
                company_name = partner_name
                contact_name = partner_name
                deal_value = round(max(pr_score * 450.0, 18000.0), 2)

                cur.execute("""
                    INSERT INTO deals (
                        id, account_id, pipeline_id, stage_id, title, value, company, contact_name, priority
                    ) VALUES (?, ?, 1, 101, ?, ?, ?, ?, 'alta')
                """, (deal_id, data.account_id, deal_title, deal_value, company_name, contact_name))

                # Disparo de mensagem no canal de comunicacao WhatsApp com link de 1 clique
                whatsapp_message_id = f"msg_pr_{uuid.uuid4().hex[:8]}"
                approval_link = f"https://dentgo.app.br/orders/quick-approve?deal_id={deal_id}&agreement_id={data.agreement_id}"
                msg_content = (
                    f"Atencao {partner_name}: Seu estoque de implantes atingiu o ponto de reposicao "
                    f"({current_stock} un <= PR {pr_score}). Clique para aprovar o pedido de reposicao imediata: {approval_link}"
                )
                cur.execute("""
                    INSERT INTO omnichannel_messages (
                        id, account_id, instance_name, remote_jid, sender_phone, message_type, content, from_me
                    ) VALUES (?, ?, 'default_instance', 'clinic@c.us', '551199999999', 'text', ?, 1)
                """, (whatsapp_message_id, data.account_id, msg_content))
                whatsapp_sent = True

            recommendation = (
                f"Estoque em nivel critico ({current_stock} un <= PR {pr_score}). "
                "Oportunidade de recompra gerada no funil e notificacao WhatsApp disparada para a clinica."
            )
        else:
            recommendation = f"Estoque dentro dos parametros de seguranca ({current_stock} un > PR {pr_score}). Nenhuma acao necessaria."

        record_id = f"pred_pr_{uuid.uuid4().hex[:10]}"
        cur.execute("""
            INSERT INTO kp_predictive_inventory_scores (
                id, account_id, agreement_id, sok_score, is_idle, pr_score, current_stock,
                replenishment_needed, recommendation, deal_id, created_at
            ) VALUES (?, ?, ?, 0.0, 0, ?, ?, ?, ?, ?, ?)
        """, (
            record_id,
            data.account_id,
            data.agreement_id,
            pr_score,
            current_stock,
            1 if replenishment_needed else 0,
            recommendation,
            deal_id,
            now_str
        ))
        conn.commit()

        return {
            "agreement_id": data.agreement_id,
            "pr_score": pr_score,
            "current_stock": current_stock,
            "replenishment_needed": replenishment_needed,
            "deal_id": deal_id,
            "deal_title": deal_title,
            "whatsapp_sent": whatsapp_sent,
            "whatsapp_message_id": whatsapp_message_id,
            "approval_link": approval_link,
            "recommendation": recommendation,
            "calculated_at": now_str
        }
    finally:
        conn.close()


def get_predictive_inventory_report(agreement_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Gera relatorio consolidado dos ultimos scores preditivos para o acordo consignado."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT partner_name, min_monthly_revenue, max_turnover_days FROM kp_partner_agreements WHERE id = ?", (agreement_id,))
        ag_row = cur.fetchone()
        partner_name = ag_row["partner_name"] if ag_row else "Parceiro"

        cur.execute("""
            SELECT * FROM kp_predictive_inventory_scores
            WHERE agreement_id = ? AND account_id = ?
            ORDER BY created_at DESC LIMIT 10
        """, (agreement_id, account_id))
        scores = [dict(r) for r in cur.fetchall()]

        return {
            "agreement_id": agreement_id,
            "partner_name": partner_name,
            "scores_history": scores,
            "total_records": len(scores)
        }
    finally:
        conn.close()
