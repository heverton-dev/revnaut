# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-24: Chatwoot Omnichannel Bridge & Context 360 Sidebar
"""

from pathlib import Path
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.features.keypartners import service as kp_service
from src.features.dentgo import service as dentgo_service


client = TestClient(app, headers=bearer_headers())


def test_chatwoot_context_panel_query_endpoint_and_sidebar_module():
    agr = kp_service.create_partner_agreement(
        partner_name="Clínica Oral Prime Context",
        partner_cro_uf="CRO-SP-54321",
        tier="GOLD",
        credit_limit=40000.0,
        account_id="0f14ffff",
    )
    kp_service.register_consignment_kit(
        serial_number="KIT-CW-360-01",
        name="Kit Cirúrgico Morse Chatwoot",
        account_id="0f14ffff",
    )
    kp_service.dispatch_consignment_custody(
        agreement_id=agr["id"],
        items=[
            {
                "product_id": "prod-kit-cw",
                "product_name": "Kit Cirúrgico Morse Chatwoot",
                "anvisa_reg": "80123450099",
                "batch_number": "LOTE-CW-2026",
                "serial_number": "KIT-CW-360-01",
                "quantity": 1,
                "unit_value": 5000.0,
                "sterilization_expiry_date": "2027-12-31",
            }
        ],
        account_id="0f14ffff",
    )

    resp = client.get("/api/v1/omnichannel/chatwoot-context-panel?contact_phone=CRO-SP-54321")
    assert resp.status_code == 200
    data = resp.json()
    assert data["cro_uf"] == "CRO-SP-54321"
    assert data["agreement"]["tier"] == "GOLD"
    assert data["agreement"]["available_credit"] == 35000.0
    assert any(k["serial_number"] == "KIT-CW-360-01" for k in data["consignments_in_field"])

    js_module = Path("docs/reconstruct_rvops/05_reconstructed_app/js/modules/inbox-context-sidebar.js")
    assert js_module.exists()
    content = js_module.read_text(encoding="utf-8")
    assert "fetchOmnichannelContext360" in content
    assert "renderInboxContextSidebar" in content
