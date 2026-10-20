# -*- coding: utf-8 -*-
"""Rota POST /api/v1/keypartners/agreements/{id}/dispatch-custody (modal "Remeter Lotes para Custódia")."""

from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.core.database import init_db
from src.features.keypartners import service as kp_service


@pytest.fixture
def client():
    return TestClient(app, headers=bearer_headers())


@pytest.fixture
def agreement():
    init_db()
    return kp_service.create_partner_agreement(
        partner_name="Clínica Remessa Custódia SP",
        partner_cro_uf="CRO-SP-77001",
        tier="GOLD",
        credit_limit=10000.0,
        min_monthly_revenue=3000.0,
        max_turnover_days=45,
        account_id="0f14ffff",
    )


def _lot(qty, unit_value, days_valid=180, batch="LOTE-DC-01"):
    return {
        "product_id": "IMP-CM-4311",
        "product_name": "Implante Cone Morse 4.3x11mm",
        "anvisa_reg": "ANVISA-80123456789",
        "batch_number": batch,
        "quantity": qty,
        "unit_value": unit_value,
        "sterilization_expiry_date": (datetime.now(timezone.utc) + timedelta(days=days_valid)).strftime("%Y-%m-%d"),
    }


def test_dispatch_custody_multi_lot_updates_ledger(client, agreement):
    res = client.post(
        f"/api/v1/keypartners/agreements/{agreement['id']}/dispatch-custody",
        json={"items": [_lot(4, 500.0), _lot(2, 1000.0, batch="LOTE-DC-02")], "account_id": "0f14ffff"},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["status"] == "DISPATCHED"
    assert body["total_remittance_value"] == 4000.0
    assert body["available_credit"] == 6000.0
    assert body["entries_count"] == 2

    summary = client.get(f"/api/v1/keypartners/agreements/{agreement['id']}/custody-summary").json()
    assert summary["used_credit"] == 4000.0
    assert summary["total_items_count"] == 6


def test_dispatch_custody_blocks_over_credit_limit(client, agreement):
    res = client.post(
        f"/api/v1/keypartners/agreements/{agreement['id']}/dispatch-custody",
        json={"items": [_lot(11, 1000.0)]},
    )
    assert res.status_code == 400


def test_dispatch_custody_blocks_short_sterilization_validity(client, agreement):
    res = client.post(
        f"/api/v1/keypartners/agreements/{agreement['id']}/dispatch-custody",
        json={"items": [_lot(1, 100.0, days_valid=10)]},
    )
    assert res.status_code == 400
    assert "30 dias" in res.json()["detail"]
