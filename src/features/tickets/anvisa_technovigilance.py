# -*- coding: utf-8 -*-
"""
Vertical Slice: Módulo de Cosmovigilância, Tecnovigilância ANVISA e Garantia de Osseointegração (RMA)
Esteira regulatória de queixas técnicas, reposição em garantia e bloqueio automático de quarentena.
"""

from __future__ import annotations
import uuid
from typing import Any, Dict, List, Optional
from src.core.database import get_connection, init_db


def submit_anvisa_rma_claim(
    surgeon_cro_uf: str,
    product_id: str,
    product_name: str,
    batch_number: str,
    fdi_tooth_region: str,
    insertion_torque_ncm: float,
    surgery_date: str,
    explant_date: str,
    failure_reason: str,
    radiograph_r2_key: str,
    surgeon_name: Optional[str] = None,
    agreement_id: Optional[str] = None,
    patient_identifier: Optional[str] = None,
    serial_number: Optional[str] = None,
    notes: Optional[str] = None,
    account_id: str = "0f14ffff",
    enforce_custody_check: bool = True
) -> Dict[str, Any]:
    """
    Registra queixa técnica regulatória ANVISA com validação de custódia,
    avaliação de garantia de osseointegração e bloqueio sanitário por lote fabril.
    """
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()

        # 1. Validação cruzada com histórico de custódia (KeyPartners ou DENTGO)
        custody_verified = False
        cur.execute("""
            SELECT id FROM kp_custody_ledger
            WHERE account_id = ? AND batch_number = ?
            LIMIT 1
        """, (account_id, batch_number))
        if cur.fetchone():
            custody_verified = True

        if not custody_verified:
            cur.execute("""
                SELECT id FROM dentgo_hub_inventory
                WHERE account_id = ? AND batch_number = ?
                LIMIT 1
            """, (account_id, batch_number))
            if cur.fetchone():
                custody_verified = True

        if enforce_custody_check and not custody_verified:
            raise ValueError(f"Lote {batch_number} não localizado no histórico de custódia ou distribuição da fábrica.")

        # 2. Abertura do ticket regulatório
        ticket_id = f"tkt-anvisa-{uuid.uuid4().hex[:8]}"
        claim_id = f"rma-{uuid.uuid4().hex[:8]}"
        title = f"RMA ANVISA: Queixa Técnica Lote {batch_number} - {product_name} (Dente {fdi_tooth_region})"
        cust_name = surgeon_name or f"Cirurgião {surgeon_cro_uf}"

        cur.execute("""
            INSERT INTO tickets (id, account_id, title, customer_name, priority, status, category)
            VALUES (?, ?, ?, ?, 'alta', 'aberto', 'Tecnovigilância ANVISA - RMA')
        """, (ticket_id, account_id, title, cust_name))

        # 3. Cálculo da taxa acumulada de perda por lote fabril
        cur.execute("""
            SELECT COUNT(*) FROM anvisa_rma_claims
            WHERE account_id = ? AND batch_number = ?
        """, (account_id, batch_number))
        existing_failures = cur.fetchone()[0]
        total_failures = existing_failures + 1

        # Obter total de unidades distribuídas para este lote
        cur.execute("""
            SELECT COALESCE(SUM(quantity), 0) FROM kp_custody_ledger
            WHERE account_id = ? AND batch_number = ?
        """, (account_id, batch_number))
        distributed_kp = cur.fetchone()[0] or 0

        cur.execute("""
            SELECT COALESCE(SUM(quantity_available), 0) FROM dentgo_hub_inventory
            WHERE account_id = ? AND batch_number = ?
        """, (account_id, batch_number))
        distributed_hub = cur.fetchone()[0] or 0

        total_distributed = distributed_kp + distributed_hub
        if total_distributed == 0:
            total_distributed = 100  # Baseline padrão de lote

        failure_rate = (total_failures / total_distributed) * 100.0
        quarantine_triggered = False

        # Se falha acumulada > 2.5%, acionar recall preventivo e quarentena sanitária
        if failure_rate > 2.5:
            quarantine_triggered = True
            quarantine_id = f"quar-{uuid.uuid4().hex[:8]}"
            reason = (
                f"Taxa acumulada de falha clínica atingiu {failure_rate:.2f}% "
                f"({total_failures}/{total_distributed} unidades), ultrapassando o teto regulatório ANVISA de 2.5%."
            )

            # Grava/Atualiza na tabela anvisa_batch_quarantines
            cur.execute("""
                INSERT INTO anvisa_batch_quarantines (
                    id, account_id, batch_number, product_id, total_distributed,
                    total_failures, failure_rate_percent, status, reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'QUARANTINE_BLOCKED', ?)
                ON CONFLICT(account_id, batch_number) DO UPDATE SET
                    total_failures = excluded.total_failures,
                    failure_rate_percent = excluded.failure_rate_percent,
                    status = 'QUARANTINE_BLOCKED',
                    reason = excluded.reason
            """, (
                quarantine_id, account_id, batch_number, product_id,
                total_distributed, total_failures, round(failure_rate, 2), reason
            ))

            # Bloqueio imediato no DENTGO Hub Inventory
            cur.execute("""
                UPDATE dentgo_hub_inventory
                SET status = 'QUARANTINE_BLOCKED'
                WHERE account_id = ? AND batch_number = ?
            """, (account_id, batch_number))

            # Bloqueio de kits em consignação KeyPartners
            cur.execute("""
                UPDATE kp_consignment_kits
                SET status = 'QUARANTINE_BLOCKED'
                WHERE account_id = ? AND (serial_number = ? OR composition_json LIKE ?)
            """, (account_id, serial_number or '', f"%{batch_number}%"))

        # 4. Homologação da Reposição em Garantia
        warranty_approved = False
        replacement_order_id = None
        claim_status = "SUBMITTED"

        if radiograph_r2_key and custody_verified:
            warranty_approved = True
            claim_status = "REPLACED_UNDER_WARRANTY"
            replacement_order_id = f"rep-rma-{uuid.uuid4().hex[:8]}"

        # 5. Inserção do claim
        cur.execute("""
            INSERT INTO anvisa_rma_claims (
                id, account_id, ticket_id, agreement_id, surgeon_name, surgeon_cro_uf,
                patient_identifier, product_id, product_name, batch_number, serial_number,
                fdi_tooth_region, insertion_torque_ncm, surgery_date, explant_date,
                failure_reason, radiograph_r2_key, status, warranty_approved,
                replacement_order_id, quarantine_triggered, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            claim_id, account_id, ticket_id, agreement_id, cust_name, surgeon_cro_uf,
            patient_identifier, product_id, product_name, batch_number, serial_number,
            fdi_tooth_region, insertion_torque_ncm, surgery_date, explant_date,
            failure_reason, radiograph_r2_key, claim_status, 1 if warranty_approved else 0,
            replacement_order_id, 1 if quarantine_triggered else 0, notes
        ))
        conn.commit()

        # Obter data de criação real gravada
        cur.execute("SELECT created_at FROM anvisa_rma_claims WHERE id = ?", (claim_id,))
        row = cur.fetchone()
        created_at = row[0] if row else "2026-10-18T00:00:00"

        return {
            "id": claim_id,
            "account_id": account_id,
            "ticket_id": ticket_id,
            "agreement_id": agreement_id,
            "surgeon_name": cust_name,
            "surgeon_cro_uf": surgeon_cro_uf,
            "patient_identifier": patient_identifier,
            "product_id": product_id,
            "product_name": product_name,
            "batch_number": batch_number,
            "serial_number": serial_number,
            "fdi_tooth_region": fdi_tooth_region,
            "insertion_torque_ncm": insertion_torque_ncm,
            "surgery_date": surgery_date,
            "explant_date": explant_date,
            "failure_reason": failure_reason,
            "radiograph_r2_key": radiograph_r2_key,
            "status": claim_status,
            "warranty_approved": warranty_approved,
            "replacement_order_id": replacement_order_id,
            "quarantine_triggered": quarantine_triggered,
            "batch_failure_rate_percent": round(failure_rate, 2),
            "notes": notes,
            "created_at": str(created_at)
        }
    finally:
        conn.close()


def get_batch_quarantine_info(batch_number: str, account_id: str = "0f14ffff") -> Optional[Dict[str, Any]]:
    """Consulta se um lote fabril está em bloqueio preventivo / quarentena sanitária ANVISA."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, account_id, batch_number, product_id, total_distributed,
                   total_failures, failure_rate_percent, status, reason, blocked_at, unblocked_at
            FROM anvisa_batch_quarantines
            WHERE account_id = ? AND batch_number = ?
        """, (account_id, batch_number))
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "account_id": row["account_id"],
            "batch_number": row["batch_number"],
            "product_id": row["product_id"],
            "total_distributed": row["total_distributed"],
            "total_failures": row["total_failures"],
            "failure_rate_percent": row["failure_rate_percent"],
            "status": row["status"],
            "reason": row["reason"],
            "blocked_at": str(row["blocked_at"]),
            "unblocked_at": str(row["unblocked_at"]) if row["unblocked_at"] else None
        }
    finally:
        conn.close()


def list_anvisa_rma_claims(
    account_id: str = "0f14ffff",
    batch_number: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lista queixas técnicas e pedidos de reposição em garantia."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = "SELECT * FROM anvisa_rma_claims WHERE account_id = ?"
        params = [account_id]
        if batch_number:
            query += " AND batch_number = ?"
            params.append(batch_number)
        query += " ORDER BY created_at DESC"

        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        claims = []
        for r in rows:
            claims.append({
                "id": r["id"],
                "account_id": r["account_id"],
                "ticket_id": r["ticket_id"],
                "agreement_id": r["agreement_id"],
                "surgeon_name": r["surgeon_name"],
                "surgeon_cro_uf": r["surgeon_cro_uf"],
                "patient_identifier": r["patient_identifier"],
                "product_id": r["product_id"],
                "product_name": r["product_name"],
                "batch_number": r["batch_number"],
                "serial_number": r["serial_number"],
                "fdi_tooth_region": r["fdi_tooth_region"],
                "insertion_torque_ncm": r["insertion_torque_ncm"],
                "surgery_date": r["surgery_date"],
                "explant_date": r["explant_date"],
                "failure_reason": r["failure_reason"],
                "radiograph_r2_key": r["radiograph_r2_key"],
                "status": r["status"],
                "warranty_approved": bool(r["warranty_approved"]),
                "replacement_order_id": r["replacement_order_id"],
                "quarantine_triggered": bool(r["quarantine_triggered"]),
                "batch_failure_rate_percent": 0.0,
                "notes": r["notes"],
                "created_at": str(r["created_at"])
            })
        return claims
    finally:
        conn.close()


def get_anvisa_rma_claim(claim_id: str, account_id: str = "0f14ffff") -> Optional[Dict[str, Any]]:
    """Obtém detalhes de um processo de RMA por ID."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM anvisa_rma_claims WHERE id = ? AND account_id = ?", (claim_id, account_id))
        r = cur.fetchone()
        if not r:
            return None
        return {
            "id": r["id"],
            "account_id": r["account_id"],
            "ticket_id": r["ticket_id"],
            "agreement_id": r["agreement_id"],
            "surgeon_name": r["surgeon_name"],
            "surgeon_cro_uf": r["surgeon_cro_uf"],
            "patient_identifier": r["patient_identifier"],
            "product_id": r["product_id"],
            "product_name": r["product_name"],
            "batch_number": r["batch_number"],
            "serial_number": r["serial_number"],
            "fdi_tooth_region": r["fdi_tooth_region"],
            "insertion_torque_ncm": r["insertion_torque_ncm"],
            "surgery_date": r["surgery_date"],
            "explant_date": r["explant_date"],
            "failure_reason": r["failure_reason"],
            "radiograph_r2_key": r["radiograph_r2_key"],
            "status": r["status"],
            "warranty_approved": bool(r["warranty_approved"]),
            "replacement_order_id": r["replacement_order_id"],
            "quarantine_triggered": bool(r["quarantine_triggered"]),
            "batch_failure_rate_percent": 0.0,
            "notes": r["notes"],
            "created_at": str(r["created_at"])
        }
    finally:
        conn.close()
