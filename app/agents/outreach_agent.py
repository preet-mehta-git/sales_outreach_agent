from typing import Any
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState, OutreachStatus
from app.db.models import Business, DecisionMakerRecord, WebsiteAudit, OutreachDraft
from app.orchestrator.engine import OrchestratorEngine
from app.core.logging import get_logger

logger = get_logger("OutreachAgent")


class OutreachAgent(BaseAgent[dict[str, Any]]):
    name = "OutreachAgent"
    version = "1.0"

    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.orchestrator = OrchestratorEngine(self.db)

    def run(self, input_data: AgentInput) -> dict[str, Any]:
        lead = self.db.query(Business).filter(Business.id == input_data.lead_id).first()
        if not lead:
            raise ValueError(f"Business lead with ID {input_data.lead_id} not found.")

        dm = self.db.query(DecisionMakerRecord).filter(DecisionMakerRecord.business_id == lead.id).first()
        audit = self.db.query(WebsiteAudit).filter(WebsiteAudit.business_id == lead.id).first()
        draft = self.db.query(OutreachDraft).filter(OutreachDraft.business_id == lead.id).first()

        dm_name = dm.name if (dm and dm.name) else "Restaurant Owner"
        demo_url = draft.demo_url if (draft and draft.demo_url) else f"/static/demos/{lead.id}/index.html"

        # Generate Email Copy
        subject = f"Growth opportunity for {lead.name} in {lead.city}"
        
        email_body = f"""Hi {dm_name},

I came across {lead.name} while researching top {lead.category}s in {lead.city}. Your {lead.rating or 4.5}⭐ rating with {lead.review_count or 10}+ customer reviews is fantastic.

However, we noticed a critical digital presence gap: potential customers searching online are unable to view a mobile-optimized menu or place instant orders via WhatsApp. Based on search patterns in {lead.city}, this results in missed orders every month.

To show you how easy this is to solve, we built a personalized interactive web demo for {lead.name}:
{demo_url}

Features built into your demo:
- Instant WhatsApp Click-to-Order button
- Mobile-responsive digital menu with prices
- One-tap Google Maps directions & table booking form

Would you be open to a 5-minute call this Thursday to see how we can deploy this for {lead.name}?

Best regards,
Outreach Specialist | Antigravity AI Systems

---
If you prefer not to receive future communications, please reply with "REMOVE" or update your outreach preferences.
"""

        # Generate WhatsApp Copy
        whatsapp_body = (
            f"Hi {dm_name}! 👋 We built a custom mobile web demo for {lead.name} "
            f"including instant WhatsApp ordering & digital menu. "
            f"Check it out here: {demo_url} - Would love your thoughts!"
        )

        # Create or Update OutreachDraft record
        if not draft:
            draft = OutreachDraft(
                business_id=lead.id,
                email_subject=subject,
                email_body=email_body,
                whatsapp_body=whatsapp_body,
                demo_url=demo_url,
                status=OutreachStatus.AWAITING_APPROVAL
            )
            self.db.add(draft)
        else:
            draft.email_subject = subject
            draft.email_body = email_body
            draft.whatsapp_body = whatsapp_body
            draft.status = OutreachStatus.AWAITING_APPROVAL

        self.db.commit()
        self.db.refresh(draft)

        # Advance state DEMO_GENERATED -> OUTREACH_DRAFTED -> AWAITING_APPROVAL
        if lead.workflow_state == WorkflowState.DEMO_GENERATED:
            self.orchestrator.transition_lead(
                lead_id=lead.id,
                target_state=WorkflowState.OUTREACH_DRAFTED,
                agent_name=self.name,
                payload_snapshot={"draft_id": draft.id}
            )

        if lead.workflow_state == WorkflowState.OUTREACH_DRAFTED:
            self.orchestrator.transition_lead(
                lead_id=lead.id,
                target_state=WorkflowState.AWAITING_APPROVAL,
                agent_name=self.name,
                payload_snapshot={
                    "draft_id": draft.id,
                    "status": draft.status.value,
                    "demo_url": demo_url
                }
            )

        logger.info(f"OutreachAgent created drafts for lead {lead.id}: Draft ID={draft.id}")
        return {
            "lead_id": lead.id,
            "draft_id": draft.id,
            "email_subject": subject,
            "email_body": email_body,
            "whatsapp_body": whatsapp_body,
            "demo_url": demo_url,
            "status": draft.status.value
        }
