import math
from typing import Any
from app.db.models import Business, WebsiteAudit
from app.schemas.enums import WebsiteStatus, WebsiteVerificationStatus
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
        ver_status = business.website_verification_status

        if ver_status == WebsiteVerificationStatus.NO_WEBSITE_CONFIRMED or status == WebsiteStatus.NO_WEBSITE or not business.website_url:
            digital_gap_score = 35.0
        elif status == WebsiteStatus.WEBSITE_UNREACHABLE:
            digital_gap_score = 35.0
        elif audit and audit.quality_score is not None:
            qs = max(0.0, min(100.0, audit.quality_score))
            digital_gap_score = 35.0 * (1.0 - (qs / 100.0))
        elif status == WebsiteStatus.WEAK_WEBSITE:
            digital_gap_score = 28.0
        else:
            digital_gap_score = 15.0

        digital_gap_score = round(max(0.0, min(35.0, digital_gap_score)), 1)

        # 2. Customer Traction (Max 25 pts)
        reviews = business.review_count or 0
        if reviews <= 0:
            review_score = 0.0
        else:
            review_score = min(15.0, math.log10(reviews) * 5.0)

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

        recent_activity_score = 0.0
        if reviews >= 50 and rating >= 4.0:
            recent_activity_score = 5.0
        elif reviews >= 10:
            recent_activity_score = 2.5

        customer_traction_score = round(min(25.0, review_score + rating_score + recent_activity_score), 1)

        # 3. Commercial Potential (Max 20 pts)
        comm_price = 3.0
        comm_scale = 3.0
        comm_opportunity = 4.0 if digital_gap_score >= 20.0 else 2.0
        comm_brand = 3.0

        if reviews >= 500:
            comm_scale = 5.0
            comm_price = 4.0
        elif reviews < 10:
            comm_scale = 1.0

        commercial_potential_score = round(min(20.0, comm_price + comm_scale + comm_opportunity + comm_brand), 1)

        # 4. Contactability (Max 10 pts)
        dm_score = 0.0
        if decision_maker_confidence in ("HIGH", "MEDIUM"):
            dm_score = 5.0
        elif decision_maker_confidence == "LOW":
            dm_score = 2.0

        contact_avail = 0.0
        if business.phone and business.phone.strip():
            contact_avail += 3.0
        if business.address and business.address.strip():
            contact_avail += 2.0

        contactability_score = round(min(10.0, dm_score + contact_avail), 1)

        # 5. Purchase Signals (Max 10 pts)
        signal_reasons = []
        if purchase_signals:
            signal_reasons = list(purchase_signals)
        elif business.purchase_signal_evidence and isinstance(business.purchase_signal_evidence, list):
            signal_reasons = list(business.purchase_signal_evidence)
        else:
            # Check implicit verified expansion signals
            if reviews >= 500:
                signal_reasons.append("High review volume (500+) indicates high transaction capacity and potential digital expansion intent.")

        if not signal_reasons:
            purchase_signals_score = 0.0
            signal_reasons = ["No verified public purchase signal found."]
        else:
            purchase_signals_score = round(min(10.0, len([s for s in signal_reasons if "No verified" not in s]) * 5.0), 1)
            if purchase_signals_score == 0.0 and len(signal_reasons) > 0 and "No verified" not in signal_reasons[0]:
                purchase_signals_score = 5.0

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
            "components": {
                "digital_opportunity_gap": {
                    "raw_score": round((digital_gap_score / 35.0) * 100.0, 1),
                    "weight_pct": 35.0,
                    "contribution": digital_gap_score,
                    "reason": f"Digital Gap Score {digital_gap_score}/35.0 (Website verification status: {ver_status.value if ver_status else status.value if status else 'NO_WEBSITE'})",
                    "evidence": {"website_status": status.value if status else None, "quality_score": audit.quality_score if audit else None}
                },
                "customer_traction": {
                    "raw_score": round((customer_traction_score / 25.0) * 100.0, 1),
                    "weight_pct": 25.0,
                    "contribution": customer_traction_score,
                    "reason": f"Customer Traction Score {customer_traction_score}/25.0 based on {reviews} reviews & {rating} rating",
                    "evidence": {"reviews": reviews, "rating": rating}
                },
                "commercial_potential": {
                    "raw_score": round((commercial_potential_score / 20.0) * 100.0, 1),
                    "weight_pct": 20.0,
                    "contribution": commercial_potential_score,
                    "reason": f"Commercial Potential Score {commercial_potential_score}/20.0 based on business scale and revenue gap",
                    "evidence": {"reviews": reviews, "price_positioning": comm_price, "scale": comm_scale}
                },
                "contactability": {
                    "raw_score": round((contactability_score / 10.0) * 100.0, 1),
                    "weight_pct": 10.0,
                    "contribution": contactability_score,
                    "reason": f"Contactability Score {contactability_score}/10.0 (Phone: {'Yes' if business.phone else 'No'}, DM confidence: {decision_maker_confidence or 'NOT_FOUND'})",
                    "evidence": {"phone_present": bool(business.phone), "dm_confidence": decision_maker_confidence}
                },
                "purchase_signals": {
                    "raw_score": round((purchase_signals_score / 10.0) * 100.0, 1),
                    "weight_pct": 10.0,
                    "contribution": purchase_signals_score,
                    "reason": f"Purchase Signals Score {purchase_signals_score}/10.0: {signal_reasons[0]}",
                    "evidence": {"signals": signal_reasons}
                }
            },
            "reasons": {
                "digital_gap_reason": f"Digital Gap Score {digital_gap_score}/35.0 (Website verification status: {ver_status.value if ver_status else status.value if status else 'NO_WEBSITE'})",
                "traction_reason": f"Customer Traction Score {customer_traction_score}/25.0 based on {reviews} reviews & {rating} rating",
                "commercial_reason": f"Commercial Potential Score {commercial_potential_score}/20.0 based on business scale and revenue gap",
                "contactability_reason": f"Contactability Score {contactability_score}/10.0 (Phone: {'Yes' if business.phone else 'No'}, DM confidence: {decision_maker_confidence or 'NOT_FOUND'})",
                "purchase_signals_reason": f"Purchase Signals Score {purchase_signals_score}/10.0: {signal_reasons[0]}"
            },
            "evidence": {
                "reviews": reviews,
                "rating": rating,
                "website_status": status.value if status else None,
                "website_verification_status": ver_status.value if ver_status else None,
                "quality_score": audit.quality_score if audit else None,
                "decision_maker_confidence": decision_maker_confidence,
                "purchase_signals": signal_reasons
            },
            "score_version": "V1_AGREED_35_25_20_10_10"
        }

        logger.info(f"Calculated V1 opportunity score for '{business.name}': {total_score}/100.0")
        return breakdown
