from typing import Any, Tuple, List, Optional
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import (
    WorkflowState, OutreachStatus, ConfidenceLevel, EntityType,
    EntityVerificationStatus, WebsiteVerificationStatus, OutreachReadiness,
    ContactTargetStatus, DemoAccessStatus
)
from app.db.models import Business, DecisionMakerRecord, WebsiteAudit, OutreachDraft
from app.orchestrator.engine import OrchestratorEngine
from app.core.logging import get_logger

logger = get_logger("OutreachAgent")


class OutreachAgent(BaseAgent[dict[str, Any]]):
    name = "OutreachAgent"
    version = "2.1"

    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.orchestrator = OrchestratorEngine(self.db)

    def evaluate_readiness(self, lead: Business, draft: OutreachDraft | None) -> Tuple[OutreachReadiness, List[str]]:
        reasons = []
        is_ready = True

        # Checklist 1: Entity Verified
        if lead.entity_type != EntityType.BUSINESS or lead.entity_verification_status != EntityVerificationStatus.VERIFIED:
            is_ready = False
            reasons.append("Entity is not a verified commercial business.")

        # Checklist 2: Website Status Verified
        if lead.website_verification_status not in [WebsiteVerificationStatus.OFFICIAL_WEBSITE_VERIFIED, WebsiteVerificationStatus.NO_WEBSITE_CONFIRMED]:
            is_ready = False
            reasons.append(f"Website status is unverified or conflicting ({lead.website_verification_status}).")

        # Checklist 3: Contact Route / Target Status Verified
        if lead.contact_target_status == ContactTargetStatus.NOT_FOUND and not lead.phone and not lead.email:
            is_ready = False
            reasons.append("No verified individual decision maker or business contact route available.")
        elif not lead.phone and not lead.email:
            is_ready = False
            reasons.append("No phone or email contact route available.")

        # Checklist 4: Suppression Check
        if lead.is_suppressed:
            return OutreachReadiness.SUPPRESSED, ["Lead is explicitly suppressed."]

        # Checklist 5: Demo Access Check (Demo URL optional for outreach if non-public)
        if lead.demo_access_status != DemoAccessStatus.PUBLIC_ACCESSIBLE:
            reasons.append(f"Demo URL is local/non-public ({lead.demo_access_status or 'LOCAL_ONLY'}). Non-public demo URL excluded from outreach copy.")

        if is_ready:
            return OutreachReadiness.READY_FOR_APPROVAL, ["All required Phase 11.1 outreach readiness criteria passed."]
        else:
            return OutreachReadiness.MANUAL_REVIEW, reasons

    def determine_greeting(self, lead: Business, dm: Optional[DecisionMakerRecord]) -> str:
        target_status = lead.contact_target_status

        if target_status == ContactTargetStatus.VERIFIED_PERSON and dm and dm.name:
            first_name = dm.name.split()[0]
            return f"Hi {first_name},"
        elif target_status == ContactTargetStatus.VERIFIED_ROLE and dm and dm.title:
            return f"Hello {dm.title},"
        elif target_status in (ContactTargetStatus.BUSINESS_CONTACT_ONLY, ContactTargetStatus.NOT_FOUND, ContactTargetStatus.MANUAL_REVIEW):
            return f"Hello {lead.name} Team,"
        else:
            return f"Hello {lead.name} Team,"

    def run(self, input_data: AgentInput) -> dict[str, Any]:
        lead = self.db.query(Business).filter(Business.id == input_data.lead_id).first()
        if not lead:
            raise ValueError(f"Business lead with ID {input_data.lead_id} not found.")

        # Invariant: NON_BUSINESS => NEVER_SALES_PROSPECT (Exclude from outreach drafting)
        is_explicit_non_business = (
            (lead.entity_verification_status and lead.entity_verification_status.value == "REJECTED") or
            (lead.entity_type and lead.entity_type.value == "NON_BUSINESS")
        )
        if is_explicit_non_business:
            logger.info(f"Lead {lead.id} ({lead.name}) is a non-business entity ({lead.entity_verification_status}). Skipping outreach drafting.")
            lead.outreach_readiness = OutreachReadiness.NOT_READY
            lead.outreach_readiness_reasons = ["Entity is not a verified commercial business."]
            self.db.commit()
            return {
                "lead_id": lead.id,
                "status": "SKIPPED_NON_BUSINESS",
                "outreach_readiness": OutreachReadiness.NOT_READY.value,
                "readiness_reasons": ["Entity is not a verified commercial business."]
            }

        dm = self.db.query(DecisionMakerRecord).filter(DecisionMakerRecord.business_id == lead.id).first()
        audit = self.db.query(WebsiteAudit).filter(WebsiteAudit.business_id == lead.id).first()
        draft = self.db.query(OutreachDraft).filter(OutreachDraft.business_id == lead.id).first()

        greeting = self.determine_greeting(lead, dm)

        # Include demo URL ONLY if genuinely PUBLIC_ACCESSIBLE
        is_demo_public = (lead.demo_access_status == DemoAccessStatus.PUBLIC_ACCESSIBLE and bool(lead.public_demo_url))
        demo_url = lead.public_demo_url if is_demo_public else None

        subject = f"Digital opportunity assessment for {lead.name}"

        if demo_url:
            demo_section = f"""To demonstrate how this can be resolved, we assembled a live mobile prototype for {lead.name}:
{demo_url}

Prototype features included:
- Instant WhatsApp Click-to-Order CTA
- Mobile-responsive menu display
- One-tap location & enquiry form"""
            wa_demo_text = f" View it here: {demo_url} -"
        else:
            demo_section = f"""We have conducted a digital audit and prototype design for {lead.name} to optimize direct online customer ordering and reservation conversion."""
            wa_demo_text = ""

        email_body = f"""{greeting}

I came across {lead.name} while reviewing commercial businesses in {lead.city}. Your {lead.rating or '4.0'}⭐ public rating across {lead.review_count or '10+'} Google reviews reflects strong customer interest.

Based on our digital audit, we identified a key growth opportunity: online searchers looking for {lead.name} currently lack a direct mobile menu and WhatsApp instant ordering route.

{demo_section}

Would you be open to a 5-minute call this week to review how this can be enabled for {lead.name}?

Best regards,
Outreach Team | Antigravity AI Systems

---
To update outreach preferences or opt out, please reply with "REMOVE".
"""

        whatsapp_body = (
            f"{greeting} We reviewed the online presence for {lead.name} "
            f"and identified opportunities for instant WhatsApp ordering and mobile menu.{wa_demo_text} "
            f"Let us know if you would like to view our findings!"
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
            draft.demo_url = demo_url
            draft.status = OutreachStatus.AWAITING_APPROVAL

        # Evaluate Outreach Readiness
        readiness, readiness_reasons = self.evaluate_readiness(lead, draft)
        lead.outreach_readiness = readiness
        lead.outreach_readiness_reasons = readiness_reasons

        self.db.commit()
        self.db.refresh(draft)
        self.db.refresh(lead)

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
                    "outreach_readiness": readiness.value,
                    "readiness_reasons": readiness_reasons,
                    "demo_url": demo_url
                }
            )

        logger.info(f"OutreachAgent created drafts for lead {lead.id}: Draft ID={draft.id}, Readiness={readiness.value}, TargetStatus={lead.contact_target_status.value if lead.contact_target_status else 'NONE'}")
        return {
            "lead_id": lead.id,
            "draft_id": draft.id,
            "email_subject": subject,
            "email_body": email_body,
            "whatsapp_body": whatsapp_body,
            "demo_url": demo_url,
            "status": draft.status.value,
            "outreach_readiness": readiness.value,
            "readiness_reasons": readiness_reasons
        }

