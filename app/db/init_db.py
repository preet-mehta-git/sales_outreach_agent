from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.db.models import Campaign
from app.core.logging import get_logger

logger = get_logger("DBInit")


def init_db(db: Session | None = None) -> None:
    """Create tables and initialize default Ahmedabad Restaurant/Cafe campaign if missing."""
    Base.metadata.create_all(bind=engine)
    
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True
        
    try:
        existing_campaign = db.query(Campaign).filter(Campaign.name == "Ahmedabad Restaurant & Cafe Campaign").first()
        if not existing_campaign:
            default_campaign = Campaign(
                name="Ahmedabad Restaurant & Cafe Campaign",
                industry="restaurant_cafe",
                city="Ahmedabad",
                state="Gujarat",
                country="India",
                min_opportunity_score=70,
                priority_score=80,
                is_active=True
            )
            db.add(default_campaign)
            db.commit()
            logger.info("Initialized default campaign: Ahmedabad Restaurant & Cafe Campaign")
    finally:
        if close_session:
            db.close()


if __name__ == "__main__":
    init_db()
