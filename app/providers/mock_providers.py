from typing import Any
from app.providers.base import BasePlacesProvider, BaseSearchProvider, BaseLLMProvider, BaseAuditProvider


class MockPlacesProvider(BasePlacesProvider):
    def __init__(self):
        self._mock_db = [
            {
                "place_id": "ch_ahmedabad_001",
                "name": "Makarba Social Cafe",
                "category": "cafe",
                "address": "SG Highway, Makarba, Ahmedabad, Gujarat 380051",
                "city": "Ahmedabad",
                "phone": "+91 98765 43210",
                "rating": 4.6,
                "review_count": 1250,
                "website_url": None,  # No website prospect
                "source": "Mock Google Places API"
            },
            {
                "place_id": "ch_ahmedabad_002",
                "name": "Vastrapur Heritage Dining",
                "category": "restaurant",
                "address": "Near Vastrapur Lake, Ahmedabad, Gujarat 380015",
                "city": "Ahmedabad",
                "phone": "+91 98765 12345",
                "rating": 4.3,
                "review_count": 890,
                "website_url": "http://vastrapurheritagedining.example.com",  # Weak website prospect
                "source": "Mock Google Places API"
            },
            {
                "place_id": "ch_ahmedabad_003",
                "name": "Navrangpura Artisanal Bakery",
                "category": "bakery",
                "address": "CG Road, Navrangpura, Ahmedabad, Gujarat 380009",
                "city": "Ahmedabad",
                "phone": "+91 98765 67890",
                "rating": 4.8,
                "review_count": 420,
                "website_url": None,  # No website prospect
                "source": "Mock Google Places API"
            }
        ]

    def search_places(self, query: str, city: str = "Ahmedabad", limit: int = 10) -> list[dict[str, Any]]:
        return self._mock_db[:limit]

    def get_place_details(self, place_id: str) -> dict[str, Any]:
        for place in self._mock_db:
            if place["place_id"] == place_id:
                return place
        return {
            "place_id": place_id,
            "name": "Unknown Business",
            "category": "restaurant",
            "address": "Ahmedabad, Gujarat",
            "city": "Ahmedabad",
            "rating": 4.0,
            "review_count": 50,
            "website_url": None,
            "source": "Mock Google Places API"
        }


class MockSearchProvider(BaseSearchProvider):
    def search_web(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        return [
            {
                "title": f"Search result for {query}",
                "snippet": "Local dining option in Ahmedabad with authentic cuisine.",
                "link": "https://directory-example.com/biz/123"
            }
        ]


class MockLLMProvider(BaseLLMProvider):
    def generate_structured(self, prompt: str, schema: type) -> Any:
        # Returns a mock instance conforming to schema if possible
        if hasattr(schema, "mock"):
            return schema.mock()
        return {}

    def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        return f"[MOCK LLM GENERATION]: Response generated for prompt '{prompt[:40]}...'"


class MockAuditProvider(BaseAuditProvider):
    def inspect_url(self, url: str) -> dict[str, Any]:
        if "weak" in url or "example" in url:
            return {
                "reachable": True,
                "status_code": 200,
                "title": "Welcome to Our Restaurant",
                "has_meta_viewport": False,
                "has_menu_link": False,
                "has_booking_cta": False,
                "has_whatsapp_cta": False,
                "performance_score": 35.0,
                "mobile_score": 30.0,
                "design_score": 40.0
            }
        return {
            "reachable": False,
            "status_code": 404,
            "title": None,
            "has_meta_viewport": False,
            "performance_score": 0.0,
            "mobile_score": 0.0,
            "design_score": 0.0
        }
