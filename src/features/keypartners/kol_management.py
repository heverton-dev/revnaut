# -*- coding: utf-8 -*-
"""
Vertical Slice: KeyPartners KOL Management & Comodato
Gestão de Key Opinion Leaders, Embaixadores, Ativos em Comodato e Auditoria de Metas.
"""

from __future__ import annotations
import json
import uuid
from typing import Any, Dict, List, Optional
from src.core.database import get_connection, init_db


def create_kol_contract(
    kol_name: str,
    cro_uf: str,
    equipment_name: str,
    asset_tag: str,
    min_monthly_implants_target: int = 20,
    clinical_lectures_quota: int = 1,
    agreement_id: Optional[str] = None,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Cadastra novo contrato de comodato para cirurgião parceiro / KOL."""
    init_db()
    conn = get_connection()
    try:
        kol_id = f"kol-{uuid.uuid4().hex[:8]}"
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO kp_kol_contracts (
                id, account_id, agreement_id, kol_name, cro_uf,
                equipment_name, asset_tag, min_monthly_implants_target,
                clinical_lectures_quota, current_month_consumption,
                compliance_status, evidence_r2_keys_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'COMPLIANT', '[]')
            ON CONFLICT(asset_tag) DO UPDATE SET
                kol_name = excluded.kol_name,
                cro_uf = excluded.cro_uf,
                equipment_name = excluded.equipment_name,
                min_monthly_implants_target = excluded.min_monthly_implants_target,
                clinical_lectures_quota = excluded.clinical_lectures_quota,
                current_month_consumption = 0,
                compliance_status = 'COMPLIANT',
                evidence_r2_keys_json = '[]',
                updated_at = CURRENT_TIMESTAMP
        """, (
            kol_id, account_id, agreement_id, kol_name, cro_uf,
            equipment_name, asset_tag.strip().upper(), min_monthly_implants_target,
            clinical_lectures_quota
        ))
        conn.commit()

        cur.execute("SELECT * FROM kp_kol_contracts WHERE asset_tag = ?", (asset_tag.strip().upper(),))
        return dict(cur.fetchone())
    finally:
        conn.close()


def record_monthly_consumption(
    contract_id: str,
    consumed_implants_count: int,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Registra consumo mensal de implantes e audita contrapartida de comodato:
    - Se >= meta: status COMPLIANT
    - Se < meta: status NON_COMPLIANT_ALERT com aviso à gerência regional.
    """
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM kp_kol_contracts WHERE id = ? AND account_id = ?", (contract_id, account_id))
        kol = cur.fetchone()
        if not kol:
            raise ValueError(f"Contrato de KOL {contract_id} não encontrado")

        target = int(kol["min_monthly_implants_target"])
        is_compliant = consumed_implants_count >= target

        new_status = "COMPLIANT" if is_compliant else "NON_COMPLIANT_ALERT"
        regional_alert = not is_compliant
        alert_msg = None
        if regional_alert:
            alert_msg = (
                f"Alerta para Gerência Regional: Consumo de {consumed_implants_count} implantes "
                f"abaixo da meta mínima contratual de {target}/mês para o ativo {kol['asset_tag']}."
            )

        cur.execute("""
            UPDATE kp_kol_contracts
            SET current_month_consumption = ?,
                compliance_status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (consumed_implants_count, new_status, contract_id))
        conn.commit()

        return {
            "compliance_status": new_status,
            "current_month_consumption": consumed_implants_count,
            "min_monthly_implants_target": target,
            "regional_alert": regional_alert,
            "alert_message": alert_msg,
        }
    finally:
        conn.close()


def submit_clinical_evidence(
    contract_id: str,
    r2_key: str,
    title: str,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Armazena caso clínico / vídeo de palestra submetido pelo embaixador no Cloudflare R2."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT evidence_r2_keys_json FROM kp_kol_contracts WHERE id = ? AND account_id = ?", (contract_id, account_id))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Contrato de KOL {contract_id} não encontrado")

        try:
            evidences = json.loads(row["evidence_r2_keys_json"] or "[]")
        except json.JSONDecodeError:
            evidences = []

        evidences.append({
            "r2_key": r2_key,
            "title": title,
            "submitted_at": "2026-10-18T00:00:00Z"
        })

        new_json = json.dumps(evidences, ensure_ascii=False)
        cur.execute("UPDATE kp_kol_contracts SET evidence_r2_keys_json = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_json, contract_id))
        conn.commit()

        return {
            "success": True,
            "contract_id": contract_id,
            "evidence_r2_keys_json": new_json
        }
    finally:
        conn.close()


def list_kol_contracts(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    """Lista todos os contratos de comodato e KOL do tenant."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM kp_kol_contracts WHERE account_id = ? ORDER BY created_at DESC", (account_id,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_kol_contract(contract_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Busca detalhes de um contrato de KOL específico."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM kp_kol_contracts WHERE id = ? AND account_id = ?", (contract_id, account_id))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Contrato de KOL {contract_id} não encontrado")
        return dict(row)
    finally:
        conn.close()
