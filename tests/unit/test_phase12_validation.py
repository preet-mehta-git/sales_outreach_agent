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
from app.agents.entity_verifier_agent import EntityVerifierAgent
from app.agents.website_verifier_agent import WebsiteVerifierAgent
from app.agents.contact_discovery_agent import ContactDiscoveryAgent
from app.agents.demo_generator_agent import DemoGeneratorAgent
from app.agents.outreach_agent import OutreachAgent
from app.orchestrator.pipeline import CampaignPipelineRunner
from app.schemas.agent import AgentInput
from scripts.run_phase12_validation import AHMEDABAD_PHASE12_SAMPLE, determine_final_action


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_phase12_sample_size_and_diversity():
    """Verify that the Phase 12 validation sample meets the required 30-50 size."""
    assert len(AHMEDABAD_PHASE12_SAMPLE) >= 30
    assert len(AHMEDABAD_PHASE12_SAMPLE) <= 50


def test_phase12_non_business_entity_filtering(db):
    """Verify that non-business entities (food markets, food parks, food streets) are rejected."""
    agent = EntityVerifierAgent(db)
    
    entities_to_test = [
        ("Manek Chowk Night Food Market", "street food market"),
        ("Urban Chowk Food Park", "food park"),
        ("Law Garden Khau Gali", "food street"),
        ("Sindhu Bhavan Food Park", "food park")
    ]
    
    for name, cat in entities_to_test:
        biz = Business(
            name=name,
            category=cat,
            address="Ahmedabad",
            city="Ahmedabad"
        )
        db.add(biz)
        db.commit()
        
        res = agent.run(AgentInput(lead_id=biz.id))
        assert res["verification_status"] == "REJECTED"
        assert res["entity_type"] == "NON_BUSINESS"
        assert biz.workflow_state == WorkflowState.REJECTED


def test_phase12_zero_fabrication_contact_discovery(db):
    """Verify that no decision maker names, roles, or phones are fabricated for arbitrary businesses."""
    biz = Business(
        name="Das Khaman",
        category="traditional snacks",
        address="Nehrunagar, Ahmedabad",
        city="Ahmedabad",
        phone="+91 79 2630 4567"
    )
    db.add(biz)
    db.commit()

    agent = ContactDiscoveryAgent(db)
    res = agent.run(AgentInput(lead_id=biz.id))

    assert res["full_name"] is None
    assert res["contact_target_status"] == ContactTargetStatus.BUSINESS_CONTACT_ONLY.value
    assert res["phone"] == "+91 79 2630 4567"


def test_phase12_demo_gating_and_no_localhost_leak(db):
    """Verify that local-only demo URLs never leak into outreach drafts."""
    biz = Business(
        name="Lucky Tea Stall",
        category="cafe",
        address="Mirzapur, Ahmedabad",
        city="Ahmedabad",
        phone="+91 79 2562 1100",
        rating=4.3,
        review_count=760,
        website_status=WebsiteStatus.NO_WEBSITE,
        website_verification_status=WebsiteVerificationStatus.NO_WEBSITE_CONFIRMED,
        entity_verification_status=EntityVerificationStatus.VERIFIED,
        entity_type=EntityType.BUSINESS,
        workflow_state=WorkflowState.BUSINESS_AUDITED
    )
    db.add(biz)
    db.commit()

    demo_agent = DemoGeneratorAgent(db)
    demo_agent.run(AgentInput(lead_id=biz.id))

    assert biz.demo_access_status == DemoAccessStatus.LOCAL_ONLY
    assert "localhost" in biz.local_preview_url

    outreach_agent = OutreachAgent(db)
    outreach_res = outreach_agent.run(AgentInput(lead_id=biz.id))

    assert "localhost" not in outreach_res["email_body"]
    assert "localhost" not in outreach_res["whatsapp_body"]
    assert outreach_res["demo_url"] is None


def test_phase12_final_action_semantics_comprehensive():
    """Verify all combinations of final action resolution in Phase 12."""
    assert determine_final_action("REVIEW_REQUIRED", "PRIORITY", "READY_FOR_APPROVAL") == "REQUIRES_MANUAL_REVIEW"
    assert determine_final_action("REVIEW_RECOMMENDED", "PRIORITY", "READY_FOR_APPROVAL") == "REVIEW_RECOMMENDED"
    assert determine_final_action("NO_REVIEW_REQUIRED", "PRIORITY", "READY_FOR_APPROVAL") == "AWAITING_HUMAN_OUTREACH_APPROVAL"
    assert determine_final_action("NO_REVIEW_REQUIRED", "REJECTED", "NOT_READY") == "REJECTED"
    assert determine_final_action("NO_REVIEW_REQUIRED", "QUALIFIED", "NOT_READY") == "QUALIFIED_NOT_READY"
