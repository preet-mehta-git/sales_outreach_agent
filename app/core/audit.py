from typing import Any
from sqlalchemy.orm import Session
from app.db.models import AuditLog
from app.core.logging import get_logger

logger = get_logger("AuditService")


class AuditService:
    @staticmethod
    def record_transition(
        db: Session,
        business_id: str | None,
        action: str,
        from_state: str | None,
        to_state: str | None,
        agent_name: str | None = None,
        payload_snapshot: dict[str, Any] | None = None
    ) -> AuditLog:
        """
        Record an immutable audit log entry for system actions and state changes.
        """
        log_entry = AuditLog(
            business_id=business_id,
            action=action,
            from_state=from_state,
            to_state=to_state,
            agent_name=agent_name,
            payload_snapshot=payload_snapshot
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        
        logger.info(
            f"AUDIT_RECORD: business_id={business_id} action={action} "
            f"state={from_state}->{to_state} agent={agent_name}"
        )
        return log_entry
