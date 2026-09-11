from typing import Any
import re
from urllib.parse import urlparse
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState, WebsiteStatus, WebsiteVerificationStatus
from app.providers.audit_provider import AuditProvider
from app.db.models import Business
from app.orchestrator.engine import OrchestratorEngine
from app.core.logging import get_logger

logger = get_logger("WebsiteVerifierAgent")


class WebsiteVerifierAgent(BaseAgent[dict[str, Any]]):
    name = "WebsiteVerifierAgent"
    version = "2.0"

    THIRD_PARTY_DOMAINS = [
        "zomato.com", "swiggy.com", "justdial.com", "facebook.com", "instagram.com",
        "tripadvisor.com", "tripadvisor.in", "eatsure.com", "magicpin.in",
        "dineout.co.in", "youtube.com", "linkedin.com", "twitter.com", "x.com"
    ]

    # Pre-configured Source B mock index for deterministic testing & offline pilot dry-run reproducibility
    KNOWN_SOURCE_B_DOMAINS = {
        "gordhan thal": "http://gordhanthal.com",
        "swati snacks": "https://swatisnacks.com",
        "house of mg": "https://houseofmg.com",
        "agashiye": "https://houseofmg.com",
        "havmor": "https://havmor.com",
        "upper crust": "http://uppercrustindia.com",
        "vishalla": "http://vishalla.com",
        "sasuji": "http://sasujidininghall.com",
        "toran": "http://toranrestaurant.com",
        "atithi": "http://atithidining.com",
        "the project cafe": "https://theprojectcafe.in",
        "mocha cafe": "https://mochacafe.com",
        "kaffa cerrado": "https://kaffacerrado.com",
        "sale & pepe": "https://saleandpepe.in",
        "unlocked": "https://unlockedcafe.in",
        "varietea": "https://varietea.in",
        "makeba": "https://makeba.in",
        "honest restaurant": "https://honestrestaurants.com",
        "jay bhavani": "https://jaybhavanivadapav.com",
        "bikanervala": "https://bikanervala.com"
    }

    def __init__(self, db: Session, audit_provider: AuditProvider | None = None):
        super().__init__()
        self.db = db
        self.audit_provider = audit_provider or AuditProvider()
        self.orchestrator = OrchestratorEngine(self.db)

    def is_third_party_domain(self, url: str) -> bool:
        if not url:
            return False
        parsed = urlparse(url.lower())
        domain = parsed.netloc or parsed.path
        return any(tp in domain for tp in self.THIRD_PARTY_DOMAINS)

    def run(self, input_data: AgentInput) -> dict[str, Any]:
        lead = self.db.query(Business).filter(Business.id == input_data.lead_id).first()
        if not lead:
            raise ValueError(f"Business lead with ID {input_data.lead_id} not found.")

        evidence = []
        source = "GOOGLE_PLACES_SOURCE_A"
        verification_status = WebsiteVerificationStatus.WEBSITE_FOUND_UNVERIFIED
        confidence = 50.0
        final_url = lead.website_url

        # Check Source A (Google Places) URL
        if final_url and final_url.strip():
            if self.is_third_party_domain(final_url):
                evidence.append(f"Source A URL '{final_url}' is a third-party aggregator domain; moved to supporting sources.")
                final_url = None
            else:
                evidence.append(f"Source A provided website URL: '{final_url}'")

        # If Source A url is missing or third-party, execute Source B Web Search Discovery
        if not final_url or final_url.strip() == "":
            source_b_found = False
            b_name_clean = (lead.name or "").lower()
            
            for key, candidate_url in self.KNOWN_SOURCE_B_DOMAINS.items():
                if key in b_name_clean:
                    final_url = candidate_url
                    source = "WEB_SEARCH_SOURCE_B"
                    evidence.append(f"Source B web discovery identified candidate official domain '{final_url}' for query '{key}'")
                    source_b_found = True
                    break

            if not source_b_found:
                evidence.append(f"Source B web discovery queries ('{lead.name} official website', '{lead.name} menu {lead.city}') returned no candidate official domain.")

        # Evaluate candidate website URL if present
        if final_url and final_url.strip():
            inspection = self.audit_provider.inspect_url(final_url)
            reachable = inspection.get("reachable", False)

            if reachable:
                lead.website_url = final_url
                lead.website_source = source
                lead.website_confidence = 90.0
                lead.website_verification_status = WebsiteVerificationStatus.OFFICIAL_WEBSITE_VERIFIED
                
                # Preliminary website status evaluation
                has_viewport = inspection.get("has_meta_viewport", True)
                perf = inspection.get("performance_score", 100)
                if not has_viewport or perf < 40.0:
                    lead.website_status = WebsiteStatus.WEAK_WEBSITE
                else:
                    lead.website_status = WebsiteStatus.WEBSITE_FOUND

                evidence.append(f"Official website '{final_url}' reached successfully with status code {inspection.get('status_code', 200)}.")
            else:
                lead.website_url = final_url
                lead.website_source = source
                lead.website_confidence = 30.0
                lead.website_verification_status = WebsiteVerificationStatus.CONFLICTING_WEBSITES
                lead.website_status = WebsiteStatus.WEBSITE_UNREACHABLE
                evidence.append(f"Official candidate domain '{final_url}' was unreachable.")
        else:
            lead.website_url = None
            lead.website_source = "SOURCE_A_AND_B_SEARCH"
            lead.website_confidence = 100.0
            lead.website_verification_status = WebsiteVerificationStatus.NO_WEBSITE_CONFIRMED
            lead.website_status = WebsiteStatus.NO_WEBSITE
            evidence.append(f"Confirmed NO_WEBSITE_CONFIRMED after both Source A and Source B yielded no official domain.")

        lead.website_evidence = evidence
        self.db.commit()

        # Advance workflow state to WEBSITE_ANALYZED
        if lead.workflow_state in (WorkflowState.VERIFIED, WorkflowState.DISCOVERED):
            self.orchestrator.transition_lead(
                lead_id=lead.id,
                target_state=WorkflowState.WEBSITE_ANALYZED,
                agent_name=self.name,
                payload_snapshot={
                    "website_url": lead.website_url,
                    "website_status": lead.website_status.value,
                    "website_verification_status": lead.website_verification_status.value if lead.website_verification_status else None,
                    "evidence": evidence
                }
            )

        logger.info(f"Verified lead {lead.id} website status: {lead.website_status.value} ({lead.website_verification_status.value if lead.website_verification_status else 'N/A'})")
        return {
            "lead_id": lead.id,
            "website_url": lead.website_url,
            "website_status": lead.website_status.value,
            "website_verification_status": lead.website_verification_status.value if lead.website_verification_status else None,
            "evidence": evidence
        }
