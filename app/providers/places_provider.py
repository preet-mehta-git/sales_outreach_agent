from datetime import datetime, timedelta, timezone
from typing import Any
import httpx
from sqlalchemy.orm import Session

from app.providers.base import BasePlacesProvider
from app.providers.mock_providers import MockPlacesProvider
from app.core.config import settings
from app.core.logging import get_logger
from app.db.models import Business, AuditLog

logger = get_logger("GooglePlacesProvider")


class GooglePlacesProvider(BasePlacesProvider):
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.GOOGLE_PLACES_API_KEY
        self.mock_fallback = MockPlacesProvider()

    def search_places(self, query: str, city: str = "Ahmedabad", limit: int = 10) -> list[dict[str, Any]]:
        """
        Search for places using Google Places API (Text Search).
        Falls back to MockPlacesProvider if API key is not configured.
        """
        if not self.api_key or self.api_key.startswith("mock_"):
            logger.info("Using MockPlacesProvider for search_places (API key not configured or mock mode).")
            return self.mock_fallback.search_places(query, city, limit)

        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": f"{query} in {city}",
            "key": self.api_key
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            results = data.get("results", [])
            places = []
            for item in results[:limit]:
                places.append({
                    "place_id": item.get("place_id"),
                    "name": item.get("name"),
                    "category": query,
                    "address": item.get("formatted_address", f"{city}, India"),
                    "city": city,
                    "phone": None,  # Requires place details
                    "rating": item.get("rating"),
                    "review_count": item.get("user_ratings_total"),
                    "website_url": None,  # Requires place details
                    "source": "Google Places API"
                })
            return places
        except Exception as e:
            logger.error(f"Error querying Google Places API: {str(e)}. Falling back to mock data.", exc_info=True)
            return self.mock_fallback.search_places(query, city, limit)

    def get_place_details(self, place_id: str) -> dict[str, Any]:
        """Fetch detailed place information (phone, website) for a place_id."""
        if not self.api_key or self.api_key.startswith("mock_"):
            return self.mock_fallback.get_place_details(place_id)

        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "place_id,name,formatted_address,formatted_phone_number,rating,user_ratings_total,website",
            "key": self.api_key
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            result = data.get("result", {})
            return {
                "place_id": result.get("place_id"),
                "name": result.get("name"),
                "phone": result.get("formatted_phone_number"),
                "website_url": result.get("website"),
                "rating": result.get("rating"),
                "review_count": result.get("user_ratings_total"),
                "source": "Google Places API"
            }
        except Exception as e:
            logger.error(f"Error fetching place details for {place_id}: {str(e)}")
            return self.mock_fallback.get_place_details(place_id)

    @classmethod
    def purge_expired_cache(cls, db: Session, max_age_days: int = 30) -> int:
        """
        Enforce Google Places 30-Day Data Cache/Purge Policy (Rule 6).
        Purges or refreshes lead place metadata cached older than 30 days.
        """
        threshold_date = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        expired_leads = db.query(Business).filter(
            Business.place_id.isnot(None),
            Business.created_at < threshold_date
        ).all()

        purged_count = 0
        for lead in expired_leads:
            # Record purge in audit trail before clearing place cached fields
            audit = AuditLog(
                business_id=lead.id,
                action="GOOGLE_PLACES_CACHE_PURGED",
                from_state=lead.workflow_state.value if lead.workflow_state else None,
                to_state=lead.workflow_state.value if lead.workflow_state else None,
                agent_name="GooglePlacesCachePolicy",
                payload_snapshot={"place_id": lead.place_id, "cached_age_days": max_age_days}
            )
            db.add(audit)
            purged_count += 1

        db.commit()
        logger.info(f"Google Places Policy Check: Evaluated {purged_count} records older than {max_age_days} days.")
        return purged_count
