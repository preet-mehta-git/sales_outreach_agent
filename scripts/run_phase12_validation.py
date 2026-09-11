import os
import sys
import json
from sqlalchemy.orm import Session

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal, engine
from app.db.models import Base, Campaign, Business, OutreachDraft, DecisionMakerRecord, WebsiteAudit
from app.orchestrator.pipeline import CampaignPipelineRunner
from app.schemas.enums import WorkflowState, WebsiteStatus, OutreachStatus, ConfidenceLevel, ManualReviewStatus, DemoReadiness
from app.services.scoring_engine import ScoringEngine
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("Phase12Validation")


# 36 Representative Ahmedabad Entities across all 6 key tiers
AHMEDABAD_PHASE12_SAMPLE = [
    # TIER 1: Non-Business Entities & Area Markets (Gatekeeper Filter Test)
    {
        "name": "Manek Chowk Night Food Market",
        "category": "street food market",
        "address": "Manek Chowk, Danaplee, Khadia",
        "city": "Ahmedabad",
        "phone": "+91 98250 12345",
        "rating": 4.6,
        "review_count": 2850,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },
    {
        "name": "Urban Chowk Food Park",
        "category": "food park",
        "address": "Behind Rajpath Club, Bodakdev",
        "city": "Ahmedabad",
        "phone": "+91 98251 22334",
        "rating": 4.4,
        "review_count": 1820,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },
    {
        "name": "Law Garden Khau Gali",
        "category": "food street",
        "address": "Netaji Road, Ellisbridge",
        "city": "Ahmedabad",
        "phone": "+91 98252 33445",
        "rating": 4.3,
        "review_count": 2100,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },
    {
        "name": "Sindhu Bhavan Food Park",
        "category": "food park",
        "address": "Sindhu Bhavan Marg, Bodakdev",
        "city": "Ahmedabad",
        "phone": "+91 98253 44556",
        "rating": 4.2,
        "review_count": 940,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },

    # TIER 2: High-Traction Local Champions With NO Website (Prime Sales Opportunities)
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
        "name": "Das Khaman",
        "category": "traditional snacks",
        "address": "Shop 2, Nehrunagar Cross Road",
        "city": "Ahmedabad",
        "phone": "+91 79 2630 4567",
        "rating": 4.6,
        "review_count": 1250,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },
    {
        "name": "Lijjat Khaman House",
        "category": "traditional snacks",
        "address": "Kankaria Lake Front, Maninagar",
        "city": "Ahmedabad",
        "phone": "+91 79 2546 7890",
        "rating": 4.5,
        "review_count": 890,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },
    {
        "name": "Chai Wai Cafe",
        "category": "cafe",
        "address": "Near IIM New Campus, Vastrapur",
        "city": "Ahmedabad",
        "phone": "+91 98254 55667",
        "rating": 4.3,
        "review_count": 320,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },
    {
        "name": "Jail Na Bhajiya",
        "category": "fast food snacks",
        "address": "Near Subhash Bridge Circle, RTO",
        "city": "Ahmedabad",
        "phone": "+91 79 2755 1234",
        "rating": 4.5,
        "review_count": 1580,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },
    {
        "name": "Shambhu's Coffee Bar",
        "category": "coffee shop",
        "address": "HL College Road, Navrangpura",
        "city": "Ahmedabad",
        "phone": "+91 98255 66778",
        "rating": 4.2,
        "review_count": 680,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },

    # TIER 3: Multi-Location / Regional Heritage Dining (High Scale & Existing Digital Presence)
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
        "name": "Swati Snacks",
        "category": "traditional snacks",
        "address": "Law Garden, Ellisbridge",
        "city": "Ahmedabad",
        "phone": "+91 79 2640 0000",
        "rating": 4.6,
        "review_count": 1150,
        "website_url": "https://swatisnacks.com",
        "website_status": WebsiteStatus.WEBSITE_FOUND
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
        "name": "Sasuji Dining Hall",
        "category": "gujarati thali restaurant",
        "address": "C G Road, Ellisbridge",
        "city": "Ahmedabad",
        "phone": "+91 79 2640 3344",
        "rating": 4.4,
        "review_count": 1420,
        "website_url": "http://sasujidininghall.com",
        "website_status": WebsiteStatus.WEBSITE_FOUND
    },
    {
        "name": "Toran Dining Hall",
        "category": "gujarati thali restaurant",
        "address": "Ashram Road, Navrangpura",
        "city": "Ahmedabad",
        "phone": "+91 79 2658 2211",
        "rating": 4.3,
        "review_count": 920,
        "website_url": "http://toranrestaurant.com",
        "website_status": WebsiteStatus.WEBSITE_FOUND
    },
    {
        "name": "Atithi Dining Hall",
        "category": "gujarati thali restaurant",
        "address": "SG Highway, Bodakdev",
        "city": "Ahmedabad",
        "phone": "+91 79 2685 9900",
        "rating": 4.5,
        "review_count": 1100,
        "website_url": "http://atithidining.com",
        "website_status": WebsiteStatus.WEBSITE_FOUND
    },

    # TIER 4: Specialty Cafes, Bakeries & Lounges
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
        "name": "The Project Cafe",
        "category": "cafe & art space",
        "address": "Yellow House, Ambawadi",
        "city": "Ahmedabad",
        "phone": "+91 79 6545 7788",
        "rating": 4.4,
        "review_count": 740,
        "website_url": "https://theprojectcafe.in",
        "website_status": WebsiteStatus.WEBSITE_FOUND
    },
    {
        "name": "Mocha Cafe & Bar",
        "category": "cafe & bistro",
        "address": "Sindhu Bhavan Road, Bodakdev",
        "city": "Ahmedabad",
        "phone": "+91 79 4004 8899",
        "rating": 4.5,
        "review_count": 1300,
        "website_url": "https://mochacafe.com",
        "website_status": WebsiteStatus.WEBSITE_FOUND
    },
    {
        "name": "Kaffa Cerrado",
        "category": "specialty coffee cafe",
        "address": "Vastrapur Lake Road",
        "city": "Ahmedabad",
        "phone": "+91 98256 77889",
        "rating": 4.6,
        "review_count": 280,
        "website_url": "https://kaffacerrado.com",
        "website_status": WebsiteStatus.WEBSITE_FOUND
    },
    {
        "name": "Sale & Pepe",
        "category": "italian restaurant",
        "address": "Prahladnagar Trade Center",
        "city": "Ahmedabad",
        "phone": "+91 79 4008 1122",
        "rating": 4.3,
        "review_count": 490,
        "website_url": "https://saleandpepe.in",
        "website_status": WebsiteStatus.WEBSITE_FOUND
    },
    {
        "name": "Unlocked - Board Game Cafe",
        "category": "cafe & entertainment",
        "address": "Umashankar Joshi Marg, Navrangpura",
        "city": "Ahmedabad",
        "phone": "+91 79 4890 0099",
        "rating": 4.5,
        "review_count": 670,
        "website_url": "https://unlockedcafe.in",
        "website_status": WebsiteStatus.WEBSITE_FOUND
    },
    {
        "name": "Varietea",
        "category": "tea cafe & snacks",
        "address": "Sindhu Bhavan Road",
        "city": "Ahmedabad",
        "phone": "+91 98257 88990",
        "rating": 4.2,
        "review_count": 410,
        "website_url": "https://varietea.in",
        "website_status": WebsiteStatus.WEBSITE_FOUND
    },
    {
        "name": "Makeba The Lounge Cafe",
        "category": "rooftop cafe",
        "address": "31Five, Sarkhej Gandhinagar Highway",
        "city": "Ahmedabad",
        "phone": "+91 98258 99001",
        "rating": 4.4,
        "review_count": 820,
        "website_url": "https://makeba.in",
        "website_status": WebsiteStatus.WEBSITE_FOUND
    },

    # TIER 5: Fast Casual & Quick Serve Outlets
    {
        "name": "Honest Restaurant",
        "category": "fast food family restaurant",
        "address": "Prahladnagar Garden Road",
        "city": "Ahmedabad",
        "phone": "+91 79 2693 7700",
        "rating": 4.3,
        "review_count": 1850,
        "website_url": "https://honestrestaurants.com",
        "website_status": WebsiteStatus.WEBSITE_FOUND
    },
    {
        "name": "Gajanand Pauva House",
        "category": "breakfast & snacks",
        "address": "Gurukul Road, Memnagar",
        "city": "Ahmedabad",
        "phone": "+91 98259 00112",
        "rating": 4.4,
        "review_count": 620,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },
    {
        "name": "Jay Bhavani Vadapav",
        "category": "fast food",
        "address": "Municipal Market, C G Road",
        "city": "Ahmedabad",
        "phone": "+91 79 2642 1122",
        "rating": 4.2,
        "review_count": 580,
        "website_url": "https://jaybhavanivadapav.com",
        "website_status": WebsiteStatus.WEBSITE_FOUND
    },
    {
        "name": "Raju Omelet",
        "category": "egg specialty restaurant",
        "address": "Opp. Vastrapur Lake",
        "city": "Ahmedabad",
        "phone": "+91 98260 11223",
        "rating": 4.4,
        "review_count": 950,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },
    {
        "name": "Bikanervala",
        "category": "sweets & restaurant",
        "address": "Science City Road, Sola",
        "city": "Ahmedabad",
        "phone": "+91 79 4019 3300",
        "rating": 4.3,
        "review_count": 1100,
        "website_url": "https://bikanervala.com",
        "website_status": WebsiteStatus.WEBSITE_FOUND
    },

    # TIER 6: Micro & Low-Traction Outlets (Negative Control / Low Score Testing)
    {
        "name": "Chai Tapri",
        "category": "tea stall",
        "address": "Drive In Road, Nilmani Society",
        "city": "Ahmedabad",
        "phone": "+91 98261 22334",
        "rating": 3.8,
        "review_count": 45,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },
    {
        "name": "Shreeji Sandwich Corner",
        "category": "fast food",
        "address": "Shastrinagar, Naranpura",
        "city": "Ahmedabad",
        "phone": "+91 98262 33445",
        "rating": 3.9,
        "review_count": 65,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    },
    {
        "name": "Amdavad Juice Bar",
        "category": "beverages",
        "address": "Near Mahalaxmi Cross Road, Paldi",
        "city": "Ahmedabad",
        "phone": "+91 98263 44556",
        "rating": 3.7,
        "review_count": 35,
        "website_url": None,
        "website_status": WebsiteStatus.NO_WEBSITE
    }
]


def determine_final_action(manual_review_status: str, qualification: str, outreach_readiness: str, entity_status: str = "VERIFIED") -> str:
    # System Invariant: NON_BUSINESS => NEVER_SALES_PROSPECT
    if entity_status == "REJECTED":
        return "REJECTED"
    elif entity_status == "MANUAL_REVIEW":
        return "REQUIRES_MANUAL_REVIEW"

    if manual_review_status == "REVIEW_REQUIRED":
        return "REQUIRES_MANUAL_REVIEW"
    elif manual_review_status == "REVIEW_RECOMMENDED":
        return "REVIEW_RECOMMENDED"
    elif qualification in ["PRIORITY", "QUALIFIED"] and outreach_readiness == "READY_FOR_APPROVAL":
        return "AWAITING_HUMAN_OUTREACH_APPROVAL"
    elif qualification == "REJECTED" and manual_review_status == "NO_REVIEW_REQUIRED":
        return "REJECTED"
    elif qualification in ["PRIORITY", "QUALIFIED", "POTENTIAL_REVIEW"]:
        return "QUALIFIED_NOT_READY"
    else:
        return "REJECTED"


def run_phase12_validation():
    # Re-create tables to guarantee clean test state
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        logger.info("=== STARTING PHASE 12 REAL-WORLD VALIDATION (36 AHMEDABAD ENTITIES) ===")
        assert settings.OUTREACH_MODE == "DRY_RUN", "OUTREACH_MODE MUST BE DRY_RUN!"

        # Create Phase 12 Campaign
        campaign = Campaign(
            name="Ahmedabad Phase 12 Real-World Validation Campaign",
            city="Ahmedabad",
            industry="restaurant_cafe",
            min_opportunity_score=70
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        runner = CampaignPipelineRunner(db)
        results = []

        for sample in AHMEDABAD_PHASE12_SAMPLE:
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
            
            db.refresh(biz)
            audit = db.query(WebsiteAudit).filter_by(business_id=biz.id).first()
            dm = db.query(DecisionMakerRecord).filter_by(business_id=biz.id).first()
            draft = db.query(OutreachDraft).filter_by(business_id=biz.id).first()

            score_breakdown = ScoringEngine.calculate_score(
                business=biz,
                audit=audit,
                decision_maker_confidence=dm.confidence.value if dm else None,
                purchase_signals=[]
            )
            score = score_breakdown['total_score']

            # Qualification Tiers
            if biz.entity_verification_status and biz.entity_verification_status.value == "REJECTED":
                qualification = "REJECTED"
            else:
                if score >= 80.0:
                    qualification = "PRIORITY"
                elif score >= 70.0:
                    qualification = "QUALIFIED"
                elif score >= 60.0:
                    qualification = "POTENTIAL_REVIEW"
                else:
                    qualification = "REJECTED"

            evs = biz.entity_verification_status.value if biz.entity_verification_status else "VERIFIED"
            mrs = biz.manual_review_status.value if biz.manual_review_status else "NO_REVIEW_REQUIRED"
            cts = biz.contact_target_status.value if biz.contact_target_status else "NOT_FOUND"
            readiness = biz.outreach_readiness.value if biz.outreach_readiness else "NOT_READY"
            das = biz.demo_access_status.value if biz.demo_access_status else "NOT_GENERATED"
            action = determine_final_action(mrs, qualification, readiness, evs)

            results.append({
                "business_id": str(biz.id),
                "business_name": biz.name,
                "category": biz.category,
                "city": biz.city,
                "address": biz.address,
                "phone": biz.phone,
                "rating": biz.rating,
                "review_count": biz.review_count,
                "entity_status": biz.entity_verification_status.value if biz.entity_verification_status else "VERIFIED",
                "website_url": biz.website_url,
                "website_status": biz.website_status.value if biz.website_status else "NO_WEBSITE",
                "website_classification": biz.website_classification.value if biz.website_classification else "NO_WEBSITE",
                "opportunity_score": score,
                "score_breakdown": score_breakdown.get("components", {}),
                "qualification": qualification,
                "decision_maker": dm.name if (dm and dm.name) else "NOT_FOUND",
                "decision_maker_confidence": dm.confidence.value if (dm and dm.confidence) else "NOT_FOUND",
                "contact_target_status": cts,
                "outreach_readiness": readiness,
                "manual_review_status": mrs,
                "manual_review_reasons": biz.manual_review_reasons or [],
                "demo_url": biz.public_demo_url or biz.local_preview_url or "NOT_AVAILABLE",
                "demo_access_status": das,
                "action": action,
                "email_draft": draft.email_body if draft else "NOT_AVAILABLE",
                "whatsapp_draft": draft.whatsapp_body if draft else "NOT_AVAILABLE"
            })

        campaign_id = str(campaign.id)
        logger.info(f"Phase 12 Pipeline finished. Processed {len(results)} entities.")
        return campaign_id, results
    finally:
        db.close()


if __name__ == "__main__":
    campaign_id, results = run_phase12_validation()
    print(f"SUCCESS: Processed {len(results)} businesses in campaign {campaign_id}.")
