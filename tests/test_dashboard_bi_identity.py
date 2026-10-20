# -*- coding: utf-8 -*-
"""
DASH4-01..08: a identidade e o tenant do dashboard BI vêm sempre da sessão assinada.
Usuário comum não pode agir como outro usuário nem em outro tenant; superadmin mantém a
impersonação legítima (X-User-Id é tratado em get_current_user).
"""

import jwt
import pytest
from fastapi.testclient import TestClient

from src.core.config import SUPERSET_SECRET_KEY
from src.core.database import get_connection, init_db
from src.features.intelligence import superset_embedded
from src.main import app
from tests.auth_helpers import SUPERADMIN_ID, bearer_headers

ACCOUNT = "0f14ffff"
SELF_USER = "usr-dash4-self"
OTHER_USER = "usr-dash4-other"
TENANT_USER = "usr-dash4-tenant"


@pytest.fixture(autouse=True)
def seed_dash4_users():
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        for uid, name, email, scope in (
            (SELF_USER, "Dash4 Self", "dash4.self@revnault.com", "self"),
            (OTHER_USER, "Dash4 Other", "dash4.other@revnault.com", "self"),
            (TENANT_USER, "Dash4 Tenant", "dash4.tenant@revnault.com", "tenant_global"),
        ):
            cur.execute(
                "INSERT OR REPLACE INTO users (id, account_id, name, email, role, custom_data_scope, "
                "is_active, is_superadmin) VALUES (?, ?, ?, ?, 'Consultor', ?, 1, 0)",
                (uid, ACCOUNT, name, email, scope),
            )
        cur.execute("DELETE FROM deals WHERE id IN ('deal-dash4-mine', 'deal-dash4-other')")
        for deal_id, owner in (("deal-dash4-mine", SELF_USER), ("deal-dash4-other", OTHER_USER)):
            cur.execute(
                "INSERT INTO deals (id, account_id, title, value, stage_id, pipeline_id, owner_id, "
                "company, contact_name) VALUES (?, ?, ?, 1, 101, 1, ?, 'Co', 'Ct')",
                (deal_id, ACCOUNT, f"DASH4 {deal_id}", owner),
            )
        conn.commit()
    finally:
        conn.close()


def _client(user_id: str) -> TestClient:
    return TestClient(app, headers=bearer_headers(user_id))


def test_guest_token_user_cannot_request_token_as_another_user():
    res = _client(SELF_USER).post(
        "/api/v1/intelligence/bi/guest-token",
        json={"user_id": SUPERADMIN_ID, "dashboard_id": "dash-x"},
    )
    assert res.status_code == 403


def test_guest_token_without_user_id_uses_session_identity():
    res = _client(SELF_USER).post(
        "/api/v1/intelligence/bi/guest-token", json={"dashboard_id": "dash-x"}
    )
    assert res.status_code == 200
    body = res.json()
    assert body["user_id"] == SELF_USER
    assert f"owner_id = '{SELF_USER}'" in body["rls_clause"]
    claims = jwt.decode(body["token"], SUPERSET_SECRET_KEY, algorithms=["HS256"])
    assert claims["rls"][0]["clause"] == body["rls_clause"]


def test_guest_token_own_user_id_is_accepted():
    res = _client(SELF_USER).post(
        "/api/v1/intelligence/bi/guest-token",
        json={"user_id": SELF_USER, "dashboard_id": "dash-x"},
    )
    assert res.status_code == 200


def test_guest_token_superadmin_may_act_as_another_user():
    res = _client(SUPERADMIN_ID).post(
        "/api/v1/intelligence/bi/guest-token",
        json={"user_id": SELF_USER, "dashboard_id": "dash-x"},
    )
    assert res.status_code == 200
    assert f"owner_id = '{SELF_USER}'" in res.json()["rls_clause"]


def test_guest_token_foreign_tenant_is_rejected():
    res = _client(SELF_USER).post(
        "/api/v1/intelligence/bi/guest-token",
        json={"dashboard_id": "dash-x", "account_id": "outro-tenant"},
    )
    assert res.status_code == 403


def test_export_user_cannot_export_as_another_user_or_tenant():
    c = _client(SELF_USER)
    as_super = c.post(
        "/api/v1/intelligence/bi/export-dataset",
        json={"dataset_name": "deals_funnel", "user_id": SUPERADMIN_ID},
    )
    other_tenant = c.post(
        "/api/v1/intelligence/bi/export-dataset",
        json={"dataset_name": "deals_funnel", "account_id": "outro-tenant"},
    )
    assert as_super.status_code == 403
    assert other_tenant.status_code == 403


def test_export_scoped_to_session_user_only():
    res = _client(SELF_USER).post(
        "/api/v1/intelligence/bi/export-dataset", json={"dataset_name": "deals_funnel"}
    )
    assert res.status_code == 200
    assert res.json()["record_count"] == 1


def test_text_to_sql_user_cannot_query_as_another_user_or_tenant():
    c = _client(SELF_USER)
    as_super = c.post(
        "/api/v1/intelligence/bi/text-to-sql",
        json={"raw_sql": "SELECT title FROM deals", "user_id": SUPERADMIN_ID},
    )
    other_tenant = c.post(
        "/api/v1/intelligence/bi/text-to-sql",
        json={"raw_sql": "SELECT title FROM deals", "account_id": "outro-tenant"},
    )
    assert as_super.status_code == 403
    assert other_tenant.status_code == 403


def test_text_to_sql_scoped_to_session_user_only():
    res = _client(SELF_USER).post(
        "/api/v1/intelligence/bi/text-to-sql", json={"raw_sql": "SELECT id, title FROM deals"}
    )
    assert res.status_code == 200
    titles = [r["title"] for r in res.json()["rows"]]
    assert "DASH4 deal-dash4-mine" in titles
    assert "DASH4 deal-dash4-other" not in titles


@pytest.mark.parametrize(
    "dataset", ["consignment_turnover", "dentgo_deliveries", "anvisa_rma"]
)
def test_export_account_wide_dataset_denied_for_self_scope(dataset):
    c = _client(SELF_USER)
    denied = c.post("/api/v1/intelligence/bi/export-dataset", json={"dataset_name": dataset})
    allowed = _client(TENANT_USER).post(
        "/api/v1/intelligence/bi/export-dataset", json={"dataset_name": dataset}
    )
    assert denied.status_code == 403
    assert allowed.status_code == 200


def test_text_to_sql_account_wide_table_denied_for_self_scope():
    res = _client(SELF_USER).post(
        "/api/v1/intelligence/bi/text-to-sql",
        json={"raw_sql": "SELECT id FROM kp_custody_ledger"},
    )
    assert res.status_code == 403


def test_text_to_sql_unknown_user_is_denied_on_account_wide_table():
    from src.features.intelligence.text_to_sql_agent import execute_analytical_query

    with pytest.raises(PermissionError):
        execute_analytical_query(
            raw_sql="SELECT id FROM kp_custody_ledger", user_id="usr-inexistente", account_id=ACCOUNT
        )


def test_rls_clause_rejects_injected_identifiers():
    conn = get_connection()
    try:
        with pytest.raises(ValueError):
            superset_embedded.build_superset_rls_clause(conn, user_id="x' OR '1'='1", account_id=ACCOUNT)
        with pytest.raises(ValueError):
            superset_embedded.build_superset_rls_clause(conn, user_id=SELF_USER, account_id="a' OR 1=1 --")
    finally:
        conn.close()


def test_guest_token_injected_user_id_is_400_for_superadmin():
    res = _client(SUPERADMIN_ID).post(
        "/api/v1/intelligence/bi/guest-token",
        json={"user_id": "x' OR '1'='1", "dashboard_id": "dash-x"},
    )
    assert res.status_code == 400


def test_export_parquet_is_rejected_instead_of_mislabeled_csv():
    res = _client(TENANT_USER).post(
        "/api/v1/intelligence/bi/export-dataset",
        json={"dataset_name": "deals_funnel", "format": "parquet"},
    )
    assert res.status_code == 422


def test_internal_error_detail_is_not_leaked(monkeypatch):
    def boom(**_kwargs):
        raise RuntimeError("segredo-interno-/srv/db.sqlite")

    monkeypatch.setattr(superset_embedded, "generate_superset_guest_token", boom)
    res = _client(SELF_USER).post(
        "/api/v1/intelligence/bi/guest-token", json={"dashboard_id": "dash-x"}
    )
    assert res.status_code == 500
    assert "segredo-interno" not in res.text
