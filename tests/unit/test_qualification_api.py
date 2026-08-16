from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db
from app.db.models import Business
from app.schemas.enums import WorkflowState, WebsiteStatus

client = TestClient(app)


def test_qualification_process_api(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        # Create lead in WEBSITE_ANALYZED state
        lead = Business(
            name="API Qualification Lead",
            category="cafe",
            address="CG Road",
            city="Ahmedabad",
            phone="+91 99999 88888",
            place_id="ch_api_qual",
            rating=4.5,
            review_count=50,
            website_status=WebsiteStatus.NO_WEBSITE,
            workflow_state=WorkflowState.WEBSITE_ANALYZED
        )
        db_session.add(lead)
        db_session.commit()

        res = client.post(f"/api/v1/qualification/process/{lead.id}")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "scoring" in data
        assert "qualification" in data
        assert data["qualification"]["qualified"] is True
    finally:
        app.dependency_overrides.clear()
