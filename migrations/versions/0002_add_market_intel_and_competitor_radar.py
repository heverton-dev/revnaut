# -*- coding: utf-8 -*-
"""Market Intelligence, Competitor Radar and 15-day deterministic campaign dispatch (TICKET-MKTINTEL-01).

Revision ID: 0002_add_market_intel_and_competitor_radar
Revises: 0001_initial_schema
Create Date: 2026-10-20 08:00:00
"""

from __future__ import annotations
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002_add_market_intel_and_competitor_radar"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "market_signals",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), nullable=False, server_default="acc_default"),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("source_url", sa.String(), nullable=False, unique=True),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("raw_content", sa.Text(), nullable=False),
        sa.Column("structured_payload", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("geographic_scope", sa.String(), nullable=False, server_default="GLOBAL"),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.CheckConstraint(
            "source_type IN ('scientific_journal', 'regulatory_anvisa', 'congress_ciosp', 'news')",
            name="ck_market_signals_source_type",
        ),
        if_not_exists=True,
    )
    op.create_index("idx_mkt_signals_scope", "market_signals", ["account_id", "geographic_scope", "created_at"], if_not_exists=True)
    op.create_index("idx_mkt_signals_type", "market_signals", ["account_id", "source_type"], if_not_exists=True)

    op.create_table(
        "competitors",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), nullable=False, server_default="acc_default"),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("domain", sa.String(), nullable=False, unique=True),
        sa.Column("social_handles", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("active", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("crawl_frequency_hours", sa.Integer(), nullable=False, server_default="72"),
        sa.Column("last_scraped_at", sa.String(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=False),
        if_not_exists=True,
    )
    op.create_index("idx_competitors_acc", "competitors", ["account_id", "active"], if_not_exists=True)

    op.create_table(
        "competitor_snapshots",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), nullable=False, server_default="acc_default"),
        sa.Column("competitor_id", sa.String(), sa.ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("page_type", sa.String(), nullable=False),
        sa.Column("extracted_title", sa.String(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("detected_offers", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("tactical_summary", sa.Text(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.CheckConstraint(
            "page_type IN ('pricing_table', 'catalog', 'blog_post', 'social_ad')",
            name="ck_competitor_snapshots_page_type",
        ),
        if_not_exists=True,
    )
    op.create_index(
        "idx_comp_snap_lookup", "competitor_snapshots", ["account_id", "competitor_id", "page_type", "created_at"], if_not_exists=True
    )
    op.create_index("idx_comp_snap_hash", "competitor_snapshots", ["competitor_id", "content_hash"], if_not_exists=True)

    op.create_table(
        "market_opportunities",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), nullable=False, server_default="acc_default"),
        sa.Column("signal_id", sa.String(), sa.ForeignKey("market_signals.id", ondelete="SET NULL"), nullable=True),
        sa.Column(
            "competitor_snapshot_id", sa.String(), sa.ForeignKey("competitor_snapshots.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column("bu_target", sa.String(), nullable=False),
        sa.Column("recommended_product_ids", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("opportunity_type", sa.String(), nullable=False),
        sa.Column("suggested_action", sa.Text(), nullable=False),
        sa.Column("region_code", sa.String(), nullable=False, server_default="GLOBAL"),
        sa.Column("status", sa.String(), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.CheckConstraint("bu_target IN ('Implantodontia', 'Prótese Digital', 'Biomateriais')", name="ck_mkt_opp_bu"),
        sa.CheckConstraint(
            "opportunity_type IN ('PRICE_COUNTER_ATTACK', 'CLINICAL_UPGRADE', 'EVENT_SURGE')", name="ck_mkt_opp_type"
        ),
        sa.CheckConstraint("status IN ('PENDING', 'CAMPAIGN_TRIGGERED', 'DISMISSED')", name="ck_mkt_opp_status"),
        if_not_exists=True,
    )
    op.create_index(
        "idx_mkt_opp_filter", "market_opportunities", ["account_id", "region_code", "bu_target", "status"], if_not_exists=True
    )

    op.create_table(
        "targeted_campaigns",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), nullable=False, server_default="acc_default"),
        sa.Column(
            "opportunity_id", sa.String(), sa.ForeignKey("market_opportunities.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("target_audience_filter", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("message_template", sa.Text(), nullable=False),
        sa.Column("channel", sa.String(), nullable=False),
        sa.Column("dispatch_status", sa.String(), nullable=False, server_default="DRAFT"),
        sa.Column("scheduled_for", sa.String(), nullable=True),
        sa.Column("sent_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skipped_cooldown_15d_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by_user_id", sa.String(), nullable=True),
        sa.Column("approved_by_user_id", sa.String(), nullable=True),
        sa.Column("executed_at", sa.String(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.CheckConstraint("channel IN ('WHATSAPP', 'EMAIL')", name="ck_tgt_camp_channel"),
        sa.CheckConstraint("dispatch_status IN ('DRAFT', 'SCHEDULED', 'EXECUTED')", name="ck_tgt_camp_status"),
        if_not_exists=True,
    )
    op.create_index(
        "idx_tgt_camp_status", "targeted_campaigns", ["account_id", "dispatch_status", "created_at"], if_not_exists=True
    )

    op.create_table(
        "campaign_recipient_locks",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), nullable=False, server_default="acc_default"),
        sa.Column("contact_id", sa.String(), nullable=False),
        sa.Column("campaign_id", sa.String(), nullable=False),
        sa.Column("opportunity_id", sa.String(), nullable=True),
        sa.Column("channel", sa.String(), nullable=False),
        sa.Column("sent_at", sa.String(), nullable=False),
        if_not_exists=True,
    )
    op.create_index(
        "idx_camp_locks_contact", "campaign_recipient_locks", ["account_id", "contact_id", "sent_at"], if_not_exists=True
    )
    op.create_index("idx_camp_locks_campaign", "campaign_recipient_locks", ["campaign_id"], if_not_exists=True)


def downgrade() -> None:
    for idx, tbl in [
        ("idx_camp_locks_campaign", "campaign_recipient_locks"),
        ("idx_camp_locks_contact", "campaign_recipient_locks"),
        ("idx_tgt_camp_status", "targeted_campaigns"),
        ("idx_mkt_opp_filter", "market_opportunities"),
        ("idx_comp_snap_hash", "competitor_snapshots"),
        ("idx_comp_snap_lookup", "competitor_snapshots"),
        ("idx_competitors_acc", "competitors"),
        ("idx_mkt_signals_type", "market_signals"),
        ("idx_mkt_signals_scope", "market_signals"),
    ]:
        op.drop_index(idx, table_name=tbl, if_exists=True)
    for tbl in [
        "campaign_recipient_locks",
        "targeted_campaigns",
        "market_opportunities",
        "competitor_snapshots",
        "competitors",
        "market_signals",
    ]:
        op.drop_table(tbl, if_exists=True)
