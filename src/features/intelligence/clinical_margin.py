# -*- coding: utf-8 -*-
"""
Vertical Slice: Clinical Procedure Margin Intelligence
Calculadora de Margem Liquida Real por Procedimento Cirurgico para Clinicas e Franquias Odontologicas.
"""

from __future__ import annotations
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.core.database import get_connection, init_db
from src.features.intelligence.schemas import (
    ClinicalMarginCalculateRequest,
    ClinicalMarginCalculateResponse,
    ClinicalMarginSummaryReportResponse
)


def calculate_procedure_net_margin(data: ClinicalMarginCalculateRequest) -> Dict[str, Any]:
    """
    Calcula a Margem Liquida Real por procedimento cirurgico:
    Margem Liquida = V_procedimento - (C_insumos + C_lab + C_honorario + C_hora_cadeira + C_imposto)

    Emite alerta (is_low_margin = True) quando a margem liquida for inferior a 15.0%.
    """
    init_db()

    total_chair_cost = round(data.chair_hours * data.chair_hour_cost, 2)
    tax_amount = round(data.gross_revenue * (data.tax_rate_percent / 100.0), 2)
    lab_cost = round(data.lab_cost or 0.0, 2)
    supplies_cost = round(data.supplies_cost or 0.0, 2)
    surgeon_fee = round(data.surgeon_fee, 2)

    conn = get_connection()
    try:
        cur = conn.cursor()
        if data.surgery_order_id and supplies_cost <= 0.0:
            cur.execute(
                "SELECT consumed_items_json, remitted_items_json FROM kp_surgical_orders WHERE id = ? AND account_id = ?",
                (data.surgery_order_id, data.account_id),
            )
            surg_row = cur.fetchone()
            if surg_row:
                raw_json = surg_row["consumed_items_json"]
                items_list = []
                if raw_json and raw_json != "[]":
                    try:
                        items_list = json.loads(raw_json)
                    except Exception:
                        items_list = []
                if not items_list and surg_row["remitted_items_json"]:
                    try:
                        items_list = json.loads(surg_row["remitted_items_json"])
                    except Exception:
                        items_list = []
                if items_list:
                    supplies_cost = round(
                        sum(float(it.get("unit_value", 0.0)) * int(it.get("quantity", 1)) for it in items_list),
                        2,
                    )

        total_cost = round(supplies_cost + lab_cost + surgeon_fee + total_chair_cost + tax_amount, 2)
        net_margin_value = round(data.gross_revenue - total_cost, 2)

        if data.gross_revenue > 0:
            net_margin_percent = round((net_margin_value / data.gross_revenue) * 100.0, 2)
        else:
            net_margin_percent = 0.0

        is_low_margin = net_margin_percent < 15.0

        if is_low_margin:
            status_code = "LOW_MARGIN_RISK"
            recommendation = (
                f"Alerta de margem critica ({net_margin_percent}% < 15%). "
                "Rever custos laboratoriais, otimizar horas de cadeira ou reprecificar procedimento."
            )
        else:
            status_code = "HEALTHY_MARGIN"
            recommendation = f"Procedimento altamente rentavel ({net_margin_percent}% >= 15%). Margem operacional saudavel."

        margin_id = f"clm_{uuid.uuid4().hex[:10]}"
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT INTO clinical_procedure_margins (
                id, account_id, clinic_id, surgery_order_id, procedure_name, patient_identifier,
                gross_revenue, supplies_cost, lab_cost, surgeon_fee, chair_hours, chair_hour_cost,
                total_chair_cost, tax_rate_percent, tax_amount, net_margin_value, net_margin_percent,
                is_low_margin, recommendation, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            margin_id,
            data.account_id,
            data.clinic_id,
            data.surgery_order_id,
            data.procedure_name,
            data.patient_identifier,
            data.gross_revenue,
            supplies_cost,
            lab_cost,
            surgeon_fee,
            data.chair_hours,
            data.chair_hour_cost,
            total_chair_cost,
            data.tax_rate_percent,
            tax_amount,
            net_margin_value,
            net_margin_percent,
            1 if is_low_margin else 0,
            recommendation,
            now_str
        ))
        conn.commit()

        return {
            "id": margin_id,
            "procedure_name": data.procedure_name,
            "gross_revenue": data.gross_revenue,
            "supplies_cost": supplies_cost,
            "lab_cost": lab_cost,
            "surgeon_fee": surgeon_fee,
            "chair_hours": data.chair_hours,
            "chair_hour_cost": data.chair_hour_cost,
            "total_chair_cost": total_chair_cost,
            "tax_rate_percent": data.tax_rate_percent,
            "tax_amount": tax_amount,
            "total_cost": total_cost,
            "net_margin_value": net_margin_value,
            "net_margin_percent": net_margin_percent,
            "is_low_margin": is_low_margin,
            "status": status_code,
            "recommendation": recommendation,
            "clinic_id": data.clinic_id,
            "surgery_order_id": data.surgery_order_id,
            "patient_identifier": data.patient_identifier,
            "calculated_at": now_str
        }
    finally:
        conn.close()


def get_clinic_margin_summary(clinic_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Retorna consolidado analitico de margens por clinica com destaque para procedimentos criticos."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM clinical_procedure_margins
            WHERE clinic_id = ? AND account_id = ?
            ORDER BY created_at DESC LIMIT 50
        """, (clinic_id, account_id))
        rows = [dict(r) for r in cur.fetchall()]

        total_analyzed = len(rows)
        if total_analyzed > 0:
            avg_margin = round(sum(r["net_margin_percent"] for r in rows) / total_analyzed, 2)
            low_count = sum(1 for r in rows if r["is_low_margin"] == 1)
        else:
            avg_margin = 0.0
            low_count = 0

        return {
            "clinic_id": clinic_id,
            "total_procedures_analyzed": total_analyzed,
            "average_margin_percent": avg_margin,
            "low_margin_count": low_count,
            "items": rows
        }
    finally:
        conn.close()
