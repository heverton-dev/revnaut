# -*- coding: utf-8 -*-
"""
Vertical Slice: KeyPartners Loyalty Engine ("Moeda Cirúrgica")
Razão de pontos e recompensas técnicas para cirurgiões parceiros.
Progressão automática de tiers (SILVER -> GOLD -> BLACK_KOL) e resgate de vouchers no DENTGO.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.core.database import get_connection, init_db


DEFAULT_REWARDS = [
    {
        "id": "rew-dentgo-express",
        "name": "Voucher Frete Express Grátis DENTGO",
        "reward_type": "DENTGO_EXPRESS_VOUCHER",
        "points_cost": 500,
        "monetary_value_equivalent": 85.0
    },
    {
        "id": "rew-guided-kit",
        "name": "Abatimento na Locação de Kit Cirurgia Guiada",
        "reward_type": "GUIDED_SURGERY_KIT",
        "points_cost": 2000,
        "monetary_value_equivalent": 350.0
    },
    {
        "id": "rew-motor-rental",
        "name": "Diária de Locação de Motor Cirúrgico Odontológico",
        "reward_type": "MOTOR_RENTAL_DISCOUNT",
        "points_cost": 3000,
        "monetary_value_equivalent": 500.0
    },
    {
        "id": "rew-immersion-course",
        "name": "Inscrição em Imersão Cirúrgica Avançada",
        "reward_type": "IMMERSION_COURSE",
        "points_cost": 5000,
        "monetary_value_equivalent": 1200.0
    }
]


def ensure_rewards_catalog(conn, account_id: str = "0f14ffff") -> None:
    """Garante que o catálogo inicial de recompensas esteja populado."""
    cur = conn.cursor()
    for rew in DEFAULT_REWARDS:
        cur.execute("""
            INSERT OR IGNORE INTO kp_loyalty_rewards_catalog (
                id, account_id, name, reward_type, points_cost, monetary_value_equivalent, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (rew["id"], account_id, rew["name"], rew["reward_type"], rew["points_cost"], rew["monetary_value_equivalent"]))


def _compute_tier(implants_billed_total: int) -> str:
    """Classifica o parceiro no tier correspondente pelo volume de implantes faturados."""
    if implants_billed_total >= 100:
        return "BLACK_KOL"
    if implants_billed_total >= 25:
        return "GOLD"
    return "SILVER"


def credit_loyalty_points(
    partner_id: str,
    partner_name: str,
    implants_count: int,
    event_origin: str = "deal.won",
    reference_id: Optional[str] = None,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Credita Moedas Cirúrgicas (100 pontos por implante faturado).
    Atualiza total de implantes, avalia progressão de tier e registra transação imutável.
    """
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        ensure_rewards_catalog(conn, account_id)

        # 1. Obtém ou cria a carteira do parceiro
        cur.execute("""
            SELECT * FROM kp_loyalty_wallets WHERE partner_id = ? AND account_id = ?
        """, (partner_id, account_id))
        wallet_row = cur.fetchone()

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        if not wallet_row:
            wallet_id = f"wal_{uuid.uuid4().hex[:10]}"
            cur.execute("""
                INSERT INTO kp_loyalty_wallets (
                    id, account_id, partner_id, partner_name, points_balance,
                    lifetime_points, current_tier, implants_billed_total, created_at, updated_at
                ) VALUES (?, ?, ?, ?, 0, 0, 'SILVER', 0, ?, ?)
            """, (wallet_id, account_id, partner_id, partner_name, now_str, now_str))
            cur.execute("SELECT * FROM kp_loyalty_wallets WHERE id = ?", (wallet_id,))
            wallet_row = cur.fetchone()

        old_tier = wallet_row["current_tier"]
        current_balance = int(wallet_row["points_balance"])
        current_lifetime = int(wallet_row["lifetime_points"])
        current_implants = int(wallet_row["implants_billed_total"])

        points_earned = int(implants_count) * 100
        new_balance = current_balance + points_earned
        new_lifetime = current_lifetime + points_earned
        new_implants = current_implants + int(implants_count)
        new_tier = _compute_tier(new_implants)
        tier_promoted = new_tier != old_tier

        # 2. Atualiza a carteira
        cur.execute("""
            UPDATE kp_loyalty_wallets
            SET points_balance = ?,
                lifetime_points = ?,
                implants_billed_total = ?,
                current_tier = ?,
                updated_at = ?
            WHERE id = ?
        """, (new_balance, new_lifetime, new_implants, new_tier, now_str, wallet_row["id"]))

        # 3. Registra transação no razão imutável
        tx_id = f"tx_cred_{uuid.uuid4().hex[:10]}"
        desc = f"Credito de {points_earned} Moedas Cirurgicas ({implants_count} implantes via {event_origin})"
        cur.execute("""
            INSERT INTO kp_loyalty_transactions (
                id, account_id, wallet_id, partner_id, transaction_type, event_origin,
                points, balance_after, description, reference_id, created_at
            ) VALUES (?, ?, ?, ?, 'CREDIT', ?, ?, ?, ?, ?, ?)
        """, (tx_id, account_id, wallet_row["id"], partner_id, event_origin, points_earned, new_balance, desc, reference_id, now_str))

        conn.commit()

        return {
            "wallet_id": wallet_row["id"],
            "partner_id": partner_id,
            "partner_name": partner_name,
            "points_earned": points_earned,
            "points_balance": new_balance,
            "lifetime_points": new_lifetime,
            "implants_billed_total": new_implants,
            "previous_tier": old_tier,
            "current_tier": new_tier,
            "tier_promoted": tier_promoted,
            "transaction_id": tx_id
        }
    finally:
        conn.close()


def redeem_loyalty_reward(
    partner_id: str,
    reward_type_or_id: str,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Resgata uma recompensa técnica abatendo pontos da carteira.
    Gera voucher único utilizável no DENTGO ou em ordens comerciais.
    """
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        ensure_rewards_catalog(conn, account_id)

        # 1. Busca carteira
        cur.execute("""
            SELECT * FROM kp_loyalty_wallets WHERE partner_id = ? AND account_id = ?
        """, (partner_id, account_id))
        wallet = cur.fetchone()
        if not wallet:
            raise ValueError(f"Carteira de Moedas Cirúrgicas não encontrada para o parceiro '{partner_id}'")

        # 2. Busca item do catálogo
        cur.execute("""
            SELECT * FROM kp_loyalty_rewards_catalog
            WHERE (id = ? OR reward_type = ?) AND account_id = ? AND is_active = 1
            LIMIT 1
        """, (reward_type_or_id, reward_type_or_id, account_id))
        reward = cur.fetchone()
        if not reward:
            # Fallback para recompensa padrão DENTGO
            reward = DEFAULT_REWARDS[0]

        points_cost = int(reward["points_cost"])
        current_balance = int(wallet["points_balance"])

        if current_balance < points_cost:
            raise ValueError(f"Saldo insuficiente ({current_balance} Moedas). Necessario {points_cost} Moedas.")

        new_balance = current_balance - points_cost
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # 3. Debita carteira
        cur.execute("""
            UPDATE kp_loyalty_wallets
            SET points_balance = ?, updated_at = ?
            WHERE id = ?
        """, (new_balance, now_str, wallet["id"]))

        # 4. Registra transação de débito
        clean_code = uuid.uuid4().hex[:8].upper()
        voucher_code = f"MOEDA-EXPRESS-{clean_code}"
        tx_id = f"tx_deb_{uuid.uuid4().hex[:10]}"
        desc = f"Resgate de recompensa '{reward['name']}' ({points_cost} Moedas) - Voucher: {voucher_code}"

        cur.execute("""
            INSERT INTO kp_loyalty_transactions (
                id, account_id, wallet_id, partner_id, transaction_type, event_origin,
                points, balance_after, description, reference_id, created_at
            ) VALUES (?, ?, ?, ?, 'DEBIT', 'reward.redemption', ?, ?, ?, ?, ?)
        """, (tx_id, account_id, wallet["id"], partner_id, -points_cost, new_balance, desc, voucher_code, now_str))

        conn.commit()

        return {
            "partner_id": partner_id,
            "reward_name": reward["name"],
            "reward_type": reward["reward_type"],
            "points_debited": points_cost,
            "points_balance_remaining": new_balance,
            "voucher_code": voucher_code,
            "monetary_value_equivalent": float(reward["monetary_value_equivalent"]),
            "transaction_id": tx_id,
            "redeemed_at": now_str
        }
    finally:
        conn.close()


def get_partner_loyalty_wallet(partner_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Retorna detalhes da carteira de fidelidade e histórico recente de transações."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        ensure_rewards_catalog(conn, account_id)

        cur.execute("""
            SELECT * FROM kp_loyalty_wallets WHERE partner_id = ? AND account_id = ?
        """, (partner_id, account_id))
        wallet = cur.fetchone()
        if not wallet:
            return {
                "partner_id": partner_id,
                "partner_name": "Parceiro",
                "points_balance": 0,
                "lifetime_points": 0,
                "current_tier": "SILVER",
                "implants_billed_total": 0,
                "transactions": []
            }

        cur.execute("""
            SELECT * FROM kp_loyalty_transactions
            WHERE wallet_id = ? AND account_id = ?
            ORDER BY created_at DESC LIMIT 15
        """, (wallet["id"], account_id))
        transactions = [dict(r) for r in cur.fetchall()]

        return {
            "wallet_id": wallet["id"],
            "partner_id": wallet["partner_id"],
            "partner_name": wallet["partner_name"],
            "points_balance": wallet["points_balance"],
            "lifetime_points": wallet["lifetime_points"],
            "current_tier": wallet["current_tier"],
            "implants_billed_total": wallet["implants_billed_total"],
            "transactions": transactions
        }
    finally:
        conn.close()


def list_rewards_catalog(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    """Lista catálogo de recompensas disponíveis para resgate."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        ensure_rewards_catalog(conn, account_id)
        cur.execute("""
            SELECT * FROM kp_loyalty_rewards_catalog
            WHERE account_id = ? AND is_active = 1
            ORDER BY points_cost ASC
        """, (account_id,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
