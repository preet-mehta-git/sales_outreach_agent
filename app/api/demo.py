import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent import AgentInput
from app.agents.demo_generator_agent import DemoGeneratorAgent

router = APIRouter(prefix="/demo", tags=["Demo"])


@router.post("/generate/{lead_id}", status_code=status.HTTP_200_OK)
def generate_lead_demo(lead_id: str, db: Session = Depends(get_db)):
    workflow_run_id = str(uuid.uuid4())
    agent_input = AgentInput(lead_id=lead_id, workflow_run_id=workflow_run_id)

    agent = DemoGeneratorAgent(db)
    agent_out = agent.execute(agent_input)
    if not agent_out.success:
        raise HTTPException(
            status_code=500,
            detail=f"DemoGeneratorAgent failed: {', '.join(agent_out.errors)}"
        )

    return {
        "status": "success",
        "lead_id": lead_id,
        "demo": agent_out.data
    }
