from typing import Any
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState, ConfidenceLevel
from app.db.models import Business, DecisionMakerRecord
from app.orchestrator.engine import OrchestratorEngine
from app.core.logging import get_logger

logger = get_logger("ContactDiscoveryAgent")


class ContactDiscoveryAgent(BaseAgent[dict[str, Any]]):
    name = "ContactDiscoveryAgent"
    version = "1.0"

    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.orchestrator = OrchestratorEngine(self.db)

    def run(self, input_data: AgentInput) -> dict[str, Any]:
        lead = self.db.query(Business).filter(Business.id == input_data.lead_id).first()
        if not lead:
            raise ValueError(f"Business lead with ID {input_data.lead_id} not found.")

        # Check if verified custom owner parameters were explicitly provided
        params = {**input_data.parameters, **input_data.custom_params}
        explicit_owner = params.get("owner_name")
        explicit_title = params.get("owner_title", "Owner / Manager")

        if explicit_owner and explicit_owner.strip():
            dm_name = explicit_owner.strip()
            role_title = explicit_title.strip()
            confidence = ConfidenceLevel.HIGH
            evidence = {"source": "Verified User Input", "explicit_name": True}
        else:
            # NO owner fabricated. Never invent a person's name without evidence.
            dm_name = None
            role_title = None
            confidence = ConfidenceLevel.NOT_FOUND
            evidence = {"source": "Discovery Provider", "explicit_name": False, "status": "NOT_FOUND"}

        phone = lead.phone
        email = lead.email  # Real email only, never fabricate contact@domain.com

        # Create or update DecisionMakerRecord
        dm_record = self.db.query(DecisionMakerRecord).filter(DecisionMakerRecord.business_id == lead.id).first()
        if not dm_record:
            dm_record = DecisionMakerRecord(
                business_id=lead.id,
                name=dm_name,
                title=role_title,
                contact_phone=phone,
                contact_email=email,
                confidence=confidence,
                evidence=evidence
            )
            self.db.add(dm_record)
        else:
            dm_record.name = dm_name
            dm_record.title = role_title
            dm_record.contact_phone = phone
            dm_record.contact_email = email
            dm_record.confidence = confidence
            dm_record.evidence = evidence

        self.db.commit()
        self.db.refresh(dm_record)

        # Advance state QUALIFIED -> DECISION_MAKER_RESEARCHED via Orchestrator
        if lead.workflow_state == WorkflowState.QUALIFIED:
            self.orchestrator.transition_lead(
                lead_id=lead.id,
                target_state=WorkflowState.DECISION_MAKER_RESEARCHED,
                agent_name=self.name,
                payload_snapshot={
                    "decision_maker_id": dm_record.id,
                    "confidence_level": confidence.value,
                    "role_title": role_title,
                    "decision_maker_name": dm_name
                }
            )

        logger.info(f"ContactDiscoveryAgent completed DM research for lead {lead.id}: DM={dm_name} ({confidence.value})")
        return {
            "lead_id": lead.id,
            "decision_maker_id": dm_record.id,
            "full_name": dm_record.name,
            "role_title": dm_record.title,
            "phone": dm_record.contact_phone,
            "email": dm_record.contact_email,
            "confidence_level": confidence.value
        }
