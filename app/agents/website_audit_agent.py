from typing import Any
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WebsiteStatus
from app.providers.audit_provider import AuditProvider
from app.db.models import Business, WebsiteAudit
from app.core.logging import get_logger

logger = get_logger("WebsiteAuditAgent")


class WebsiteAuditAgent(BaseAgent[dict[str, Any]]):
    name = "WebsiteAuditAgent"
    version = "1.0"

    def __init__(self, db: Session, audit_provider: AuditProvider | None = None):
        super().__init__()
        self.db = db
        self.audit_provider = audit_provider or AuditProvider()

    def run(self, input_data: AgentInput) -> dict[str, Any]:
        lead = self.db.query(Business).filter(Business.id == input_data.lead_id).first()
        if not lead:
            raise ValueError(f"Business lead with ID {input_data.lead_id} not found.")

        missing_elements = []
        raw_metrics = {}

        # Case 1: No website or Unreachable Website
        if lead.website_status in [WebsiteStatus.NO_WEBSITE, WebsiteStatus.WEBSITE_UNREACHABLE] or not lead.website_url:
            missing_elements = [
                "missing_website",
                "missing_mobile_optimization",
                "missing_online_menu",
                "missing_booking_cta",
                "missing_whatsapp_cta"
            ]
            quality_score = 0.0
            mobile_score = 0.0
            performance_score = 0.0
            design_score = 0.0
            conversion_score = 0.0
            raw_metrics = {"reason": "No website or unreachable"}
        else:
            # Case 2: Inspect existing website
            inspection = self.audit_provider.inspect_url(lead.website_url)
            raw_metrics = inspection

            if not inspection.get("has_meta_viewport"):
                missing_elements.append("missing_mobile_optimization")
            if not inspection.get("has_menu_link"):
                missing_elements.append("missing_online_menu")
            if not inspection.get("has_booking_cta"):
                missing_elements.append("missing_booking_cta")
            if not inspection.get("has_whatsapp_cta"):
                missing_elements.append("missing_whatsapp_cta")

            mobile_score = inspection.get("mobile_score", 50.0)
            performance_score = inspection.get("performance_score", 50.0)
            design_score = inspection.get("design_score", 50.0)
            
            # Conversion score based on CTAs present
            conversion_score = 100.0 - (len(missing_elements) * 20.0)
            conversion_score = max(0.0, conversion_score)

            # Overall composite quality score
            quality_score = (mobile_score * 0.3) + (performance_score * 0.2) + (design_score * 0.25) + (conversion_score * 0.25)

        # Create or update WebsiteAudit record
        audit_record = self.db.query(WebsiteAudit).filter(WebsiteAudit.business_id == lead.id).first()
        if not audit_record:
            audit_record = WebsiteAudit(
                business_id=lead.id,
                quality_score=quality_score,
                performance_score=performance_score,
                mobile_score=mobile_score,
                design_score=design_score,
                conversion_score=conversion_score,
                missing_elements={"elements": missing_elements},
                raw_metrics=raw_metrics
            )
            self.db.add(audit_record)
        else:
            audit_record.quality_score = quality_score
            audit_record.performance_score = performance_score
            audit_record.mobile_score = mobile_score
            audit_record.design_score = design_score
            audit_record.conversion_score = conversion_score
            audit_record.missing_elements = {"elements": missing_elements}
            audit_record.raw_metrics = raw_metrics

        self.db.commit()
        self.db.refresh(audit_record)

        logger.info(f"Audited lead {lead.id} ({lead.name}): Quality Score={quality_score:.1f}")
        return {
            "lead_id": lead.id,
            "quality_score": quality_score,
            "mobile_score": mobile_score,
            "performance_score": performance_score,
            "design_score": design_score,
            "conversion_score": conversion_score,
            "missing_elements": missing_elements
        }
