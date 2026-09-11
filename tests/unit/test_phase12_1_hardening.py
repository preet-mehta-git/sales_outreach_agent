import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import Business, WebsiteAudit, DecisionMakerRecord, OutreachDraft, Campaign
from app.schemas.enums import (
    WorkflowState, WebsiteStatus, WebsiteVerificationStatus, WebsiteClassification,
    EntityVerificationStatus, EntityType, OutreachReadiness, ContactTargetStatus,
    DemoAccessStatus, ManualReviewStatus, DemoReadiness
)
from app.services.scoring_engine import ScoringEngine
from app.agents.website_verifier_agent import WebsiteVerifierAgent
from app.agents.website_audit_agent import WebsiteAuditAgent
from app.agents.opportunity_scorer_agent import OpportunityScorerAgent
from app.agents.qualification_agent import QualificationAgent
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


def test_timeout_does_not_become_no_website(db):
    """1. Verify timeout results in CONTENT_UNVERIFIED and never NO_WEBSITE."""
    biz = Business(
        name="Timeout Cafe",
        category="cafe",
        address="Navrangpura, Ahmedabad",
        city="Ahmedabad",
        website_url="http://timeout-test.com",
        workflow_state=WorkflowState.VERIFIED
    )
    db.add(biz)
    db.commit()

    agent = WebsiteVerifierAgent(db)
    res = agent.run(AgentInput(lead_id=biz.id))

    assert res["website_status"] != WebsiteStatus.NO_WEBSITE.value
    assert res["website_verification_status"] == WebsiteVerificationStatus.CONTENT_UNVERIFIED.value
    assert biz.website_url == "http://timeout-test.com"


def test_http_403_does_not_become_no_website(db):
    """2. Verify HTTP 403 results in CONTENT_UNVERIFIED and never NO_WEBSITE."""
    biz = Business(
        name="Forbidden Bistro",
        category="restaurant",
        address="Bodakdev, Ahmedabad",
        city="Ahmedabad",
        website_url="http://forbidden-test.com",
        workflow_state=WorkflowState.VERIFIED
    )
    db.add(biz)
    db.commit()

    agent = WebsiteVerifierAgent(db)
    res = agent.run(AgentInput(lead_id=biz.id))

    assert res["website_status"] != WebsiteStatus.NO_WEBSITE.value
    assert res["website_verification_status"] == WebsiteVerificationStatus.CONTENT_UNVERIFIED.value


def test_http_429_does_not_become_no_website(db):
    """3. Verify HTTP 429 results in CONTENT_UNVERIFIED and never NO_WEBSITE."""
    biz = Business(
        name="RateLimited Diner",
        category="diner",
        address="SG Highway, Ahmedabad",
        city="Ahmedabad",
        website_url="http://ratelimit-test.com",
        workflow_state=WorkflowState.VERIFIED
    )
    db.add(biz)
    db.commit()

    agent = WebsiteVerifierAgent(db)
    res = agent.run(AgentInput(lead_id=biz.id))

    assert res["website_status"] != WebsiteStatus.NO_WEBSITE.value
    assert res["website_verification_status"] == WebsiteVerificationStatus.CONTENT_UNVERIFIED.value


def test_http_500_does_not_become_no_website(db):
    """4. Verify HTTP 500 results in CONTENT_UNVERIFIED and never NO_WEBSITE."""
    biz = Business(
        name="ServerError Eatery",
        category="restaurant",
        address="Prahladnagar, Ahmedabad",
        city="Ahmedabad",
        website_url="http://servererror-test.com",
        workflow_state=WorkflowState.VERIFIED
    )
    db.add(biz)
    db.commit()

    agent = WebsiteVerifierAgent(db)
    res = agent.run(AgentInput(lead_id=biz.id))

    assert res["website_status"] != WebsiteStatus.NO_WEBSITE.value
    assert res["website_verification_status"] == WebsiteVerificationStatus.CONTENT_UNVERIFIED.value


def test_dns_failure_treated_as_stronger_evidence_of_unavailable(db):
    """5. Verify DNS failure is marked as MANUAL_REVIEW / DNS_FAILURE and not NO_WEBSITE without discovery."""
    biz = Business(
        name="Dead Domain Cafe",
        category="cafe",
        address="Ellisbridge, Ahmedabad",
        city="Ahmedabad",
        website_url="http://dnsfail-domain.com",
        workflow_state=WorkflowState.VERIFIED
    )
    db.add(biz)
    db.commit()

    agent = WebsiteVerifierAgent(db)
    res = agent.run(AgentInput(lead_id=biz.id))

    assert res["website_status"] == WebsiteStatus.WEBSITE_UNREACHABLE.value
    assert res["website_verification_status"] == WebsiteVerificationStatus.MANUAL_REVIEW.value


def test_successful_response_requires_business_identity_matching(db):
    """6. Verify successful HTTP response still enforces domain validation and prevents aggregator takeover."""
    biz = Business(
        name="Zomato Listed Cafe",
        category="cafe",
        address="Vastrapur, Ahmedabad",
        city="Ahmedabad",
        website_url="https://www.zomato.com/ahmedabad/cafe-123",
        workflow_state=WorkflowState.VERIFIED
    )
    db.add(biz)
    db.commit()

    agent = WebsiteVerifierAgent(db)
    res = agent.run(AgentInput(lead_id=biz.id))

    # Aggregator URL must be stripped and not treated as official verified domain
    assert res["website_url"] != "https://www.zomato.com/ahmedabad/cafe-123"


def test_conflicting_websites_remain_manual_review(db):
    """7. Verify conflicting website situations require manual review in pipeline."""
    biz = Business(
        name="Conflicting Brand",
        category="restaurant",
        address="Paldi, Ahmedabad",
        city="Ahmedabad",
        website_status=WebsiteStatus.WEBSITE_UNREACHABLE,
        website_verification_status=WebsiteVerificationStatus.CONFLICTING_WEBSITES,
        entity_verification_status=EntityVerificationStatus.VERIFIED,
        opportunity_score=75.0
    )
    db.add(biz)
    db.commit()

    runner = CampaignPipelineRunner(db)
    runner._update_manual_review_status(biz)

    assert biz.manual_review_status == ManualReviewStatus.REVIEW_REQUIRED


def test_temporary_failures_do_not_inflate_digital_gap(db):
    """8. Verify temporary network failures do not award 35.0 maximum Digital Opportunity Gap."""
    biz = Business(
        name="Transient Cafe",
        category="cafe",
        address="Navrangpura, Ahmedabad",
        city="Ahmedabad",
        rating=4.5,
        review_count=800,
        website_url="http://timeout-test.com",
        website_status=WebsiteStatus.WEBSITE_UNREACHABLE,
        website_verification_status=WebsiteVerificationStatus.CONTENT_UNVERIFIED
    )
    db.add(biz)
    db.commit()

    breakdown = ScoringEngine.calculate_score(biz)
    digital_gap = breakdown["components"]["digital_opportunity_gap"]["contribution"]

    # Digital gap should be conservative neutral (17.5) and NOT inflated to 35.0
    assert digital_gap < 35.0
    assert digital_gap == 17.5


def test_makeba_recheck_with_good_website(db):
    """9. Recheck Makeba The Lounge Cafe with active good website: verifies score drops to ~56.0 and REJECTED."""
    biz = Business(
        name="Makeba The Lounge Cafe",
        category="rooftop cafe",
        address="31Five, SG Highway, Ahmedabad",
        city="Ahmedabad",
        phone="+91 98258 99001",
        rating=4.4,
        review_count=820,
        website_url="https://makeba.in",
        website_status=WebsiteStatus.WEBSITE_FOUND,
        website_verification_status=WebsiteVerificationStatus.OFFICIAL_WEBSITE_VERIFIED,
        entity_verification_status=EntityVerificationStatus.VERIFIED,
        workflow_state=WorkflowState.WEBSITE_ANALYZED
    )
    db.add(biz)
    db.commit()

    # Step 1: Website Audit
    audit_agent = WebsiteAuditAgent(db)
    audit_agent.run(AgentInput(lead_id=biz.id))

    # Step 2: Scoring
    scorer = OpportunityScorerAgent(db)
    score_out = scorer.run(AgentInput(lead_id=biz.id))

    # Step 3: Qualification
    qual_agent = QualificationAgent(db)
    qual_out = qual_agent.run(AgentInput(lead_id=biz.id))

    # Score should be ~52.0 (Digital gap is small because Makeba has a good website)
    score = score_out["opportunity_score"]
    assert score < 60.0, f"Expected Makeba score < 60.0, got {score}"
    assert qual_out["classification"] == "REJECTED"
