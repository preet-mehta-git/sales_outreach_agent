from app.schemas.enums import WorkflowState


class InvalidStateTransitionError(Exception):
    def __init__(self, from_state: WorkflowState, to_state: WorkflowState):
        super().__init__(f"Invalid workflow transition: Cannot move from {from_state.value} to {to_state.value}")
        self.from_state = from_state
        self.to_state = to_state


class WorkflowStateMachine:
    # Explicit mapping of allowed state transitions
    ALLOWED_TRANSITIONS: dict[WorkflowState, set[WorkflowState]] = {
        WorkflowState.DISCOVERED: {
            WorkflowState.VERIFIED,
            WorkflowState.REJECTED,
            WorkflowState.FAILED
        },
        WorkflowState.VERIFIED: {
            WorkflowState.WEBSITE_ANALYZED,
            WorkflowState.REJECTED,
            WorkflowState.FAILED
        },
        WorkflowState.WEBSITE_ANALYZED: {
            WorkflowState.SCORED,
            WorkflowState.REJECTED,
            WorkflowState.FAILED
        },
        WorkflowState.SCORED: {
            WorkflowState.QUALIFIED,
            WorkflowState.DECISION_MAKER_RESEARCHED,  # Proceed to decision maker if qualified
            WorkflowState.REJECTED,
            WorkflowState.FAILED
        },
        WorkflowState.QUALIFIED: {
            WorkflowState.DECISION_MAKER_RESEARCHED,
            WorkflowState.REJECTED
        },
        WorkflowState.DECISION_MAKER_RESEARCHED: {
            WorkflowState.BUSINESS_AUDITED,
            WorkflowState.FAILED
        },
        WorkflowState.BUSINESS_AUDITED: {
            WorkflowState.DEMO_GENERATED,
            WorkflowState.FAILED
        },
        WorkflowState.DEMO_GENERATED: {
            WorkflowState.OUTREACH_DRAFTED,
            WorkflowState.FAILED
        },
        WorkflowState.OUTREACH_DRAFTED: {
            WorkflowState.AWAITING_APPROVAL,
            WorkflowState.FAILED
        },
        WorkflowState.AWAITING_APPROVAL: {
            WorkflowState.APPROVED,
            WorkflowState.REJECTED,
            WorkflowState.MANUAL_REVIEW,
            WorkflowState.DO_NOT_CONTACT
        },
        WorkflowState.APPROVED: {
            WorkflowState.CONTACTED,
            WorkflowState.FAILED
        },
        WorkflowState.CONTACTED: {
            WorkflowState.REPLIED,
            WorkflowState.DO_NOT_CONTACT
        },
        WorkflowState.REPLIED: {
            WorkflowState.QUALIFIED_OPPORTUNITY,
            WorkflowState.WON,
            WorkflowState.LOST,
            WorkflowState.DO_NOT_CONTACT
        },
        
        # Terminal / Exit states can transition to DO_NOT_CONTACT or remain terminal
        WorkflowState.REJECTED: {WorkflowState.DO_NOT_CONTACT},
        WorkflowState.FAILED: {WorkflowState.DISCOVERED, WorkflowState.DO_NOT_CONTACT},
        WorkflowState.DO_NOT_CONTACT: set()
    }

    @classmethod
    def validate_transition(cls, current_state: WorkflowState, target_state: WorkflowState) -> bool:
        """
        Validate whether transitioning from current_state to target_state is legal.
        Raises InvalidStateTransitionError if illegal.
        """
        if current_state == target_state:
            return True  # Idempotent state re-validation
            
        allowed = cls.ALLOWED_TRANSITIONS.get(current_state, set())
        if target_state not in allowed:
            raise InvalidStateTransitionError(current_state, target_state)
        return True
