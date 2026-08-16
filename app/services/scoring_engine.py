from typing import Any
from app.db.models import Business, WebsiteAudit
from app.schemas.enums import WebsiteStatus
from app.core.logging import get_logger

logger = get_logger("ScoringEngine")


class ScoringEngine:
    @classmethod
    def calculate_score(cls, business: Business, audit: WebsiteAudit | None = None) -> dict[str, Any]:
        """
        Calculate composite opportunity score (0.0 to 100.0) for a lead based on:
        1. Website Gap Signal (35 pts max)
        2. Commercial Viability Signal (25 pts max)
        3. Digital Presence Gap Signal (20 pts max)
        4. Reachability & Contactability Signal (20 pts max)
        """
        website_score = 0.0
        viability_score = 0.0
        gap_score = 0.0
        reachability_score = 0.0

        # Signal 1: Website Gap (Max 35 pts)
        status = business.website_status
        if status == WebsiteStatus.NO_WEBSITE or not business.website_url:
            website_score = 35.0
        elif status == WebsiteStatus.WEBSITE_UNREACHABLE:
            website_score = 30.0
        elif status == WebsiteStatus.WEAK_WEBSITE:
            website_score = 25.0
        elif status == WebsiteStatus.WEBSITE_FOUND:
            # Low quality site -> higher sales opportunity
            if audit and audit.quality_score is not None:
                if audit.quality_score < 40.0:
                    website_score = 20.0
                elif audit.quality_score < 70.0:
                    website_score = 12.0
                else:
                    website_score = 5.0
            else:
                website_score = 10.0

        # Signal 2: Commercial Viability (Max 25 pts)
        rating = business.rating or 0.0
        reviews = business.review_count or 0

        if rating >= 4.5:
            viability_score += 15.0
        elif rating >= 4.0:
            viability_score += 10.0
        elif rating >= 3.5:
            viability_score += 5.0

        if reviews >= 50:
            viability_score += 10.0
        elif reviews >= 20:
            viability_score += 5.0
        elif reviews >= 5:
            viability_score += 2.0

        viability_score = min(25.0, viability_score)

        # Signal 3: Digital Presence Gaps (Max 20 pts)
        if audit and audit.missing_elements and "elements" in audit.missing_elements:
            missing = audit.missing_elements["elements"]
            if "missing_online_menu" in missing:
                gap_score += 7.0
            if "missing_booking_cta" in missing:
                gap_score += 7.0
            if "missing_whatsapp_cta" in missing:
                gap_score += 6.0
        else:
            # If no site exists, all gaps apply
            if website_score >= 30.0:
                gap_score = 20.0

        gap_score = min(20.0, gap_score)

        # Signal 4: Reachability & Contactability (Max 20 pts)
        if business.phone and business.phone.strip():
            reachability_score += 10.0

        if business.place_id and business.address:
            reachability_score += 10.0
        elif business.address:
            reachability_score += 5.0

        reachability_score = min(20.0, reachability_score)

        # Total Composite Score
        total_score = website_score + viability_score + gap_score + reachability_score
        total_score = round(min(100.0, max(0.0, total_score)), 1)

        breakdown = {
            "total_score": total_score,
            "website_gap_score": website_score,
            "commercial_viability_score": viability_score,
            "digital_gap_score": gap_score,
            "reachability_score": reachability_score
        }

        logger.info(f"Calculated opportunity score for '{business.name}': {total_score}/100.0")
        return breakdown
