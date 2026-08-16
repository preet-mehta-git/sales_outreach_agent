import math
from typing import Any
from app.db.models import Business, WebsiteAudit
from app.schemas.enums import WebsiteStatus
from app.core.logging import get_logger

logger = get_logger("ScoringEngine")


class ScoringEngine:
    """
    Agreed V1 Opportunity Scoring Engine (0.0 to 100.0)
    
    Breakdown:
    1. Digital Opportunity Gap: 35 pts max
    2. Customer Traction: 25 pts max
    3. Commercial Potential: 20 pts max
    4. Contactability: 10 pts max
    5. Purchase Signals: 10 pts max
    """
    
    @classmethod
    def calculate_score(
        cls,
        business: Business,
        audit: WebsiteAudit | None = None,
        decision_maker_confidence: str | None = None,
        purchase_signals: list[str] | None = None
    ) -> dict[str, Any]:
        
        # 1. Digital Opportunity Gap (Max 35 pts)
        status = business.website_status
        if status == WebsiteStatus.NO_WEBSITE or not business.website_url:
            digital_gap_score = 35.0
        elif status == WebsiteStatus.WEBSITE_UNREACHABLE:
            digital_gap_score = 35.0
        elif audit and audit.quality_score is not None:
            # Formula: 35 * (1 - quality_score / 100)
            qs = max(0.0, min(100.0, audit.quality_score))
            digital_gap_score = 35.0 * (1.0 - (qs / 100.0))
        elif status == WebsiteStatus.WEAK_WEBSITE:
            digital_gap_score = 28.0
        else:
            digital_gap_score = 15.0

        digital_gap_score = round(max(0.0, min(35.0, digital_gap_score)), 1)

        # 2. Customer Traction (Max 25 pts)
        # Review volume (Max 15 pts) - Logarithmic diminishing returns
        reviews = business.review_count or 0
        if reviews <= 0:
            review_score = 0.0
        else:
            # log10(1) = 0, log10(10) = 1, log10(100) = 2, log10(1000) = 3
            # Scale log10(reviews) * 5, capped at 15.0 (for 1000+ reviews)
            review_score = min(15.0, math.log10(reviews) * 5.0)

        # Rating (Max 5 pts)
        rating = business.rating or 0.0
        if rating >= 4.5:
            rating_score = 5.0
        elif rating >= 4.0:
            rating_score = 4.0
        elif rating >= 3.5:
            rating_score = 2.5
        elif rating >= 3.0:
            rating_score = 1.0
        else:
            rating_score = 0.0

        # Recent activity (Max 5 pts) - Score conservatively if unverified
        recent_activity_score = 0.0
        if reviews >= 50 and rating >= 4.0:
            # Strong proxy for active customer flow
            recent_activity_score = 5.0
        elif reviews >= 10:
            recent_activity_score = 2.5

        customer_traction_score = round(min(25.0, review_score + rating_score + recent_activity_score), 1)

        # 3. Commercial Potential (Max 20 pts)
        # Price/positioning (5 pts), Business scale (5 pts), Digital revenue opportunity (5 pts), Brand sophistication (5 pts)
        comm_price = 3.0
        comm_scale = 3.0
        comm_opportunity = 4.0 if digital_gap_score >= 20.0 else 2.0
        comm_brand = 3.0

        # Adjust based on review scale & rating evidence
        if reviews >= 500:
            comm_scale = 5.0
            comm_price = 4.0
        elif reviews < 10:
            comm_scale = 1.0

        commercial_potential_score = round(min(20.0, comm_price + comm_scale + comm_opportunity + comm_brand), 1)

        # 4. Contactability (Max 10 pts)
        # Decision maker confidence (5 pts)
        dm_score = 0.0
        if decision_maker_confidence in ("HIGH", "MEDIUM"):
            dm_score = 5.0
        elif decision_maker_confidence == "LOW":
            dm_score = 2.0

        # Business contact availability (5 pts)
        contact_avail = 0.0
        if business.phone and business.phone.strip():
            contact_avail += 3.0
        if business.address and business.address.strip():
            contact_avail += 2.0

        contactability_score = round(min(10.0, dm_score + contact_avail), 1)

        # 5. Purchase Signals (Max 10 pts)
        purchase_signals = purchase_signals or []
        purchase_signals_score = round(min(10.0, len(purchase_signals) * 3.5), 1)

        # Total Composite Score
        total_score = digital_gap_score + customer_traction_score + commercial_potential_score + contactability_score + purchase_signals_score
        total_score = round(max(0.0, min(100.0, total_score)), 1)

        breakdown = {
            "total_score": total_score,
            "digital_opportunity_gap_score": digital_gap_score,
            "customer_traction_score": customer_traction_score,
            "commercial_potential_score": commercial_potential_score,
            "contactability_score": contactability_score,
            "purchase_signals_score": purchase_signals_score,
            "evidence": {
                "reviews": reviews,
                "rating": rating,
                "website_status": status.value if status else None,
                "quality_score": audit.quality_score if audit else None,
                "decision_maker_confidence": decision_maker_confidence,
                "purchase_signals": purchase_signals
            },
            "score_version": "V1_AGREED_35_25_20_10_10"
        }

        logger.info(f"Calculated V1 opportunity score for '{business.name}': {total_score}/100.0")
        return breakdown
