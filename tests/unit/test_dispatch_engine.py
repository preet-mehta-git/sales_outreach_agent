from app.services.dispatch_engine import OutreachDispatchEngine
from app.schemas.enums import WorkflowState, OutreachStatus
from app.db.models import Business, OutreachDraft, DecisionMakerRecord


def test_dispatch_engine_dry_run(db_session):
    lead = Business(
        name="Dispatch Test Bistro",
        category="bistro",
        address="Bodakdev",
        city="Ahmedabad",
        phone="+91 99999 11111",
        workflow_state=WorkflowState.APPROVED
    )
    db_session.add(lead)
    db_session.commit()

    dm = DecisionMakerRecord(
        business_id=lead.id,
        name="Owner John",
        contact_email="john@bistro.com"
    )
    db_session.add(dm)

    draft = OutreachDraft(
        business_id=lead.id,
        email_subject="Test Subject",
        email_body="Test Body",
        whatsapp_body="Test WA",
        demo_url=f"/static/demos/{lead.id}/index.html",
        status=OutreachStatus.APPROVED
    )
    db_session.add(draft)
    db_session.commit()

    engine = OutreachDispatchEngine(db_session)
    res = engine.dispatch_outreach(draft.id)

    assert res["status"] == "DISPATCH_SIMULATED_DRY_RUN"
    assert res["dispatch_payload"]["recipient_email"] == "john@bistro.com"

    db_session.refresh(draft)
    assert draft.status == OutreachStatus.DISPATCHED

    db_session.refresh(lead)
    assert lead.workflow_state == WorkflowState.CONTACTED
