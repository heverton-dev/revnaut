# -*- coding: utf-8 -*-
"""
Vertical Slice: Scoring Service (SQLite WAL)
Motor de Lead Scoring Determinístico e Classificação ICP.
"""

from __future__ import annotations
import json
import uuid
from typing import Any, Dict, List, Optional
from src.core.database import get_connection
from src.features.scoring.schemas import ScoringRuleCreate, ScoringRuleUpdate, RecalculateResponse, LeadRankItem


def list_rules(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, account_id, name, category, condition_key, condition_val, points, "
        "impact_description, is_active, created_at "
        "FROM scoring_rules WHERE account_id = ? ORDER BY points DESC, created_at ASC",
        (account_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_rule(data: ScoringRuleCreate, account_id: str = "0f14ffff") -> Dict[str, Any]:
    rule_id = f"sr-{uuid.uuid4().hex[:6]}"
    conn = get_connection()
    with conn:
        conn.execute(
            "INSERT INTO scoring_rules (id, account_id, name, category, condition_key, condition_val, "
            "points, impact_description, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                rule_id,
                account_id,
                data.name,
                data.category,
                data.condition_key,
                data.condition_val,
                data.points,
                data.impact_description,
                data.is_active
            )
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM scoring_rules WHERE id = ?", (rule_id,))
        row = cur.fetchone()
    conn.close()
    return dict(row)


def update_rule(rule_id: str, data: ScoringRuleUpdate) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM scoring_rules WHERE id = ?", (rule_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return None

        current = dict(row)
        name = data.name if data.name is not None else current["name"]
        category = data.category if data.category is not None else current["category"]
        c_key = data.condition_key if data.condition_key is not None else current["condition_key"]
        c_val = data.condition_val if data.condition_val is not None else current["condition_val"]
        points = data.points if data.points is not None else current["points"]
        impact = data.impact_description if data.impact_description is not None else current["impact_description"]
        active = data.is_active if data.is_active is not None else current["is_active"]

        cur.execute(
            "UPDATE scoring_rules SET name = ?, category = ?, condition_key = ?, condition_val = ?, "
            "points = ?, impact_description = ?, is_active = ? WHERE id = ?",
            (name, category, c_key, c_val, points, impact, active, rule_id)
        )
        cur.execute("SELECT * FROM scoring_rules WHERE id = ?", (rule_id,))
        updated_row = cur.fetchone()
    conn.close()
    return dict(updated_row) if updated_row else None


def delete_rule(rule_id: str) -> bool:
    conn = get_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM scoring_rules WHERE id = ?", (rule_id,))
        deleted = cur.rowcount > 0
    conn.close()
    return deleted


def recalculate_all_scores(account_id: str = "0f14ffff") -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()

    # 1. Obter regras ativas
    cur.execute(
        "SELECT condition_key, condition_val, points FROM scoring_rules WHERE account_id = ? AND is_active = 1",
        (account_id,)
    )
    rules = [dict(r) for r in cur.fetchall()]

    # 2. Obter contatos e conversas
    cur.execute("SELECT id, name, email, phone, company, tags, score FROM contacts WHERE account_id = ?", (account_id,))
    contacts = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT contact_name, company FROM conversations WHERE account_id = ?", (account_id,))
    convs = [dict(r) for r in cur.fetchall()]
    conv_contacts = {c["contact_name"].lower() for c in convs} | {c["company"].lower() for c in convs}

    ranked: List[Dict[str, Any]] = []
    tier_a = 0
    tier_b = 0
    tier_c = 0
    total_score_sum = 0

    with conn:
        for c in contacts:
            score = 20  # Base inicial de contato verificado
            tags_list = []
            try:
                raw_tags = c.get("tags") or "[]"
                tags_list = json.loads(raw_tags) if isinstance(raw_tags, str) else list(raw_tags)
            except Exception:
                tags_list = []

            tags_lower = [t.lower() for t in tags_list]
            company_lower = (c.get("company") or "").lower()
            name_lower = (c.get("name") or "").lower()

            for r in rules:
                key = r["condition_key"].lower()
                targets = [v.strip().lower() for v in r["condition_val"].split(",") if v.strip()]
                pts = int(r["points"])

                if key in ("tag", "source"):
                    if any(target in tag for target in targets for tag in tags_lower):
                        score += pts
                elif key == "company":
                    if any(target in company_lower for target in targets):
                        score += pts
                elif key == "interaction":
                    if name_lower in conv_contacts or company_lower in conv_contacts:
                        score += pts

            # Limita entre 0 e 100
            final_score = max(0, min(100, score))
            total_score_sum += final_score

            tier = "Tier A" if final_score >= 80 else ("Tier B" if final_score >= 50 else "Tier C")
            if tier == "Tier A":
                tier_a += 1
            elif tier == "Tier B":
                tier_b += 1
            else:
                tier_c += 1

            conn.execute("UPDATE contacts SET score = ? WHERE id = ?", (final_score, c["id"]))

            ranked.append({
                "id": c["id"],
                "name": c["name"],
                "company": c["company"],
                "email": c["email"],
                "score": final_score,
                "tier": tier,
                "tags": tags_list
            })

    conn.close()

    ranked.sort(key=lambda x: x["score"], reverse=True)
    avg_score = round(total_score_sum / len(ranked), 1) if ranked else 0.0

    return {
        "recalculated_count": len(ranked),
        "tier_a_count": tier_a,
        "tier_b_count": tier_b,
        "tier_c_count": tier_c,
        "avg_score": avg_score,
        "ranked_leads": ranked
    }
