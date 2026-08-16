import uuid
from app.agents.business_audit_agent import BusinessAuditAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState
from app.db.models import Business


def test_business_audit_agent(db_session):
    lead = Business(
        name="Ambience Restaurant",
        category="restaurant",
        address="Drive In Road",
        city="Ahmedabad",
        review_count=120,
        workflow_state=WorkflowState.DECISION_MAKER_RESEARCHED
    )
    db_session.add(lead)
    db_session.commit()

    agent = BusinessAuditAgent(db_session)
    inp = AgentInput(lead_id=lead.id, workflow_run_id=str(uuid.uuid4()))

    out = agent.execute(inp)
    assert out.success is True
    assert "known_facts" in out.data
    assert "<untrusted_external_content>" in out.data["untrusted_content"]

    # Verify transition to BUSINESS_AUDITED
    db_session.refresh(lead)
    assert lead.workflow_state == WorkflowState.BUSINESS_AUDITED
