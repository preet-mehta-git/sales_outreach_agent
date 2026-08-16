from sqlalchemy.orm import Session
from app.db.models import Business
from app.schemas.lead import BusinessCreate
from app.schemas.enums import WorkflowState, WebsiteStatus, VerificationStatus
from app.services.deduplication import DeduplicationEngine
from app.core.audit import AuditService
from app.core.logging import get_logger

logger = get_logger("LeadService")


class LeadService:
    @staticmethod
    def create_lead(db: Session, lead_data: BusinessCreate, campaign_id: str | None = None) -> tuple[Business, bool]:
        """
        Create a new lead with automatic deduplication.
        Returns tuple: (Business entity, is_new_boolean).
        """
        # Step 1: Check for duplicate
        existing = DeduplicationEngine.find_duplicate(db, lead_data)
        if existing:
            logger.info(f"Duplicate lead detected. Returning existing lead id={existing.id}")
            return existing, False

        # Step 2: Classify initial website status
        if not lead_data.website_url or lead_data.website_url.strip() == "":
            initial_web_status = WebsiteStatus.NO_WEBSITE
        else:
            initial_web_status = WebsiteStatus.WEBSITE_FOUND

        # Step 3: Instantiate and persist lead
        lead = Business(
            campaign_id=campaign_id,
            name=lead_data.name,
            category=lead_data.category,
            address=lead_data.address,
            city=lead_data.city,
            state=lead_data.state,
            country=lead_data.country,
            phone=lead_data.phone,
            email=lead_data.email,
            place_id=lead_data.place_id,
            rating=lead_data.rating,
            review_count=lead_data.review_count,
            website_url=lead_data.website_url,
            website_status=initial_web_status,
            verification_status=VerificationStatus.UNVERIFIED,
            workflow_state=WorkflowState.DISCOVERED,
            is_suppressed=False
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)

        # Audit recording
        AuditService.record_transition(
            db=db,
            business_id=lead.id,
            action="LEAD_CREATED",
            from_state=None,
            to_state=WorkflowState.DISCOVERED.value,
            agent_name="DiscoveryAgent",
            payload_snapshot={"name": lead.name, "source": lead_data.source_name}
        )

        logger.info(f"Created new lead: {lead.name} (id={lead.id})")
        return lead, True

    @staticmethod
    def get_lead(db: Session, lead_id: str) -> Business | None:
        return db.query(Business).filter(Business.id == lead_id).first()

    @staticmethod
    def list_leads(
        db: Session,
        city: str | None = None,
        category: str | None = None,
        workflow_state: WorkflowState | None = None,
        min_score: float | None = None,
        exclude_suppressed: bool = True,
        limit: int = 50,
        offset: int = 0
    ) -> list[Business]:
        query = db.query(Business)
        
        if exclude_suppressed:
            query = query.filter(Business.is_suppressed.is_(False))
        if city:
            query = query.filter(Business.city.ilike(f"%{city}%"))
        if category:
            query = query.filter(Business.category.ilike(f"%{category}%"))
        if workflow_state:
            query = query.filter(Business.workflow_state == workflow_state)
        if min_score is not None:
            query = query.filter(Business.opportunity_score >= min_score)
            
        return query.order_by(Business.opportunity_score.desc().nullslast()).offset(offset).limit(limit).all()

    @staticmethod
    def suppress_lead(db: Session, lead_id: str, reason: str = "DO_NOT_CONTACT") -> Business | None:
        """Mark a lead as suppressed and update workflow state to DO_NOT_CONTACT."""
        lead = db.query(Business).filter(Business.id == lead_id).first()
        if not lead:
            return None

        old_state = lead.workflow_state.value if lead.workflow_state else None
        lead.is_suppressed = True
        lead.workflow_state = WorkflowState.DO_NOT_CONTACT
        db.commit()
        db.refresh(lead)

        AuditService.record_transition(
            db=db,
            business_id=lead.id,
            action="LEAD_SUPPRESSED",
            from_state=old_state,
            to_state=WorkflowState.DO_NOT_CONTACT.value,
            agent_name="SuppressionService",
            payload_snapshot={"reason": reason}
        )

        logger.info(f"Suppressed lead {lead.id} ({lead.name}). Marked DO_NOT_CONTACT.")
        return lead
