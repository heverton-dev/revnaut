# -*- coding: utf-8 -*-
"""Nightly competitor-radar batch scheduler ledger (one tick per hourly slot and tenant).

Revision ID: 0004_add_market_intel_batch_ticks
Revises: 0003_add_users_region_code
Create Date: 2026-10-20 16:00:00
"""

from __future__ import annotations
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0004_add_market_intel_batch_ticks"
down_revision: Union[str, None] = "0003_add_users_region_code"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "market_intel_batch_ticks",
        sa.Column("slot_key", sa.String(), nullable=False),
        sa.Column("account_id", sa.String(), nullable=False),
        sa.Column("published_at", sa.String(), nullable=False),
        sa.Column("stream_message_id", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("slot_key", "account_id"),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("market_intel_batch_ticks", if_exists=True)
