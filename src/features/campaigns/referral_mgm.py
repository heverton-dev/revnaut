# -*- coding: utf-8 -*-
"""
Vertical Slice: Member-Get-Member (MGM) Referral Engine B2B
Loop viral de indicação entre cirurgiões-dentistas com validação de CRO,
prevenção contra auto-indicação, aceleração de lead scoring (+40 pts) e bonificação mútua no deal.won.
"""

from __future__ import annotations
import uuid
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.core.database import get_connection, init_db
from src.features.contacts.cro_validator import validate_cro_syntax
from src.features.keypartners import loyalty_engine


def generate_referral_link(
    referrer_id: str,
    referrer_name: str,
    referrer_cro_uf: str,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Gera link único de indicação B2B para o cirurgião promotor.
    Dispara convite personalizado no WhatsApp para compartilhamento com colegas de pós/CRO.
    """
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()

        # Verifica se já possui link ativo
        cur.execute("""
            SELECT * FROM referral_links
            WHERE referrer_id = ? AND account_id = ?
        """, (referrer_id, account_id))
        existing = cur.fetchone()
        if existing:
            return dict(existing)

        clean_cro = referrer_cro_uf.replace(" ", "-").replace("/", "-").upper()
        referral_code = f"MGM-{clean_cro}"
        referral_url = f"https://revnault.app.br/r/{referral_code}"
        link_id = f"reflink_{uuid.uuid4().hex[:10]}"
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("""
            INSERT INTO referral_links (
                id, account_id, referrer_id, referrer_name, referrer_cro_uf, referral_code, referral_url, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (link_id, account_id, referrer_id, referrer_name, referrer_cro_uf, referral_code, referral_url, now_str))

        # Dispara mensagem de WhatsApp com o convite pronto
        wa_msg_id = f"wa_ref_{uuid.uuid4().hex[:8]}"
        wa_content = (
            f"Dr(a). {referrer_name}, seu link exclusivo do Programa de Indicação KeyPartners está ativo: {referral_url}. "
            "Ao indicar um colega cirurgião, ambos recebem R$ 600 em bonificação na primeira cirurgia."
        )
        cur.execute("""
            INSERT INTO omnichannel_messages (
                id, account_id, instance_name, remote_jid, sender_phone, message_type, content, from_me
            ) VALUES (?, ?, 'default_instance', 'clinic@c.us', '551199999999', 'text', ?, 1)
        """, (wa_msg_id, account_id, wa_content))

        conn.commit()

        return {
            "id": link_id,
            "account_id": account_id,
            "referrer_id": referrer_id,
            "referrer_name": referrer_name,
            "referrer_cro_uf": referrer_cro_uf,
            "referral_code": referral_code,
            "referral_url": referral_url,
            "created_at": now_str
        }
    finally:
        conn.close()


def register_referral_lead(
    referral_code: str,
    referred_name: str,
    referred_cro_uf: str,
    referred_phone: Optional[str] = None,
    referred_email: Optional[str] = None,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Cadastra colega cirurgião indicado via link de indicação MGM.
    Valida prevenção contra auto-indicação e acelera o lead score em +40 pontos.
    """
    init_db()
    cro_check = validate_cro_syntax(referred_cro_uf)
    if not cro_check.get("is_valid"):
        raise ValueError(f"CRO inválido para indicação B2B: '{referred_cro_uf}'.")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM referral_links WHERE referral_code = ? AND account_id = ?
        """, (referral_code, account_id))
        ref_link = cur.fetchone()
        if not ref_link:
            raise ValueError(f"Link de indicação com código '{referral_code}' não encontrado.")

        # Trava inquebrável contra auto-indicação
        clean_ref_cro = ref_link["referrer_cro_uf"].strip().upper()
        clean_cand_cro = referred_cro_uf.strip().upper()
        if clean_ref_cro == clean_cand_cro:
            raise ValueError("Auto-indicação proibida: o indicado possui o mesmo CRO/UF do indicador.")

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # 1. Cria ou atualiza Contato no CRM com Lead Score acelerado (+40 pts)
        cur.execute("SELECT id FROM contacts WHERE cro_uf = ? AND account_id = ?", (clean_cand_cro, account_id))
        contact_row = cur.fetchone()
        if contact_row:
            contact_id = str(contact_row["id"])
            cur.execute("""
                UPDATE contacts
                SET tags = '["origem_indicacao_kol"]',
                    score = MIN(100, COALESCE(score, 10) + 40)
                WHERE id = ?
            """, (contact_id,))
        else:
            cur.execute("""
                INSERT INTO contacts (
                    account_id, name, email, phone, cro_uf, tags, score
                ) VALUES (?, ?, ?, ?, ?, '["origem_indicacao_kol"]', 50)
            """, (
                account_id,
                referred_name,
                referred_email or f"{clean_cand_cro.lower().replace(' ', '')}@clinica.com.br",
                referred_phone or "+5511999998888",
                clean_cand_cro
            ))
            contact_id = str(cur.lastrowid)

        # 2. Registra conversão de indicação
        conversion_id = f"refconv_{uuid.uuid4().hex[:10]}"
        cur.execute("""
            INSERT INTO referral_conversions (
                id, account_id, referral_link_id, referrer_id, referred_contact_id,
                referred_name, referred_cro_uf, lead_id, lead_score_boost, tags,
                status, referrer_bonus_amount, referred_bonus_amount, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 40, '["origem_indicacao_kol"]', 'LEAD_CAPTURED', 600.0, 600.0, ?)
        """, (
            conversion_id,
            account_id,
            ref_link["id"],
            ref_link["referrer_id"],
            contact_id,
            referred_name,
            clean_cand_cro,
            contact_id,
            now_str
        ))
        conn.commit()

        return {
            "conversion_id": conversion_id,
            "referral_code": referral_code,
            "referrer_id": ref_link["referrer_id"],
            "referrer_name": ref_link["referrer_name"],
            "referred_contact_id": contact_id,
            "referred_name": referred_name,
            "referred_cro_uf": clean_cand_cro,
            "lead_score_boost": 40,
            "status": "LEAD_CAPTURED",
            "message": "Cirurgião indicado cadastrado com sucesso. Bônus de R$ 600 liberado após primeiro Deal faturado."
        }
    finally:
        conn.close()


def qualify_referral_deal_won(
    deal_id: str,
    referred_cro_uf: Optional[str] = None,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Processa o fechamento do primeiro Deal do indicado:
    Libera R$ 600 em bonificação (Moedas Cirúrgicas) para o indicador e para o indicado.
    """
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()

        if referred_cro_uf:
            clean_cro = referred_cro_uf.strip().upper()
            cur.execute("""
                SELECT * FROM referral_conversions
                WHERE referred_cro_uf = ? AND account_id = ?
                ORDER BY created_at DESC LIMIT 1
            """, (clean_cro, account_id))
        else:
            cur.execute("""
                SELECT * FROM referral_conversions
                WHERE account_id = ? AND (first_deal_id = ? OR status = 'LEAD_CAPTURED')
                ORDER BY created_at DESC LIMIT 1
            """, (account_id, deal_id))

        conv = cur.fetchone()
        if not conv:
            raise ValueError("Nenhuma indicação pendente encontrada para qualificação.")

        if conv["status"] == "BONUS_CREDITED":
            return {
                "status": "ALREADY_CREDITED",
                "conversion_id": conv["id"],
                "referrer_bonus_amount": conv["referrer_bonus_amount"],
                "referred_bonus_amount": conv["referred_bonus_amount"],
                "message": "Bonificação já havia sido creditada para esta indicação."
            }

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # Atualiza status da conversão
        cur.execute("""
            UPDATE referral_conversions
            SET status = 'BONUS_CREDITED',
                first_deal_id = ?,
                qualified_at = ?
            WHERE id = ?
        """, (deal_id, now_str, conv["id"]))
        conn.commit()

        # Credita R$ 600 em Moedas Cirúrgicas (600 pts) para o indicador
        cur.execute("SELECT referrer_name FROM referral_links WHERE id = ?", (conv["referral_link_id"],))
        link_row = cur.fetchone()
        referrer_name = link_row["referrer_name"] if link_row else "Indicador"

        loyalty_engine.credit_loyalty_points(
            partner_id=conv["referrer_id"],
            partner_name=referrer_name,
            implants_count=6,  # 6 * 100 = 600 pontos = R$ 600 de bônus
            event_origin="deal.won",
            reference_id=deal_id,
            account_id=account_id
        )

        # Credita R$ 600 em Moedas Cirúrgicas (600 pts) para o indicado
        loyalty_engine.credit_loyalty_points(
            partner_id=str(conv["referred_contact_id"]),
            partner_name=conv["referred_name"],
            implants_count=6,  # 6 * 100 = 600 pontos = R$ 600 de bônus
            event_origin="deal.won",
            reference_id=deal_id,
            account_id=account_id
        )

        return {
            "status": "BONUS_CREDITED",
            "conversion_id": conv["id"],
            "deal_id": deal_id,
            "referrer_id": conv["referrer_id"],
            "referred_contact_id": conv["referred_contact_id"],
            "referrer_bonus_amount": 600.0,
            "referred_bonus_amount": 600.0,
            "qualified_at": now_str,
            "message": "Bônus de R$ 600 creditado com sucesso para indicador e indicado."
        }
    finally:
        conn.close()


def get_referral_dashboard(referrer_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Retorna métricas de indicações e lista de colegas convidados."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM referral_links WHERE referrer_id = ? AND account_id = ?
        """, (referrer_id, account_id))
        link = cur.fetchone()
        if not link:
            return {
                "referrer_id": referrer_id,
                "total_referrals": 0,
                "qualified_referrals": 0,
                "total_bonus_earned": 0.0,
                "referral_url": None,
                "conversions": []
            }

        cur.execute("""
            SELECT * FROM referral_conversions
            WHERE referrer_id = ? AND account_id = ?
            ORDER BY created_at DESC
        """, (referrer_id, account_id))
        conversions = [dict(r) for r in cur.fetchall()]

        total_refs = len(conversions)
        qualified_refs = sum(1 for c in conversions if c["status"] == "BONUS_CREDITED")
        total_bonus = sum(float(c["referrer_bonus_amount"]) for c in conversions if c["status"] == "BONUS_CREDITED")

        return {
            "referrer_id": referrer_id,
            "referral_code": link["referral_code"],
            "referral_url": link["referral_url"],
            "total_referrals": total_refs,
            "qualified_referrals": qualified_refs,
            "total_bonus_earned": total_bonus,
            "conversions": conversions
        }
    finally:
        conn.close()
