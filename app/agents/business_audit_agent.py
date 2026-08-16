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

        # Evidence-Based Audit Categories (Section 5.5)
        known_facts = {
            "business_name": lead.name,
            "category": lead.category,
            "city": lead.city,
            "rating": lead.rating,
            "review_count": lead.review_count,
            "website_status": lead.website_status.value if lead.website_status else "UNKNOWN",
            "has_phone": bool(lead.phone),
            "has_address": bool(lead.address)
        }

        inferred_insights = []
        if lead.review_count and lead.review_count >= 50:
            inferred_insights.append("Strong local customer demand and Google search discovery volume.")
        if lead.website_status == WebsiteStatus.NO_WEBSITE:
            inferred_insights.append("Customers rely entirely on third-party aggregators and Google Maps listing.")

        potential_opportunities = [
            "Owned mobile digital menu with instant QR accessibility",
            "Direct WhatsApp click-to-chat ordering CTA",
            "Direct table enquiry & reservation button"
        ]

        unknown_variables = [
            "Exact website conversion rate (requires website analytics)",
            "Exact monthly revenue impact (requires internal financial records)",
            "Customer acquisition cost via third-party platforms"
        ]

        # Safely wrap any raw external text content snippet
        raw_text_snippet = f"Business: {lead.name}, Category: {lead.category}, City: {lead.city}"
        safe_wrapped_content = AuditProvider.wrap_untrusted_content(raw_text_snippet)

        audit_summary = {
            "business_id": lead.id,
            "business_name": lead.name,
            "known_facts": known_facts,
            "inferred_insights": inferred_insights,
            "potential_opportunities": potential_opportunities,
            "unknown_variables": unknown_variables,
            "digital_gaps": missing_gaps,
            "untrusted_content": safe_wrapped_content
        }

        # Advance state DECISION_MAKER_RESEARCHED -> BUSINESS_AUDITED via Orchestrator
        if lead.workflow_state == WorkflowState.DECISION_MAKER_RESEARCHED:
            self.orchestrator.transition_lead(
                lead_id=lead.id,
                target_state=WorkflowState.BUSINESS_AUDITED,
                agent_name=self.name,
                payload_snapshot={
                    "gap_count": len(missing_gaps),
                    "known_facts_count": len(known_facts)
                }
            )

        logger.info(f"BusinessAuditAgent completed evidence-based audit for lead {lead.id} ({lead.name})")
        return audit_summary
