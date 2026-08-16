import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent import AgentInput
from app.agents.contact_discovery_agent import ContactDiscoveryAgent
from app.agents.business_audit_agent import BusinessAuditAgent

router = APIRouter(prefix="/research", tags=["Research"])


@router.post("/lead/{lead_id}", status_code=status.HTTP_200_OK)
def deep_research_lead(lead_id: str, db: Session = Depends(get_db)):
    workflow_run_id = str(uuid.uuid4())
    agent_input = AgentInput(lead_id=lead_id, workflow_run_id=workflow_run_id)

    # Step 1: Run Contact Discovery Agent
    contact_agent = ContactDiscoveryAgent(db)
    contact_out = contact_agent.execute(agent_input)
    if not contact_out.success:
        raise HTTPException(
            status_code=500,
            detail=f"ContactDiscoveryAgent failed: {', '.join(contact_out.errors)}"
        )

    # Step 2: Run Business Audit Agent
    audit_agent = BusinessAuditAgent(db)
    audit_out = audit_agent.execute(agent_input)
    if not audit_out.success:
        raise HTTPException(
            status_code=500,
            detail=f"BusinessAuditAgent failed: {', '.join(audit_out.errors)}"
        )

    return {
        "status": "success",
        "lead_id": lead_id,
        "contact_discovery": contact_out.data,
        "business_audit": audit_out.data
    }
