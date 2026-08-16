import pytest
from app.db.session import SessionLocal, engine
from app.db.models import Base, Business, DecisionMakerRecord, WebsiteAudit, OutreachDraft
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState, ConfidenceLevel
from app.agents.contact_discovery_agent import ContactDiscoveryAgent
from app.agents.business_audit_agent import BusinessAuditAgent
from app.agents.outreach_agent import OutreachAgent

Base.metadata.create_all(bind=engine)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_contact_discovery_no_fabricated_owner(db_session):
    lead = Business(
        name="No Owner Cafe",
        category="cafe",
        address="Navrangpura",
        city="Ahmedabad",
        phone="+919876543299",
        workflow_state=WorkflowState.QUALIFIED
    )
    db_session.add(lead)
    db_session.commit()

    agent = ContactDiscoveryAgent(db_session)
    res = agent.execute(AgentInput(lead_id=lead.id))

    assert res.data["full_name"] is None
    assert res.data["confidence_level"] == ConfidenceLevel.NOT_FOUND.value

    dm_record = db_session.query(DecisionMakerRecord).filter_by(business_id=lead.id).first()
    assert dm_record.name is None
    assert dm_record.confidence == ConfidenceLevel.NOT_FOUND


def test_business_audit_no_fabricated_revenue(db_session):
    lead = Business(
        name="Truth Restaurant",
        category="restaurant",
        address="SG Highway",
        city="Ahmedabad",
        phone="+919876543298",
        workflow_state=WorkflowState.DECISION_MAKER_RESEARCHED
    )
    db_session.add(lead)
    db_session.commit()

    agent = BusinessAuditAgent(db_session)
    res = agent.execute(AgentInput(lead_id=lead.id))

    assert "estimated_lost_monthly_revenue_inr" not in res.data
    assert "known_facts" in res.data
    assert "inferred_insights" in res.data
    assert "potential_opportunities" in res.data
    assert "unknown_variables" in res.data
    assert "Exact monthly revenue impact (requires internal financial records)" in res.data["unknown_variables"]


def test_outreach_low_confidence_generic_greeting(db_session):
    lead = Business(
        name="Uncertain Dining",
        category="restaurant",
        address="C G Road",
        city="Ahmedabad",
        phone="+919876543297",
        workflow_state=WorkflowState.DEMO_GENERATED
    )
    db_session.add(lead)
    db_session.commit()

    # Create DM record with LOW confidence
    dm = DecisionMakerRecord(
        business_id=lead.id,
        name=None,
        confidence=ConfidenceLevel.NOT_FOUND
    )
    db_session.add(dm)
    db_session.commit()

    agent = OutreachAgent(db_session)
    res = agent.execute(AgentInput(lead_id=lead.id))

    assert "Hello Uncertain Dining Team," in res.data["email_body"]
    assert "Hi Restaurant Owner," not in res.data["email_body"]
