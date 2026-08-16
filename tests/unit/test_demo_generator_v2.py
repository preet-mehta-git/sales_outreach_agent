import os
import uuid
from app.agents.demo_generator_agent import DemoGeneratorAgent
from app.schemas.agent import AgentInput
from app.db.models import Business
from app.schemas.enums import WorkflowState


def test_demo_generator_escapes_script_tags(db_session, tmp_path):
    malicious_name = "Malicious Cafe <script>alert('XSS')</script>"
    lead = Business(
        name=malicious_name,
        category="cafe",
        address="Navrangpura",
        city="Ahmedabad",
        phone="+919876543210",
        workflow_state=WorkflowState.BUSINESS_AUDITED
    )
    db_session.add(lead)
    db_session.commit()

    agent = DemoGeneratorAgent(db_session, base_static_dir=str(tmp_path))
    res = agent.execute(AgentInput(lead_id=lead.id, workflow_run_id=str(uuid.uuid4())))

    assert res.success is True
    file_path = res.data["file_path"]
    assert os.path.exists(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Raw script tags must NOT be present
    assert "<script>alert('XSS')</script>" not in content
    # Escaped tags MUST be present
    assert "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;" in content or "&lt;script&gt;" in content


def test_demo_generator_handles_missing_website_gracefully(db_session, tmp_path):
    lead = Business(
        name="No Site Diner",
        category="diner",
        address="SG Highway",
        city="Ahmedabad",
        website_url=None,
        workflow_state=WorkflowState.BUSINESS_AUDITED
    )
    db_session.add(lead)
    db_session.commit()

    agent = DemoGeneratorAgent(db_session, base_static_dir=str(tmp_path))
    res = agent.execute(AgentInput(lead_id=lead.id, workflow_run_id=str(uuid.uuid4())))

    assert res.success is True
    assert os.path.exists(res.data["file_path"])
