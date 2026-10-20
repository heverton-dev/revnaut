# -*- coding: utf-8 -*-
"""Territorial region of each user for the Market Intel RBAC matrix (TICKET-MKTINTEL-06).

Revision ID: 0003_add_users_region_code
Revises: 0002_add_market_intel_and_competitor_radar
Create Date: 2026-10-20 14:00:00
"""

from __future__ import annotations
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0003_add_users_region_code"
down_revision: Union[str, None] = "0002_add_market_intel_and_competitor_radar"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("region_code", sa.String(), nullable=False, server_default="BR-SP"))


def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_column("region_code")
