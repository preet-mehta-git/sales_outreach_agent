import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent import AgentInput
from app.agents.opportunity_scorer_agent import OpportunityScorerAgent
from app.agents.qualification_agent import QualificationAgent

router = APIRouter(prefix="/qualification", tags=["Qualification"])


@router.post("/process/{lead_id}", status_code=status.HTTP_200_OK)
def process_lead_qualification(lead_id: str, db: Session = Depends(get_db)):
    workflow_run_id = str(uuid.uuid4())
    agent_input = AgentInput(lead_id=lead_id, workflow_run_id=workflow_run_id)

    # Step 1: Run Opportunity Scorer Agent
    scorer = OpportunityScorerAgent(db)
    scorer_out = scorer.execute(agent_input)
    if not scorer_out.success:
        raise HTTPException(
            status_code=500,
            detail=f"OpportunityScorerAgent failed: {', '.join(scorer_out.errors)}"
        )

    # Step 2: Run Qualification Agent
    qualifier = QualificationAgent(db)
    qualifier_out = qualifier.execute(agent_input)
    if not qualifier_out.success:
        raise HTTPException(
            status_code=500,
            detail=f"QualificationAgent failed: {', '.join(qualifier_out.errors)}"
        )

    return {
        "status": "success",
        "lead_id": lead_id,
        "scoring": scorer_out.data,
        "qualification": qualifier_out.data
    }
