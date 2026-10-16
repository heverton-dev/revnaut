# -*- coding: utf-8 -*-
"""
Vertical Slice: Deals & Pipeline Service
Regras de negócio e operações transacionais com auditoria.
"""

from __future__ import annotations
import time
import json
from typing import Any, Dict, List, Optional
from src.core.database import get_connection
from src.features.deals.schemas import DealCreate, DealMove


from src.core.security import get_user_context, resolve_data_scope_clause


def list_pipelines() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM pipelines ORDER BY id ASC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_pipeline_and_deals(
    pipeline_id: Optional[int] = None, 
    account_id: str = "0f14ffff", 
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    conn = get_connection()
    try:
        user_ctx = get_user_context(conn, user_id, account_id) if user_id else None
        scope_clause, scope_params = resolve_data_scope_clause(conn, user_ctx, account_id, table_alias="d")

        cur = conn.cursor()
        target_pipe = pipeline_id if pipeline_id is not None else 1

        cur.execute(
            "SELECT id, name, color, step_order, probability FROM stages WHERE pipeline_id = ? ORDER BY step_order ASC",
            (target_pipe,)
        )
        stages = [dict(r) for r in cur.fetchall()]

        query = f"""
            SELECT d.id, d.title, d.value, d.company, d.contact_name, d.stage_id, d.priority, 
                   d.owner_id, d.team_id, s.name as stage_name, s.color as stage_color
            FROM deals d
            JOIN stages s ON d.stage_id = s.id
            WHERE d.pipeline_id = ? AND {scope_clause}
            ORDER BY d.created_at DESC
        """
        params = [target_pipe] + list(scope_params)
        cur.execute(query, tuple(params))
        deals = [dict(r) for r in cur.fetchall()]

        return {"stages": stages, "deals": deals}
    finally:
        conn.close()


def get_metrics() -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT SUM(value), COUNT(*) FROM deals")
    total_val, total_count = cur.fetchone()
    conn.close()
    return {
        "mrr": 142800.0,
        "mrrGrowth": "+14.8%",
        "pipelineTotal": total_val or 0.0,
        "dealsCount": total_count or 0,
        "winRate": "34.2%",
        "avgCycleDays": 19
    }


def create_deal(payload: DealCreate) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    deal_id = f"d-{int(time.time() * 1000)}"
    cur.execute("""
        INSERT INTO deals (id, account_id, pipeline_id, stage_id, title, value, company, contact_name, priority)
        VALUES (?, '0f14ffff', 1, ?, ?, ?, ?, ?, ?)
    """, (deal_id, payload.stage_id, payload.title, payload.value, payload.company, payload.contact_name, payload.priority))
    conn.commit()
    conn.close()
    return {
        "id": deal_id,
        "status": "created",
        "title": payload.title,
        "value": payload.value,
        "company": payload.company,
        "contact_name": payload.contact_name,
        "stage_id": payload.stage_id,
        "priority": payload.priority
    }


def move_deal_stage(
    deal_id: str, 
    new_stage_id: int, 
    user_id: Optional[str] = None, 
    author_name: str = "Consultor"
) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, value, stage_id FROM deals WHERE id = ?", (deal_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False

    old_stage_id = row["stage_id"]
    deal_value = float(row["value"] or 0.0)

    # Regra Setorial: Trava de Limite de Crédito para Consignação/Fechamento (> R$ 150.000)
    # Estágio 104 (Negociação/Consignação) ou 105 (Fechado) exige trava de crédito
    if new_stage_id in (104, 105) and deal_value > 150000.0:
        # Verifica se há aprovação registrada em audit logs
        cur.execute("""
            SELECT COUNT(*) FROM deal_audit_logs 
            WHERE deal_id = ? AND action = 'CREDIT_LIMIT_APPROVED'
        """, (deal_id,))
        approved = cur.fetchone()[0] > 0
        if not approved:
            conn.close()
            raise ValueError(
                f"Trava de Limite de Crédito: Operações acima de R$ 150.000,00 ({deal_value:,.2f}) "
                "exigem aprovação prévia de crédito antes da liberação de consignação/fechamento."
            )

    cur.execute("UPDATE deals SET stage_id = ? WHERE id = ?", (new_stage_id, deal_id))
    
    # Registro formal na timeline de auditoria
    cur.execute("""
        INSERT INTO deal_audit_logs (deal_id, user_id, author_name, action, old_value, new_value, comment)
        VALUES (?, ?, ?, 'STAGE_CHANGE', ?, ?, 'Movimentação de estágio no funil comercial')
    """, (deal_id, user_id, author_name, str(old_stage_id), str(new_stage_id)))

    # Registro de auditoria do webhook
    payload = json.dumps({
        "event": "deal.stage_changed",
        "deal_id": deal_id,
        "title": row["title"],
        "old_stage_id": old_stage_id,
        "new_stage_id": new_stage_id,
        "timestamp": time.time()
    })
    cur.execute("""
        INSERT INTO webhook_logs (webhook_id, payload, status_code, response_body)
        VALUES (1, ?, 200, '{"delivered": true}')
    """, (payload,))
    
    conn.commit()
    conn.close()
    return True


def update_deal(
    deal_id: str, 
    data: Dict[str, Any], 
    user_id: Optional[str] = None, 
    author_name: str = "Consultor"
) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM deals WHERE id = ?", (deal_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise KeyError("Negócio não encontrado.")

    updates = []
    params = []
    audit_entries = []

    if "title" in data and data["title"] is not None:
        updates.append("title = ?")
        params.append(data["title"])
        audit_entries.append(("TITLE_UPDATE", str(row["title"]), str(data["title"]), "Edição de título"))

    if "value" in data and data["value"] is not None:
        updates.append("value = ?")
        params.append(float(data["value"]))
        audit_entries.append(("VALUE_UPDATE", str(row["value"]), str(data["value"]), "Alteração de valor"))

    if "priority" in data and data["priority"] is not None:
        updates.append("priority = ?")
        params.append(data["priority"])
        audit_entries.append(("PRIORITY_UPDATE", str(row["priority"]), str(data["priority"]), "Alteração de prioridade"))

    if "expected_close_date" in data and data["expected_close_date"] is not None:
        updates.append("expected_close_date = ?")
        params.append(data["expected_close_date"])
        audit_entries.append(("CLOSE_DATE_UPDATE", str(row["expected_close_date"] or ""), str(data["expected_close_date"]), "Prazo de fechamento"))

    if not updates:
        conn.close()
        return dict(row)

    params.append(deal_id)
    cur.execute(f"UPDATE deals SET {', '.join(updates)} WHERE id = ?", tuple(params))

    # Inserção de log de auditoria
    comment = data.get("comment") or "Atualização inline de dados do negócio"
    for action, old_v, new_v, item_label in audit_entries:
        cur.execute("""
            INSERT INTO deal_audit_logs (deal_id, user_id, author_name, action, old_value, new_value, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (deal_id, user_id, author_name, action, old_v, new_v, f"{item_label}: {comment}"))

    conn.commit()
    cur.execute("SELECT * FROM deals WHERE id = ?", (deal_id,))
    updated_deal = dict(cur.fetchone())
    conn.close()
    return updated_deal


def approve_deal_credit_limit(deal_id: str, approver_name: str = "Diretor Financeiro", user_id: Optional[str] = None) -> bool:
    """Aprova limite de crédito para liberação de consignação ou fechamento de alto valor."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, value FROM deals WHERE id = ?", (deal_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False

    cur.execute("""
        INSERT INTO deal_audit_logs (deal_id, user_id, author_name, action, old_value, new_value, comment)
        VALUES (?, ?, ?, 'CREDIT_LIMIT_APPROVED', 'PENDING', 'APPROVED', 'Limite de crédito homologado pela controladoria')
    """, (deal_id, user_id, approver_name))
    conn.commit()
    conn.close()
    return True


def get_deal_timeline(deal_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, deal_id, user_id, author_name, action, old_value, new_value, comment, created_at
        FROM deal_audit_logs
        WHERE deal_id = ?
        ORDER BY created_at DESC, id DESC
    """, (deal_id,))
    logs = [dict(r) for r in cur.fetchall()]
    conn.close()
    return logs


def export_deals_csv(
    pipeline_id: Optional[int] = None, 
    account_id: str = "0f14ffff", 
    user_id: Optional[str] = None
) -> str:
    result = get_pipeline_and_deals(pipeline_id=pipeline_id, account_id=account_id, user_id=user_id)
    deals = result.get("deals", [])
    
    import io, csv
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["ID", "Titulo", "Empresa", "Contato", "Valor_R$", "Estagio", "Prioridade", "Previsao_Fechamento"])
    
    for d in deals:
        writer.writerow([
            d.get("id", ""),
            d.get("title", ""),
            d.get("company", ""),
            d.get("contact_name", ""),
            f"{float(d.get('value', 0.0)):.2f}",
            d.get("stage_name", ""),
            d.get("priority", ""),
            d.get("expected_close_date", "") or ""
        ])
    
    return output.getvalue()

