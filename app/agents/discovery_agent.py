from typing import Any
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.schemas.agent import AgentInput
from app.schemas.lead import BusinessCreate
from app.schemas.enums import WorkflowState, VerificationStatus
from app.providers.places_provider import GooglePlacesProvider
from app.services.lead_service import LeadService
from app.orchestrator.engine import OrchestratorEngine
from app.core.logging import get_logger

logger = get_logger("DiscoveryAgent")


class DiscoveryAgent(BaseAgent[dict[str, Any]]):
    name = "DiscoveryAgent"
    version = "1.0"

    def __init__(self, db: Session, places_provider: GooglePlacesProvider | None = None):
        super().__init__()
        self.db = db
        self.places_provider = places_provider or GooglePlacesProvider()
        self.orchestrator = OrchestratorEngine(self.db)

    def run(self, input_data: AgentInput) -> dict[str, Any]:
        params = input_data.parameters
        city = params.get("city", "Ahmedabad")
        keywords = params.get("keywords", ["restaurant", "cafe", "bakery"])
        limit_per_keyword = params.get("limit_per_keyword", 5)
        campaign_id = params.get("campaign_id")

        discovered_count = 0
        new_leads_count = 0
        duplicate_count = 0
        processed_lead_ids = []

        for kw in keywords:
            places = self.places_provider.search_places(query=kw, city=city, limit=limit_per_keyword)
            discovered_count += len(places)

            for item in places:
                # Fetch full place details if place_id is available
                place_id = item.get("place_id")
                if place_id:
                    details = self.places_provider.get_place_details(place_id)
                    phone = details.get("phone") or item.get("phone")
                    website_url = details.get("website_url") or item.get("website_url")
                else:
                    phone = item.get("phone")
                    website_url = item.get("website_url")

                lead_create = BusinessCreate(
                    name=item.get("name", "Unknown Business"),
                    category=item.get("category", kw),
                    address=item.get("address", f"{city}, Gujarat, India"),
                    city=city,
                    phone=phone,
                    place_id=place_id,
                    rating=item.get("rating"),
                    review_count=item.get("review_count"),
                    website_url=website_url,
                    source_name=item.get("source", "Google Places API")
                )

                # Ingest via LeadService with automatic deduplication
                lead, is_new = LeadService.create_lead(self.db, lead_create, campaign_id=campaign_id)
                
                if is_new:
                    new_leads_count += 1
                    # Transition newly created lead from DISCOVERED -> VERIFIED
                    if lead.name and lead.address:
                        lead.verification_status = VerificationStatus.VERIFIED
                        self.db.commit()
                        self.orchestrator.transition_lead(
                            lead_id=lead.id,
                            target_state=WorkflowState.VERIFIED,
                            agent_name=self.name,
                            payload_snapshot={"keyword": kw, "place_id": place_id}
                        )
                else:
                    duplicate_count += 1

                processed_lead_ids.append(lead.id)

        result_stats = {
            "city": city,
            "discovered_count": discovered_count,
            "new_leads_count": new_leads_count,
            "duplicate_count": duplicate_count,
            "processed_lead_ids": processed_lead_ids
        }
        
        logger.info(
            f"DiscoveryAgent finished: Discovered={discovered_count}, "
            f"New={new_leads_count}, Duplicates={duplicate_count}"
        )
        return result_stats
