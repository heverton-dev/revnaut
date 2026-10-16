# -*- coding: utf-8 -*-
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection

client = TestClient(app)

def test_contact_full_profile_and_timeline():
    # 1. Fetch contacts
    res = client.get("/api/v1/contacts")
    assert res.status_code == 200
    contacts = res.json()
    assert len(contacts) > 0
    c_id = contacts[0]["id"]
    
    # 2. Fetch full profile
    res_prof = client.get(f"/api/v1/contacts/{c_id}/profile")
    assert res_prof.status_code == 200
    prof = res_prof.json()
    assert prof["id"] == c_id
    assert "timeline" in prof
    assert "deals" in prof
    assert len(prof["timeline"]) >= 1
    
    # 3. Add timeline comment
    res_comm = client.post(
        f"/api/v1/contacts/{c_id}/timeline/comments",
        json={"comment": "Cirurgião solicitou demonstração de kits e catalogo 2026."}
    )
    assert res_comm.status_code == 201
    
    # 4. Verify comment in timeline
    res_tl = client.get(f"/api/v1/contacts/{c_id}/timeline")
    assert res_tl.status_code == 200
    tl = res_tl.json()["timeline"]
    assert any("Cirurgião solicitou demonstração" in log.get("comment", "") for log in tl)
