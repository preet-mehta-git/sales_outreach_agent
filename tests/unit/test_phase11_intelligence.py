import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import Business, Campaign, DecisionMakerRecord, WebsiteAudit, OutreachDraft
from app.schemas.enums import (
    EntityType, EntityVerificationStatus, WebsiteStatus, WebsiteVerificationStatus,
    WebsiteClassification, ConfidenceLevel, OutreachStatus, OutreachReadiness, WorkflowState
)
from app.schemas.agent import AgentInput
from app.agents.entity_verifier_agent import EntityVerifierAgent
from app.agents.website_verifier_agent import WebsiteVerifierAgent
from app.agents.website_audit_agent import WebsiteAuditAgent
from app.agents.contact_discovery_agent import ContactDiscoveryAgent
from app.agents.business_audit_agent import BusinessAuditAgent
from app.agents.demo_generator_agent import DemoGeneratorAgent
from app.agents.outreach_agent import OutreachAgent
from app.services.scoring_engine import ScoringEngine


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_01_source_b_discovers_missing_website(db_session):
    b = Business(
        name="Gordhan Thal",
        category="Restaurant",
        address="SG Highway, Ahmedabad",
        city="Ahmedabad",
        website_url=None,
        workflow_state=WorkflowState.VERIFIED
    )
    db_session.add(b)
    db_session.commit()

    agent = WebsiteVerifierAgent(db_session)
    res = agent.execute(AgentInput(lead_id=b.id))

    assert res.success is True
    assert b.website_url == "http://gordhanthal.com"
    assert b.website_source == "WEB_SEARCH_SOURCE_B"
    assert b.website_verification_status == WebsiteVerificationStatus.OFFICIAL_WEBSITE_VERIFIED


def test_02_source_b_replaces_third_party_url(db_session):
    b = Business(
        name="Swati Snacks",
        category="Restaurant",
        address="Law Garden, Ahmedabad",
        city="Ahmedabad",
        website_url="https://www.zomato.com/ahmedabad/swati-snacks-law-garden",
        workflow_state=WorkflowState.VERIFIED
    )
    db_session.add(b)
    db_session.commit()

    agent = WebsiteVerifierAgent(db_session)
    res = agent.execute(AgentInput(lead_id=b.id))

    assert res.success is True
    assert b.website_url == "https://swatisnacks.com"
    assert b.website_source == "WEB_SEARCH_SOURCE_B"


def test_03_non_business_entity_filtering(db_session):
    b = Business(
        name="Manek Chowk Night Food Market",
        category="Food Market Location",
        address="Manek Chowk, Old City, Ahmedabad",
        city="Ahmedabad"
    )
    db_session.add(b)
    db_session.commit()

    agent = EntityVerifierAgent(db_session)
    res = agent.execute(AgentInput(lead_id=b.id))

    assert res.success is True
    assert b.entity_type == EntityType.NON_BUSINESS
    assert b.entity_verification_status == EntityVerificationStatus.REJECTED
    assert b.workflow_state == WorkflowState.REJECTED


def test_04_official_website_domain_matching(db_session):
    b = Business(
        name="House of MG",
        category="Hotel & Heritage Dining",
        address="Lal Darwaja, Ahmedabad",
        city="Ahmedabad",
        website_url="https://houseofmg.com",
        workflow_state=WorkflowState.VERIFIED
    )
    db_session.add(b)
    db_session.commit()

    agent = WebsiteVerifierAgent(db_session)
    res = agent.execute(AgentInput(lead_id=b.id))

    assert res.success is True
    assert b.website_verification_status == WebsiteVerificationStatus.OFFICIAL_WEBSITE_VERIFIED


def test_05_third_party_directory_rejection(db_session):
    b = Business(
        name="Unknown Small Food Stall",
        category="Fast Food",
        address="CG Road, Ahmedabad",
        city="Ahmedabad",
        website_url="https://www.justdial.com/Ahmedabad/Unknown-Stall",
        workflow_state=WorkflowState.VERIFIED
    )
    db_session.add(b)
    db_session.commit()

    agent = WebsiteVerifierAgent(db_session)
    res = agent.execute(AgentInput(lead_id=b.id))

    assert res.success is True
    assert b.website_url is None
    assert b.website_verification_status == WebsiteVerificationStatus.NO_WEBSITE_CONFIRMED


def test_06_unverified_decision_maker_zero_fabrication(db_session):
    b = Business(
        name="Random Local Cafe",
        category="Cafe",
        address="Vastrapur, Ahmedabad",
        city="Ahmedabad"
    )
    db_session.add(b)
    db_session.commit()

    agent = ContactDiscoveryAgent(db_session)
    res = agent.execute(AgentInput(lead_id=b.id))

    assert res.success is True
    dm = db_session.query(DecisionMakerRecord).filter(DecisionMakerRecord.business_id == b.id).first()
    assert dm.name is None
    assert dm.confidence == ConfidenceLevel.NOT_FOUND


def test_07_verified_decision_maker_evidence(db_session):
    b = Business(
        name="Agashiye - House of MG",
        category="Restaurant",
        address="Lal Darwaja, Ahmedabad",
        city="Ahmedabad"
    )
    db_session.add(b)
    db_session.commit()

    agent = ContactDiscoveryAgent(db_session)
    res = agent.execute(AgentInput(lead_id=b.id))

    assert res.success is True
    dm = db_session.query(DecisionMakerRecord).filter(DecisionMakerRecord.business_id == b.id).first()
    assert dm.name == "Abhay Mangaldas"
    assert dm.confidence == ConfidenceLevel.HIGH


def test_08_website_classification_rules(db_session):
    b = Business(
        name="Tech Cafe",
        category="Cafe",
        address="Bodakdev, Ahmedabad",
        city="Ahmedabad",
        website_url="https://techcafe.com",
        website_verification_status=WebsiteVerificationStatus.OFFICIAL_WEBSITE_VERIFIED,
        website_status=WebsiteStatus.WEBSITE_FOUND
    )
    db_session.add(b)
    db_session.commit()

    agent = WebsiteAuditAgent(db_session)
    res = agent.execute(AgentInput(lead_id=b.id))

    assert res.success is True
    assert b.website_classification in [
        WebsiteClassification.GOOD_WEBSITE,
        WebsiteClassification.EXCELLENT_WEBSITE,
        WebsiteClassification.POOR_CONVERSION,
        WebsiteClassification.TECHNICALLY_GOOD,
        WebsiteClassification.OUTDATED_WEBSITE,
        WebsiteClassification.WEAK_WEBSITE
    ]


def test_09_unsupported_claims_check_in_outreach(db_session):
    b = Business(
        name="Gordhan Thal",
        category="Restaurant",
        address="SG Highway, Ahmedabad",
        city="Ahmedabad",
        phone="+919825000000",
        rating=4.4,
        review_count=1200,
        entity_type=EntityType.BUSINESS,
        entity_verification_status=EntityVerificationStatus.VERIFIED,
        website_verification_status=WebsiteVerificationStatus.OFFICIAL_WEBSITE_VERIFIED,
        public_demo_url="http://localhost:8000/static/demos/test/index.html"
    )
    db_session.add(b)
    db_session.commit()

    agent = OutreachAgent(db_session)
    res = agent.execute(AgentInput(lead_id=b.id))

    assert res.success is True
    draft = db_session.query(OutreachDraft).filter(OutreachDraft.business_id == b.id).first()
    assert "100% revenue" not in draft.email_body
    assert "top restaurant" not in draft.email_body.lower()


def test_10_public_demo_url_format(db_session):
    b = Business(
        name="Upper Crust",
        category="Bakery",
        address="Vijay Cross Road, Ahmedabad",
        city="Ahmedabad"
    )
    db_session.add(b)
    db_session.commit()

    agent = DemoGeneratorAgent(db_session, public_base_url="https://demos.example.com")
    res = agent.execute(AgentInput(lead_id=b.id))

    assert res.success is True
    assert b.local_preview_url.startswith("http://localhost:8000/static/demos/")
    assert b.public_demo_url is not None
    assert b.public_demo_url.startswith("https://demos.example.com/static/demos/")



def test_11_suppression_flag_override(db_session):
    b = Business(
        name="Suppressed Cafe",
        category="Cafe",
        address="Prahlad Nagar, Ahmedabad",
        city="Ahmedabad",
        is_suppressed=True,
        phone="+919898000000",
        entity_type=EntityType.BUSINESS,
        entity_verification_status=EntityVerificationStatus.VERIFIED,
        website_verification_status=WebsiteVerificationStatus.NO_WEBSITE_CONFIRMED,
        public_demo_url="http://localhost:8000/static/demos/test/index.html"
    )
    db_session.add(b)
    db_session.commit()

    agent = OutreachAgent(db_session)
    res = agent.execute(AgentInput(lead_id=b.id))

    assert res.success is True
    assert b.outreach_readiness == OutreachReadiness.SUPPRESSED


def test_12_sample_data_labeling_in_demo(db_session):
    b = Business(
        name="Havmor Restaurant",
        category="Restaurant",
        address="Navrangpura, Ahmedabad",
        city="Ahmedabad"
    )
    db_session.add(b)
    db_session.commit()

    agent = DemoGeneratorAgent(db_session)
    res = agent.execute(AgentInput(lead_id=b.id))

    assert res.success is True
    file_path = res.data["file_path"]
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "SAMPLE / DEMO DATA" in content


def test_13_opportunity_score_vs_outreach_readiness_decoupling(db_session):
    b = Business(
        name="Unverified High Rating Spot",
        category="Restaurant",
        address="C G Road, Ahmedabad",
        city="Ahmedabad",
        rating=4.8,
        review_count=1500,
        phone="+919876543210",
        entity_type=EntityType.UNCERTAIN,
        entity_verification_status=EntityVerificationStatus.MANUAL_REVIEW,
        website_verification_status=WebsiteVerificationStatus.WEBSITE_FOUND_UNVERIFIED
    )
    db_session.add(b)
    db_session.commit()

    score_dict = ScoringEngine.calculate_score(b)
    assert score_dict["total_score"] >= 70.0

    agent = OutreachAgent(db_session)
    agent.execute(AgentInput(lead_id=b.id))

    assert b.outreach_readiness == OutreachReadiness.MANUAL_REVIEW


def test_14_full_pipeline_pass_rate(db_session):
    campaign = Campaign(name="Phase 11 Verification Campaign", city="Ahmedabad")
    db_session.add(campaign)
    db_session.commit()

    b = Business(
        campaign_id=campaign.id,
        name="Gordhan Thal",
        category="Thali Restaurant",
        address="SG Highway, Ahmedabad",
        city="Ahmedabad",
        phone="+917926871222",
        rating=4.4,
        review_count=850
    )
    db_session.add(b)
    db_session.commit()

    from app.orchestrator.pipeline import CampaignPipelineRunner
    runner = CampaignPipelineRunner(db_session)
    res = runner.run_lead_pipeline(b)

    assert res["status"] == "COMPLETED"
    assert res["qualified"] is True
    assert b.outreach_readiness == OutreachReadiness.READY_FOR_APPROVAL
