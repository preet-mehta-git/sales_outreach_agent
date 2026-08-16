import os
import uuid
import shutil
from app.agents.demo_generator_agent import DemoGeneratorAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState
from app.db.models import Business, OutreachDraft


def test_demo_generator_agent(db_session, tmp_path):
    lead = Business(
        name="Grand Feast Restaurant",
        category="fine dining",
        address="SG Highway",
        city="Ahmedabad",
        phone="+91 98989 77777",
        workflow_state=WorkflowState.BUSINESS_AUDITED
    )
    db_session.add(lead)
    db_session.commit()

    test_static_dir = str(tmp_path / "static" / "demos")
    agent = DemoGeneratorAgent(db_session, base_static_dir=test_static_dir)
    inp = AgentInput(lead_id=lead.id, workflow_run_id=str(uuid.uuid4()))

    out = agent.execute(inp)
    assert out.success is True
    assert "/static/demos/" in out.data["demo_url"]
    
    # Check generated file exists on disk
    file_path = out.data["file_path"]
    assert os.path.exists(file_path) is True
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Grand Feast Restaurant" in content
        assert "WhatsApp Order" in content

    # Check OutreachDraft updated
    draft = db_session.query(OutreachDraft).filter(OutreachDraft.business_id == lead.id).first()
    assert draft is not None
    assert draft.demo_url == out.data["public_demo_url"]

    # Verify state transition to DEMO_GENERATED
    db_session.refresh(lead)
    assert lead.workflow_state == WorkflowState.DEMO_GENERATED
