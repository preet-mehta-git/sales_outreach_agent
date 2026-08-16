import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent import AgentInput
from app.agents.discovery_agent import DiscoveryAgent

router = APIRouter(prefix="/discovery", tags=["Discovery"])


class DiscoveryRunRequest(BaseModel):
    campaign_id: str | None = None
    city: str = "Ahmedabad"
    keywords: list[str] = Field(default_factory=lambda: ["restaurant", "cafe", "bakery"])
    limit_per_keyword: int = Field(default=5, ge=1, le=20)


@router.post("/run", status_code=status.HTTP_200_OK)
def run_discovery(req: DiscoveryRunRequest, db: Session = Depends(get_db)):
    agent = DiscoveryAgent(db)
    workflow_run_id = str(uuid.uuid4())
    
    agent_input = AgentInput(
        lead_id="batch_discovery",
        workflow_run_id=workflow_run_id,
        parameters={
            "campaign_id": req.campaign_id,
            "city": req.city,
            "keywords": req.keywords,
            "limit_per_keyword": req.limit_per_keyword
        }
    )

    output = agent.execute(agent_input)
    if not output.success:
        raise HTTPException(
            status_code=500,
            detail=f"DiscoveryAgent execution failed: {', '.join(output.errors)}"
        )

    return {
        "status": "success",
        "workflow_run_id": workflow_run_id,
        "metrics": output.data,
        "duration_ms": output.duration_ms
    }
