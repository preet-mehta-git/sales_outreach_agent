import re
from typing import Any
import httpx
from app.providers.base import BaseAuditProvider
from app.providers.mock_providers import MockAuditProvider
from app.core.logging import get_logger

logger = get_logger("AuditProvider")


class AuditProvider(BaseAuditProvider):
    def __init__(self):
        self.mock_provider = MockAuditProvider()

    @staticmethod
    def wrap_untrusted_content(content: str) -> str:
        """
        Isolate untrusted external website content inside XML tags (Rule 18 / Prompt Injection Defense).
        """
        clean_content = content.replace("<untrusted_external_content>", "").replace("</untrusted_external_content>", "")
        return f"<untrusted_external_content>\n{clean_content[:5000]}\n</untrusted_external_content>"

    def inspect_url(self, url: str | None) -> dict[str, Any]:
        """
        Inspect website URL for reachability, mobile layout signals, menu presence, booking CTAs, and WhatsApp link.
        """
        if not url or "example.com" in url or url.startswith("mock"):
            logger.info(f"Using MockAuditProvider for URL: {url}")
            return self.mock_provider.inspect_url(url or "")

        if not url.startswith(("http://", "https://")):
            url = f"http://{url}"

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            with httpx.Client(timeout=8.0, follow_redirects=True, headers=headers) as client:
                resp = client.get(url)

            reachable = resp.status_code < 400
            html_lower = resp.text.lower()

            # Analyze structural signals
            has_meta_viewport = "name=\"viewport\"" in html_lower or "name='viewport'" in html_lower
            has_menu_link = any(kw in html_lower for kw in ["menu", "food", "dining", "dishes", "pdf"])
            has_booking_cta = any(kw in html_lower for kw in ["reserve", "book", "table", "order online", "swiggy", "zomato"])
            has_whatsapp_cta = "wa.me" in html_lower or "api.whatsapp.com" in html_lower or "whatsapp" in html_lower

            # Wrap content safely against prompt injection
            safe_content_snippet = self.wrap_untrusted_content(resp.text)

            # Score estimates
            mobile_score = 80.0 if has_meta_viewport else 25.0
            design_score = 75.0 if has_booking_cta else 40.0
            performance_score = 70.0 if resp.elapsed.total_seconds() < 2.0 else 35.0

            return {
                "reachable": reachable,
                "status_code": resp.status_code,
                "final_url": str(resp.url),
                "is_https": str(resp.url).startswith("https://"),
                "has_meta_viewport": has_meta_viewport,
                "has_menu_link": has_menu_link,
                "has_booking_cta": has_booking_cta,
                "has_whatsapp_cta": has_whatsapp_cta,
                "performance_score": performance_score,
                "mobile_score": mobile_score,
                "design_score": design_score,
                "untrusted_content_snippet": safe_content_snippet
            }

        except Exception as e:
            logger.warning(f"Failed to inspect website URL {url}: {str(e)}")
            return {
                "reachable": False,
                "status_code": 0,
                "error": str(e),
                "has_meta_viewport": False,
                "has_menu_link": False,
                "has_booking_cta": False,
                "has_whatsapp_cta": False,
                "performance_score": 0.0,
                "mobile_score": 0.0,
                "design_score": 0.0,
                "untrusted_content_snippet": self.wrap_untrusted_content(f"Error fetching URL: {str(e)}")
            }
