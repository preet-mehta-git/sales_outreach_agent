import uuid
from app.agents.website_audit_agent import WebsiteAuditAgent
from app.providers.audit_provider import AuditProvider
from app.schemas.agent import AgentInput
from app.db.models import Business, WebsiteAudit


def test_prompt_injection_defense_wrapping():
    raw_html = "<html><body><h1>Welcome</h1><script>alert('hack')</script></body></html>"
    wrapped = AuditProvider.wrap_untrusted_content(raw_html)
    assert wrapped.startswith("<untrusted_external_content>")
    assert wrapped.endswith("</untrusted_external_content>")
    assert "alert('hack')" in wrapped


def test_website_audit_agent_no_website(db_session, sample_business):
    agent = WebsiteAuditAgent(db_session)
    inp = AgentInput(lead_id=sample_business.id, workflow_run_id=str(uuid.uuid4()))

    out = agent.execute(inp)
    assert out.success is True
    assert out.data["quality_score"] == 0.0
    assert "missing_website" in out.data["missing_elements"]

    # Verify WebsiteAudit ORM record persisted
    audit_rec = db_session.query(WebsiteAudit).filter(WebsiteAudit.business_id == sample_business.id).first()
    assert audit_rec is not None
    assert audit_rec.quality_score == 0.0


def test_website_audit_agent_existing_site(db_session):
    lead = Business(
        name="Audited Bistro",
        category="restaurant",
        address="Navrangpura",
        city="Ahmedabad",
        website_url="http://vastrapurheritagedining.example.com"
    )
    db_session.add(lead)
    db_session.commit()

    agent = WebsiteAuditAgent(db_session)
    inp = AgentInput(lead_id=lead.id, workflow_run_id=str(uuid.uuid4()))
    out = agent.execute(inp)

    assert out.success is True
    assert "quality_score" in out.data
    assert "missing_elements" in out.data

    audit_rec = db_session.query(WebsiteAudit).filter(WebsiteAudit.business_id == lead.id).first()
    assert audit_rec is not None
