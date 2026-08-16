from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db
from app.db.models import Business
from app.schemas.enums import WorkflowState

client = TestClient(app)


def test_deep_research_lead_api(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        # Create lead in QUALIFIED state
        lead = Business(
            name="API Research Lead",
            category="restaurant",
            address="Prahlad Nagar",
            city="Ahmedabad",
            phone="+91 91111 22222",
            place_id="ch_api_research",
            workflow_state=WorkflowState.QUALIFIED
        )
        db_session.add(lead)
        db_session.commit()

        res = client.post(f"/api/v1/research/lead/{lead.id}")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "contact_discovery" in data
        assert "business_audit" in data

        db_session.refresh(lead)
        assert lead.workflow_state == WorkflowState.BUSINESS_AUDITED
    finally:
        app.dependency_overrides.clear()
