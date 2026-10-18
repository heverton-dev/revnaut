# -*- coding: utf-8 -*-
"""
Vertical Slice: Réguas Automatizadas de Acompanhamento Pós-Operatório Clínico B2C (24h / 48h / 72h / 7d)
Monitoramento ativo de sinais de dor, edema, sangramento e adesão medicamentosa pós-cirúrgica.
"""

from __future__ import annotations
import json
import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from src.core.database import get_connection, init_db

CRITICAL_TRIGGERS = [
    "sangramento", "hemorragia", "sangrando", "febre", "dor forte", "dor intensa",
    "dor insuportavel", "dor insuportável", "muita dor", "parafuso soltou", "soltou o parafuso",
    "pus", "secrecao", "secreção", "inchaco", "inchaço", "edema", "edema intenso",
    "formigamento", "parestesia", "dormencia", "dormência", "latejando muito"
]


def start_postop_care_schedule(
    patient_name: str,
    patient_phone: str,
    surgeon_name: str,
    surgeon_phone: str,
    procedure_name: str,
    surgery_date: str,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Inicia régua automatizada pós-operatória de 4 marcos clínicos:
    +24h (Dor/Sangramento), +48h (Edema/Gelo), +72h (Regressão) e +7d (Remoção de Pontos).
    """
    init_db()
    schedule_id = f"posop-{uuid.uuid4().hex[:8]}"

    try:
        s_date = datetime.strptime(surgery_date[:10], "%Y-%m-%d")
    except Exception:
        s_date = datetime.now()

    d_24h = (s_date + timedelta(days=1)).strftime("%Y-%m-%d")
    d_48h = (s_date + timedelta(days=2)).strftime("%Y-%m-%d")
    d_72h = (s_date + timedelta(days=3)).strftime("%Y-%m-%d")
    d_7d = (s_date + timedelta(days=7)).strftime("%Y-%m-%d")

    milestones = [
        {
            "code": "24h",
            "target_date": d_24h,
            "title": "Primeiro Dia: Dor, Sangramento & Medicação",
            "status": "SCHEDULED",
            "template_message": (
                f"Olá {patient_name}, aqui é da equipe do Dr. {surgeon_name}. "
                f"Como você passou a primeira noite após a cirurgia de {procedure_name}? "
                "Está conseguindo tomar a medicação nos horários e aplicando gelo? Nos conte como está se sentindo."
            ),
            "feedback_received": None,
            "evaluated_alert": None
        },
        {
            "code": "48h",
            "target_date": d_48h,
            "title": "Segundo Dia: Pico de Edema & Higiene Bucal",
            "status": "SCHEDULED",
            "template_message": (
                f"Olá {patient_name}! Hoje é comum notar um pico normal de inchaço. "
                "Como está a dor e a mastigação? Lembre-se de não bochechar com força e manter o repouso."
            ),
            "feedback_received": None,
            "evaluated_alert": None
        },
        {
            "code": "72h",
            "target_date": d_72h,
            "title": "Terceiro Dia: Regressão & Conforto",
            "status": "SCHEDULED",
            "template_message": (
                f"Olá {patient_name}, terceiro dia pós-operatório! "
                "O inchaço deve começar a regredir. Alguma dúvida sobre os antibióticos ou desconforto restante?"
            ),
            "feedback_received": None,
            "evaluated_alert": None
        },
        {
            "code": "7d",
            "target_date": d_7d,
            "title": "Sétimo Dia: Remoção de Suturas & Cicatrização",
            "status": "SCHEDULED",
            "template_message": (
                f"Olá {patient_name}! Completamos 7 dias da cirurgia. "
                f"Lembramos da sua consulta agendada para remoção dos pontos e revisão com o Dr. {surgeon_name}."
            ),
            "feedback_received": None,
            "evaluated_alert": None
        }
    ]

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO postop_patient_care_schedules (
                id, account_id, patient_name, patient_phone, surgeon_name,
                surgeon_phone, procedure_name, surgery_date, status, milestones_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
        """, (
            schedule_id, account_id, patient_name, patient_phone, surgeon_name,
            surgeon_phone, procedure_name, surgery_date[:10], json.dumps(milestones)
        ))
        conn.commit()

        cur.execute("SELECT created_at FROM postop_patient_care_schedules WHERE id = ?", (schedule_id,))
        row = cur.fetchone()
        created_at = row[0] if row else "2026-10-18T00:00:00"

        return {
            "id": schedule_id,
            "account_id": account_id,
            "patient_name": patient_name,
            "patient_phone": patient_phone,
            "surgeon_name": surgeon_name,
            "surgeon_phone": surgeon_phone,
            "procedure_name": procedure_name,
            "surgery_date": surgery_date[:10],
            "status": "ACTIVE",
            "milestones": milestones,
            "alert_ticket_id": None,
            "last_interaction_notes": None,
            "created_at": str(created_at)
        }
    finally:
        conn.close()


def process_patient_feedback(
    schedule_id: str,
    feedback_text: str,
    milestone_code: str = "24h",
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Analisa mensagem ou transcrição de áudio do paciente via NLP determinístico.
    Se detectar sinais de dor aguda, febre, sangramento ou deiscência,
    abre imediatamente chamado vermelho (P0 / Prioridade Alta) para o cirurgião.
    """
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, patient_name, patient_phone, surgeon_name, surgeon_phone,
                   procedure_name, status, milestones_json, alert_ticket_id
            FROM postop_patient_care_schedules
            WHERE id = ? AND account_id = ?
        """, (schedule_id, account_id))
        sched = cur.fetchone()
        if not sched:
            raise ValueError(f"Régua pós-operatória {schedule_id} não encontrada.")

        patient_name = sched["patient_name"]
        surgeon_name = sched["surgeon_name"]
        surgeon_phone = sched["surgeon_phone"]
        current_status = sched["status"]
        milestones = json.loads(sched["milestones_json"])

        # Triagem de palavras-chave críticas
        clean_text = feedback_text.lower()
        detected_triggers = []
        for trigger in CRITICAL_TRIGGERS:
            pattern = rf"\b{re.escape(trigger)}\b"
            if re.search(pattern, clean_text):
                detected_triggers.append(trigger)

        is_critical = len(detected_triggers) > 0
        alert_ticket_id = sched["alert_ticket_id"]
        updated_status = current_status

        if is_critical:
            updated_status = "ALERT_TRIGGERED"
            ticket_id = f"tkt-posop-{uuid.uuid4().hex[:8]}"
            triggers_str = ", ".join(detected_triggers)
            title = f"ALERTA VERMELHO PÓS-OP ({milestone_code}): Paciente {patient_name} relata intercorrência ({triggers_str})"

            cur.execute("""
                INSERT INTO tickets (id, account_id, title, customer_name, priority, status, category)
                VALUES (?, ?, ?, ?, 'alta', 'aberto', 'Pós-Operatório Crítico')
            """, (ticket_id, account_id, title, patient_name))

            alert_ticket_id = ticket_id
            patient_msg = (
                f"Atenção: O Dr. {surgeon_name} e a coordenação cirúrgica da clínica receberam seu relato "
                f"em canal prioritário ({triggers_str}). Fique calmo(a), mantenha a compressa se orientado e "
                "nossa equipe entrará em contato com você via chamada nos próximos minutos."
            )
            surgeon_alert_sent = True
        else:
            patient_msg = (
                f"Obrigado pelo retorno, {patient_name}! Ficamos muito felizes que sua recuperação "
                "está dentro do esperado. Continue seguindo o repouso e os horários da medicação."
            )
            surgeon_alert_sent = False
            if milestone_code == "7d":
                updated_status = "COMPLETED"

        # Atualizar milestone correspondente
        for m in milestones:
            if m["code"] == milestone_code:
                m["status"] = "ALERT_DISPATCHED" if is_critical else "FEEDBACK_RECEIVED"
                m["feedback_received"] = feedback_text
                m["evaluated_alert"] = is_critical

        cur.execute("""
            UPDATE postop_patient_care_schedules
            SET status = ?, milestones_json = ?, alert_ticket_id = ?,
                last_interaction_notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND account_id = ?
        """, (
            updated_status, json.dumps(milestones), alert_ticket_id,
            f"Feedback ({milestone_code}): {feedback_text}", schedule_id, account_id
        ))
        conn.commit()

        return {
            "schedule_id": schedule_id,
            "milestone_code": milestone_code,
            "is_critical": is_critical,
            "detected_triggers": detected_triggers,
            "alert_ticket_id": alert_ticket_id,
            "patient_response_message": patient_msg,
            "surgeon_alert_sent": surgeon_alert_sent,
            "updated_status": updated_status
        }
    finally:
        conn.close()


def get_postop_schedule(schedule_id: str, account_id: str = "0f14ffff") -> Optional[Dict[str, Any]]:
    """Consulta detalhes e linha do tempo de uma régua pós-operatória."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, account_id, patient_name, patient_phone, surgeon_name,
                   surgeon_phone, procedure_name, surgery_date, status, milestones_json,
                   alert_ticket_id, last_interaction_notes, created_at
            FROM postop_patient_care_schedules
            WHERE id = ? AND account_id = ?
        """, (schedule_id, account_id))
        r = cur.fetchone()
        if not r:
            return None
        return {
            "id": r["id"],
            "account_id": r["account_id"],
            "patient_name": r["patient_name"],
            "patient_phone": r["patient_phone"],
            "surgeon_name": r["surgeon_name"],
            "surgeon_phone": r["surgeon_phone"],
            "procedure_name": r["procedure_name"],
            "surgery_date": r["surgery_date"],
            "status": r["status"],
            "milestones": json.loads(r["milestones_json"]),
            "alert_ticket_id": r["alert_ticket_id"],
            "last_interaction_notes": r["last_interaction_notes"],
            "created_at": str(r["created_at"])
        }
    finally:
        conn.close()


def list_postop_schedules(
    account_id: str = "0f14ffff",
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lista réguas pós-operatórias ativas ou com alerta disparado."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = "SELECT * FROM postop_patient_care_schedules WHERE account_id = ?"
        params = [account_id]
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC"

        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "account_id": r["account_id"],
                "patient_name": r["patient_name"],
                "patient_phone": r["patient_phone"],
                "surgeon_name": r["surgeon_name"],
                "surgeon_phone": r["surgeon_phone"],
                "procedure_name": r["procedure_name"],
                "surgery_date": r["surgery_date"],
                "status": r["status"],
                "milestones": json.loads(r["milestones_json"]),
                "alert_ticket_id": r["alert_ticket_id"],
                "last_interaction_notes": r["last_interaction_notes"],
                "created_at": str(r["created_at"])
            })
        return result
    finally:
        conn.close()
