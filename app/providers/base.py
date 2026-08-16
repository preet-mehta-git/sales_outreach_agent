from abc import ABC, abstractmethod
from typing import Any


class BasePlacesProvider(ABC):
    @abstractmethod
    def search_places(self, query: str, city: str = "Ahmedabad", limit: int = 10) -> list[dict[str, Any]]:
        """Search for businesses matching target query and location."""
        pass

    @abstractmethod
    def get_place_details(self, place_id: str) -> dict[str, Any]:
        """Fetch detailed place metadata."""
        pass


class BaseSearchProvider(ABC):
    @abstractmethod
    def search_web(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Search the web for business website discovery."""
        pass


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_structured(self, prompt: str, schema: type) -> Any:
        """Generate structured JSON conforming to Pydantic schema."""
        pass

    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate raw text response."""
        pass


class BaseAuditProvider(ABC):
    @abstractmethod
    def inspect_url(self, url: str) -> dict[str, Any]:
        """Inspect HTML DOM, meta tags, and reachability."""
        pass
