from sqlalchemy.orm import Session
from app.db.models import Campaign
from app.schemas.campaign import CampaignCreate
from app.core.logging import get_logger

logger = get_logger("CampaignService")


class CampaignService:
    @staticmethod
    def create_campaign(db: Session, campaign_data: CampaignCreate) -> Campaign:
        campaign = Campaign(
            name=campaign_data.name,
            industry=campaign_data.industry,
            city=campaign_data.city,
            state=campaign_data.state,
            country=campaign_data.country,
            min_opportunity_score=campaign_data.min_opportunity_score,
            priority_score=campaign_data.priority_score,
            is_active=campaign_data.is_active
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        logger.info(f"Created campaign: {campaign.name} (id={campaign.id})")
        return campaign

    @staticmethod
    def get_campaign(db: Session, campaign_id: str) -> Campaign | None:
        return db.query(Campaign).filter(Campaign.id == campaign_id).first()

    @staticmethod
    def list_campaigns(db: Session, active_only: bool = False) -> list[Campaign]:
        query = db.query(Campaign)
        if active_only:
            query = query.filter(Campaign.is_active.is_(True))
        return query.order_by(Campaign.created_at.desc()).all()
