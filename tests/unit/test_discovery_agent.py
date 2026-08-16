import uuid
from app.agents.discovery_agent import DiscoveryAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState
from app.db.models import Business, AuditLog


def test_discovery_agent_execution(db_session):
    agent = DiscoveryAgent(db_session)
    agent_input = AgentInput(
        lead_id="test_run",
        workflow_run_id=str(uuid.uuid4()),
        parameters={
            "city": "Ahmedabad",
            "keywords": ["cafe"],
            "limit_per_keyword": 2
        }
    )

    output = agent.execute(agent_input)
    assert output.success is True
    assert output.data["discovered_count"] > 0
    assert output.data["new_leads_count"] > 0

    # Verify leads were transitioned from DISCOVERED -> VERIFIED
    leads = db_session.query(Business).filter(Business.city == "Ahmedabad").all()
    assert len(leads) > 0
    for lead in leads:
        assert lead.workflow_state == WorkflowState.VERIFIED

    # Verify audit trail entries recorded
    transitions = db_session.query(AuditLog).filter(AuditLog.action == "TRANSITION_TO_VERIFIED").all()
    assert len(transitions) > 0


def test_discovery_agent_idempotent_deduplication(db_session):
    agent = DiscoveryAgent(db_session)
    agent_input = AgentInput(
        lead_id="test_run",
        workflow_run_id=str(uuid.uuid4()),
        parameters={"city": "Ahmedabad", "keywords": ["cafe"], "limit_per_keyword": 2}
    )

    # First run
    out1 = agent.execute(agent_input)
    new_leads_first_run = out1.data["new_leads_count"]

    # Second run with identical data
    out2 = agent.execute(agent_input)
    assert out2.data["new_leads_count"] == 0
    assert out2.data["duplicate_count"] == new_leads_first_run
