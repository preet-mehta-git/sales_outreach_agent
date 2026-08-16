import pytest
from app.core.security import validate_url_ssrf, SSRFValidationError, safe_http_fetch
from app.providers.audit_provider import AuditProvider


def test_ssrf_blocks_localhost():
    with pytest.raises(SSRFValidationError) as excinfo:
        validate_url_ssrf("http://localhost:8000/admin")
    assert "REQUEST_REJECTED" in str(excinfo.value)
    assert "localhost" in str(excinfo.value).lower()


def test_ssrf_blocks_loopback_ipv4():
    with pytest.raises(SSRFValidationError) as excinfo:
        validate_url_ssrf("http://127.0.0.1/metadata")
    assert "REQUEST_REJECTED" in str(excinfo.value)
    assert "loopback" in str(excinfo.value).lower()


def test_ssrf_blocks_cloud_metadata():
    with pytest.raises(SSRFValidationError) as excinfo:
        validate_url_ssrf("http://169.254.169.254/latest/meta-data/")
    assert "REQUEST_REJECTED" in str(excinfo.value)


def test_ssrf_blocks_rfc1918_private_ips():
    private_ips = ["http://10.0.0.1", "http://192.168.1.1", "http://172.16.0.1"]
    for url in private_ips:
        with pytest.raises(SSRFValidationError) as excinfo:
            validate_url_ssrf(url)
        assert "REQUEST_REJECTED" in str(excinfo.value)
        assert "private" in str(excinfo.value).lower() or "loopback" in str(excinfo.value).lower()


def test_ssrf_blocks_ipv6_loopback():
    with pytest.raises(SSRFValidationError) as excinfo:
        validate_url_ssrf("http://[::1]:8080/")
    assert "REQUEST_REJECTED" in str(excinfo.value)


def test_ssrf_blocks_unsupported_protocols():
    protocols = ["ftp://example.com/file", "file:///etc/passwd", "gopher://example.com"]
    for url in protocols:
        with pytest.raises(SSRFValidationError) as excinfo:
            validate_url_ssrf(url)
        assert "REQUEST_REJECTED" in str(excinfo.value)


def test_audit_provider_rejects_ssrf_url():
    provider = AuditProvider()
    res = provider.inspect_url("http://127.0.0.1:8000/secret")
    assert res["reachable"] is False
    assert res["status_code"] == 400
    assert "REQUEST_REJECTED" in res["error"]


def test_audit_provider_allows_mock_urls():
    provider = AuditProvider()
    res = provider.inspect_url("http://example.com/restaurant")
    assert res["status_code"] == 200
    assert "reachable" in res
