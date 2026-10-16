# -*- coding: utf-8 -*-
"""
Vertical Slice: Campaigns Service (SQLite WAL)
Motor de Atribuição de Mídia, Métricas de ROAS/CAC e UTMs.
"""

from __future__ import annotations
import uuid
from typing import Any, Dict, List, Optional
from src.core.database import get_connection
from src.features.campaigns.schemas import CampaignCreate


def _enrich_campaign(row: Dict[str, Any]) -> Dict[str, Any]:
    spend = float(row.get("spend") or 0.0)
    revenue = float(row.get("revenue") or 0.0)
    leads = int(row.get("leads_count") or 0)
    deals = int(row.get("deals_count") or 0)

    roas = round(revenue / spend, 2) if spend > 0 else 0.0
    cac = round(spend / deals, 2) if deals > 0 else 0.0
    conversion_rate = round((deals / leads) * 100, 2) if leads > 0 else 0.0

    data = dict(row)
    data["roas"] = roas
    data["cac"] = cac
    data["conversion_rate"] = conversion_rate
    return data


def list_campaigns(account_id: str = "0f14ffff", status: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    if status:
        cur.execute(
            "SELECT id, account_id, name, channel, utm_source, utm_medium, utm_campaign, "
            "budget, spend, revenue, leads_count, deals_count, status, created_at "
            "FROM campaigns WHERE account_id = ? AND status = ? ORDER BY created_at DESC",
            (account_id, status)
        )
    else:
        cur.execute(
            "SELECT id, account_id, name, channel, utm_source, utm_medium, utm_campaign, "
            "budget, spend, revenue, leads_count, deals_count, status, created_at "
            "FROM campaigns WHERE account_id = ? ORDER BY created_at DESC",
            (account_id,)
        )
    rows = cur.fetchall()
    conn.close()
    return [_enrich_campaign(dict(r)) for r in rows]


def create_campaign(data: CampaignCreate, account_id: str = "0f14ffff") -> Dict[str, Any]:
    camp_id = f"camp-{uuid.uuid4().hex[:6]}"
    conn = get_connection()
    with conn:
        conn.execute(
            "INSERT INTO campaigns (id, account_id, name, channel, utm_source, utm_medium, utm_campaign, "
            "budget, spend, revenue, leads_count, deals_count, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                camp_id,
                account_id,
                data.name,
                data.channel,
                data.utm_source,
                data.utm_medium,
                data.utm_campaign,
                data.budget,
                data.spend,
                data.revenue,
                data.leads_count,
                data.deals_count,
                data.status
            )
        )
        cur = conn.cursor()
        cur.execute(
            "SELECT id, account_id, name, channel, utm_source, utm_medium, utm_campaign, "
            "budget, spend, revenue, leads_count, deals_count, status, created_at "
            "FROM campaigns WHERE id = ?",
            (camp_id,)
        )
        row = cur.fetchone()
    conn.close()
    return _enrich_campaign(dict(row))


def get_campaign_metrics(account_id: str = "0f14ffff") -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT SUM(budget) as total_budget, SUM(spend) as total_spend, SUM(revenue) as total_revenue, "
        "SUM(leads_count) as total_leads, SUM(deals_count) as total_deals, "
        "COUNT(CASE WHEN status = 'ativa' THEN 1 END) as active_count "
        "FROM campaigns WHERE account_id = ?",
        (account_id,)
    )
    row = cur.fetchone()
    conn.close()

    total_budget = float(row["total_budget"] or 0.0)
    total_spend = float(row["total_spend"] or 0.0)
    total_revenue = float(row["total_revenue"] or 0.0)
    total_leads = int(row["total_leads"] or 0)
    total_deals = int(row["total_deals"] or 0)
    active_count = int(row["active_count"] or 0)

    avg_roas = round(total_revenue / total_spend, 2) if total_spend > 0 else 0.0
    avg_cac = round(total_spend / total_deals, 2) if total_deals > 0 else 0.0

    return {
        "total_budget": total_budget,
        "total_spend": total_spend,
        "total_revenue": total_revenue,
        "avg_roas": avg_roas,
        "avg_cac": avg_cac,
        "total_leads": total_leads,
        "total_deals": total_deals,
        "active_campaigns_count": active_count
    }
