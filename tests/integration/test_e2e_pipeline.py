from app.db.models import Campaign, Business, AuditLog, OutreachDraft
from app.orchestrator.pipeline import CampaignPipelineRunner
from app.services.approval_service import ApprovalWorkflowService
from app.services.dispatch_engine import OutreachDispatchEngine
from app.schemas.enums import WorkflowState, OutreachStatus


def test_e2e_campaign_pipeline_execution(db_session):
    # Step 1: Create test campaign
    campaign = Campaign(
        name="Ahmedabad Restaurant Growth Q3",
        industry="restaurant_cafe",
        city="Ahmedabad",
        state="Gujarat",
        country="India",
        min_opportunity_score=60
    )
    db_session.add(campaign)
    db_session.commit()

    # Step 2: Run End-to-End Campaign Pipeline Orchestrator
    runner = CampaignPipelineRunner(db_session)
    pipeline_res = runner.run_pipeline_for_campaign(campaign_id=campaign.id, query="cafe in Ahmedabad")

    assert pipeline_res["status"] == "COMPLETED"
    summary = pipeline_res["summary"]
    assert summary["total_ingested"] > 0
    assert summary["qualified"] > 0
    assert summary["drafts_created"] > 0

    # Step 3: Fetch drafted leads & test Human-in-the-Loop approval
    drafted_lead = db_session.query(Business).filter(
        Business.campaign_id == campaign.id,
        Business.workflow_state == WorkflowState.AWAITING_APPROVAL
    ).first()

    assert drafted_lead is not None
    draft = db_session.query(OutreachDraft).filter(OutreachDraft.business_id == drafted_lead.id).first()
    assert draft is not None
    assert draft.status == OutreachStatus.AWAITING_APPROVAL

    # Step 4: Human Review & Approval
    approval_service = ApprovalWorkflowService(db_session)
    review_res = approval_service.review_draft(
        draft_id=draft.id,
        decision="APPROVE",
        reviewer="Campaign Manager"
    )
    assert review_res["status"] == "APPROVED"

    db_session.refresh(drafted_lead)
    assert drafted_lead.workflow_state == WorkflowState.APPROVED

    # Step 5: Safe Outreach Dispatch Execution
    dispatch_engine = OutreachDispatchEngine(db_session)
    dispatch_res = dispatch_engine.dispatch_outreach(draft.id)
    assert "DISPATCH" in dispatch_res["status"]

    db_session.refresh(drafted_lead)
    assert drafted_lead.workflow_state == WorkflowState.CONTACTED

    # Step 6: Verify Immutable Audit Traceability Logs
    audit_logs = db_session.query(AuditLog).filter(AuditLog.business_id == drafted_lead.id).all()
    assert len(audit_logs) >= 8  # Full state machine transition trail
