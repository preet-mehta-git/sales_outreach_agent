from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db
from app.db.models import Business
from app.schemas.enums import WorkflowState

client = TestClient(app)


def test_analyze_lead_website_api(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        # Create lead in VERIFIED state
        lead = Business(
            name="API Audit Lead",
            category="cafe",
            address="Satellite",
            city="Ahmedabad",
            website_url="http://vastrapurheritagedining.example.com",
            workflow_state=WorkflowState.VERIFIED
        )
        db_session.add(lead)
        db_session.commit()

        # Run audit API
        res = client.post(f"/api/v1/audit/analyze/{lead.id}")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "verification" in data
        assert "audit" in data
    finally:
        app.dependency_overrides.clear()
