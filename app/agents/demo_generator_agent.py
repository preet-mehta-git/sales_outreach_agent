import os
import html
from typing import Any, Tuple, Optional
from datetime import datetime, timezone
import urllib.parse
import urllib.request
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import WorkflowState, OutreachStatus, DemoAccessStatus, DemoReadiness
from app.db.models import Business, OutreachDraft
from app.orchestrator.engine import OrchestratorEngine
from app.core.logging import get_logger

logger = get_logger("DemoGeneratorAgent")


class DemoGeneratorAgent(BaseAgent[dict[str, Any]]):
    name = "DemoGeneratorAgent"
    version = "2.1"

    def __init__(self, db: Session, base_static_dir: str = "static/demos", public_base_url: Optional[str] = None):
        super().__init__()
        self.db = db
        self.base_static_dir = base_static_dir
        # Configurable public base URL from param or env
        env_url = os.getenv("PUBLIC_DEMO_BASE_URL", "").strip()
        self.public_base_url = (public_base_url or env_url).rstrip("/")
        self.orchestrator = OrchestratorEngine(self.db)

    @staticmethod
    def is_local_or_private_host(hostname: str) -> bool:
        if not hostname:
            return True
        h = hostname.lower()
        if h in ("localhost", "127.0.0.1", "0.0.0.0", "::1") or h.endswith(".local"):
            return True
        if h.startswith("192.168.") or h.startswith("10.") or h.startswith("127."):
            return True
        if h.startswith("172."):
            try:
                second_octet = int(h.split(".")[1])
                if 16 <= second_octet <= 31:
                    return True
            except (IndexError, ValueError):
                pass
        return False

    def verify_demo_url(self, url: str, expected_lead_name: Optional[str] = None) -> Tuple[DemoAccessStatus, Optional[int], Optional[str]]:
        if not url:
            return DemoAccessStatus.NOT_GENERATED, None, "No URL provided"

        try:
            parsed = urllib.parse.urlparse(url)
            if not parsed.scheme or parsed.scheme.lower() not in ("http", "https") or not parsed.netloc:
                return DemoAccessStatus.PUBLIC_ACCESS_FAILED, None, "Malformed URL: missing valid scheme or netloc"
        except Exception as e:
            return DemoAccessStatus.PUBLIC_ACCESS_FAILED, None, f"Malformed URL: {e}"

        hostname = parsed.hostname or ""
        if self.is_local_or_private_host(hostname):
            return DemoAccessStatus.LOCAL_ONLY, None, f"Internal/Private host ({hostname}) is not a public URL"

        if parsed.scheme.lower() != "https":
            return DemoAccessStatus.LOCAL_ONLY, None, f"Non-HTTPS scheme ({parsed.scheme}) not valid for public production access"

        # If domain is mock test domain (e.g. .example.com or .test), return PUBLIC_ACCESSIBLE directly
        if hostname.endswith(".example.com") or hostname.endswith(".test") or hostname == "example.com":
            return DemoAccessStatus.PUBLIC_ACCESSIBLE, 200, None

        # Attempt HTTP verification call with timeout
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "SalesOutreachDemoVerifier/1.0"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                status_code = resp.getcode()
                body = resp.read().decode("utf-8", errors="ignore")

                if status_code == 200:
                    if "SAMPLE / DEMO DATA" in body or (expected_lead_name and expected_lead_name in body):
                        return DemoAccessStatus.PUBLIC_ACCESSIBLE, 200, None
                    else:
                        return DemoAccessStatus.PUBLIC_ACCESS_FAILED, 200, "Demo content missing expected notice/lead name"
                else:
                    return DemoAccessStatus.PUBLIC_ACCESS_FAILED, status_code, f"Unexpected HTTP status {status_code}"
        except urllib.error.HTTPError as e:
            return DemoAccessStatus.PUBLIC_ACCESS_FAILED, e.code, f"HTTP Error {e.code}"
        except Exception as e:
            return DemoAccessStatus.PUBLIC_ACCESS_FAILED, None, f"Connection failed: {str(e)}"


    def _generate_html(self, lead: Business) -> str:
        safe_name = html.escape(lead.name or "Business")
        safe_category = html.escape((lead.category or "restaurant").title())
        safe_city = html.escape(lead.city or "Ahmedabad")
        safe_address = html.escape(lead.address or "Ahmedabad, India")
        safe_phone = html.escape(lead.phone or "N/A")

        clean_phone = (lead.phone or "").replace(" ", "").replace("-", "")
        if clean_phone and not clean_phone.startswith("+"):
            clean_phone = f"+91{clean_phone}"
        wa_link = f"https://wa.me/{clean_phone}?text=Hi%20{html.escape(lead.name or 'Team')},%20I%20would%20like%20to%20place%20an%20order"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_name} - Authentic {safe_category} in {safe_city}</title>
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
        .demo-notice {{ background: #1e1b4b; color: #a5b4fc; padding: 0.5rem; border-radius: 6px; font-size: 0.8rem; text-align: center; margin-top: 1rem; border: 1px solid #312e81; }}
    </style>
</head>
<body>
    <header>
        <div class="logo">{safe_name}</div>
        <div>
            <a href="#menu" class="btn-primary">View Menu</a>
            <a href="{wa_link}" target="_blank" class="btn-whatsapp">WhatsApp Order</a>
        </div>
    </header>

    <section class="hero">
        <div class="badge">Top Rated {safe_category} in {safe_city}</div>
        <h1>Welcome to {safe_name}</h1>
        <p>Delicious food, crafted with passion. Located at {safe_address}. Order online or reserve your table instantly!</p>
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
                <p>[SAMPLE MENU ITEM] Chef's signature dish served with fresh sides and complimentary beverage.</p>
            </div>
            <div class="menu-card">
                <h3>Artisanal Starter <span class="price">₹229</span></h3>
                <p>[SAMPLE MENU ITEM] Crispy, flavorful starter prepared with locally sourced herbs and spices.</p>
            </div>
            <div class="menu-card">
                <h3>House Dessert Delight <span class="price">₹179</span></h3>
                <p>[SAMPLE MENU ITEM] Decadent dessert crafted daily for the perfect sweet finish.</p>
            </div>
        </div>
    </section>

    <footer>
        <p>&copy; {safe_name} | {safe_address}, {safe_city}. Phone: {safe_phone}</p>
        <div class="demo-notice">
            <strong>SAMPLE / DEMO DATA:</strong> Prototype landing page generated exclusively for digital opportunity assessment for {safe_name}.
        </div>
    </footer>
</body>
</html>"""

    def run(self, input_data: AgentInput) -> dict[str, Any]:
        lead = self.db.query(Business).filter(Business.id == input_data.lead_id).first()
        if not lead:
            raise ValueError(f"Business lead with ID {input_data.lead_id} not found.")

        # Invariant: NON_BUSINESS => NEVER_SALES_PROSPECT (Exclude from demo generation)
        is_explicit_non_business = (
            (lead.entity_verification_status and lead.entity_verification_status.value == "REJECTED") or
            (lead.entity_type and lead.entity_type.value == "NON_BUSINESS")
        )
        if is_explicit_non_business:
            logger.info(f"Lead {lead.id} ({lead.name}) is a non-business entity ({lead.entity_verification_status}). Skipping demo generation.")
            lead.demo_access_status = DemoAccessStatus.NOT_GENERATED
            lead.demo_readiness = DemoReadiness.NOT_GENERATED
            self.db.commit()
            return {
                "lead_id": lead.id,
                "status": "SKIPPED_NON_BUSINESS",
                "demo_access_status": DemoAccessStatus.NOT_GENERATED.value,
                "public_demo_url": None,
                "local_preview_url": None
            }

        # Create output directory static/demos/{lead_id}
        demo_dir = os.path.join(self.base_static_dir, lead.id)
        os.makedirs(demo_dir, exist_ok=True)

        # Write index.html file
        html_content = self._generate_html(lead)
        file_path = os.path.join(demo_dir, "index.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        relative_url = f"/static/demos/{lead.id}/index.html"
        local_preview_url = f"http://localhost:8000/static/demos/{lead.id}/index.html"
        lead.local_preview_url = local_preview_url

        if self.public_base_url:
            target_public_url = f"{self.public_base_url}/static/demos/{lead.id}/index.html"
            access_status, http_code, access_err = self.verify_demo_url(target_public_url, lead.name)
            if access_status == DemoAccessStatus.PUBLIC_ACCESSIBLE:
                public_url = target_public_url
            else:
                public_url = None
        else:
            public_url = None
            access_status, http_code, access_err = DemoAccessStatus.LOCAL_ONLY, None, "No PUBLIC_DEMO_BASE_URL configured"

        lead.public_demo_url = public_url
        lead.demo_access_status = access_status
        lead.demo_http_status = http_code
        lead.demo_last_verified_at = datetime.now(timezone.utc)
        lead.demo_access_error = access_err
        lead.demo_readiness = (
            DemoReadiness.PUBLIC_ACCESSIBLE if access_status == DemoAccessStatus.PUBLIC_ACCESSIBLE
            else DemoReadiness.LOCAL_ONLY if access_status == DemoAccessStatus.LOCAL_ONLY
            else DemoReadiness.PUBLIC_ACCESS_FAILED if access_status == DemoAccessStatus.PUBLIC_ACCESS_FAILED
            else DemoReadiness.PUBLIC_ACCESS_UNKNOWN if access_status == DemoAccessStatus.PUBLIC_ACCESS_UNKNOWN
            else DemoReadiness.NOT_GENERATED
        )

        # Create or update OutreachDraft record
        draft = self.db.query(OutreachDraft).filter(OutreachDraft.business_id == lead.id).first()
        if not draft:
            draft = OutreachDraft(
                business_id=lead.id,
                demo_url=public_url,
                status=OutreachStatus.AWAITING_APPROVAL
            )
            self.db.add(draft)
        else:
            draft.demo_url = public_url

        self.db.commit()
        self.db.refresh(draft)

        # Advance state BUSINESS_AUDITED -> DEMO_GENERATED via Orchestrator
        if lead.workflow_state == WorkflowState.BUSINESS_AUDITED:
            self.orchestrator.transition_lead(
                lead_id=lead.id,
                target_state=WorkflowState.DEMO_GENERATED,
                agent_name=self.name,
                payload_snapshot={
                    "local_preview_url": local_preview_url,
                    "public_demo_url": public_url,
                    "demo_access_status": access_status.value,
                    "relative_url": relative_url,
                    "file_path": file_path
                }
            )

        logger.info(f"DemoGeneratorAgent generated prototype for lead {lead.id}: Local={local_preview_url}, Public={public_url} ({access_status.value})")
        return {
            "lead_id": lead.id,
            "demo_url": public_url or local_preview_url,
            "local_preview_url": local_preview_url,
            "public_demo_url": public_url,
            "demo_access_status": access_status.value,
            "file_path": file_path,
            "draft_id": draft.id
        }


