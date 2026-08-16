import uuid
from app.agents.website_verifier_agent import WebsiteVerifierAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState, WebsiteStatus
from app.db.models import Business


def test_verifier_no_website_lead(db_session, sample_business):
    # Set lead state to VERIFIED
    sample_business.workflow_state = WorkflowState.VERIFIED
    db_session.commit()

    agent = WebsiteVerifierAgent(db_session)
    inp = AgentInput(lead_id=sample_business.id, workflow_run_id=str(uuid.uuid4()))

    out = agent.execute(inp)
    assert out.success is True
    assert out.data["website_status"] == WebsiteStatus.NO_WEBSITE.value

    # Verify state transition to WEBSITE_ANALYZED
    lead = db_session.query(Business).filter(Business.id == sample_business.id).first()
    assert lead.workflow_state == WorkflowState.WEBSITE_ANALYZED


def test_verifier_existing_website_lead(db_session):
    lead = Business(
        name="Heritage Bistro",
        category="restaurant",
        address="Vastrapur",
        city="Ahmedabad",
        website_url="http://vastrapurheritagedining.example.com",
        workflow_state=WorkflowState.VERIFIED
    )
    db_session.add(lead)
    db_session.commit()

    agent = WebsiteVerifierAgent(db_session)
    inp = AgentInput(lead_id=lead.id, workflow_run_id=str(uuid.uuid4()))
    out = agent.execute(inp)

    assert out.success is True
    assert isinstance(out.data["evidence"], list)
    assert any("reached successfully" in item for item in out.data["evidence"])

    
    db_session.refresh(lead)
    assert lead.workflow_state == WorkflowState.WEBSITE_ANALYZED
