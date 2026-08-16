import uuid
from app.agents.contact_discovery_agent import ContactDiscoveryAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState
from app.db.models import Business, DecisionMakerRecord


def test_contact_discovery_agent(db_session):
    lead = Business(
        name="Royal Cafe",
        category="cafe",
        address="Navrangpura",
        city="Ahmedabad",
        phone="+91 98765 00000",
        place_id="ch_royal_cafe",
        workflow_state=WorkflowState.QUALIFIED
    )
    db_session.add(lead)
    db_session.commit()

    agent = ContactDiscoveryAgent(db_session)
    inp = AgentInput(lead_id=lead.id, workflow_run_id=str(uuid.uuid4()))

    out = agent.execute(inp)
    assert out.success is True
    assert "decision_maker_id" in out.data
    assert out.data["confidence_level"] == "HIGH"

    # Verify DecisionMakerRecord persisted
    dm = db_session.query(DecisionMakerRecord).filter(DecisionMakerRecord.business_id == lead.id).first()
    assert dm is not None
    assert "Owner / GM" in dm.name

    # Verify transition to DECISION_MAKER_RESEARCHED
    db_session.refresh(lead)
    assert lead.workflow_state == WorkflowState.DECISION_MAKER_RESEARCHED
