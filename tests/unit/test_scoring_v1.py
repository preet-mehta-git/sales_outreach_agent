import pytest
from app.db.models import Business, WebsiteAudit
from app.schemas.enums import WebsiteStatus
from app.services.scoring_engine import ScoringEngine


def create_mock_business(name="Test Biz", website_url=None, website_status=WebsiteStatus.NO_WEBSITE, rating=4.5, review_count=1500, phone="+919876543210", address="Ahmedabad"):
    return Business(
        id="test-id",
        name=name,
        website_url=website_url,
        website_status=website_status,
        rating=rating,
        review_count=review_count,
        phone=phone,
        address=address
    )


def test_score_no_website_strong_reviews():
    biz = create_mock_business(website_url=None, website_status=WebsiteStatus.NO_WEBSITE, rating=4.7, review_count=1500)
    score_data = ScoringEngine.calculate_score(biz, decision_maker_confidence="HIGH")
    assert 0.0 <= score_data["total_score"] <= 100.0
    assert score_data["digital_opportunity_gap_score"] == 35.0
    assert score_data["total_score"] >= 80.0


def test_score_poor_website_strong_business():
    biz = create_mock_business(website_url="http://poor.com", website_status=WebsiteStatus.WEAK_WEBSITE, rating=4.5, review_count=800)
    audit = WebsiteAudit(quality_score=30.0)
    score_data = ScoringEngine.calculate_score(biz, audit=audit, decision_maker_confidence="MEDIUM")
    assert score_data["digital_opportunity_gap_score"] == 24.5  # 35 * (1 - 0.3)
    assert score_data["total_score"] >= 70.0


def test_score_excellent_website():
    biz = create_mock_business(website_url="http://excellent.com", website_status=WebsiteStatus.WEBSITE_FOUND, rating=4.8, review_count=300)
    audit = WebsiteAudit(quality_score=95.0)
    score_data = ScoringEngine.calculate_score(biz, audit=audit)
    assert score_data["digital_opportunity_gap_score"] == 1.8  # 35 * (1 - 0.95)
    assert score_data["total_score"] < 60.0


def test_score_no_website_weak_business():
    biz = create_mock_business(website_url=None, website_status=WebsiteStatus.NO_WEBSITE, rating=3.2, review_count=4)
    score_data = ScoringEngine.calculate_score(biz)
    assert score_data["digital_opportunity_gap_score"] == 35.0
    assert score_data["customer_traction_score"] < 10.0


def test_score_multiple_locations():
    biz = create_mock_business(name="Chain Restaurant Branch 3", review_count=1200, rating=4.4)
    score_data = ScoringEngine.calculate_score(biz, purchase_signals=["new_branch", "expansion"])
    assert score_data["purchase_signals_score"] == 7.0


def test_score_premium_restaurant():
    biz = create_mock_business(name="Royal Dining", rating=4.9, review_count=900)
    score_data = ScoringEngine.calculate_score(biz, decision_maker_confidence="HIGH")
    assert score_data["commercial_potential_score"] > 10.0


def test_score_small_cafe():
    biz = create_mock_business(name="Corner Chai", rating=4.1, review_count=45)
    score_data = ScoringEngine.calculate_score(biz)
    assert 0.0 <= score_data["total_score"] <= 100.0


def test_score_missing_decision_maker():
    biz = create_mock_business()
    score_data = ScoringEngine.calculate_score(biz, decision_maker_confidence=None)
    assert score_data["contactability_score"] <= 5.0  # Only phone/address points


def test_score_missing_contact():
    biz = create_mock_business(phone=None, address=None)
    score_data = ScoringEngine.calculate_score(biz)
    assert score_data["contactability_score"] == 0.0


def test_score_missing_reviews():
    biz = create_mock_business(review_count=0, rating=0.0)
    score_data = ScoringEngine.calculate_score(biz)
    assert score_data["customer_traction_score"] == 0.0


def test_score_missing_website_quality_data():
    biz = create_mock_business(website_url="http://unknown.com", website_status=WebsiteStatus.WEBSITE_FOUND)
    score_data = ScoringEngine.calculate_score(biz, audit=None)
    assert score_data["digital_opportunity_gap_score"] == 15.0


def test_score_missing_purchase_signals():
    biz = create_mock_business()
    score_data = ScoringEngine.calculate_score(biz, purchase_signals=None)
    assert score_data["purchase_signals_score"] == 0.0
