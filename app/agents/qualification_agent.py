from typing import Any
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState
from app.db.models import Business, Campaign
from app.orchestrator.engine import OrchestratorEngine
from app.core.logging import get_logger

logger = get_logger("QualificationAgent")


class QualificationAgent(BaseAgent[dict[str, Any]]):
    name = "QualificationAgent"
    version = "1.0"

    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.orchestrator = OrchestratorEngine(self.db)

    def run(self, input_data: AgentInput) -> dict[str, Any]:
        lead = self.db.query(Business).filter(Business.id == input_data.lead_id).first()
        if not lead:
            raise ValueError(f"Business lead with ID {input_data.lead_id} not found.")

        # Check suppression status
        if lead.is_suppressed or lead.workflow_state == WorkflowState.DO_NOT_CONTACT:
            logger.info(f"Lead {lead.id} is suppressed/opted-out. Qualification skipped.")
            return {
                "lead_id": lead.id,
                "qualified": False,
                "reason": "DO_NOT_CONTACT_SUPPRESSED",
                "opportunity_score": lead.opportunity_score
            }

        # Determine target qualification threshold
        threshold = 60.0
        if lead.campaign_id:
            campaign = self.db.query(Campaign).filter(Campaign.id == lead.campaign_id).first()
            if campaign and campaign.min_opportunity_score:
                threshold = campaign.min_opportunity_score

        opportunity_score = lead.opportunity_score or 0.0
        qualified = opportunity_score >= threshold

        if qualified:
            # Advance state SCORED -> QUALIFIED
            if lead.workflow_state == WorkflowState.SCORED:
                self.orchestrator.transition_lead(
                    lead_id=lead.id,
                    target_state=WorkflowState.QUALIFIED,
                    agent_name=self.name,
                    payload_snapshot={
                        "opportunity_score": opportunity_score,
                        "min_threshold": threshold
                    }
                )
            reason = "QUALIFIED_THRESHOLD_MET"
        else:
            # Reject lead: SCORED -> REJECTED
            if lead.workflow_state == WorkflowState.SCORED:
                self.orchestrator.transition_lead(
                    lead_id=lead.id,
                    target_state=WorkflowState.REJECTED,
                    agent_name=self.name,
                    payload_snapshot={
                        "reason": "SCORE_BELOW_THRESHOLD",
                        "opportunity_score": opportunity_score,
                        "min_threshold": threshold
                    }
                )
            reason = "SCORE_BELOW_THRESHOLD"

        logger.info(f"QualificationAgent evaluated lead {lead.id}: Qualified={qualified} (Score={opportunity_score}, Min={threshold})")
        return {
            "lead_id": lead.id,
            "qualified": qualified,
            "reason": reason,
            "opportunity_score": opportunity_score,
            "min_threshold": threshold
        }
