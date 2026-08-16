from typing import Any
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState
from app.db.models import Business, WebsiteAudit
from app.services.scoring_engine import ScoringEngine
from app.orchestrator.engine import OrchestratorEngine
from app.core.logging import get_logger

logger = get_logger("OpportunityScorerAgent")


class OpportunityScorerAgent(BaseAgent[dict[str, Any]]):
    name = "OpportunityScorerAgent"
    version = "1.0"

    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.orchestrator = OrchestratorEngine(self.db)

    def run(self, input_data: AgentInput) -> dict[str, Any]:
        lead = self.db.query(Business).filter(Business.id == input_data.lead_id).first()
        if not lead:
            raise ValueError(f"Business lead with ID {input_data.lead_id} not found.")

        audit = self.db.query(WebsiteAudit).filter(WebsiteAudit.business_id == lead.id).first()
        
        # Calculate breakdown score
        scoring_result = ScoringEngine.calculate_score(lead, audit)
        total_score = scoring_result["total_score"]

        # Persist updated score on Business entity
        lead.opportunity_score = total_score
        self.db.commit()

        # Advance state WEBSITE_ANALYZED -> SCORED via Orchestrator
        if lead.workflow_state == WorkflowState.WEBSITE_ANALYZED:
            self.orchestrator.transition_lead(
                lead_id=lead.id,
                target_state=WorkflowState.SCORED,
                agent_name=self.name,
                payload_snapshot=scoring_result
            )

        logger.info(f"OpportunityScorerAgent scored lead {lead.id}: {total_score}/100.0")
        return {
            "lead_id": lead.id,
            "opportunity_score": total_score,
            "breakdown": scoring_result
        }
