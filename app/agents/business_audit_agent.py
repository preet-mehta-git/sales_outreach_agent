from typing import Any
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState, WebsiteStatus, WebsiteVerificationStatus
from app.db.models import Business, WebsiteAudit
from app.providers.audit_provider import AuditProvider
from app.orchestrator.engine import OrchestratorEngine
from app.core.logging import get_logger

logger = get_logger("BusinessAuditAgent")


class BusinessAuditAgent(BaseAgent[dict[str, Any]]):
    name = "BusinessAuditAgent"
    version = "2.0"

    CATEGORY_OPPORTUNITIES = {
        "restaurant": [
            "Owned mobile digital menu with instant QR accessibility",
            "Direct table enquiry & reservation booking form",
            "Instant WhatsApp click-to-order CTA"
        ],
        "cafe": [
            "Mobile menu showcase with beverage & snack items",
            "Direct WhatsApp click-to-order CTA",
            "Table reservation & event enquiry form"
        ],
        "hotel": [
            "Direct room reservation engine to reduce OTA commission dependency",
            "Interactive room showcase & amenities gallery",
            "Direct banquet & dining enquiry form"
        ],
        "bakery": [
            "Product catalog showcasing custom cakes & baked items",
            "Custom order & pickup enquiry via WhatsApp",
            "Seasonal offer & catering lead capture form"
        ],
        "service": [
            "Service catalog and pricing package overview",
            "Direct appointment scheduling & lead capture form",
            "Customer testimonial & portfolio section"
        ]
    }

    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.orchestrator = OrchestratorEngine(self.db)

    def get_category_key(self, category: str | None) -> str:
        cat = (category or "").lower()
        if any(term in cat for term in ["restaurant", "thali", "eatery", "dining", "fast food"]):
            return "restaurant"
        elif any(term in cat for term in ["cafe", "coffee", "tea"]):
            return "cafe"
        elif any(term in cat for term in ["hotel", "resort", "stay"]):
            return "hotel"
        elif any(term in cat for term in ["bakery", "cake", "confectionery"]):
            return "bakery"
        else:
            return "service"

    def run(self, input_data: AgentInput) -> dict[str, Any]:
        lead = self.db.query(Business).filter(Business.id == input_data.lead_id).first()
        if not lead:
            raise ValueError(f"Business lead with ID {input_data.lead_id} not found.")

        audit = self.db.query(WebsiteAudit).filter(WebsiteAudit.business_id == lead.id).first()

        missing_gaps = []
        if audit and audit.missing_elements and "elements" in audit.missing_elements:
            missing_gaps = audit.missing_elements["elements"]

        # 1. VERIFIED_FACT
        verified_facts = [
            f"Business Name: '{lead.name}', Category: '{lead.category}', Location: '{lead.city}'.",
            f"Discovery rating: {lead.rating if lead.rating else 'N/A'} with {lead.review_count if lead.review_count else 0} public reviews.",
            f"Website Verification Status: {lead.website_verification_status.value if lead.website_verification_status else 'UNVERIFIED'}.",
            f"Phone contact route: {'Available' if lead.phone else 'Not provided'}."
        ]

        # 2. INFERENCE
        inferences = []
        if lead.review_count and lead.review_count >= 100:
            inferences.append(f"Significant customer search demand indicated by {lead.review_count}+ public reviews.")
        if lead.website_verification_status == WebsiteVerificationStatus.NO_WEBSITE_CONFIRMED:
            inferences.append("Online searchers rely on Google Maps listing and third-party pages due to lack of an official website.")
        elif audit and audit.quality_score < 50.0:
            inferences.append("Existing digital channel presents user-experience or mobile conversion limitations.")

        # 3. OPPORTUNITY (Business-Specific)
        cat_key = self.get_category_key(lead.category)
        opportunities = list(self.CATEGORY_OPPORTUNITIES.get(cat_key, self.CATEGORY_OPPORTUNITIES["service"]))

        # 4. UNKNOWN
        unknown_variables = [
            "Exact monthly direct customer website traffic (requires web analytics)",
            "Financial commission split paid to third-party platforms (requires internal finance records)",
            "Exact conversion rate of phone inquiries into bookings"
        ]

        # Safely wrap untrusted content snippet
        raw_text_snippet = f"Business: {lead.name}, Category: {lead.category}, City: {lead.city}"
        safe_wrapped_content = AuditProvider.wrap_untrusted_content(raw_text_snippet)

        audit_summary = {
            "business_id": lead.id,
            "business_name": lead.name,
            "verified_facts": verified_facts,
            "inferences": inferences,
            "opportunities": opportunities,
            "unknown_variables": unknown_variables,
            "digital_gaps": missing_gaps,
            "untrusted_content": safe_wrapped_content,
            # Backward-compatibility wrappers
            "known_facts": {
                "business_name": lead.name,
                "category": lead.category,
                "city": lead.city,
                "rating": lead.rating,
                "review_count": lead.review_count,
                "website_status": lead.website_status.value if lead.website_status else "UNKNOWN"
            },
            "inferred_insights": inferences,
            "potential_opportunities": opportunities
        }

        # Advance state DECISION_MAKER_RESEARCHED -> BUSINESS_AUDITED via Orchestrator
        if lead.workflow_state == WorkflowState.DECISION_MAKER_RESEARCHED:
            self.orchestrator.transition_lead(
                lead_id=lead.id,
                target_state=WorkflowState.BUSINESS_AUDITED,
                agent_name=self.name,
                payload_snapshot={
                    "verified_facts_count": len(verified_facts),
                    "opportunities_count": len(opportunities)
                }
            )

        logger.info(f"BusinessAuditAgent completed evidence-based audit for lead {lead.id} ({lead.name})")
        return audit_summary
