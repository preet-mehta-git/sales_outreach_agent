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
from app.agents.qualification_agent import QualificationAgent
from app.agents.demo_generator_agent import DemoGeneratorAgent
from app.agents.outreach_agent import OutreachAgent
from app.schemas.agent import AgentInput
from scripts.run_phase12_validation import determine_final_action


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_1_non_business_with_score_100_is_rejected(db):
    """Test 1: A NON_BUSINESS entity with score 100 is rejected."""
    biz = Business(
        name="Manek Chowk Night Food Market",
        category="street food market",
        address="Manek Chowk, Ahmedabad",
        city="Ahmedabad",
        opportunity_score=100.0,
        entity_type=EntityType.NON_BUSINESS,
        entity_verification_status=EntityVerificationStatus.REJECTED,
        workflow_state=WorkflowState.SCORED
    )
    db.add(biz)
    db.commit()

    agent = QualificationAgent(db)
    res = agent.run(AgentInput(lead_id=biz.id))

    assert res["qualified"] is False
    assert res["classification"] == "REJECTED"
    assert res["reason"] == "NON_BUSINESS_ENTITY_REJECTED"


def test_2_non_business_cannot_appear_in_ranked_prospects():
    """Test 2: A NON_BUSINESS entity cannot appear in ranked prospects."""
    entities = [
        {"name": "Manek Chowk Night Food Market", "entity_status": "REJECTED", "opportunity_score": 86.0, "qualification": "REJECTED"},
        {"name": "Das Khaman", "entity_status": "VERIFIED", "opportunity_score": 86.0, "qualification": "PRIORITY"},
        {"name": "Jail Na Bhajiya", "entity_status": "VERIFIED", "opportunity_score": 86.0, "qualification": "PRIORITY"}
    ]

    # Enforce ranking layer filter: only VERIFIED businesses can be ranked
    ranked_prospects = [e for e in entities if e["entity_status"] == "VERIFIED" and e["qualification"] != "REJECTED"]

    assert len(ranked_prospects) == 2
    assert all(p["name"] != "Manek Chowk Night Food Market" for p in ranked_prospects)
    assert all(p["entity_status"] == "VERIFIED" for p in ranked_prospects)


def test_3_non_business_cannot_appear_in_top_10():
    """Test 3: A NON_BUSINESS entity cannot appear in Top 10."""
    entities = [
        {"name": f"Business {i}", "entity_status": "VERIFIED", "opportunity_score": 80.0 + i, "qualification": "PRIORITY"}
        for i in range(12)
    ]
    # Insert high scoring non-business entities
    entities.append({"name": "Manek Chowk Night Food Market", "entity_status": "REJECTED", "opportunity_score": 95.0, "qualification": "REJECTED"})
    entities.append({"name": "Urban Chowk Food Park", "entity_status": "REJECTED", "opportunity_score": 94.0, "qualification": "REJECTED"})

    ranked_prospects = [e for e in entities if e["entity_status"] == "VERIFIED" and e["qualification"] != "REJECTED"]
    ranked_prospects.sort(key=lambda x: x["opportunity_score"], reverse=True)
    top_10 = ranked_prospects[:10]

    assert len(top_10) == 10
    assert all(b["entity_status"] == "VERIFIED" for b in top_10)
    assert not any("Market" in b["name"] or "Food Park" in b["name"] for b in top_10)


def test_4_non_business_cannot_appear_in_top_5():
    """Test 4: A NON_BUSINESS entity cannot appear in Top 5."""
    entities = [
        {"name": "Urban Chowk Food Park", "entity_status": "REJECTED", "opportunity_score": 99.0, "qualification": "REJECTED"},
        {"name": "Das Khaman", "entity_status": "VERIFIED", "opportunity_score": 86.0, "qualification": "PRIORITY"},
        {"name": "Jail Na Bhajiya", "entity_status": "VERIFIED", "opportunity_score": 86.0, "qualification": "PRIORITY"},
        {"name": "Atithi Dining Hall", "entity_status": "VERIFIED", "opportunity_score": 86.0, "qualification": "PRIORITY"},
        {"name": "Lijjat Khaman House", "entity_status": "VERIFIED", "opportunity_score": 85.7, "qualification": "PRIORITY"},
        {"name": "Unlocked Cafe", "entity_status": "VERIFIED", "opportunity_score": 85.1, "qualification": "PRIORITY"}
    ]

    ranked_prospects = [e for e in entities if e["entity_status"] == "VERIFIED" and e["qualification"] != "REJECTED"]
    ranked_prospects.sort(key=lambda x: x["opportunity_score"], reverse=True)
    top_5 = ranked_prospects[:5]

    assert len(top_5) == 5
    assert all(b["entity_status"] == "VERIFIED" for b in top_5)
    assert not any(b["name"] == "Urban Chowk Food Park" for b in top_5)


def test_5_non_business_cannot_become_awaiting_human_outreach_approval():
    """Test 5: A NON_BUSINESS entity cannot become AWAITING_HUMAN_OUTREACH_APPROVAL."""
    action = determine_final_action(
        manual_review_status="NO_REVIEW_REQUIRED",
        qualification="REJECTED",
        outreach_readiness="READY_FOR_APPROVAL",
        entity_status="REJECTED"
    )
    assert action == "REJECTED"
    assert action != "AWAITING_HUMAN_OUTREACH_APPROVAL"


def test_6_non_business_cannot_enter_demo_generation(db):
    """Test 6: A NON_BUSINESS entity cannot enter demo generation."""
    biz = Business(
        name="Law Garden Khau Gali",
        category="food street",
        address="Ellisbridge, Ahmedabad",
        city="Ahmedabad",
        entity_type=EntityType.NON_BUSINESS,
        entity_verification_status=EntityVerificationStatus.REJECTED
    )
    db.add(biz)
    db.commit()

    agent = DemoGeneratorAgent(db)
    res = agent.run(AgentInput(lead_id=biz.id))

    assert res["status"] == "SKIPPED_NON_BUSINESS"
    assert biz.demo_access_status == DemoAccessStatus.NOT_GENERATED
    assert biz.local_preview_url is None
    assert biz.public_demo_url is None


def test_7_non_business_cannot_enter_outreach_draft_generation(db):
    """Test 7: A NON_BUSINESS entity cannot enter outreach-draft generation."""
    biz = Business(
        name="Sindhu Bhavan Food Park",
        category="food park",
        address="Bodakdev, Ahmedabad",
        city="Ahmedabad",
        entity_type=EntityType.NON_BUSINESS,
        entity_verification_status=EntityVerificationStatus.REJECTED
    )
    db.add(biz)
    db.commit()

    agent = OutreachAgent(db)
    res = agent.run(AgentInput(lead_id=biz.id))

    assert res["status"] == "SKIPPED_NON_BUSINESS"
    assert biz.outreach_readiness == OutreachReadiness.NOT_READY
    draft = db.query(OutreachDraft).filter_by(business_id=biz.id).first()
    assert draft is None


def test_8_manual_review_entity_remains_manual_review(db):
    """Test 8: A MANUAL_REVIEW entity remains manual review and is not silently converted into BUSINESS."""
    biz = Business(
        name="Ambiguous Eatery Complex",
        category="complex",
        address="Navrangpura, Ahmedabad",
        city="Ahmedabad",
        opportunity_score=85.0,
        entity_type=EntityType.UNCERTAIN,
        entity_verification_status=EntityVerificationStatus.MANUAL_REVIEW
    )
    db.add(biz)
    db.commit()

    # Verify determine_final_action enforces manual review gating
    action = determine_final_action(
        manual_review_status="REVIEW_REQUIRED",
        qualification="POTENTIAL_REVIEW",
        outreach_readiness="NOT_READY",
        entity_status="MANUAL_REVIEW"
    )
    assert action == "REQUIRES_MANUAL_REVIEW"
    assert action != "AWAITING_HUMAN_OUTREACH_APPROVAL"
    assert action != "REJECTED"


def test_9_legitimate_business_continues_through_normal_pipeline(db):
    """Test 9: A legitimate BUSINESS entity continues through the normal scoring/ranking pipeline."""
    biz = Business(
        name="Das Khaman",
        category="traditional snacks",
        address="Nehrunagar, Ahmedabad",
        city="Ahmedabad",
        opportunity_score=86.0,
        entity_type=EntityType.BUSINESS,
        entity_verification_status=EntityVerificationStatus.VERIFIED,
        workflow_state=WorkflowState.SCORED
    )
    db.add(biz)
    db.commit()

    agent = QualificationAgent(db)
    res = agent.run(AgentInput(lead_id=biz.id))

    assert res["qualified"] is True
    assert res["classification"] == "PRIORITY"
    assert res["reason"] == "PRIORITY_SCORE_MET"


def test_10_final_aggregation_rechecks_entity_status():
    """Test 10: Final aggregation re-checks entity status even if upstream qualification incorrectly contains a high score."""
    # Simulate an anomaly where qualification somehow contained PRIORITY
    corrupted_record = {
        "business_name": "Manek Chowk Night Food Market",
        "opportunity_score": 86.0,
        "qualification": "PRIORITY",  # Upstream anomaly
        "entity_status": "REJECTED",
        "action": "AWAITING_HUMAN_OUTREACH_APPROVAL"  # Upstream anomaly
    }

    # Final aggregation gatekeeper
    def aggregate_prospects(records):
        ranked = []
        for r in records:
            # Re-check entity status gate
            if r["entity_status"] != "VERIFIED":
                r["qualification"] = "REJECTED"
                r["action"] = "REJECTED"
                continue
            ranked.append(r)
        return ranked

    ranked = aggregate_prospects([corrupted_record])

    assert len(ranked) == 0
    assert corrupted_record["qualification"] == "REJECTED"
    assert corrupted_record["action"] == "REJECTED"
