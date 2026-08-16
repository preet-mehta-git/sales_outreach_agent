from typing import Any
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.schemas.agent import AgentInput
from app.db.models import Business, AuditLog
from app.schemas.enums import EntityType, EntityVerificationStatus, WorkflowState


class EntityVerifierAgent(BaseAgent[dict[str, Any]]):
    name = "EntityVerifierAgent"
    version = "1.0"

    NON_BUSINESS_KEYWORDS = [
        "market", "food market", "night market", "food street", "bazaar",
        "landmark", "park", "garden", "road", "street", "area", "neighborhood",
        "mall", "shopping center", "complex", "building", "tourist attraction",
        "temple", "stadium", "lake", "bridge", "monument", "bus stop",
        "railway station", "airport", "circle", "cross road"
    ]

    VALID_BUSINESS_CATEGORIES = [
        "restaurant", "cafe", "hotel", "bakery", "salon", "clinic", "retail",
        "shop", "fast food", "sweets", "thali", "diner", "bistro", "eatery",
        "store", "spa", "gym", "pharmacy", "boutique"
    ]

    def __init__(self, db: Session):
        super().__init__()
        self.db = db

    def run(self, input_data: AgentInput) -> dict[str, Any]:
        business = self.db.query(Business).filter(Business.id == input_data.lead_id).first()
        if not business:
            raise ValueError(f"Business with ID {input_data.lead_id} not found.")

        name_lower = (business.name or "").lower()
        cat_lower = (business.category or "").lower()

        evidence = []
        entity_type = EntityType.BUSINESS
        verification_status = EntityVerificationStatus.VERIFIED
        confidence = 90.0

        # Check non-business keywords
        matched_nb_kw = [kw for kw in self.NON_BUSINESS_KEYWORDS if kw in name_lower or kw in cat_lower]

        # Explicit check for markets / food streets / geographic landmarks
        if any(market_term in name_lower for market_term in ["night food market", "market", "food street", "bazaar"]):
            # Unless category explicitly indicates a single business shop inside
            if not any(cat in cat_lower for cat in ["fast food", "bakery", "cafe"]):
                entity_type = EntityType.NON_BUSINESS
                verification_status = EntityVerificationStatus.REJECTED
                confidence = 95.0
                evidence.append(f"Entity name/category indicates market/food-street area rather than a single commercial business: {matched_nb_kw}")

        if entity_type == EntityType.BUSINESS and matched_nb_kw:
            # Check if name ends with landmark or road without business descriptor
            if any(name_lower.endswith(kw) for kw in ["market", "street", "road", "park", "garden"]):
                entity_type = EntityType.NON_BUSINESS
                verification_status = EntityVerificationStatus.REJECTED
                confidence = 90.0
                evidence.append(f"Entity name ends with non-business spatial term: {matched_nb_kw}")
            else:
                # Could be a business located near/named after a landmark (e.g. Navrangpura Bus Stop -> check category)
                if any(cat_term in cat_lower for cat_term in self.VALID_BUSINESS_CATEGORIES):
                    evidence.append(f"Contains location landmark in name ({matched_nb_kw}) but category matches single business type ({business.category})")
                else:
                    entity_type = EntityType.UNCERTAIN
                    verification_status = EntityVerificationStatus.MANUAL_REVIEW
                    confidence = 50.0
                    evidence.append(f"Uncertain entity status due to landmark terms in name/category: {matched_nb_kw}")

        if entity_type == EntityType.BUSINESS:
            evidence.append(f"Verified single business entity: '{business.name}' (Category: {business.category})")

        # Save to database
        business.entity_type = entity_type
        business.entity_verification_status = verification_status
        business.entity_verification_confidence = confidence
        business.entity_verification_evidence = evidence

        # If rejected non-business, update workflow state
        if verification_status == EntityVerificationStatus.REJECTED:
            from_state = business.workflow_state.value if business.workflow_state else "DISCOVERED"
            business.workflow_state = WorkflowState.REJECTED
            audit_log = AuditLog(
                business_id=business.id,
                action="ENTITY_VERIFICATION_REJECTED",
                from_state=from_state,
                to_state="REJECTED",
                agent_name=self.name,
                payload_snapshot={"entity_type": entity_type.value, "evidence": evidence}
            )
            self.db.add(audit_log)
        else:
            business.workflow_state = WorkflowState.VERIFIED

        self.db.commit()
        self.db.refresh(business)

        return {
            "entity_type": entity_type.value,
            "verification_status": verification_status.value,
            "confidence": confidence,
            "evidence": evidence
        }
