import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent import AgentInput
from app.agents.website_verifier_agent import WebsiteVerifierAgent
from app.agents.website_audit_agent import WebsiteAuditAgent

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.post("/analyze/{lead_id}", status_code=status.HTTP_200_OK)
def analyze_lead_website(lead_id: str, db: Session = Depends(get_db)):
    workflow_run_id = str(uuid.uuid4())
    agent_input = AgentInput(lead_id=lead_id, workflow_run_id=workflow_run_id)

    # Step 1: Run Website Verifier Agent
    verifier = WebsiteVerifierAgent(db)
    verifier_out = verifier.execute(agent_input)
    if not verifier_out.success:
        raise HTTPException(
            status_code=500,
            detail=f"WebsiteVerifierAgent failed: {', '.join(verifier_out.errors)}"
        )

    # Step 2: Run Website Audit Agent
    audit_agent = WebsiteAuditAgent(db)
    audit_out = audit_agent.execute(agent_input)
    if not audit_out.success:
        raise HTTPException(
            status_code=500,
            detail=f"WebsiteAuditAgent failed: {', '.join(audit_out.errors)}"
        )

    return {
        "status": "success",
        "lead_id": lead_id,
        "verification": verifier_out.data,
        "audit": audit_out.data
    }
