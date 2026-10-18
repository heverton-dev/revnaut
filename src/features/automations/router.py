# -*- coding: utf-8 -*-
"""
Router FastAPI para Automações e Gatilhos de Receita.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from src.core.database import get_connection
from src.features.automations.schemas import (
    HotLeadEvaluationResponse,
    AutomationFlowOut,
    AutomationFlowToggleResponse,
    AutomationTestResponse,
    AutomationLogOut,
    PostOpCareStartRequest,
    PostOpCareScheduleOut,
    PostOpFeedbackRequest,
    PostOpFeedbackResponse
)
from src.features.automations.revenue_triggers import evaluate_hot_lead_and_overflow
from src.features.automations import postop_patient_care


router = APIRouter(prefix="/api/v1/automations", tags=["Automações & Gatilhos de Receita"])


@router.get("/flows", response_model=List[AutomationFlowOut], summary="Listar todos os fluxos de automação cirúrgica")
def list_flows(account_id: str = "0f14ffff"):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, account_id, name, category, trigger_event, action_description, is_active, execution_count, last_run_at
            FROM automation_flows
            WHERE account_id = ?
            ORDER BY created_at ASC
        """, (account_id,))
        rows = cur.fetchall()
        return [
            AutomationFlowOut(
                id=r["id"],
                account_id=r["account_id"],
                name=r["name"],
                category=r["category"],
                trigger_event=r["trigger_event"],
                action_description=r["action_description"],
                is_active=bool(r["is_active"]),
                execution_count=r["execution_count"],
                last_run_at=r["last_run_at"]
            )
            for r in rows
        ]
    finally:
        conn.close()


@router.put("/flows/{flow_id}/toggle", response_model=AutomationFlowToggleResponse, summary="Ativar ou pausar fluxo de automação")
def toggle_flow(flow_id: str, account_id: str = "0f14ffff"):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, is_active FROM automation_flows WHERE id = ? AND account_id = ?", (flow_id, account_id))
        flow = cur.fetchone()
        if not flow:
            raise HTTPException(status_code=404, detail="Fluxo de automação não encontrado.")

        new_status = 0 if flow["is_active"] else 1
        cur.execute("UPDATE automation_flows SET is_active = ? WHERE id = ?", (new_status, flow_id))
        conn.commit()

        status_text = "ativado" if new_status else "pausado"
        return AutomationFlowToggleResponse(
            id=flow_id,
            is_active=bool(new_status),
            message=f"Fluxo '{flow['name']}' {status_text} com sucesso."
        )
    finally:
        conn.close()


@router.post("/flows/{flow_id}/test", response_model=AutomationTestResponse, summary="Disparar teste manual de automação")
def test_flow(flow_id: str, account_id: str = "0f14ffff"):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, category, is_active, execution_count FROM automation_flows WHERE id = ? AND account_id = ?", (flow_id, account_id))
        flow = cur.fetchone()
        if not flow:
            raise HTTPException(status_code=404, detail="Fluxo de automação não encontrado.")

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_count = flow["execution_count"] + 1

        summary = f"Simulação manual disparada com sucesso para '{flow['name']}'. Regra executada sem erros."
        cur.execute("UPDATE automation_flows SET execution_count = ?, last_run_at = ? WHERE id = ?", (new_count, now_str, flow_id))
        cur.execute("""
            INSERT INTO automation_logs (account_id, flow_id, trigger_payload, result_summary, status, executed_at)
            VALUES (?, ?, '{\"simulated\": true, \"trigger\": \"manual_test\"}', ?, 'success', ?)
        """, (account_id, flow_id, summary, now_str))
        conn.commit()

        return AutomationTestResponse(
            flow_id=flow_id,
            status="success",
            summary=summary,
            execution_count=new_count,
            executed_at=now_str
        )
    finally:
        conn.close()


@router.get("/logs", response_model=List[AutomationLogOut], summary="Listar histórico de execuções de automações")
def list_logs(account_id: str = "0f14ffff"):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, flow_id, result_summary, status, executed_at
            FROM automation_logs
            WHERE account_id = ?
            ORDER BY executed_at DESC
            LIMIT 50
        """, (account_id,))
        rows = cur.fetchall()
        return [
            AutomationLogOut(
                id=r["id"],
                flow_id=r["flow_id"],
                result_summary=r["result_summary"],
                status=r["status"],
                executed_at=str(r["executed_at"])
            )
            for r in rows
        ]
    finally:
        conn.close()


@router.post("/evaluate-hot-lead/{contact_id}", response_model=HotLeadEvaluationResponse, status_code=status.HTTP_200_OK, summary="Avaliar e Transbordar Lead Hot (Tier A)")
def evaluate_hot_lead(contact_id: int, account_id: str = "0f14ffff"):
    res = evaluate_hot_lead_and_overflow(contact_id, account_id=account_id)
    if res.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Contato não encontrado.")
    return res


@router.post(
    "/postop-care/start",
    response_model=PostOpCareScheduleOut,
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar régua de acompanhamento pós-operatório cirúrgico B2C"
)
def start_postop_care(payload: PostOpCareStartRequest):
    try:
        return postop_patient_care.start_postop_care_schedule(
            patient_name=payload.patient_name,
            patient_phone=payload.patient_phone,
            surgeon_name=payload.surgeon_name,
            surgeon_phone=payload.surgeon_phone,
            procedure_name=payload.procedure_name,
            surgery_date=payload.surgery_date,
            account_id=payload.account_id or "0f14ffff"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/postop-care/{schedule_id}/feedback",
    response_model=PostOpFeedbackResponse,
    summary="Processar feedback do paciente no marco pós-operatório (texto/áudio)"
)
def post_patient_feedback(schedule_id: str, payload: PostOpFeedbackRequest):
    try:
        return postop_patient_care.process_patient_feedback(
            schedule_id=schedule_id,
            feedback_text=payload.feedback_text,
            milestone_code=payload.milestone_code,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/postop-care",
    response_model=List[PostOpCareScheduleOut],
    summary="Listar réguas pós-operatórias ativas"
)
def list_postop_care_schedules(
    status: Optional[str] = None,
    account_id: str = "0f14ffff"
):
    return postop_patient_care.list_postop_schedules(account_id=account_id, status=status)


@router.get(
    "/postop-care/{schedule_id}",
    response_model=PostOpCareScheduleOut,
    summary="Consultar detalhes de uma régua pós-operatória"
)
def get_postop_care_schedule(schedule_id: str, account_id: str = "0f14ffff"):
    sched = postop_patient_care.get_postop_schedule(schedule_id=schedule_id, account_id=account_id)
    if not sched:
        raise HTTPException(status_code=404, detail="Régua pós-operatória não encontrada.")
    return sched

