from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db.models import Business, AuditLog
from app.core.logging import get_logger

logger = get_logger("CachePurgerService")


class CachePurgerService:
    """
    Google Places Storage Compliance Purger Service (Section 3.2.3 TOS).
    Purges raw cached Google Places attributes older than 30 days while retaining place_id
    and system-derived metadata (opportunity scores, audit logs, workflow state).
    """
    
    @classmethod
    def run_compliance_purge(cls, db: Session, max_age_days: int = 30) -> dict[str, int]:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        
        expired_businesses = db.query(Business).filter(
            Business.place_id.isnot(None),
            Business.created_at < cutoff_date
        ).all()

        purged_count = 0
        for biz in expired_businesses:
            # Retain place_id and system-derived identifiers.
            # Purge raw cached Google Places attributes per Google Maps TOS 3.2.3
            biz.rating = None
            biz.review_count = None
            biz.phone = None
            
            audit = AuditLog(
                business_id=biz.id,
                action="GOOGLE_PLACES_30DAY_COMPLIANCE_PURGE",
                from_state=biz.workflow_state.value if biz.workflow_state else None,
                to_state=biz.workflow_state.value if biz.workflow_state else None,
                agent_name="CachePurgerService",
                payload_snapshot={
                    "place_id": biz.place_id,
                    "purged_fields": ["rating", "review_count", "phone"],
                    "purged_at": datetime.now(timezone.utc).isoformat()
                }
            )
            db.add(audit)
            purged_count += 1

        db.commit()
        logger.info(f"CachePurgerService completed compliance purge: {purged_count} records processed.")
        return {"records_processed": purged_count}
