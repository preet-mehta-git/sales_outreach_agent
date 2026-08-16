from sqlalchemy.orm import Session
from app.db.models import Business
from app.schemas.enums import WorkflowState
from app.orchestrator.state import WorkflowStateMachine
from app.core.audit import AuditService
from app.core.logging import get_logger

logger = get_logger("OrchestratorEngine")


class OrchestratorEngine:
    def __init__(self, db: Session):
        self.db = db

    def transition_lead(
        self,
        lead_id: str,
        target_state: WorkflowState,
        agent_name: str | None = None,
        payload_snapshot: dict | None = None
    ) -> Business:
        """
        Safely transition a business lead to a target state with validation and audit trail.
        """
        lead = self.db.query(Business).filter(Business.id == lead_id).first()
        if not lead:
            raise ValueError(f"Business lead with ID {lead_id} not found.")

        # Check suppression rule (Rule 28)
        if lead.is_suppressed and target_state != WorkflowState.DO_NOT_CONTACT:
            logger.warning(f"Lead {lead_id} is marked DO_NOT_CONTACT. Halting transition to {target_state.value}")
            return lead

        current_state = lead.workflow_state

        # Validate legal transition
        WorkflowStateMachine.validate_transition(current_state, target_state)

        # Update lead workflow state
        lead.workflow_state = target_state
        self.db.commit()
        self.db.refresh(lead)

        # Record immutable audit log
        AuditService.record_transition(
            db=self.db,
            business_id=lead.id,
            action=f"TRANSITION_TO_{target_state.value}",
            from_state=current_state.value,
            to_state=target_state.value,
            agent_name=agent_name,
            payload_snapshot=payload_snapshot
        )

        logger.info(f"Successfully transitioned lead {lead_id} from {current_state.value} to {target_state.value}")
        return lead
