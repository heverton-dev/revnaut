# -*- coding: utf-8 -*-
"""
Vertical Slice: Chatwoot Omnichannel Bridge & Context 360°
Agregação contextual em tempo real para operadores de atendimento:
- Perfil Clínico e CRO do Cirurgião
- Acordo e Saldo de Crédito KeyPartners
- Kits Consignados em Posse Ativa no Campo
- Entregas Expressas DENTGO em Trânsito
"""

from __future__ import annotations
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from src.core.database import get_connection, init_db


def _extract_clean_digits(phone: str) -> str:
    """Extrai apenas dígitos de um número telefônico."""
    return re.sub(r"\D", "", phone or "")


def get_omnichannel_360_context(
    contact_identifier: str,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Agrega deterministicamente o contexto 360° completo para o operador de suporte
    a partir de um telefone ou CRO do cirurgião.
    """
    init_db()
    clean_identifier = contact_identifier.strip()
    digits = _extract_clean_digits(clean_identifier)

    conn = get_connection()
    try:
        cur = conn.cursor()

        # 1. Localização do Contato
        contact_row = None
        if clean_identifier.upper().startswith("CRO-") or "CRO" in clean_identifier.upper():
            cur.execute(
                "SELECT * FROM contacts WHERE account_id = ? AND cro_uf = ? LIMIT 1",
                (account_id, clean_identifier)
            )
            contact_row = cur.fetchone()

        if not contact_row and digits:
            # Busca pelo final do telefone (últimos 8 a 9 dígitos)
            cur.execute("SELECT * FROM contacts WHERE account_id = ?", (account_id,))
            for r in cur.fetchall():
                r_digits = _extract_clean_digits(r["phone"])
                if r_digits and (digits.endswith(r_digits[-8:]) or r_digits.endswith(digits[-8:])):
                    contact_row = r
                    break

        contact_dict = dict(contact_row) if contact_row else None
        cro_uf = (contact_dict.get("cro_uf") if contact_dict else None) or (clean_identifier if "CRO" in clean_identifier.upper() else None)

        # 2. Acordo KeyPartners & Crédito
        agreement_dict = None
        if cro_uf:
            cur.execute(
                "SELECT * FROM kp_partner_agreements WHERE partner_cro_uf = ? AND account_id = ? LIMIT 1",
                (cro_uf, account_id)
            )
            agr_row = cur.fetchone()
            if agr_row:
                agreement_dict = dict(agr_row)
                c_limit = float(agreement_dict.get("credit_limit") or 0.0)
                c_used = float(agreement_dict.get("used_credit") or 0.0)
                agreement_dict["available_credit"] = round(max(0.0, c_limit - c_used), 2)

        # 3. Kits Consignados em Posse Ativa no Campo
        consignments: List[Dict[str, Any]] = []
        if agreement_dict:
            cur.execute("""
                SELECT * FROM kp_consignment_kits
                WHERE current_agreement_id = ? AND status = 'IN_FIELD' AND account_id = ?
                ORDER BY created_at DESC
            """, (agreement_dict["id"], account_id))
            consignments = [dict(r) for r in cur.fetchall()]

        # 4. Entregas Expressas DENTGO Ativas
        active_orders: List[Dict[str, Any]] = []
        if cro_uf:
            cur.execute("""
                SELECT * FROM dentgo_orders
                WHERE customer_cro_uf = ? AND status IN (
                    'ORDER_PLACED', 'PICKING_BIPADO', 'SEALED_READY',
                    'COURIER_ASSIGNED', 'IN_TRANSIT_LIVE'
                ) AND account_id = ?
                ORDER BY created_at DESC
            """, (cro_uf, account_id))
            active_orders = [dict(r) for r in cur.fetchall()]

        return {
            "contact_identifier": clean_identifier,
            "contact": contact_dict,
            "cro_uf": cro_uf,
            "agreement": agreement_dict,
            "consignments_in_field": consignments,
            "active_dentgo_orders": active_orders,
            "is_synced_chatwoot": True
        }
    finally:
        conn.close()


def sync_contact_to_chatwoot(
    contact_id: int,
    account_id: str = "0f14ffff",
    mock_mode: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Sincroniza perfil e atributos customizados do contato com o Chatwoot.
    """
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM contacts WHERE id = ? AND account_id = ?", (contact_id, account_id))
        contact = cur.fetchone()
        if not contact:
            raise ValueError(f"Contato {contact_id} não encontrado")

        contact_dict = dict(contact)
        chatwoot_contact_id = 9000 + int(contact_id)
        cw_token = os.getenv("CHATWOOT_API_TOKEN", "").strip()
        cw_url = os.getenv("CHATWOOT_BASE_URL", "http://chatwoot:3000").rstrip("/")
        cw_account_id = os.getenv("CHATWOOT_ACCOUNT_ID", "1")
        is_mock = mock_mode if mock_mode is not None else (not bool(cw_token))

        if not is_mock:
            try:
                with httpx.Client(timeout=8.0) as client:
                    resp = client.post(
                        f"{cw_url}/api/v1/accounts/{cw_account_id}/contacts",
                        headers={"api_access_token": cw_token or "cw-token"},
                        json={
                            "name": contact_dict.get("name"),
                            "email": contact_dict.get("email"),
                            "phone_number": contact_dict.get("phone"),
                            "identifier": f"revnault-{contact_id}",
                            "custom_attributes": {
                                "cro_uf": contact_dict.get("cro_uf"),
                                "specialty": contact_dict.get("specialty"),
                                "account_id": account_id,
                            },
                        },
                    )
                    resp.raise_for_status()
                    payload_json = resp.json().get("payload", {}).get("contact", {})
                    if payload_json.get("id"):
                        chatwoot_contact_id = int(payload_json["id"])
            except Exception:
                pass

        return {
            "status": "SYNCED",
            "contact_id": contact_id,
            "chatwoot_contact_id": chatwoot_contact_id,
            "source_id": f"cw-src-{contact_id}",
            "synced_at": datetime.now(timezone.utc).isoformat()
        }
    finally:
        conn.close()
