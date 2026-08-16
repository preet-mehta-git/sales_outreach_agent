from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db
from app.db.models import Business
from app.schemas.enums import WorkflowState

client = TestClient(app)


def test_draft_lead_outreach_api(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        # Create lead in DEMO_GENERATED state
        lead = Business(
            name="API Outreach Lead",
            category="cafe",
            address="CG Road",
            city="Ahmedabad",
            phone="+91 95555 44444",
            workflow_state=WorkflowState.DEMO_GENERATED
        )
        db_session.add(lead)
        db_session.commit()

        # Trigger draft generation endpoint
        res = client.post(f"/api/v1/outreach/draft/{lead.id}")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "outreach_draft" in data
        assert "email_subject" in data["outreach_draft"]

        # Fetch draft endpoint
        res_get = client.get(f"/api/v1/outreach/draft/{lead.id}")
        assert res_get.status_code == 200
        get_data = res_get.json()
        assert get_data["business_id"] == lead.id
        assert get_data["status"] == "AWAITING_APPROVAL"

        db_session.refresh(lead)
        assert lead.workflow_state == WorkflowState.OUTREACH_DRAFTED
    finally:
        app.dependency_overrides.clear()
