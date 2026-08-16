from app.schemas.lead import BusinessCreate
from app.schemas.enums import WorkflowState, WebsiteStatus
from app.services.lead_service import LeadService


def test_create_lead_website_classification(db_session):
    # No website
    lead_no_web = BusinessCreate(
        name="No Web Cafe",
        category="cafe",
        address="Address 1",
        website_url=None
    )
    b1, is_new1 = LeadService.create_lead(db_session, lead_no_web)
    assert is_new1 is True
    assert b1.website_status == WebsiteStatus.NO_WEBSITE

    # With website
    lead_web = BusinessCreate(
        name="Web Cafe",
        category="cafe",
        address="Address 2",
        website_url="http://webcafe.com"
    )
    b2, is_new2 = LeadService.create_lead(db_session, lead_web)
    assert is_new2 is True
    assert b2.website_status == WebsiteStatus.WEBSITE_FOUND


def test_suppress_lead(db_session):
    lead_data = BusinessCreate(
        name="Suppression Target Cafe",
        category="cafe",
        address="Address 3"
    )
    lead, _ = LeadService.create_lead(db_session, lead_data)
    assert lead.is_suppressed is False

    suppressed = LeadService.suppress_lead(db_session, lead.id, reason="Opted out via phone")
    assert suppressed is not None
    assert suppressed.is_suppressed is True
    assert suppressed.workflow_state == WorkflowState.DO_NOT_CONTACT

    # Verify excluded from default listing
    leads = LeadService.list_leads(db_session, exclude_suppressed=True)
    assert len(leads) == 0
