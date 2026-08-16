import uuid
from app.agents.opportunity_scorer_agent import OpportunityScorerAgent
from app.agents.qualification_agent import QualificationAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState, WebsiteStatus
from app.db.models import Business, AuditLog


def test_scorer_and_qualification_pipeline_qualify(db_session):
    lead = Business(
        name="High Value Restaurant",
        category="restaurant",
        address="Bodakdev",
        city="Ahmedabad",
        phone="+919800000001",
        place_id="ch_high_value",
        rating=4.7,
        review_count=80,
        website_status=WebsiteStatus.NO_WEBSITE,
        workflow_state=WorkflowState.WEBSITE_ANALYZED
    )
    db_session.add(lead)
    db_session.commit()

    inp = AgentInput(lead_id=lead.id, workflow_run_id=str(uuid.uuid4()))

    # Run Scorer Agent
    scorer = OpportunityScorerAgent(db_session)
    scorer_out = scorer.execute(inp)
    assert scorer_out.success is True
    assert scorer_out.data["opportunity_score"] >= 60.0

    db_session.refresh(lead)
    assert lead.workflow_state == WorkflowState.SCORED

    # Run Qualification Agent
    qualifier = QualificationAgent(db_session)
    qual_out = qualifier.execute(inp)
    assert qual_out.success is True
    assert qual_out.data["qualified"] is True

    db_session.refresh(lead)
    assert lead.workflow_state == WorkflowState.QUALIFIED


def test_scorer_and_qualification_pipeline_reject(db_session):
    lead = Business(
        name="Low Score Business",
        category="food_stall",
        address="Remote",
        city="Ahmedabad",
        rating=2.0,
        review_count=1,
        website_url="http://existing.example.com",
        website_status=WebsiteStatus.WEBSITE_FOUND,
        workflow_state=WorkflowState.WEBSITE_ANALYZED
    )
    db_session.add(lead)
    db_session.commit()

    inp = AgentInput(lead_id=lead.id, workflow_run_id=str(uuid.uuid4()))

    scorer = OpportunityScorerAgent(db_session)
    scorer.execute(inp)

    qualifier = QualificationAgent(db_session)
    qual_out = qualifier.execute(inp)
    assert qual_out.success is True
    assert qual_out.data["qualified"] is False

    db_session.refresh(lead)
    assert lead.workflow_state == WorkflowState.REJECTED
