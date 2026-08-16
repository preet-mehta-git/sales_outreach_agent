from app.services.approval_service import ApprovalWorkflowService
from app.schemas.enums import WorkflowState, OutreachStatus
from app.db.models import Business, OutreachDraft


def test_approval_service_approve(db_session):
    lead = Business(
        name="Approval Test Cafe",
        category="cafe",
        address="Navrangpura",
        city="Ahmedabad",
        workflow_state=WorkflowState.AWAITING_APPROVAL
    )
    db_session.add(lead)
    db_session.commit()

    draft = OutreachDraft(
        business_id=lead.id,
        email_subject="Initial Subject",
        email_body="Initial Body",
        status=OutreachStatus.AWAITING_APPROVAL
    )
    db_session.add(draft)
    db_session.commit()

    service = ApprovalWorkflowService(db_session)
    res = service.review_draft(
        draft_id=draft.id,
        decision="APPROVE",
        reviewer="Sales Manager",
        edits={"email_subject": "Updated Subject Line"}
    )

    assert res["status"] == "APPROVED"
    assert res["workflow_state"] == "APPROVED"

    db_session.refresh(draft)
    assert draft.status == OutreachStatus.APPROVED
    assert draft.email_subject == "Updated Subject Line"
    assert draft.approved_by == "Sales Manager"

    db_session.refresh(lead)
    assert lead.workflow_state == WorkflowState.APPROVED


def test_approval_service_reject(db_session):
    lead = Business(
        name="Reject Test Cafe",
        category="cafe",
        address="Vastrapur",
        city="Ahmedabad",
        workflow_state=WorkflowState.AWAITING_APPROVAL
    )
    db_session.add(lead)
    db_session.commit()

    draft = OutreachDraft(
        business_id=lead.id,
        status=OutreachStatus.AWAITING_APPROVAL
    )
    db_session.add(draft)
    db_session.commit()

    service = ApprovalWorkflowService(db_session)
    res = service.review_draft(
        draft_id=draft.id,
        decision="REJECT",
        reviewer="Quality Auditor"
    )

    assert res["status"] == "REJECTED"
    db_session.refresh(lead)
    assert lead.workflow_state == WorkflowState.REJECTED
