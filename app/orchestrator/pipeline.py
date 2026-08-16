import uuid
from typing import Any
from sqlalchemy.orm import Session

from app.schemas.agent import AgentInput
from app.db.models import Campaign, Business
from app.schemas.enums import WorkflowState
from app.agents.discovery_agent import DiscoveryAgent
from app.agents.website_verifier_agent import WebsiteVerifierAgent
from app.agents.website_audit_agent import WebsiteAuditAgent
from app.agents.opportunity_scorer_agent import OpportunityScorerAgent
from app.agents.qualification_agent import QualificationAgent
from app.agents.contact_discovery_agent import ContactDiscoveryAgent
from app.agents.business_audit_agent import BusinessAuditAgent
from app.agents.demo_generator_agent import DemoGeneratorAgent
from app.agents.outreach_agent import OutreachAgent
from app.core.logging import get_logger

logger = get_logger("CampaignPipelineRunner")


class CampaignPipelineRunner:
    def __init__(self, db: Session):
        self.db = db
        self.verifier = WebsiteVerifierAgent(self.db)
        self.web_auditor = WebsiteAuditAgent(self.db)
        self.scorer = OpportunityScorerAgent(self.db)
        self.qualifier = QualificationAgent(self.db)
        self.contact_finder = ContactDiscoveryAgent(self.db)
        self.biz_auditor = BusinessAuditAgent(self.db)
        self.demo_gen = DemoGeneratorAgent(self.db)
        self.outreach_gen = OutreachAgent(self.db)

    def run_lead_pipeline(self, lead: Business, workflow_run_id: str | None = None) -> dict[str, Any]:
        run_id = workflow_run_id or str(uuid.uuid4())
        inp = AgentInput(lead_id=lead.id, workflow_run_id=run_id)

        # Step 2: Verification
        self.verifier.execute(inp)

        # Step 3: Website Audit
        self.web_auditor.execute(inp)

        # Step 4: Scoring
        self.scorer.execute(inp)

        # Step 5: Qualification
        qual_out = self.qualifier.execute(inp)
        if not qual_out.success or not qual_out.data.get("qualified"):
            return {"status": "REJECTED", "qualified": False, "run_id": run_id}

        # Step 6: Contact Discovery
        self.contact_finder.execute(inp)

        # Step 7: Business Audit
        self.biz_auditor.execute(inp)

        # Step 8: Demo Generation
        self.demo_gen.execute(inp)

        # Step 9: Outreach Draft Generation
        outreach_out = self.outreach_gen.execute(inp)

        return {"status": "COMPLETED", "qualified": True, "run_id": run_id, "outreach": outreach_out.data}

    def run_pipeline_for_campaign(self, campaign_id: str, query: str = "restaurants in Ahmedabad") -> dict[str, Any]:
        campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found.")

        workflow_run_id = str(uuid.uuid4())
        logger.info(f"Starting Campaign Pipeline for campaign '{campaign.name}' (Run ID: {workflow_run_id})")

        # Step 1: Discovery Phase
        discovery_agent = DiscoveryAgent(self.db)
        discovery_input = AgentInput(
            campaign_id=campaign.id,
            workflow_run_id=workflow_run_id,
            custom_params={"query": query, "location": campaign.city}
        )
        disc_res = discovery_agent.execute(discovery_input)
        if not disc_res.success:
            return {"status": "FAILED", "stage": "DISCOVERY", "errors": disc_res.errors}

        discovered_leads = self.db.query(Business).filter(Business.campaign_id == campaign.id).all()
        summary_stats = {
            "campaign_id": campaign.id,
            "total_ingested": len(discovered_leads),
            "qualified": 0,
            "rejected": 0,
            "drafts_created": 0
        }

        for lead in discovered_leads:
            res = self.run_lead_pipeline(lead, workflow_run_id=workflow_run_id)
            if res.get("qualified"):
                summary_stats["qualified"] += 1
                summary_stats["drafts_created"] += 1
            else:
                summary_stats["rejected"] += 1

        logger.info(f"Campaign Pipeline completed for '{campaign.name}': {summary_stats}")
        return {
            "status": "COMPLETED",
            "run_id": workflow_run_id,
            "summary": summary_stats
        }
