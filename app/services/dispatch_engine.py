from typing import Any
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Business, OutreachDraft, DecisionMakerRecord
from app.schemas.enums import WorkflowState, OutreachStatus
from app.orchestrator.engine import OrchestratorEngine
from app.core.logging import get_logger

logger = get_logger("OutreachDispatchEngine")


class OutreachDispatchEngine:
    def __init__(self, db: Session):
        self.db = db
        self.orchestrator = OrchestratorEngine(self.db)
        self.outreach_mode = settings.OUTREACH_MODE.upper()

    def dispatch_outreach(self, draft_id: str) -> dict[str, Any]:
        draft = self.db.query(OutreachDraft).filter(OutreachDraft.id == draft_id).first()
        if not draft:
            raise ValueError(f"OutreachDraft with ID {draft_id} not found.")

        lead = self.db.query(Business).filter(Business.id == draft.business_id).first()
        if not lead:
            raise ValueError(f"Business lead with ID {draft.business_id} not found.")

        dm = self.db.query(DecisionMakerRecord).filter(DecisionMakerRecord.business_id == lead.id).first()

        # Suppression Guard
        if lead.is_suppressed or lead.workflow_state == WorkflowState.DO_NOT_CONTACT:
            logger.warning(f"Lead {lead.id} is suppressed/opted-out. Dispatch aborted.")
            return {
                "status": "ABORTED_SUPPRESSED",
                "lead_id": lead.id,
                "reason": "DO_NOT_CONTACT_SUPPRESSED"
            }

        recipient_email = (dm.contact_email if (dm and dm.contact_email) else lead.email) or f"contact@{lead.name.lower().replace(' ', '')}.com"
        recipient_phone = (dm.contact_phone if (dm and dm.contact_phone) else lead.phone) or "N/A"

        dispatch_payload = {
            "draft_id": draft.id,
            "lead_id": lead.id,
            "business_name": lead.name,
            "recipient_email": recipient_email,
            "recipient_phone": recipient_phone,
            "email_subject": draft.email_subject,
            "email_body": draft.email_body,
            "whatsapp_body": draft.whatsapp_body,
            "demo_url": draft.demo_url,
            "mode": self.outreach_mode
        }

        if self.outreach_mode == "DRY_RUN":
            logger.info(f"[SAFETY LOCK DRY_RUN] Simulated outreach dispatch for '{lead.name}' -> {recipient_email}")
            draft.status = OutreachStatus.DISPATCHED
            self.db.commit()

            # Advance state APPROVED -> CONTACTED
            if lead.workflow_state == WorkflowState.APPROVED:
                self.orchestrator.transition_lead(
                    lead_id=lead.id,
                    target_state=WorkflowState.CONTACTED,
                    agent_name="OutreachDispatchEngine",
                    payload_snapshot={
                        "mode": "DRY_RUN",
                        "recipient_email": recipient_email,
                        "recipient_phone": recipient_phone
                    }
                )

            return {
                "status": "DISPATCH_SIMULATED_DRY_RUN",
                "lead_id": lead.id,
                "dispatch_payload": dispatch_payload
            }

        else:
            # LIVE outreach execution
            logger.info(f"[LIVE DISPATCH] Executing live outreach transmission for '{lead.name}' -> {recipient_email}")
            draft.status = OutreachStatus.DISPATCHED
            self.db.commit()

            if lead.workflow_state == WorkflowState.APPROVED:
                self.orchestrator.transition_lead(
                    lead_id=lead.id,
                    target_state=WorkflowState.CONTACTED,
                    agent_name="OutreachDispatchEngine",
                    payload_snapshot={
                        "mode": "LIVE",
                        "recipient_email": recipient_email,
                        "recipient_phone": recipient_phone
                    }
                )

            return {
                "status": "DISPATCH_EXECUTED_LIVE",
                "lead_id": lead.id,
                "dispatch_payload": dispatch_payload
            }
