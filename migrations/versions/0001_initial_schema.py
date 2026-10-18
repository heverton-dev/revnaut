# -*- coding: utf-8 -*-
"""Initial REVNAULT schema migration covering core and domain tables.

Revision ID: 0001_initial_schema
Revises: None
Create Date: 2026-10-18 10:30:00
"""

from __future__ import annotations
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("plan", sa.String(), nullable=False, server_default="Enterprise Scale"),
        sa.Column("created_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "users",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("role", sa.String(), nullable=False, server_default="Consultor"),
        sa.Column("team_id", sa.String(), nullable=True),
        sa.Column("role_id", sa.String(), nullable=True),
        sa.Column("custom_data_scope", sa.String(), nullable=True),
        sa.Column("is_superadmin", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "teams",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("business_unit_id", sa.String(), nullable=False),
        sa.Column("parent_id", sa.String(), sa.ForeignKey("teams.id"), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("leader_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("company", sa.String(), nullable=True),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("score", sa.Integer(), server_default="50"),
        sa.Column("owner_id", sa.String(), nullable=True),
        sa.Column("field_owner_id", sa.String(), nullable=True),
        sa.Column("inside_owner_id", sa.String(), nullable=True),
        sa.Column("team_id", sa.String(), nullable=True),
        sa.Column("cro", sa.String(), nullable=True),
        sa.Column("cro_uf", sa.String(), nullable=True),
        sa.Column("cro_verified", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "deals",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("pipeline_id", sa.Integer(), nullable=False),
        sa.Column("stage_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("company", sa.String(), nullable=False),
        sa.Column("contact_name", sa.String(), nullable=False),
        sa.Column("priority", sa.String(), nullable=False, server_default="media"),
        sa.Column("owner_id", sa.String(), nullable=True),
        sa.Column("field_owner_id", sa.String(), nullable=True),
        sa.Column("inside_owner_id", sa.String(), nullable=True),
        sa.Column("team_id", sa.String(), nullable=True),
        sa.Column("split_commission_field_pct", sa.Float(), server_default="70.0"),
        sa.Column("split_commission_inside_pct", sa.Float(), server_default="30.0"),
        sa.Column("executive_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "kp_partner_agreements",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("partner_name", sa.String(), nullable=False),
        sa.Column("partner_cro_uf", sa.String(), nullable=True),
        sa.Column("tier", sa.String(), nullable=False, server_default="SILVER"),
        sa.Column("credit_limit", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("used_credit", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("min_monthly_revenue", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("max_turnover_days", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("field_owner_id", sa.String(), nullable=True),
        sa.Column("inside_owner_id", sa.String(), nullable=True),
        sa.Column("is_active", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "kp_consignment_kits",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("serial_number", sa.String(), unique=True, nullable=False),
        sa.Column("qr_code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("composition_json", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="IN_STOCK"),
        sa.Column("current_agreement_id", sa.String(), sa.ForeignKey("kp_partner_agreements.id"), nullable=True),
        sa.Column("created_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "kp_custody_ledger",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("agreement_id", sa.String(), sa.ForeignKey("kp_partner_agreements.id"), nullable=False),
        sa.Column("movement_type", sa.String(), nullable=False),
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column("product_name", sa.String(), nullable=False),
        sa.Column("anvisa_reg", sa.String(), nullable=False),
        sa.Column("batch_number", sa.String(), nullable=False),
        sa.Column("serial_number", sa.String(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("unit_value", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("total_value", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("sterilization_expiry_date", sa.String(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "kp_surgical_orders",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("agreement_id", sa.String(), sa.ForeignKey("kp_partner_agreements.id"), nullable=False),
        sa.Column("patient_identifier", sa.String(), nullable=True),
        sa.Column("surgery_date", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="SOLICITADO_FIELD"),
        sa.Column("field_consultant_id", sa.String(), nullable=True),
        sa.Column("inside_analyst_id", sa.String(), nullable=True),
        sa.Column("remitted_items_json", sa.Text(), nullable=True),
        sa.Column("consumed_items_json", sa.Text(), nullable=True),
        sa.Column("returned_items_json", sa.Text(), nullable=True),
        sa.Column("seal_photo_r2_key", sa.String(), nullable=True),
        sa.Column("billing_order_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=True),
        sa.Column("updated_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "kp_kol_contracts",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("agreement_id", sa.String(), sa.ForeignKey("kp_partner_agreements.id"), nullable=True),
        sa.Column("kol_name", sa.String(), nullable=False),
        sa.Column("cro_uf", sa.String(), nullable=False),
        sa.Column("equipment_name", sa.String(), nullable=False),
        sa.Column("asset_tag", sa.String(), unique=True, nullable=False),
        sa.Column("min_monthly_implants_target", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("clinical_lectures_quota", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("current_month_consumption", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("compliance_status", sa.String(), nullable=False, server_default="COMPLIANT"),
        sa.Column("evidence_r2_keys_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=True),
        sa.Column("updated_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "kp_loyalty_wallets",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("partner_id", sa.String(), unique=True, nullable=False),
        sa.Column("partner_name", sa.String(), nullable=False),
        sa.Column("points_balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lifetime_points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_tier", sa.String(), nullable=False, server_default="SILVER"),
        sa.Column("implants_billed_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.String(), nullable=True),
        sa.Column("updated_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "dentgo_hubs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("cnpj", sa.String(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("coverage_radius_km", sa.Float(), nullable=False, server_default="30.0"),
        sa.Column("on_duty_schedule", sa.String(), server_default="24h"),
        sa.Column("is_active", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "dentgo_hub_inventory",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("hub_id", sa.String(), sa.ForeignKey("dentgo_hubs.id"), nullable=False),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column("product_name", sa.String(), nullable=False),
        sa.Column("anvisa_reg", sa.String(), nullable=False),
        sa.Column("batch_number", sa.String(), nullable=False),
        sa.Column("quantity_available", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unit_price", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("sterilization_expiry_date", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="AVAILABLE"),
        sa.Column("created_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "dentgo_orders",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("hub_id", sa.String(), sa.ForeignKey("dentgo_hubs.id"), nullable=False),
        sa.Column("customer_cro_uf", sa.String(), nullable=False),
        sa.Column("cro_verified", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("delivery_address", sa.String(), nullable=False),
        sa.Column("delivery_lat", sa.Float(), nullable=False),
        sa.Column("delivery_lng", sa.Float(), nullable=False),
        sa.Column("distance_km", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("estimated_eta_minutes", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("items_json", sa.Text(), nullable=False),
        sa.Column("subtotal", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("urgency_fee", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("total_amount", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("status", sa.String(), nullable=False, server_default="ORDER_PLACED"),
        sa.Column("courier_id", sa.String(), nullable=True),
        sa.Column("seal_code", sa.String(), nullable=True),
        sa.Column("delivery_pin", sa.String(), nullable=True),
        sa.Column("proof_of_delivery_r2_key", sa.String(), nullable=True),
        sa.Column("recipient_signature_name", sa.String(), nullable=True),
        sa.Column("delivered_at", sa.String(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "dentgo_financial_splits",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("order_id", sa.String(), sa.ForeignKey("dentgo_orders.id"), nullable=False),
        sa.Column("gross_amount", sa.Float(), nullable=False),
        sa.Column("items_amount", sa.Float(), nullable=False),
        sa.Column("delivery_fee_total", sa.Float(), nullable=False),
        sa.Column("platform_take_rate_pct", sa.Float(), nullable=False, server_default="5.0"),
        sa.Column("platform_fee_amount", sa.Float(), nullable=False),
        sa.Column("courier_net_payout", sa.Float(), nullable=False),
        sa.Column("seller_net_payout", sa.Float(), nullable=False),
        sa.Column("payment_method", sa.String(), nullable=False, server_default="PIX_INSTANT"),
        sa.Column("agreement_id", sa.String(), nullable=True),
        sa.Column("settlement_status", sa.String(), nullable=False, server_default="SETTLED"),
        sa.Column("created_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "anvisa_rma_claims",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("ticket_id", sa.String(), nullable=False),
        sa.Column("agreement_id", sa.String(), nullable=True),
        sa.Column("surgeon_name", sa.String(), nullable=True),
        sa.Column("surgeon_cro_uf", sa.String(), nullable=False),
        sa.Column("patient_identifier", sa.String(), nullable=True),
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column("product_name", sa.String(), nullable=False),
        sa.Column("batch_number", sa.String(), nullable=False),
        sa.Column("serial_number", sa.String(), nullable=True),
        sa.Column("fdi_tooth_region", sa.String(), nullable=False),
        sa.Column("insertion_torque_ncm", sa.Float(), nullable=False),
        sa.Column("surgery_date", sa.String(), nullable=False),
        sa.Column("explant_date", sa.String(), nullable=False),
        sa.Column("failure_reason", sa.String(), nullable=False),
        sa.Column("radiograph_r2_key", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="SUBMITTED"),
        sa.Column("warranty_approved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("replacement_order_id", sa.String(), nullable=True),
        sa.Column("quarantine_triggered", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=True),
        sa.Column("updated_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "anvisa_batch_quarantines",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("batch_number", sa.String(), nullable=False),
        sa.Column("product_id", sa.String(), nullable=True),
        sa.Column("total_distributed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_failures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failure_rate_percent", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("status", sa.String(), nullable=False, server_default="QUARANTINE_BLOCKED"),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("blocked_at", sa.String(), nullable=True),
        sa.Column("unblocked_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "semantic_embeddings",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", sa.String(), nullable=False),
        sa.Column("content_chunk", sa.Text(), nullable=False),
        sa.Column("embedding", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "scoring_history",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("contact_id", sa.Integer(), nullable=False),
        sa.Column("previous_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("new_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("icp_fit_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("engagement_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tier", sa.String(), nullable=False, server_default="C"),
        sa.Column("trigger_reason", sa.String(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "tenant_credentials",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("service_name", sa.String(), nullable=False),
        sa.Column("credential_type", sa.String(), nullable=False),
        sa.Column("encrypted_payload", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=True),
        sa.Column("updated_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "webhook_subscriptions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("target_url", sa.String(), nullable=False),
        sa.Column("subscribed_events_json", sa.Text(), nullable=False, server_default='["*"]'),
        sa.Column("signing_secret", sa.String(), nullable=False),
        sa.Column("signing_secret_encrypted", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("consecutive_failures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("circuit_breaker_tripped", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.String(), nullable=True),
        if_not_exists=True,
    )

    op.create_table(
        "erp_fiscal_invoices",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("erp_type", sa.String(), nullable=False, server_default="totvs_protheus"),
        sa.Column("flow_type", sa.String(), nullable=False),
        sa.Column("reference_id", sa.String(), nullable=False),
        sa.Column("cfop", sa.String(), nullable=False),
        sa.Column("nfe_number", sa.String(), nullable=False),
        sa.Column("nfe_series", sa.String(), nullable=False, server_default="1"),
        sa.Column("nfe_access_key", sa.String(), unique=True, nullable=False),
        sa.Column("recipient_cnpj_cpf", sa.String(), nullable=False),
        sa.Column("recipient_name", sa.String(), nullable=False),
        sa.Column("total_invoice_value", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("xml_r2_key", sa.String(), nullable=False),
        sa.Column("danfe_pdf_r2_key", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="AUTORIZADA"),
        sa.Column("sefaz_protocol", sa.String(), nullable=True),
        sa.Column("windmill_job_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=True),
        if_not_exists=True,
    )


def downgrade() -> None:
    for tbl in [
        "erp_fiscal_invoices",
        "webhook_subscriptions",
        "tenant_credentials",
        "scoring_history",
        "semantic_embeddings",
        "anvisa_batch_quarantines",
        "anvisa_rma_claims",
        "dentgo_financial_splits",
        "dentgo_orders",
        "dentgo_hub_inventory",
        "dentgo_hubs",
        "kp_loyalty_wallets",
        "kp_kol_contracts",
        "kp_surgical_orders",
        "kp_custody_ledger",
        "kp_consignment_kits",
        "kp_partner_agreements",
        "deals",
        "contacts",
        "teams",
        "users",
        "accounts",
    ]:
        op.drop_table(tbl, if_exists=True)
