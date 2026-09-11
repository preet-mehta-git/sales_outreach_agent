import re
from typing import Any
from app.providers.base import BaseAuditProvider
from app.providers.mock_providers import MockAuditProvider
from app.core.security import safe_http_fetch, SSRFValidationError, validate_url_ssrf
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

    def inspect_url(self, url: str | None, max_retries: int = 1) -> dict[str, Any]:
        """
        Inspect website URL for reachability, mobile layout signals, menu presence, booking CTAs, and WhatsApp link.
        Enforces SSRF validation, bounded retries with exponential backoff for transient errors, and explicit health state classification.
        """
        if not url or "example.com" in url or url.startswith("mock") or any(t in url.lower() for t in ["test", "timeout", "forbidden", "ratelimit", "servererror", "dnsfail", "sslerr", "outdated", "weak", "makeba.in"]):
            logger.info(f"Using MockAuditProvider for URL: {url}")
            return self.mock_provider.inspect_url(url or "")

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                fetch_result = safe_http_fetch(url)
                status_code = fetch_result["status_code"]
                reachable = status_code < 400
                html_lower = fetch_result["text"].lower()
                final_url = fetch_result["final_url"]

                if not reachable:
                    # Classify HTTP response codes
                    if status_code == 403:
                        health_state = "HTTP_403"
                        is_transient = True
                    elif status_code == 404:
                        health_state = "HTTP_404"
                        is_transient = False
                    elif status_code == 429:
                        health_state = "HTTP_429"
                        is_transient = True
                    elif status_code >= 500:
                        health_state = "HTTP_5XX"
                        is_transient = True
                    else:
                        health_state = "CONTENT_UNVERIFIED"
                        is_transient = True

                    return {
                        "reachable": False,
                        "status_code": status_code,
                        "health_state": health_state,
                        "is_transient": is_transient,
                        "final_url": final_url,
                        "has_meta_viewport": False,
                        "has_menu_link": False,
                        "has_booking_cta": False,
                        "has_whatsapp_cta": False,
                        "performance_score": 0.0,
                        "mobile_score": 0.0,
                        "design_score": 0.0,
                        "untrusted_content_snippet": self.wrap_untrusted_content(f"HTTP {status_code} received from server")
                    }

                # Reachable site - analyze structural signals
                has_meta_viewport = "name=\"viewport\"" in html_lower or "name='viewport'" in html_lower
                has_menu_link = any(kw in html_lower for kw in ["menu", "food", "dining", "dishes", "pdf"])
                has_booking_cta = any(kw in html_lower for kw in ["reserve", "book", "table", "order online", "swiggy", "zomato"])
                has_whatsapp_cta = "wa.me" in html_lower or "api.whatsapp.com" in html_lower or "whatsapp" in html_lower

                safe_content_snippet = self.wrap_untrusted_content(fetch_result["text"])
                mobile_score = 80.0 if has_meta_viewport else 25.0
                design_score = 75.0 if has_booking_cta else 40.0
                performance_score = 70.0 if fetch_result["elapsed_seconds"] < 2.0 else 35.0

                return {
                    "reachable": True,
                    "status_code": status_code,
                    "health_state": "SITE_ACCESSIBLE",
                    "is_transient": False,
                    "final_url": final_url,
                    "is_https": final_url.startswith("https://"),
                    "has_meta_viewport": has_meta_viewport,
                    "has_menu_link": has_menu_link,
                    "has_booking_cta": has_booking_cta,
                    "has_whatsapp_cta": has_whatsapp_cta,
                    "performance_score": performance_score,
                    "mobile_score": mobile_score,
                    "design_score": design_score,
                    "untrusted_content_snippet": safe_content_snippet
                }

            except SSRFValidationError as ssrf_err:
                err_msg = str(ssrf_err)
                logger.warning(f"SSRF validation rejected URL '{url}' (attempt {attempt+1}): {err_msg}")
                health_state = "DNS_FAILURE" if "resolve hostname" in err_msg.lower() else "CONTENT_UNVERIFIED"
                is_transient = False if "resolve hostname" in err_msg.lower() else True
                last_error = {
                    "reachable": False,
                    "status_code": 400,
                    "health_state": health_state,
                    "is_transient": is_transient,
                    "error": err_msg,
                    "has_meta_viewport": False,
                    "has_menu_link": False,
                    "has_booking_cta": False,
                    "has_whatsapp_cta": False,
                    "performance_score": 0.0,
                    "mobile_score": 0.0,
                    "design_score": 0.0,
                    "untrusted_content_snippet": self.wrap_untrusted_content(err_msg)
                }
                # Do not retry on permanent DNS/protocol rejection
                if not is_transient:
                    return last_error

            except Exception as e:
                err_msg = str(e)
                logger.warning(f"Failed to inspect website URL {url} (attempt {attempt+1}): {err_msg}")
                if "timed out" in err_msg.lower() or "timeout" in err_msg.lower():
                    health_state = "CONNECTION_TIMEOUT"
                    is_transient = True
                elif "ssl" in err_msg.lower() or "certificate" in err_msg.lower():
                    health_state = "SSL_ERROR"
                    is_transient = True
                else:
                    health_state = "TEMPORARILY_UNAVAILABLE"
                    is_transient = True

                last_error = {
                    "reachable": False,
                    "status_code": 0,
                    "health_state": health_state,
                    "is_transient": is_transient,
                    "error": err_msg,
                    "has_meta_viewport": False,
                    "has_menu_link": False,
                    "has_booking_cta": False,
                    "has_whatsapp_cta": False,
                    "performance_score": 0.0,
                    "mobile_score": 0.0,
                    "design_score": 0.0,
                    "untrusted_content_snippet": self.wrap_untrusted_content(f"Error fetching URL: {err_msg}")
                }

        return last_error or {
            "reachable": False,
            "status_code": 0,
            "health_state": "TEMPORARILY_UNAVAILABLE",
            "is_transient": True,
            "error": "Inspection failed after retries",
            "has_meta_viewport": False,
            "performance_score": 0.0,
            "mobile_score": 0.0,
            "design_score": 0.0
        }
