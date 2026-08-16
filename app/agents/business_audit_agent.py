from typing import Any
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState, WebsiteStatus
from app.db.models import Business, WebsiteAudit
from app.providers.audit_provider import AuditProvider
from app.orchestrator.engine import OrchestratorEngine
from app.core.logging import get_logger

logger = get_logger("BusinessAuditAgent")


class BusinessAuditAgent(BaseAgent[dict[str, Any]]):
    name = "BusinessAuditAgent"
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

        missing_gaps = []
        if audit and audit.missing_elements and "elements" in audit.missing_elements:
            missing_gaps = audit.missing_elements["elements"]
        elif lead.website_status == WebsiteStatus.NO_WEBSITE:
            missing_gaps = ["missing_website", "missing_mobile_optimization", "missing_online_menu", "missing_whatsapp_cta"]

        # Calculate estimated business impact
        review_count = lead.review_count or 10
        est_daily_foot_traffic = int(review_count * 1.5)
        est_lost_monthly_customers = int(est_daily_foot_traffic * 0.20 * 30)  # 20% searchers lost due to missing/poor digital presence
        est_lost_monthly_revenue_inr = est_lost_monthly_customers * 450  # Average check size 450 INR

        # Safely wrap any raw external text content snippet
        raw_text_snippet = f"Business: {lead.name}, Category: {lead.category}, City: {lead.city}"
        safe_wrapped_content = AuditProvider.wrap_untrusted_content(raw_text_snippet)

        audit_summary = {
            "business_id": lead.id,
            "business_name": lead.name,
            "category": lead.category,
            "city": lead.city,
            "digital_gaps": missing_gaps,
            "estimated_lost_monthly_customers": est_lost_monthly_customers,
            "estimated_lost_monthly_revenue_inr": est_lost_monthly_revenue_inr,
            "recommendations": [
                "Deploy modern mobile-first landing page with online QR code menu",
                "Integrate instant WhatsApp click-to-chat order/table inquiry button",
                "Implement direct Google Maps reservation & direction action buttons"
            ],
            "untrusted_content": safe_wrapped_content
        }

        # Advance state DECISION_MAKER_RESEARCHED -> BUSINESS_AUDITED via Orchestrator
        if lead.workflow_state == WorkflowState.DECISION_MAKER_RESEARCHED:
            self.orchestrator.transition_lead(
                lead_id=lead.id,
                target_state=WorkflowState.BUSINESS_AUDITED,
                agent_name=self.name,
                payload_snapshot={
                    "est_lost_monthly_revenue_inr": est_lost_monthly_revenue_inr,
                    "gap_count": len(missing_gaps)
                }
            )

        logger.info(f"BusinessAuditAgent completed audit for lead {lead.id}: Est Lost Rev=₹{est_lost_monthly_revenue_inr:,}")
        return audit_summary
