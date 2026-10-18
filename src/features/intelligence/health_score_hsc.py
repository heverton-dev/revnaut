# -*- coding: utf-8 -*-
"""
Vertical Slice: Surgical Health Score (HSC) & Anti-Churn Engine
Implementação do motor determinístico de saúde cirúrgica da conta (HSC):
HSC = 0.4 * F_cirurgica + 0.3 * G_consignado + 0.2 * S_atendimento + 0.1 * E_canal
Dispara playbooks de resgate (HSC < 40) com tarefa presencial e voucher DENTGO,
e playbooks de expansão/MGM para contas promotoras (HSC > 75).
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.core.database import get_connection, init_db
from src.core.events import StreamName, default_event_bus
from src.features.intelligence.schemas import (
    HealthScoreCalculateRequest,
    HealthScoreCalculateResponse,
    HealthScoreSummaryResponse
)


def calculate_surgical_health_score(data: HealthScoreCalculateRequest) -> Dict[str, Any]:
    """
    Calcula determinísticamente o Health Score Cirúrgico (HSC) da clínica/parceiro:
    HSC = 0.4 * F_cirurgica + 0.3 * G_consignado + 0.2 * S_atendimento + 0.1 * E_canal
    """
    init_db()

    # 1. Determina F_cirurgica (Frequência cirúrgica)
    if data.f_cirurgica is not None:
        f_val = float(data.f_cirurgica)
    elif data.current_interval_days is not None:
        base_days = data.baseline_interval_days if data.baseline_interval_days > 0 else 7.0
        curr_days = float(data.current_interval_days)
        if curr_days <= base_days:
            f_val = 100.0
        else:
            # Penaliza proporcionalmente desvios no ciclo cirúrgico
            ratio = curr_days / base_days
            f_val = max(0.0, min(100.0, 100.0 - (ratio - 1.0) * 20.0))
    else:
        f_val = 80.0

    # 2. Determina G_consignado (Giro do estoque consignado)
    if data.g_consignado is not None:
        g_val = float(data.g_consignado)
    else:
        g_val = 70.0

    # 3. Determina S_atendimento (Satisfação e ausência de RMAs)
    if data.s_atendimento is not None:
        s_val = float(data.s_atendimento)
    elif data.rma_claims_count is not None and data.rma_claims_count > 0:
        # Cada queixa de RMA penaliza severamente o indicador
        s_val = max(0.0, min(100.0, 100.0 - (data.rma_claims_count * 37.5)))
    else:
        s_val = 90.0

    # 4. Determina E_canal (Engajamento no WhatsApp/canais de atendimento)
    if data.e_canal is not None:
        e_val = float(data.e_canal)
    else:
        e_val = 75.0

    raw_hsc = (0.4 * f_val) + (0.3 * g_val) + (0.2 * s_val) + (0.1 * e_val)
    hsc_score = round(raw_hsc, 2)

    rescue_task_id = None
    dentgo_voucher_code = None
    upsell_eligible = False
    mgm_eligible = False

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # 5. Playbook autônomo por faixa
    if hsc_score < 40.0:
        classification = "CRITICAL_RISK"
        rescue_task_id = f"task-rescue-{uuid.uuid4().hex[:8]}"
        clean_partner_id = "".join(c for c in data.partner_id if c.isalnum()).upper()[:6]
        dentgo_voucher_code = f"DENTGO-EXPRESS-{clean_partner_id}"

        recommendation = (
            f"Risco Critico de Churn (HSC {hsc_score} < 40). "
            "Tarefa de visita presencial urgente gerada para o consultor e voucher de Frete Express Gratis DENTGO emitido."
        )

        conn = get_connection()
        try:
            cur = conn.cursor()
            # Cria tarefa crítica para consultor externo
            task_title = f"Visita presencial urgente de resgate: {data.partner_name} (HSC {hsc_score})"
            cur.execute("""
                INSERT INTO tasks (
                    id, account_id, title, due_date, assignee, priority, completed, created_at
                ) VALUES (?, ?, ?, 'Hoje, 18:00', 'Consultor Externo / CS', 'alta', 0, ?)
            """, (rescue_task_id, data.account_id, task_title, now_str))

            # Notifica a clínica via WhatsApp com o voucher do DENTGO
            wa_msg_id = f"msg_hsc_{uuid.uuid4().hex[:8]}"
            wa_content = (
                f"Ola Dr(a). {data.partner_name}! Preparamos um voucher de Frete Express Gratis no DENTGO "
                f"({dentgo_voucher_code}) para destravar sua proxima cirurgia sem custo de entrega."
            )
            cur.execute("""
                INSERT INTO omnichannel_messages (
                    id, account_id, instance_name, remote_jid, sender_phone, message_type, content, from_me
                ) VALUES (?, ?, 'default_instance', 'clinic@c.us', '551199999999', 'text', ?, 1)
            """, (wa_msg_id, data.account_id, wa_content))
            conn.commit()
        finally:
            conn.close()

        default_event_bus.publish_sync(
            stream=StreamName.GROWTH,
            event_type="growth.hsc_critical",
            account_id=data.account_id,
            payload={
                "partner_id": data.partner_id,
                "partner_name": data.partner_name,
                "hsc_score": hsc_score,
                "classification": classification,
                "rescue_task_id": rescue_task_id,
                "dentgo_voucher_code": dentgo_voucher_code,
            },
        )

    elif hsc_score > 75.0:
        classification = "PROMOTER"
        upsell_eligible = True
        mgm_eligible = True
        recommendation = (
            f"Conta Promotora (HSC {hsc_score} > 75). "
            "Habilitada para upsell de fluxo digital (scanners/kits guiados) e convite ao programa de indicacao MGM."
        )
    else:
        classification = "STABLE"
        recommendation = f"Conta Estavel (HSC {hsc_score}). Manter rotina de acompanhamento pos-operatorio."

    score_id = f"hsc_{uuid.uuid4().hex[:10]}"
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO kp_surgical_health_scores (
                id, account_id, partner_id, partner_name, f_cirurgica, g_consignado,
                s_atendimento, e_canal, hsc_score, classification, rescue_task_id,
                dentgo_voucher_code, upsell_eligible, mgm_eligible, recommendation, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            score_id,
            data.account_id,
            data.partner_id,
            data.partner_name,
            f_val,
            g_val,
            s_val,
            e_val,
            hsc_score,
            classification,
            rescue_task_id,
            dentgo_voucher_code,
            1 if upsell_eligible else 0,
            1 if mgm_eligible else 0,
            recommendation,
            now_str
        ))
        conn.commit()

        return {
            "id": score_id,
            "partner_id": data.partner_id,
            "partner_name": data.partner_name,
            "f_cirurgica": f_val,
            "g_consignado": g_val,
            "s_atendimento": s_val,
            "e_canal": e_val,
            "hsc_score": hsc_score,
            "classification": classification,
            "rescue_task_id": rescue_task_id,
            "dentgo_voucher_code": dentgo_voucher_code,
            "upsell_eligible": upsell_eligible,
            "mgm_eligible": mgm_eligible,
            "recommendation": recommendation,
            "calculated_at": now_str
        }
    finally:
        conn.close()


def get_health_score_history(partner_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Retorna o histórico dos últimos scores HSC do parceiro."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM kp_surgical_health_scores
            WHERE partner_id = ? AND account_id = ?
            ORDER BY created_at DESC LIMIT 20
        """, (partner_id, account_id))
        records = [dict(r) for r in cur.fetchall()]

        return {
            "partner_id": partner_id,
            "total_records": len(records),
            "history": records
        }
    finally:
        conn.close()
