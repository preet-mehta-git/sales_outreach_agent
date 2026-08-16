import pytest
from app.orchestrator.engine import OrchestratorEngine
from app.orchestrator.state import WorkflowStateMachine, InvalidStateTransitionError
from app.schemas.enums import WorkflowState


def test_legal_state_transitions(db_session, sample_business):
    engine = OrchestratorEngine(db_session)
    
    # DISCOVERED -> VERIFIED
    updated_lead = engine.transition_lead(sample_business.id, WorkflowState.VERIFIED)
    assert updated_lead.workflow_state == WorkflowState.VERIFIED

    # VERIFIED -> WEBSITE_ANALYZED
    updated_lead = engine.transition_lead(sample_business.id, WorkflowState.WEBSITE_ANALYZED)
    assert updated_lead.workflow_state == WorkflowState.WEBSITE_ANALYZED

    # WEBSITE_ANALYZED -> SCORED
    updated_lead = engine.transition_lead(sample_business.id, WorkflowState.SCORED)
    assert updated_lead.workflow_state == WorkflowState.SCORED


def test_illegal_state_transition_raises_error(db_session, sample_business):
    engine = OrchestratorEngine(db_session)
    
    # DISCOVERED -> DEMO_GENERATED (Illegal jump!)
    with pytest.raises(InvalidStateTransitionError):
        engine.transition_lead(sample_business.id, WorkflowState.DEMO_GENERATED)


def test_suppressed_lead_transition_halted(db_session, sample_business):
    engine = OrchestratorEngine(db_session)
    sample_business.is_suppressed = True
    db_session.commit()

    # Attempting to transition a suppressed lead
    updated_lead = engine.transition_lead(sample_business.id, WorkflowState.VERIFIED)
    # Workflow state should remain DISCOVERED
    assert updated_lead.workflow_state == WorkflowState.DISCOVERED
