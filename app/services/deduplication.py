import re
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from app.db.models import Business
from app.schemas.lead import BusinessCreate
from app.core.logging import get_logger

logger = get_logger("DeduplicationEngine")


class DeduplicationEngine:
    @staticmethod
    def normalize_phone(phone: str | None) -> str | None:
        """Strip non-digit characters from phone number."""
        if not phone:
            return None
        digits = re.sub(r"\D", "", phone)
        # Handle standard Indian country code 91 prefix
        if len(digits) > 10 and digits.startswith("91"):
            digits = digits[2:]
        return digits if len(digits) >= 10 else None

    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize business name by removing punctuation and lowercasing."""
        clean = re.sub(r"[^\w\s]", "", name.lower())
        return " ".join(clean.split())

    @staticmethod
    def extract_domain(url: str | None) -> str | None:
        """Extract canonical domain name from URL."""
        if not url:
            return None
        try:
            if not url.startswith(("http://", "https://")):
                url = f"http://{url}"
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            domain = domain.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain if domain else None
        except Exception:
            return None

    @classmethod
    def find_duplicate(cls, db: Session, lead_data: BusinessCreate) -> Business | None:
        """
        Check database for potential duplicate lead using multi-tiered strategy.
        Returns matching Business entity if found, otherwise None.
        """
        # Tier 1: Exact Place ID Match
        if lead_data.place_id:
            existing = db.query(Business).filter(Business.place_id == lead_data.place_id).first()
            if existing:
                logger.info(f"DEDUPLICATION_MATCH [Place ID]: {lead_data.place_id} matches existing lead {existing.id}")
                return existing

        # Tier 2: Normalized Phone Match
        norm_phone = cls.normalize_phone(lead_data.phone)
        if norm_phone:
            all_leads = db.query(Business).filter(Business.phone.isnot(None)).all()
            for existing in all_leads:
                if cls.normalize_phone(existing.phone) == norm_phone:
                    logger.info(f"DEDUPLICATION_MATCH [Phone]: {lead_data.phone} matches existing lead {existing.id}")
                    return existing

        # Tier 3: Canonical Domain Match
        target_domain = cls.extract_domain(lead_data.website_url)
        if target_domain:
            all_leads = db.query(Business).filter(Business.website_url.isnot(None)).all()
            for existing in all_leads:
                if cls.extract_domain(existing.website_url) == target_domain:
                    logger.info(f"DEDUPLICATION_MATCH [Domain]: {target_domain} matches existing lead {existing.id}")
                    return existing

        # Tier 4: Normalized Name + City Match
        norm_name = cls.normalize_name(lead_data.name)
        norm_city = lead_data.city.lower().strip()
        candidates = db.query(Business).filter(Business.city.ilike(norm_city)).all()
        for existing in candidates:
            if cls.normalize_name(existing.name) == norm_name:
                logger.info(f"DEDUPLICATION_MATCH [Name+City]: {lead_data.name} matches existing lead {existing.id}")
                return existing

        return None
