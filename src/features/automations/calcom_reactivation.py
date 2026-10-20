# -*- coding: utf-8 -*-
"""
Vertical Slice: Motor de Agendamento Inteligente Cal.com e
Loop de Reativação Preventiva de Pacientes (6/12/18m).
"""

from __future__ import annotations
import json
import os
import urllib.parse
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.core.database import get_connection, init_db
from src.core.events import EventBus, StreamName
from src.features.communications.livekit_service import generate_room_token


def generate_calcom_booking_link(
    calcom_username: str = "dr-lucas-mendes",
    event_slug: str = "manutencao-peri-implantar",
    patient_name: str = "",
    patient_phone: str = "",
    patient_email: Optional[str] = None,
    base_url: str = "https://cal.com",
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Gera link direto de agendamento em 1 clique do Cal.com pré-preenchendo dados do paciente.
    """
    clean_base = base_url.rstrip("/")
    if "/" in calcom_username and ("cal.com" in calcom_username or "http" in calcom_username):
        url_path = f"{calcom_username.rstrip('/')}/{event_slug}"
    else:
        url_path = f"{clean_base}/{calcom_username}/{event_slug}"

    params: Dict[str, str] = {}
    if patient_name:
        params["name"] = patient_name
    if patient_phone:
        params["phone"] = patient_phone
    if patient_email:
        params["email"] = patient_email
    if metadata:
        for k, v in metadata.items():
            params[f"metadata[{k}]"] = str(v)

    query_str = urllib.parse.urlencode(params)
    return f"{url_path}?{query_str}" if query_str else url_path


def schedule_patient_reactivation(
    patient_name: str,
    patient_phone: str,
    surgeon_name: str,
    procedure_name: str,
    surgery_date: str,
    account_id: str = "0f14ffff",
    calcom_event_slug: str = "manutencao-peri-implantar",
    base_calcom_url: str = "https://cal.com/dr-lucas-mendes",
) -> List[Dict[str, Any]]:
    """
    Registra deterministicamente os 3 marcos de reativação preventiva pós-operatória:
    180 dias (6 meses), 365 dias (12 meses) e 540 dias (18 meses).
    """
    init_db()
    try:
        s_date = datetime.strptime(surgery_date[:10], "%Y-%m-%d")
    except Exception:
        s_date = datetime.now()

    milestone_days_list = [180, 365, 540]
    created_schedules: List[Dict[str, Any]] = []

    conn = get_connection()
    try:
        cur = conn.cursor()
        for m_days in milestone_days_list:
            sched_id = f"reactiv-{uuid.uuid4().hex[:8]}"
            dispatch_date = (s_date + timedelta(days=m_days)).strftime("%Y-%m-%d")

            booking_link = generate_calcom_booking_link(
                calcom_username=base_calcom_url,
                event_slug=calcom_event_slug,
                patient_name=patient_name,
                patient_phone=patient_phone,
                metadata={
                    "milestone": m_days,
                    "procedure": procedure_name,
                    "surgeon": surgeon_name,
                },
            )

            cur.execute("""
                INSERT INTO patient_reactivation_schedules (
                    id, account_id, patient_name, patient_phone, surgeon_name,
                    procedure_name, surgery_date, milestone_days, scheduled_dispatch_date,
                    calcom_booking_link, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
            """, (
                sched_id, account_id, patient_name, patient_phone, surgeon_name,
                procedure_name, s_date.strftime("%Y-%m-%d"), m_days, dispatch_date,
                booking_link,
            ))

            created_schedules.append({
                "id": sched_id,
                "account_id": account_id,
                "patient_name": patient_name,
                "patient_phone": patient_phone,
                "surgeon_name": surgeon_name,
                "procedure_name": procedure_name,
                "surgery_date": s_date.strftime("%Y-%m-%d"),
                "milestone_days": m_days,
                "scheduled_dispatch_date": dispatch_date,
                "calcom_booking_link": booking_link,
                "status": "PENDING",
            })

        conn.commit()
    finally:
        conn.close()

    return created_schedules


def scan_and_dispatch_due_reactivations(
    reference_date: Optional[str] = None,
    account_id: str = "0f14ffff",
) -> Dict[str, Any]:
    """
    Varredura ativa que identifica procedimentos que atingiram a data limite dos marcos
    e dispara mensagem humanizada via WhatsApp (Evolution API / Omnichannel).
    """
    init_db()
    ref_dt = reference_date or datetime.now().strftime("%Y-%m-%d")

    conn = get_connection()
    dispatched_items: List[Dict[str, Any]] = []

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, account_id, patient_name, patient_phone, surgeon_name,
                   procedure_name, surgery_date, milestone_days, scheduled_dispatch_date,
                   calcom_booking_link
            FROM patient_reactivation_schedules
            WHERE account_id = ?
              AND scheduled_dispatch_date <= ?
              AND status = 'PENDING'
            ORDER BY scheduled_dispatch_date ASC
        """, (account_id, ref_dt))

        rows = cur.fetchall()

        for r in rows:
            sched_id = r["id"]
            patient_name = r["patient_name"]
            patient_phone = r["patient_phone"]
            surgeon_name = r["surgeon_name"]
            proc_name = r["procedure_name"]
            m_days = r["milestone_days"]
            link = r["calcom_booking_link"]

            months_label = "6 meses" if m_days == 180 else ("12 meses" if m_days == 365 else "18 meses")
            message_text = (
                f"Olá {patient_name}, aqui é da equipe do {surgeon_name}. "
                f"Completam-se {months_label} ({m_days} dias) da sua cirurgia de {proc_name}. "
                "Para assegurar a longevidade dos seus implantes e a garantia do tratamento, "
                "é fundamental realizarmos a manutenção preventiva e profilaxia peri-implantar. "
                f"Escolha o melhor dia e horário diretamente na agenda: {link}"
            )

            msg_id = f"msg-reactiv-{uuid.uuid4().hex[:8]}"
            clean_phone = patient_phone.replace("+", "").replace("-", "").replace(" ", "")
            remote_jid = f"{clean_phone}@s.whatsapp.net"

            cur.execute("""
                INSERT INTO omnichannel_messages (
                    id, account_id, instance_name, remote_jid, sender_phone,
                    message_type, content, from_me
                ) VALUES (?, ?, 'evolution_main', ?, ?, 'text', ?, 1)
            """, (msg_id, account_id, remote_jid, patient_phone, message_text))

            now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                UPDATE patient_reactivation_schedules
                SET status = 'DISPATCHED', message_dispatched_at = ?
                WHERE id = ?
            """, (now_iso, sched_id))

            dispatched_items.append({
                "schedule_id": sched_id,
                "patient_name": patient_name,
                "patient_phone": patient_phone,
                "milestone_days": m_days,
                "scheduled_dispatch_date": r["scheduled_dispatch_date"],
                "calcom_booking_link": link,
                "status": "DISPATCHED",
                "message_dispatched_at": now_iso,
            })

        conn.commit()
    finally:
        conn.close()

    return {
        "scanned_count": len(dispatched_items),
        "dispatched_count": len(dispatched_items),
        "reference_date": ref_dt,
        "dispatched_items": dispatched_items,
    }


def process_calcom_webhook(
    payload: Dict[str, Any],
    account_id: str = "0f14ffff",
) -> Dict[str, Any]:
    """
    Processa webhook BOOKING_CREATED do Cal.com:
    1. Cria agendamento na tabela calcom_bookings.
    2. Gera sala LiveKit se for reunião online/teleconsulta.
    3. Cria tarefa em tasks.
    4. Cria Deal de manutenção no Pipeline 1.
    5. Atualiza régua do paciente para BOOKED.
    6. Dispara confirmação via WhatsApp.
    """
    init_db()

    payload_data = payload.get("payload") or payload
    if payload.get("triggerEvent") in ("SCHEDULE_BLOCKED_MATERIAL", "BLOCK_MATERIAL_SHORTAGE") or payload_data.get("status") == "BLOQUEADO_MATERIAL":
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE patient_reactivation_schedules
                SET status = 'BLOQUEADO_MATERIAL'
                WHERE account_id = ? AND status IN ('PENDING', 'DISPATCHED')
            """, (account_id,))
            conn.commit()
            return {
                "status": "BLOQUEADO_MATERIAL",
                "message": "Agenda bloqueada por falta de material cirúrgico",
                "affected_slots": cur.rowcount
            }
        finally:
            conn.close()
    booking_uid = str(payload_data.get("uid") or payload_data.get("id") or uuid.uuid4().hex[:12])
    title = payload_data.get("title") or payload_data.get("eventTitle") or "Consulta / Manutenção Preventiva"
    start_time = payload_data.get("startTime") or payload_data.get("start") or datetime.now().isoformat()
    end_time = payload_data.get("endTime") or payload_data.get("end") or (datetime.now() + timedelta(minutes=45)).isoformat()
    location = payload_data.get("location") or ""

    attendees = payload_data.get("attendees") or []
    attendee = attendees[0] if attendees else {}
    patient_name = attendee.get("name") or "Paciente"
    patient_email = attendee.get("email")

    metadata = payload_data.get("metadata") or {}
    patient_phone = metadata.get("patient_phone") or attendee.get("phoneNumber") or ""

    organizer = payload_data.get("organizer") or {}
    host_name = organizer.get("name") or "Dr. Lucas Mendes"
    host_email = organizer.get("email") or "dr.lucas@revnault.internal"

    is_online = 1 if any(k in location.lower() for k in ["livekit", "online", "video", "meet", "webrtc"]) else 0
    meeting_url: Optional[str] = None

    if is_online:
        room_name = f"room-cal-{booking_uid}"
        token = generate_room_token(
            room_name=room_name,
            identity=patient_name,
            name=patient_name,
            account_id=account_id,
            ttl_seconds=7200,
        )
        meeting_url = f"https://meet.revnault.internal/{room_name}?token={token}"
    elif location:
        meeting_url = location

    task_id = f"task-cal-{uuid.uuid4().hex[:8]}"
    deal_id = f"deal-cal-{uuid.uuid4().hex[:8]}"
    booking_db_id = f"cal-{uuid.uuid4().hex[:8]}"

    conn = get_connection()
    schedule_id: Optional[str] = None

    try:
        cur = conn.cursor()

        # Localiza se há agendamento prévio na régua
        if patient_phone:
            cur.execute("""
                SELECT id FROM patient_reactivation_schedules
                WHERE account_id = ?
                  AND patient_phone = ?
                  AND status IN ('PENDING', 'DISPATCHED')
                ORDER BY scheduled_dispatch_date ASC LIMIT 1
            """, (account_id, patient_phone))
            s_row = cur.fetchone()
            if s_row:
                schedule_id = s_row["id"]

        if not schedule_id and patient_name:
            cur.execute("""
                SELECT id FROM patient_reactivation_schedules
                WHERE account_id = ?
                  AND patient_name LIKE ?
                  AND status IN ('PENDING', 'DISPATCHED')
                ORDER BY scheduled_dispatch_date ASC LIMIT 1
            """, (account_id, f"%{patient_name}%"))
            s_row = cur.fetchone()
            if s_row:
                schedule_id = s_row["id"]

        if schedule_id:
            cur.execute(
                "UPDATE patient_reactivation_schedules SET status = 'BOOKED' WHERE id = ?",
                (schedule_id,),
            )

        # 1. Cria tarefa de acompanhamento
        task_title = f"Consulta Agendada (Cal.com): {title} - {patient_name}"
        due_date_str = str(start_time)[:19].replace("T", " ")
        cur.execute("""
            INSERT INTO tasks (
                id, account_id, title, due_date, assignee, priority, completed
            ) VALUES (?, ?, ?, ?, ?, 'alta', 0)
        """, (task_id, account_id, task_title, due_date_str, host_name))

        # 2. Cria Deal no Pipeline 1 (Cirurgiões & Venda Direta / Consignação de Caixas ou Manutenção)
        deal_title = f"Reativação Preventiva - {patient_name}"
        cur.execute("SELECT id FROM stages WHERE pipeline_id = 1 ORDER BY step_order ASC LIMIT 1")
        stg_row = cur.fetchone()
        target_stage_id = stg_row["id"] if stg_row else 101

        cur.execute("""
            INSERT INTO deals (
                id, account_id, pipeline_id, stage_id, title, value,
                company, contact_name, priority
            ) VALUES (?, ?, 1, ?, ?, 850.0, ?, ?, 'alta')
        """, (deal_id, account_id, target_stage_id, deal_title, f"Clínica {host_name}", patient_name))

        # 3. Registra booking no banco
        raw_json = json.dumps(payload, ensure_ascii=False)
        cur.execute("""
            INSERT INTO calcom_bookings (
                id, account_id, calcom_booking_uid, schedule_id, patient_name,
                patient_email, patient_phone, host_name, host_email,
                event_type_title, start_time, end_time, meeting_url,
                is_online, deal_id, task_id, status, raw_payload
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CONFIRMED', ?)
        """, (
            booking_db_id, account_id, booking_uid, schedule_id, patient_name,
            patient_email, patient_phone, host_name, host_email,
            title, str(start_time), str(end_time), meeting_url,
            is_online, deal_id, task_id, raw_json,
        ))

        # 4. Dispara confirmação via WhatsApp
        confirm_text = (
            f"Olá {patient_name}! Seu agendamento para '{title}' foi confirmado com sucesso. "
            f"Horário: {str(start_time)[:16].replace('T', ' às ')}. "
            f"Profissional responsável: {host_name}."
        )
        if meeting_url:
            confirm_text += f" Link da sala de atendimento online: {meeting_url}"

        msg_id = f"msg-conf-{uuid.uuid4().hex[:8]}"
        clean_phone = (patient_phone or "").replace("+", "").replace("-", "").replace(" ", "")
        remote_jid = f"{clean_phone}@s.whatsapp.net" if clean_phone else "paciente@s.whatsapp.net"

        cur.execute("""
            INSERT INTO omnichannel_messages (
                id, account_id, instance_name, remote_jid, sender_phone,
                message_type, content, from_me
            ) VALUES (?, ?, 'evolution_main', ?, ?, 'text', ?, 1)
        """, (msg_id, account_id, remote_jid, patient_phone or "", confirm_text))

        conn.commit()
    finally:
        conn.close()

    # Publica evento de auditoria no EventBus
    try:
        EventBus.publish_sync(
            StreamName.AUDIT,
            {
                "event": "calcom.booking_created",
                "booking_uid": booking_uid,
                "deal_id": deal_id,
                "task_id": task_id,
                "patient_name": patient_name,
                "meeting_url": meeting_url,
            },
        )
    except Exception:
        pass

    return {
        "success": True,
        "booking_id": booking_db_id,
        "booking_uid": booking_uid,
        "deal_id": deal_id,
        "task_id": task_id,
        "meeting_url": meeting_url,
        "patient_name": patient_name,
        "start_time": str(start_time),
        "status": "CONFIRMED",
    }


def list_calcom_schedules(
    patient_name: Optional[str] = None,
    status: Optional[str] = None,
    account_id: str = "0f14ffff",
) -> List[Dict[str, Any]]:
    """Consulta réguas de reativação cadastradas."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = """
            SELECT id, account_id, patient_name, patient_phone, surgeon_name,
                   procedure_name, surgery_date, milestone_days, scheduled_dispatch_date,
                   calcom_booking_link, status, message_dispatched_at, created_at
            FROM patient_reactivation_schedules
            WHERE account_id = ?
        """
        params: List[Any] = [account_id]

        if patient_name:
            query += " AND patient_name LIKE ?"
            params.append(f"%{patient_name}%")
        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY scheduled_dispatch_date ASC"
        cur.execute(query, tuple(params))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def list_calcom_bookings(
    account_id: str = "0f14ffff",
) -> List[Dict[str, Any]]:
    """Consulta agendamentos confirmados via Cal.com."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, account_id, calcom_booking_uid, schedule_id, patient_name,
                   patient_email, patient_phone, host_name, host_email,
                   event_type_title, start_time, end_time, meeting_url,
                   is_online, deal_id, task_id, status, created_at
            FROM calcom_bookings
            WHERE account_id = ?
            ORDER BY created_at DESC
        """, (account_id,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
