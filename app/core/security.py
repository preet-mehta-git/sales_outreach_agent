import ipaddress
import socket
import urllib.parse
from typing import Any
import httpx

from app.core.logging import get_logger

logger = get_logger("Security")


class SSRFValidationError(ValueError):
    """Raised when a URL fails SSRF safety validation."""
    pass


def validate_url_ssrf(url: str) -> str:
    """
    Validates a target URL against SSRF vulnerabilities.
    
    Checks:
    - Allowed protocols: http, https
    - Hostname presence & localhost rejection
    - DNS resolution of all IP addresses
    - Rejection of loopback, private IPv4/IPv6, link-local, multicast, reserved, unspecified, and cloud metadata IPs.
    
    Returns normalized URL or raises SSRFValidationError.
    """
    if not url or not isinstance(url, str):
        raise SSRFValidationError("REQUEST_REJECTED: Invalid or empty URL provided.")

    url_clean = url.strip()
    if not url_clean.startswith(("http://", "https://")):
        url_clean = f"http://{url_clean}"

    parsed = urllib.parse.urlparse(url_clean)

    # 1. Scheme check
    if parsed.scheme.lower() not in ("http", "https"):
        raise SSRFValidationError(f"REQUEST_REJECTED: Unsupported protocol '{parsed.scheme}'. Only http and https are allowed.")

    # 2. Hostname presence check
    hostname = parsed.hostname
    if not hostname:
        raise SSRFValidationError("REQUEST_REJECTED: Missing target hostname.")

    hostname_lower = hostname.lower().strip()

    # 3. Explicit localhost string check
    if hostname_lower == "localhost" or hostname_lower.endswith(".localhost"):
        raise SSRFValidationError("REQUEST_REJECTED: Requests to 'localhost' are blocked.")

    # 4. Resolve DNS and validate IP addresses
    try:
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as e:
        raise SSRFValidationError(f"REQUEST_REJECTED: Unable to resolve hostname '{hostname}': {str(e)}")

    if not addr_info:
        raise SSRFValidationError(f"REQUEST_REJECTED: Hostname '{hostname}' resolved to no valid IP addresses.")

    resolved_ips = set()
    for item in addr_info:
        ip_str = item[4][0]
        resolved_ips.add(ip_str)

    for ip_str in resolved_ips:
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            raise SSRFValidationError(f"REQUEST_REJECTED: Invalid IP address format '{ip_str}'.")

        # Check IP ranges
        if ip.is_loopback:
            raise SSRFValidationError(f"REQUEST_REJECTED: IP address '{ip_str}' is a loopback address.")
        if ip.is_private:
            raise SSRFValidationError(f"REQUEST_REJECTED: IP address '{ip_str}' is a private network address.")
        if ip.is_link_local:
            raise SSRFValidationError(f"REQUEST_REJECTED: IP address '{ip_str}' is a link-local address.")
        if ip.is_multicast:
            raise SSRFValidationError(f"REQUEST_REJECTED: IP address '{ip_str}' is a multicast address.")
        if ip.is_reserved:
            raise SSRFValidationError(f"REQUEST_REJECTED: IP address '{ip_str}' is a reserved address.")
        if ip.is_unspecified:
            raise SSRFValidationError(f"REQUEST_REJECTED: IP address '{ip_str}' is an unspecified address.")

        # Special Cloud Metadata IPs check (e.g. AWS/GCP/Azure 169.254.169.254, 169.254.169.250, 169.254.170.2)
        if str(ip) in ("169.254.169.254", "169.254.169.250", "169.254.170.2"):
            raise SSRFValidationError(f"REQUEST_REJECTED: IP address '{ip_str}' is a cloud metadata endpoint.")

    return url_clean


def safe_http_fetch(
    url: str,
    max_redirects: int = 3,
    timeout_seconds: float = 8.0,
    max_size_bytes: int = 2 * 1024 * 1024
) -> dict[str, Any]:
    """
    Safely fetches external HTTP/HTTPS content enforcing SSRF protections:
    - Initial URL SSRF validation
    - Manual redirect re-validation loop up to max_redirects
    - Strict connection/read timeouts
    - Response body size limit enforcement
    
    Returns dict with status_code, final_url, text, elapsed_seconds, headers.
    """
    current_url = validate_url_ssrf(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    redirect_count = 0
    timeout_config = httpx.Timeout(timeout_seconds, connect=4.0)

    with httpx.Client(timeout=timeout_config, follow_redirects=False, headers=headers) as client:
        while True:
            try:
                resp = client.get(current_url)
            except httpx.RequestError as exc:
                raise SSRFValidationError(f"REQUEST_REJECTED: HTTP request error to '{current_url}': {str(exc)}")

            # Handle Redirects manually to re-validate destination URL against SSRF rules
            if resp.status_code in (301, 302, 303, 307, 308):
                redirect_count += 1
                if redirect_count > max_redirects:
                    raise SSRFValidationError(f"REQUEST_REJECTED: Exceeded maximum allowed redirects ({max_redirects}).")

                location = resp.headers.get("Location")
                if not location:
                    raise SSRFValidationError("REQUEST_REJECTED: Redirect response missing Location header.")

                # Resolve relative redirect URLs
                next_url = urllib.parse.urljoin(current_url, location)
                # Revalidate new redirect URL against SSRF policy
                current_url = validate_url_ssrf(next_url)
                continue

            # Read content with max size limit
            content_bytes = resp.content
            if len(content_bytes) > max_size_bytes:
                content_bytes = content_bytes[:max_size_bytes]

            try:
                text_content = content_bytes.decode(resp.encoding or "utf-8", errors="replace")
            except Exception:
                text_content = content_bytes.decode("utf-8", errors="replace")

            return {
                "status_code": resp.status_code,
                "final_url": current_url,
                "text": text_content,
                "elapsed_seconds": resp.elapsed.total_seconds(),
                "headers": dict(resp.headers)
            }
