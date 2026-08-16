import uuid
from app.agents.outreach_agent import OutreachAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState, OutreachStatus, ConfidenceLevel
from app.db.models import Business, OutreachDraft, DecisionMakerRecord


def test_outreach_agent_drafting(db_session):
    lead = Business(
        name="Flavor Bistro",
        category="bistro",
        address="Navrangpura",
        city="Ahmedabad",
        phone="+91 98000 11111",
        workflow_state=WorkflowState.DEMO_GENERATED
    )
    db_session.add(lead)
    db_session.commit()

    dm = DecisionMakerRecord(
        business_id=lead.id,
        name="Mr. Rajesh Patel",
        title="Owner",
        confidence=ConfidenceLevel.HIGH
    )
    db_session.add(dm)

    draft = OutreachDraft(
        business_id=lead.id,
        demo_url=f"/static/demos/{lead.id}/index.html",
        status=OutreachStatus.AWAITING_APPROVAL
    )
    db_session.add(draft)
    db_session.commit()

    agent = OutreachAgent(db_session)
    inp = AgentInput(lead_id=lead.id, workflow_run_id=str(uuid.uuid4()))

    out = agent.execute(inp)
    assert out.success is True
    assert "Growth opportunity for Flavor Bistro" in out.data["email_subject"]
    assert "Mr. Rajesh Patel" in out.data["email_body"]
    assert "REMOVE" in out.data["email_body"]  # Opt-out compliance check
    assert "/static/demos/" in out.data["whatsapp_body"]

    # Verify state transition to AWAITING_APPROVAL
    db_session.refresh(lead)
    assert lead.workflow_state == WorkflowState.AWAITING_APPROVAL
