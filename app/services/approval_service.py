from datetime import datetime, timezone
from typing import Any
from sqlalchemy.orm import Session

from app.db.models import Business, OutreachDraft
from app.schemas.enums import WorkflowState, OutreachStatus
from app.orchestrator.engine import OrchestratorEngine
from app.core.logging import get_logger

logger = get_logger("ApprovalWorkflowService")


class ApprovalWorkflowService:
    def __init__(self, db: Session):
        self.db = db
        self.orchestrator = OrchestratorEngine(self.db)

    def review_draft(
        self,
        draft_id: str,
        decision: str,
        reviewer: str = "Admin Reviewer",
        edits: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Human-in-the-loop review mechanism for drafted outreach content.
        Supported decisions: 'APPROVE', 'REJECT'
        """
        draft = self.db.query(OutreachDraft).filter(OutreachDraft.id == draft_id).first()
        if not draft:
            raise ValueError(f"OutreachDraft with ID {draft_id} not found.")

        lead = self.db.query(Business).filter(Business.id == draft.business_id).first()
        if not lead:
            raise ValueError(f"Associated business lead with ID {draft.business_id} not found.")

        decision_upper = decision.upper()

        if decision_upper == "APPROVE":
            # Apply edits if provided
            if edits:
                if "email_subject" in edits and edits["email_subject"]:
                    draft.email_subject = edits["email_subject"]
                if "email_body" in edits and edits["email_body"]:
                    draft.email_body = edits["email_body"]
                if "whatsapp_body" in edits and edits["whatsapp_body"]:
                    draft.whatsapp_body = edits["whatsapp_body"]

            draft.status = OutreachStatus.APPROVED
            draft.approved_by = reviewer
            draft.approved_at = datetime.now(timezone.utc)
            self.db.commit()

            # Advance lead state AWAITING_APPROVAL -> APPROVED
            if lead.workflow_state in (WorkflowState.AWAITING_APPROVAL, WorkflowState.OUTREACH_DRAFTED):
                if lead.workflow_state == WorkflowState.OUTREACH_DRAFTED:
                    self.orchestrator.transition_lead(
                        lead_id=lead.id,
                        target_state=WorkflowState.AWAITING_APPROVAL,
                        agent_name="ApprovalWorkflowService"
                    )

                self.orchestrator.transition_lead(
                    lead_id=lead.id,
                    target_state=WorkflowState.APPROVED,
                    agent_name="ApprovalWorkflowService",
                    payload_snapshot={
                        "draft_id": draft.id,
                        "approved_by": reviewer,
                        "edits_applied": bool(edits)
                    }
                )

            logger.info(f"Outreach draft {draft.id} APPROVED by {reviewer} for lead {lead.id}")
            return {
                "draft_id": draft.id,
                "status": "APPROVED",
                "lead_id": lead.id,
                "approved_by": reviewer,
                "workflow_state": lead.workflow_state.value
            }

        elif decision_upper == "REJECT":
            draft.status = OutreachStatus.REJECTED
            self.db.commit()

            # Transition state AWAITING_APPROVAL -> REJECTED
            if lead.workflow_state in (WorkflowState.AWAITING_APPROVAL, WorkflowState.OUTREACH_DRAFTED):
                if lead.workflow_state == WorkflowState.OUTREACH_DRAFTED:
                    self.orchestrator.transition_lead(
                        lead_id=lead.id,
                        target_state=WorkflowState.AWAITING_APPROVAL,
                        agent_name="ApprovalWorkflowService"
                    )

                self.orchestrator.transition_lead(
                    lead_id=lead.id,
                    target_state=WorkflowState.REJECTED,
                    agent_name="ApprovalWorkflowService",
                    payload_snapshot={
                        "draft_id": draft.id,
                        "reason": "HUMAN_REVIEW_REJECTED",
                        "rejected_by": reviewer
                    }
                )

            logger.info(f"Outreach draft {draft.id} REJECTED by {reviewer} for lead {lead.id}")
            return {
                "draft_id": draft.id,
                "status": "REJECTED",
                "lead_id": lead.id,
                "workflow_state": lead.workflow_state.value
            }
        else:
            raise ValueError(f"Invalid review decision '{decision}'. Expected 'APPROVE' or 'REJECT'.")
