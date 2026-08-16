import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import Business, WebsiteAudit, DecisionMakerRecord, OutreachDraft, Campaign
from app.schemas.enums import (
    WorkflowState, WebsiteStatus, WebsiteVerificationStatus, EntityVerificationStatus,
    EntityType, OutreachReadiness, ContactTargetStatus, DemoAccessStatus,
    ManualReviewStatus, DemoReadiness
)
from app.services.scoring_engine import ScoringEngine
from app.agents.demo_generator_agent import DemoGeneratorAgent
from app.agents.outreach_agent import OutreachAgent
from app.orchestrator.pipeline import CampaignPipelineRunner
from app.schemas.agent import AgentInput


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_scoring_v1_component_breakdown(db):
    """Verify that ScoringEngine returns all 5 transparent components with raw_score, weight_pct, contribution, reason, and evidence."""
    biz = Business(
        name="Test Dhaba",
        category="restaurant",
        address="Navrangpura, Ahmedabad",
        city="Ahmedabad",
        phone="+91 98250 00000",
        rating=4.6,
        review_count=550,
        website_status=WebsiteStatus.NO_WEBSITE,
        website_verification_status=WebsiteVerificationStatus.NO_WEBSITE_CONFIRMED
    )
    db.add(biz)
    db.commit()

    breakdown = ScoringEngine.calculate_score(
        business=biz,
        audit=None,
        decision_maker_confidence="HIGH",
        purchase_signals=["Expansion"]
    )

    assert breakdown["score_version"] == "V1_AGREED_35_25_20_10_10"
    assert "components" in breakdown
    comps = breakdown["components"]
    
    # 1. Digital Opportunity Gap
    assert comps["digital_opportunity_gap"]["weight_pct"] == 35.0
    assert comps["digital_opportunity_gap"]["contribution"] == 35.0
    assert comps["digital_opportunity_gap"]["raw_score"] == 100.0

    # 2. Customer Traction
    assert comps["customer_traction"]["weight_pct"] == 25.0
    assert comps["customer_traction"]["contribution"] <= 25.0

    # 3. Commercial Potential
    assert comps["commercial_potential"]["weight_pct"] == 20.0

    # 4. Contactability
    assert comps["contactability"]["weight_pct"] == 10.0

    # 5. Purchase Signals
    assert comps["purchase_signals"]["weight_pct"] == 10.0

    # Total score capped <= 100.0
    assert 0.0 <= breakdown["total_score"] <= 100.0


def test_manual_review_status_assignment(db):
    """Verify that ManualReviewStatus is assigned accurately based on ambiguity or score."""
    campaign = Campaign(name="Test Campaign", city="Ahmedabad")
    db.add(campaign)
    db.commit()

    # Clear lead (no website confirmed, verified entity, phone present) -> NO_REVIEW_REQUIRED
    clear_lead = Business(
        campaign_id=campaign.id,
        name="Clear Business",
        category="restaurant",
        address="SG Highway",
        city="Ahmedabad",
        rating=4.5,
        review_count=600,
        website_status=WebsiteStatus.NO_WEBSITE,
        website_verification_status=WebsiteVerificationStatus.NO_WEBSITE_CONFIRMED,
        entity_verification_status=EntityVerificationStatus.VERIFIED,
        opportunity_score=85.0
    )
    # Ambiguous lead (conflicting websites) -> REVIEW_REQUIRED
    ambiguous_lead = Business(
        campaign_id=campaign.id,
        name="Ambiguous Business",
        category="restaurant",
        address="Law Garden",
        city="Ahmedabad",
        rating=4.0,
        review_count=100,
        website_status=WebsiteStatus.WEAK_WEBSITE,
        website_verification_status=WebsiteVerificationStatus.CONFLICTING_WEBSITES,
        entity_verification_status=EntityVerificationStatus.VERIFIED,
        opportunity_score=75.0
    )
    db.add_all([clear_lead, ambiguous_lead])
    db.commit()

    runner = CampaignPipelineRunner(db)
    runner._update_manual_review_status(clear_lead)
    runner._update_manual_review_status(ambiguous_lead)

    assert clear_lead.manual_review_status == ManualReviewStatus.NO_REVIEW_REQUIRED
    assert ambiguous_lead.manual_review_status == ManualReviewStatus.REVIEW_REQUIRED
    assert len(ambiguous_lead.manual_review_reasons) > 0


def test_public_demo_verification_and_reachability(db):
    """Verify DemoGeneratorAgent URL verification logic and PUBLIC_DEMO_BASE_URL handling."""
    agent = DemoGeneratorAgent(db=db, public_base_url="https://demo.example.com")
    
    # 1. Mock test domain -> PUBLIC_ACCESSIBLE
    status, code, err = agent.verify_demo_url("https://demo.example.com/static/demos/123/index.html")
    assert status == DemoAccessStatus.PUBLIC_ACCESSIBLE
    assert code == 200

    # 2. Localhost URL -> LOCAL_ONLY
    status_local, _, err_local = agent.verify_demo_url("http://localhost:8000/static/demos/123/index.html")
    assert status_local == DemoAccessStatus.LOCAL_ONLY
    assert "Internal/Private host" in err_local

    # 3. Non-HTTPS URL -> LOCAL_ONLY
    status_http, _, err_http = agent.verify_demo_url("http://publicdomain.com/demo.html")
    assert status_http == DemoAccessStatus.LOCAL_ONLY
    assert "Non-HTTPS" in err_http


def test_outreach_demo_link_gating(db):
    """Verify OutreachAgent only includes demo links if demo_access_status == PUBLIC_ACCESSIBLE."""
    biz = Business(
        name="Local Dhaba",
        category="restaurant",
        address="Ellisbridge",
        city="Ahmedabad",
        phone="+91 98250 11111",
        public_demo_url="http://localhost:8000/static/demos/1/index.html",
        demo_access_status=DemoAccessStatus.LOCAL_ONLY,
        entity_verification_status=EntityVerificationStatus.VERIFIED,
        website_verification_status=WebsiteVerificationStatus.NO_WEBSITE_CONFIRMED,
        contact_target_status=ContactTargetStatus.BUSINESS_CONTACT_ONLY,
        workflow_state=WorkflowState.DEMO_GENERATED
    )
    db.add(biz)
    db.commit()

    agent = OutreachAgent(db)
    res = agent.run(AgentInput(lead_id=biz.id))

    # Local demo link MUST be excluded from email and whatsapp body
    assert "http://localhost:8000" not in res["email_body"]
    assert "http://localhost:8000" not in res["whatsapp_body"]
    assert res["demo_url"] is None
