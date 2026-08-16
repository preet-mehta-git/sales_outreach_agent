from app.db.models import Business, WebsiteAudit, OpportunityScoreRecord
from app.schemas.enums import WorkflowState, WebsiteStatus


def test_create_business_and_relationships(db_session):
    business = Business(
        name="CG Road Diner",
        category="restaurant",
        address="CG Road, Ahmedabad",
        city="Ahmedabad",
        website_status=WebsiteStatus.WEBSITE_FOUND,
        workflow_state=WorkflowState.DISCOVERED
    )
    db_session.add(business)
    db_session.commit()
    db_session.refresh(business)

    assert business.id is not None
    assert business.name == "CG Road Diner"
    assert business.workflow_state == WorkflowState.DISCOVERED

    # Add website audit relationship
    audit = WebsiteAudit(
        business_id=business.id,
        quality_score=45.0,
        performance_score=40.0,
        mobile_score=50.0
    )
    db_session.add(audit)
    db_session.commit()

    db_session.refresh(business)
    assert business.website_audit is not None
    assert business.website_audit.quality_score == 45.0
