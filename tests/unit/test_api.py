from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["outreach_mode"] == "DRY_RUN"


def test_create_and_list_campaign_api(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        # Create campaign
        payload = {
            "name": "API Test Campaign",
            "industry": "restaurant_cafe",
            "city": "Ahmedabad",
            "min_opportunity_score": 75
        }
        res = client.post("/api/v1/campaigns", json=payload)
        assert res.status_code == 201
        created = res.json()
        assert created["name"] == "API Test Campaign"
        assert "id" in created

        # List campaigns
        res_list = client.get("/api/v1/campaigns")
        assert res_list.status_code == 200
        camps = res_list.json()
        assert len(camps) >= 1
    finally:
        app.dependency_overrides.clear()


def test_create_and_suppress_lead_api(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        # Create lead
        payload = {
            "name": "API Restaurant Lead",
            "category": "restaurant",
            "address": "CG Road, Ahmedabad",
            "city": "Ahmedabad",
            "phone": "+91 91234 56789"
        }
        res = client.post("/api/v1/leads", json=payload)
        assert res.status_code == 201
        lead = res.json()
        lead_id = lead["id"]
        assert lead["name"] == "API Restaurant Lead"

        # Suppress lead
        res_supp = client.post(f"/api/v1/leads/{lead_id}/suppress?reason=DO_NOT_CONTACT")
        assert res_supp.status_code == 200
        suppressed = res_supp.json()
        assert suppressed["workflow_state"] == "DO_NOT_CONTACT"
    finally:
        app.dependency_overrides.clear()
