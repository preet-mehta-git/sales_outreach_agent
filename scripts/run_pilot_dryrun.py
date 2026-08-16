import os
import sys
from sqlalchemy.orm import Session

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal, engine
from app.db.models import Base, Campaign, Business, OutreachDraft, DecisionMakerRecord, WebsiteAudit
from app.orchestrator.pipeline import CampaignPipelineRunner
from app.schemas.enums import WorkflowState, WebsiteStatus, OutreachStatus, ConfidenceLevel
from app.services.scoring_engine import ScoringEngine
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("PilotDryRun")

# Re-create tables to update schema with Phase 11 columns
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


AHMEDABAD_PILOT_SAMPLES = [
    {
        "name": "Manek Chowk Night Food Market",
        "category": "street food",
        "address": "Manek Chowk, Danaplee, Khadia",
        "city": "Ahmedabad",
        "phone": "+91 98250 12345",
        "rating": 4.6,
        "review_count": 2850,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },
    {
        "name": "Agashiye - House of MG",
        "category": "fine dining restaurant",
        "address": "Opp. Sidi Saiyyed Mosque, Lal Darwaja",
        "city": "Ahmedabad",
        "phone": "+91 79 2550 6941",
        "rating": 4.7,
        "review_count": 1420,
        "website_url": "https://houseofmg.com",
        "website_status": WebsiteStatus.WEBSITE_FOUND
    },
    {
        "name": "Gordhan Thal",
        "category": "gujarati thali restaurant",
        "address": "SG Highway, Bodakdev",
        "city": "Ahmedabad",
        "phone": "+91 79 2687 1222",
        "rating": 4.5,
        "review_count": 980,
        "website_url": "http://gordhanthal.com",
        "website_status": WebsiteStatus.WEBSITE_FOUND
    },
    {
        "name": "Zen Cafe",
        "category": "cafe",
        "address": "University Road, Navrangpura",
        "city": "Ahmedabad",
        "phone": "+91 98980 54321",
        "rating": 4.4,
        "review_count": 510,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },
    {
        "name": "Lucky Tea Stall",
        "category": "cafe & tea",
        "address": "Opp. Dinbai Tower, Mirzapur",
        "city": "Ahmedabad",
        "phone": "+91 79 2562 1100",
        "rating": 4.3,
        "review_count": 760,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },
    {
        "name": "Karnavati Dabeli & Vadapav",
        "category": "fast food",
        "address": "C G Road, Navrangpura",
        "city": "Ahmedabad",
        "phone": "+91 98240 99887",
        "rating": 4.2,
        "review_count": 340,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },
    {
        "name": "Havmor Restaurant",
        "category": "family restaurant",
        "address": "Navrangpura Bus Stop",
        "city": "Ahmedabad",
        "phone": "+91 79 2640 5000",
        "rating": 4.4,
        "review_count": 890,
        "website_url": "https://havmor.com",
        "website_status": WebsiteStatus.WEBSITE_FOUND
    },
    {
        "name": "Upper Crust Bakery & Cafe",
        "category": "bakery & cafe",
        "address": "Vijay Cross Road, Navrangpura",
        "city": "Ahmedabad",
        "phone": "+91 79 2646 4477",
        "rating": 4.5,
        "review_count": 620,
        "website_url": "http://uppercrustindia.com",
        "website_status": WebsiteStatus.WEAK_WEBSITE
    },
    {
        "name": "Swati Snacks",
        "category": "traditional snacks",
        "address": "Law Garden, Ellisbridge",
        "city": "Ahmedabad",
        "phone": "+91 79 2640 0000",
        "rating": 4.6,
        "review_count": 1150,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },
    {
        "name": "Vishalla Village Restaurant",
        "category": "heritage dining",
        "address": "Vasna Road, Opposite APMC Market",
        "city": "Ahmedabad",
        "phone": "+91 79 2660 2422",
        "rating": 4.3,
        "review_count": 1680,
        "website_url": "http://vishalla.com",
        "website_status": WebsiteStatus.WEAK_WEBSITE
    }
]


def run_dryrun():
    db: Session = SessionLocal()
    try:
        logger.info("=== STARTING AHMEDABAD PILOT DRY-RUN (OUTREACH_MODE=DRY_RUN) ===")
        assert settings.OUTREACH_MODE == "DRY_RUN", "OUTREACH_MODE MUST BE DRY_RUN!"

        # Create Pilot Campaign
        campaign = Campaign(
            name="Ahmedabad Pilot Dry Run - 10 Businesses",
            city="Ahmedabad",
            industry="restaurant_cafe",
            min_opportunity_score=70
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        runner = CampaignPipelineRunner(db)
        results = []

        for sample in AHMEDABAD_PILOT_SAMPLES:
            # Seed lead into DB
            biz = Business(
                campaign_id=campaign.id,
                name=sample["name"],
                category=sample["category"],
                address=sample["address"],
                city=sample["city"],
                phone=sample["phone"],
                rating=sample["rating"],
                review_count=sample["review_count"],
                website_url=sample["website_url"],
                website_status=sample["website_status"],
                workflow_state=WorkflowState.DISCOVERED
            )
            db.add(biz)
            db.commit()
            db.refresh(biz)

            # Process lead through pipeline
            pipeline_result = runner.run_lead_pipeline(biz)
            
            # Fetch updated state
            db.refresh(biz)
            audit = db.query(WebsiteAudit).filter_by(business_id=biz.id).first()
            dm = db.query(DecisionMakerRecord).filter_by(business_id=biz.id).first()
            draft = db.query(OutreachDraft).filter_by(business_id=biz.id).first()

            results.append({
                "id": biz.id,
                "name": biz.name,
                "category": biz.category,
                "city": biz.city,
                "website_url": biz.website_url,
                "website_status": biz.website_status.value if biz.website_status else "NO_WEBSITE",
                "quality_score": audit.quality_score if audit else "N/A",
                "opportunity_score": biz.opportunity_score or 0.0,
                "workflow_state": biz.workflow_state.value,
                "dm_name": dm.name if dm else "None",
                "dm_confidence": dm.confidence.value if dm else "NOT_FOUND",
                "draft_status": draft.status.value if draft else "N/A",
                "demo_url": draft.demo_url if draft else "N/A"
            })

        logger.info(f"Successfully executed dry-run for {len(results)} businesses.")
        return results

    finally:
        db.close()


if __name__ == "__main__":
    results = run_dryrun()
    print(f"DRY RUN SUCCESSFUL: Processed {len(results)} businesses.")
