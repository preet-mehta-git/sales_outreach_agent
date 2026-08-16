from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db
from app.db.models import Business
from app.schemas.enums import WorkflowState

client = TestClient(app)


def test_generate_lead_demo_api(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        # Create lead in BUSINESS_AUDITED state
        lead = Business(
            name="API Demo Lead",
            category="bistro",
            address="Vastrapur",
            city="Ahmedabad",
            phone="+91 97777 66666",
            workflow_state=WorkflowState.BUSINESS_AUDITED
        )
        db_session.add(lead)
        db_session.commit()

        res = client.post(f"/api/v1/demo/generate/{lead.id}")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "demo" in data
        assert "demo_url" in data["demo"]

        db_session.refresh(lead)
        assert lead.workflow_state == WorkflowState.DEMO_GENERATED
    finally:
        app.dependency_overrides.clear()
