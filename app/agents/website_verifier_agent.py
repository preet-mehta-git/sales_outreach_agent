from typing import Any
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState, WebsiteStatus
from app.providers.audit_provider import AuditProvider
from app.db.models import Business
from app.orchestrator.engine import OrchestratorEngine
from app.core.logging import get_logger

logger = get_logger("WebsiteVerifierAgent")


class WebsiteVerifierAgent(BaseAgent[dict[str, Any]]):
    name = "WebsiteVerifierAgent"
    version = "1.0"

    def __init__(self, db: Session, audit_provider: AuditProvider | None = None):
        super().__init__()
        self.db = db
        self.audit_provider = audit_provider or AuditProvider()
        self.orchestrator = OrchestratorEngine(self.db)

    def run(self, input_data: AgentInput) -> dict[str, Any]:
        lead = self.db.query(Business).filter(Business.id == input_data.lead_id).first()
        if not lead:
            raise ValueError(f"Business lead with ID {input_data.lead_id} not found.")

        # If lead has no website URL set
        if not lead.website_url or lead.website_url.strip() == "":
            lead.website_status = WebsiteStatus.NO_WEBSITE
            self.db.commit()
            
            # Transition state VERIFIED -> WEBSITE_ANALYZED
            if lead.workflow_state == WorkflowState.VERIFIED:
                self.orchestrator.transition_lead(
                    lead_id=lead.id,
                    target_state=WorkflowState.WEBSITE_ANALYZED,
                    agent_name=self.name,
                    payload_snapshot={"website_status": WebsiteStatus.NO_WEBSITE.value}
                )

            return {
                "lead_id": lead.id,
                "website_status": WebsiteStatus.NO_WEBSITE.value,
                "reachable": False,
                "reason": "No website URL provided"
            }

        # Inspect website URL via AuditProvider
        inspection = self.audit_provider.inspect_url(lead.website_url)
        reachable = inspection.get("reachable", False)

        if not reachable:
            lead.website_status = WebsiteStatus.WEBSITE_UNREACHABLE
        else:
            # Check if weak/poor-quality website
            mobile_ok = inspection.get("has_meta_viewport", True)
            perf_ok = inspection.get("performance_score", 100) >= 40.0
            if not mobile_ok or not perf_ok:
                lead.website_status = WebsiteStatus.WEAK_WEBSITE
            else:
                lead.website_status = WebsiteStatus.WEBSITE_FOUND

        self.db.commit()

        # Advance workflow state to WEBSITE_ANALYZED
        if lead.workflow_state == WorkflowState.VERIFIED:
            self.orchestrator.transition_lead(
                lead_id=lead.id,
                target_state=WorkflowState.WEBSITE_ANALYZED,
                agent_name=self.name,
                payload_snapshot={
                    "website_status": lead.website_status.value,
                    "reachable": reachable
                }
            )

        logger.info(f"Verified lead {lead.id} website status: {lead.website_status.value}")
        return {
            "lead_id": lead.id,
            "website_url": lead.website_url,
            "website_status": lead.website_status.value,
            "reachable": reachable,
            "inspection": inspection
        }
