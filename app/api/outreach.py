import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent import AgentInput
from app.agents.outreach_agent import OutreachAgent
from app.db.models import OutreachDraft
from app.schemas.enums import OutreachStatus

router = APIRouter(prefix="/outreach", tags=["Outreach"])


@router.post("/draft/{lead_id}", status_code=status.HTTP_200_OK)
def draft_lead_outreach(lead_id: str, db: Session = Depends(get_db)):
    workflow_run_id = str(uuid.uuid4())
    agent_input = AgentInput(lead_id=lead_id, workflow_run_id=workflow_run_id)

    agent = OutreachAgent(db)
    agent_out = agent.execute(agent_input)
    if not agent_out.success:
        raise HTTPException(
            status_code=500,
            detail=f"OutreachAgent failed: {', '.join(agent_out.errors)}"
        )

    return {
        "status": "success",
        "lead_id": lead_id,
        "outreach_draft": agent_out.data
    }


@router.get("/draft/{lead_id}", status_code=status.HTTP_200_OK)
def get_lead_outreach_draft(lead_id: str, db: Session = Depends(get_db)):
    draft = db.query(OutreachDraft).filter(OutreachDraft.business_id == lead_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail=f"No outreach draft found for lead {lead_id}")

    return {
        "id": draft.id,
        "business_id": draft.business_id,
        "email_subject": draft.email_subject,
        "email_body": draft.email_body,
        "whatsapp_body": draft.whatsapp_body,
        "demo_url": draft.demo_url,
        "status": draft.status.value,
        "approved_by": draft.approved_by,
        "approved_at": draft.approved_at.isoformat() if draft.approved_at else None
    }
