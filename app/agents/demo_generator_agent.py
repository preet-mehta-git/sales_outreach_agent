import os
from typing import Any
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState, OutreachStatus
from app.db.models import Business, OutreachDraft
from app.orchestrator.engine import OrchestratorEngine
from app.core.logging import get_logger

logger = get_logger("DemoGeneratorAgent")


class DemoGeneratorAgent(BaseAgent[dict[str, Any]]):
    name = "DemoGeneratorAgent"
    version = "1.0"

    def __init__(self, db: Session, base_static_dir: str = "static/demos"):
        super().__init__()
        self.db = db
        self.base_static_dir = base_static_dir
        self.orchestrator = OrchestratorEngine(self.db)

    def _generate_html(self, lead: Business) -> str:
        clean_phone = (lead.phone or "").replace(" ", "").replace("-", "")
        if clean_phone and not clean_phone.startswith("+"):
            clean_phone = f"+91{clean_phone}"
        wa_link = f"https://wa.me/{clean_phone}?text=Hi%20{lead.name},%20I%20would%20like%20to%20place%20an%20order"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{lead.name} - Authentic {lead.category.title()} in {lead.city}</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Outfit', sans-serif; }}
        body {{ background-color: #0f172a; color: #f8fafc; line-height: 1.6; }}
        header {{ display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 2rem; background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(10px); border-bottom: 1px solid #1e293b; position: sticky; top: 0; z-index: 100; }}
        .logo {{ font-size: 1.5rem; font-weight: 700; color: #f59e0b; }}
        .btn-primary {{ background: linear-gradient(135deg, #f59e0b, #d97706); color: #fff; padding: 0.6rem 1.25rem; border-radius: 8px; text-decoration: none; font-weight: 600; transition: transform 0.2s; display: inline-block; }}
        .btn-primary:hover {{ transform: translateY(-2px); }}
        .btn-whatsapp {{ background: #22c55e; color: #fff; padding: 0.6rem 1.25rem; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block; margin-left: 0.5rem; }}
        .hero {{ text-align: center; padding: 5rem 1rem 4rem; background: radial-gradient(circle at top, #1e293b 0%, #0f172a 100%); }}
        .hero h1 {{ font-size: 3rem; margin-bottom: 1rem; color: #ffffff; }}
        .hero p {{ font-size: 1.25rem; color: #94a3b8; max-width: 600px; margin: 0 auto 2rem; }}
        .badge {{ background: #334155; color: #f59e0b; padding: 0.35rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; margin-bottom: 1rem; display: inline-block; }}
        .menu-section {{ padding: 4rem 2rem; max-width: 1000px; margin: 0 auto; }}
        .menu-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-top: 2rem; }}
        .menu-card {{ background: #1e293b; border-radius: 12px; padding: 1.5rem; border: 1px solid #334155; }}
        .menu-card h3 {{ color: #f8fafc; font-size: 1.2rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; }}
        .price {{ color: #f59e0b; }}
        .menu-card p {{ color: #94a3b8; font-size: 0.9rem; }}
        footer {{ text-align: center; padding: 2rem; border-top: 1px solid #1e293b; color: #64748b; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <header>
        <div class="logo">{lead.name}</div>
        <div>
            <a href="#menu" class="btn-primary">View Menu</a>
            <a href="{wa_link}" target="_blank" class="btn-whatsapp">WhatsApp Order</a>
        </div>
    </header>

    <section class="hero">
        <div class="badge">Top Rated {lead.category.title()} in {lead.city}</div>
        <h1>Welcome to {lead.name}</h1>
        <p>Delicious food, crafted with passion. Located at {lead.address}. Order online or reserve your table instantly!</p>
        <div>
            <a href="{wa_link}" target="_blank" class="btn-whatsapp" style="padding: 0.85rem 1.75rem; font-size: 1.1rem;">Order via WhatsApp</a>
        </div>
    </section>

    <section id="menu" class="menu-section">
        <h2 style="text-align: center; font-size: 2rem; margin-bottom: 0.5rem;">Popular Specials</h2>
        <p style="text-align: center; color: #94a3b8;">Explore our chef's handpicked recommendations</p>
        <div class="menu-grid">
            <div class="menu-card">
                <h3>Special Combo Meal <span class="price">₹349</span></h3>
                <p>Chef's signature dish served with fresh sides and complimentary beverage.</p>
            </div>
            <div class="menu-card">
                <h3>Artisanal Starter <span class="price">₹229</span></h3>
                <p>Crispy, flavorful starter prepared with locally sourced herbs and spices.</p>
            </div>
            <div class="menu-card">
                <h3>House Dessert Delight <span class="price">₹179</span></h3>
                <p>Decadent dessert crafted daily for the perfect sweet finish.</p>
            </div>
        </div>
    </section>

    <footer>
        <p>&copy; {lead.name} | {lead.address}, {lead.city}. Phone: {lead.phone or 'N/A'}</p>
        <p style="margin-top: 0.5rem; font-size: 0.8rem; color: #475569;">Demo Landing Page Generated for Prospecting Assessment</p>
    </footer>
</body>
</html>"""

    def run(self, input_data: AgentInput) -> dict[str, Any]:
        lead = self.db.query(Business).filter(Business.id == input_data.lead_id).first()
        if not lead:
            raise ValueError(f"Business lead with ID {input_data.lead_id} not found.")

        # Create output directory static/demos/{lead_id}
        demo_dir = os.path.join(self.base_static_dir, lead.id)
        os.makedirs(demo_dir, exist_ok=True)

        # Write index.html file
        html_content = self._generate_html(lead)
        file_path = os.path.join(demo_dir, "index.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        demo_url = f"/static/demos/{lead.id}/index.html"

        # Create or update OutreachDraft record
        draft = self.db.query(OutreachDraft).filter(OutreachDraft.business_id == lead.id).first()
        if not draft:
            draft = OutreachDraft(
                business_id=lead.id,
                demo_url=demo_url,
                status=OutreachStatus.AWAITING_APPROVAL
            )
            self.db.add(draft)
        else:
            draft.demo_url = demo_url

        self.db.commit()
        self.db.refresh(draft)

        # Advance state BUSINESS_AUDITED -> DEMO_GENERATED via Orchestrator
        if lead.workflow_state == WorkflowState.BUSINESS_AUDITED:
            self.orchestrator.transition_lead(
                lead_id=lead.id,
                target_state=WorkflowState.DEMO_GENERATED,
                agent_name=self.name,
                payload_snapshot={
                    "demo_url": demo_url,
                    "file_path": file_path
                }
            )

        logger.info(f"DemoGeneratorAgent generated prototype for lead {lead.id}: {demo_url}")
        return {
            "lead_id": lead.id,
            "demo_url": demo_url,
            "file_path": file_path,
            "draft_id": draft.id
        }
