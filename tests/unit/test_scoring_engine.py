from app.services.scoring_engine import ScoringEngine
from app.db.models import Business, WebsiteAudit
from app.schemas.enums import WebsiteStatus


def test_scoring_engine_no_website_high_opportunity():
    business = Business(
        name="Star Cafe",
        category="cafe",
        address="Navrangpura, Ahmedabad",
        city="Ahmedabad",
        phone="+919876543210",
        place_id="ch_star_cafe",
        rating=4.6,
        review_count=65,
        website_status=WebsiteStatus.NO_WEBSITE
    )
    
    score_data = ScoringEngine.calculate_score(business, decision_maker_confidence="HIGH")
    assert score_data["total_score"] >= 70.0
    assert score_data["digital_opportunity_gap_score"] == 35.0
    assert score_data["contactability_score"] == 10.0


def test_scoring_engine_good_existing_website_low_opportunity():
    business = Business(
        name="Established Fine Dining",
        category="restaurant",
        address="SG Highway",
        city="Ahmedabad",
        phone="+919876543211",
        place_id="ch_fine_dining",
        rating=4.2,
        review_count=150,
        website_url="http://finedining.example.com",
        website_status=WebsiteStatus.WEBSITE_FOUND
    )
    audit = WebsiteAudit(
        quality_score=95.0,
        missing_elements={"elements": []}
    )

    score_data = ScoringEngine.calculate_score(business, audit)
    assert score_data["digital_opportunity_gap_score"] == 1.8  # 35 * (1 - 0.95)
    assert score_data["total_score"] < 60.0
