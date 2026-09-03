import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_db
from app.core.config import settings

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()


def test_auth_login():
    response = client.post(
        "/api/auth/login",
        json={"username": settings.SEED_OFFICER_USERNAME, "password": settings.SEED_OFFICER_PASSWORD},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == settings.SEED_OFFICER_USERNAME
    assert data["user"]["role"] == "OFFICER"
    return data["access_token"]


def test_get_canonical_screening():
    token = test_auth_login()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/screenings/SID-2026-05-21-00124", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["screening_number"] == "SID-2026-05-21-00124"
    assert data["overall_risk_score"] == 18.0
    assert data["screening_level"] == "CLEAR"
    assert "Passport Number" in data["extracted_fields"]
    assert data["extracted_fields"]["Passport Number"] == "R1234567"
    assert len(data["module_results"]) >= 4


def test_audit_verification_and_tamper_detection():
    token = test_auth_login()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Verify clean chain
    verify_resp = client.post("/api/audit/SID-2026-05-21-00124/verify", headers=headers)
    assert verify_resp.status_code == 200
    res = verify_resp.json()
    assert res["status"] == "VERIFIED"
    assert res["chain_valid"] is True

    # 2. Trigger tamper demo
    tamper_resp = client.post("/api/audit/tamper-demo?screening_id=SID-2026-05-21-00124", headers=headers)
    assert tamper_resp.status_code == 200

    # 3. Verify that audit verification now fails with AUDIT_INTEGRITY_FAILURE
    verify_again = client.post("/api/audit/SID-2026-05-21-00124/verify", headers=headers)
    assert verify_again.status_code == 200
    tampered_res = verify_again.json()
    assert tampered_res["status"] == "AUDIT_INTEGRITY_FAILURE"
    assert tampered_res["chain_valid"] is False


def test_submit_officer_review():
    token = test_auth_login()
    headers = {"Authorization": f"Bearer {token}"}

    review_payload = {
        "decision": "ACCEPT",
        "reason": "VALIDATED_CREDENTIALS",
        "notes": "Verified against physical document at secondary checkpoint. Approved entry.",
    }
    resp = client.post("/api/screenings/SID-2026-05-21-00124/review", json=review_payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["decision"] == "ACCEPT"
    assert data["reason"] == "VALIDATED_CREDENTIALS"
