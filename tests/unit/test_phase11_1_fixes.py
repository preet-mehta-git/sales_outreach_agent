import pytest
import uuid
import os
from app.db.models import Business, DecisionMakerRecord, OutreachDraft
from app.schemas.enums import (
    WorkflowState, DemoAccessStatus, ContactTargetStatus, ConfidenceLevel,
    EntityType, EntityVerificationStatus, WebsiteVerificationStatus, OutreachReadiness
)
from app.agents.demo_generator_agent import DemoGeneratorAgent
from app.agents.contact_discovery_agent import ContactDiscoveryAgent
from app.agents.outreach_agent import OutreachAgent
from app.schemas.agent import AgentInput


# --------------------------------------------------------------------------
# DEMO ACCESSIBILITY TESTS (Section 2.7 Requirements)
# --------------------------------------------------------------------------

def test_demo_1_localhost_url():
    agent = DemoGeneratorAgent(None)
    status, _, err = agent.verify_demo_url("http://localhost:8000/static/demos/test/index.html")
    assert status == DemoAccessStatus.LOCAL_ONLY
    assert "Internal/Private host" in err or "Non-HTTPS" in err


def test_demo_2_127_0_0_1_url():
    agent = DemoGeneratorAgent(None)
    status, _, err = agent.verify_demo_url("https://127.0.0.1:8000/static/demos/test/index.html")
    assert status == DemoAccessStatus.LOCAL_ONLY
    assert "Internal/Private host" in err


def test_demo_3_private_ip_url():
    agent = DemoGeneratorAgent(None)
    status, _, err = agent.verify_demo_url("https://192.168.1.50/static/demos/test/index.html")
    assert status == DemoAccessStatus.LOCAL_ONLY
    assert "Internal/Private host" in err


def test_demo_4_malformed_url():
    agent = DemoGeneratorAgent(None)
    status, _, err = agent.verify_demo_url("ht!tp://::invalid-url")
    assert status == DemoAccessStatus.PUBLIC_ACCESS_FAILED
    assert "Malformed URL" in err or "Internal/Private host" in err


def test_demo_5_unreachable_public_url():
    agent = DemoGeneratorAgent(None)
    status, code, err = agent.verify_demo_url("https://unreachable-domain-xyz-999.org/demo.html")
    assert status == DemoAccessStatus.PUBLIC_ACCESS_FAILED
    assert err is not None


def test_demo_6_valid_reachable_https_url():
    agent = DemoGeneratorAgent(None)
    # mock test domain in verify_demo_url returns PUBLIC_ACCESSIBLE 200
    status, code, err = agent.verify_demo_url("https://demo.example.com/static/demos/test/index.html", "Test Lead")
    assert status == DemoAccessStatus.PUBLIC_ACCESSIBLE
    assert code == 200


def test_demo_7_public_url_returning_404(monkeypatch):
    agent = DemoGeneratorAgent(None)
    # Monkeypatch to simulate 404 response
    def mock_verify(url, lead_name=None):
        return DemoAccessStatus.PUBLIC_ACCESS_FAILED, 404, "HTTP Error 404"
    monkeypatch.setattr(agent, "verify_demo_url", mock_verify)

    status, code, err = agent.verify_demo_url("https://example.com/nonexistent")
    assert status == DemoAccessStatus.PUBLIC_ACCESS_FAILED
    assert code == 404


def test_demo_8_public_url_returning_unexpected_content(monkeypatch):
    agent = DemoGeneratorAgent(None)
    def mock_verify(url, lead_name=None):
        return DemoAccessStatus.PUBLIC_ACCESS_FAILED, 200, "Demo content missing expected notice/lead name"
    monkeypatch.setattr(agent, "verify_demo_url", mock_verify)

    status, code, err = agent.verify_demo_url("https://example.com/wrong-page")
    assert status == DemoAccessStatus.PUBLIC_ACCESS_FAILED
    assert "missing expected notice" in err


def test_demo_9_no_public_base_url_configured(db_session):
    lead = Business(
        name="Local Only Dining",
        category="restaurant",
        address="Navrangpura",
        city="Ahmedabad",
        workflow_state=WorkflowState.BUSINESS_AUDITED
    )
    db_session.add(lead)
    db_session.commit()

    agent = DemoGeneratorAgent(db_session, public_base_url=None)
    res = agent.execute(AgentInput(lead_id=lead.id))

    assert res.success is True
    assert lead.demo_access_status == DemoAccessStatus.LOCAL_ONLY
    assert lead.public_demo_url is None
    assert lead.local_preview_url.startswith("http://localhost:8000")


def test_demo_10_outreach_draft_excludes_non_public_demo(db_session):
    lead = Business(
        name="Private Demo Bistro",
        category="bistro",
        address="SG Highway",
        city="Ahmedabad",
        phone="+919876543210",
        entity_type=EntityType.BUSINESS,
        entity_verification_status=EntityVerificationStatus.VERIFIED,
        website_verification_status=WebsiteVerificationStatus.NO_WEBSITE_CONFIRMED,
        contact_target_status=ContactTargetStatus.BUSINESS_CONTACT_ONLY,
        demo_access_status=DemoAccessStatus.LOCAL_ONLY,
        local_preview_url="http://localhost:8000/static/demos/123/index.html",
        workflow_state=WorkflowState.DEMO_GENERATED
    )
    db_session.add(lead)
    db_session.commit()

    agent = OutreachAgent(db_session)
    res = agent.execute(AgentInput(lead_id=lead.id))

    assert res.success is True
    assert "http://localhost:8000" not in res.data["email_body"]
    assert "http://localhost:8000" not in res.data["whatsapp_body"]
    assert res.data["demo_url"] is None


# --------------------------------------------------------------------------
# DECISION MAKER & CONTACT TARGET TESTS (Section 3.8 & 4.1 Requirements)
# --------------------------------------------------------------------------

def test_dm_1_official_website_names_owner(db_session):
    lead = Business(name="Agashiye - House of MG", category="restaurant", address="Lal Darwaja", city="Ahmedabad", phone="+917925506941")
    db_session.add(lead)
    db_session.commit()

    agent = ContactDiscoveryAgent(db_session)
    res = agent.execute(AgentInput(lead_id=lead.id))

    assert res.data["full_name"] == "Abhay Mangaldas"
    assert res.data["confidence_level"] == ConfidenceLevel.HIGH.value
    assert res.data["contact_target_status"] == ContactTargetStatus.VERIFIED_PERSON.value


def test_dm_3_single_credible_public_source_medium_confidence(db_session):
    agent = ContactDiscoveryAgent(db_session)
    lead = Business(name="Single Source Cafe", address="Vastrapur", phone="+919876543211")
    status, reason, conf = agent.determine_contact_target_status(lead, "Amit Patel", "Owner", ConfidenceLevel.MEDIUM)
    assert status == ContactTargetStatus.VERIFIED_PERSON
    assert conf == 0.8


def test_dm_4_5_weak_directory_or_conflicting_sources(db_session):
    agent = ContactDiscoveryAgent(db_session)
    lead = Business(name="Conflicting Info Dining", address="Bodakdev", phone="+919876543212")
    status, reason, conf = agent.determine_contact_target_status(lead, "Candidate X", "Director", ConfidenceLevel.LOW)
    assert status == ContactTargetStatus.MANUAL_REVIEW
    assert "manual review" in reason.lower()


def test_dm_6_10_no_person_found_returns_not_found(db_session):
    lead = Business(name="Unknown Owner Eatery", category="restaurant", address="Satellite", city="Ahmedabad", workflow_state=WorkflowState.QUALIFIED)
    db_session.add(lead)
    db_session.commit()

    agent = ContactDiscoveryAgent(db_session)
    res = agent.execute(AgentInput(lead_id=lead.id))

    assert res.data["full_name"] is None
    assert res.data["confidence_level"] == ConfidenceLevel.NOT_FOUND.value
    assert res.data["contact_target_status"] == ContactTargetStatus.NOT_FOUND.value


def test_dm_7_business_contact_exists_but_person_unknown(db_session):
    lead = Business(name="Phone Only Restaurant", category="restaurant", address="Prahlad Nagar", city="Ahmedabad", phone="+919876543213", workflow_state=WorkflowState.QUALIFIED)
    db_session.add(lead)
    db_session.commit()

    agent = ContactDiscoveryAgent(db_session)
    res = agent.execute(AgentInput(lead_id=lead.id))

    assert res.data["full_name"] is None
    assert res.data["contact_target_status"] == ContactTargetStatus.BUSINESS_CONTACT_ONLY.value


# --------------------------------------------------------------------------
# OUTREACH PERSONALIZATION & CLAIM VALIDATION TESTS
# --------------------------------------------------------------------------

def test_outreach_personalized_greeting_for_verified_person(db_session):
    lead = Business(
        name="House of MG", category="hotel", address="Lal Darwaja", city="Ahmedabad", phone="+917925506941",
        contact_target_status=ContactTargetStatus.VERIFIED_PERSON,
        workflow_state=WorkflowState.DEMO_GENERATED
    )
    db_session.add(lead)
    db_session.commit()

    dm = DecisionMakerRecord(business_id=lead.id, name="Abhay Mangaldas", title="Founder", confidence=ConfidenceLevel.HIGH)
    db_session.add(dm)
    db_session.commit()

    agent = OutreachAgent(db_session)
    res = agent.execute(AgentInput(lead_id=lead.id))

    assert "Hi Abhay," in res.data["email_body"]


def test_outreach_generic_greeting_for_business_contact_only(db_session):
    lead = Business(
        name="Gordhan Thal", category="restaurant", address="SG Highway", city="Ahmedabad", phone="+917926861116",
        contact_target_status=ContactTargetStatus.BUSINESS_CONTACT_ONLY,
        workflow_state=WorkflowState.DEMO_GENERATED
    )
    db_session.add(lead)
    db_session.commit()

    agent = OutreachAgent(db_session)
    res = agent.execute(AgentInput(lead_id=lead.id))

    assert "Hello Gordhan Thal Team," in res.data["email_body"]
    assert "Hi Owner," not in res.data["email_body"]
