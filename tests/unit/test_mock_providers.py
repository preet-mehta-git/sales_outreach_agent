from app.providers.mock_providers import MockPlacesProvider, MockAuditProvider
from app.core.audit import AuditService
from app.db.models import AuditLog


def test_mock_places_provider():
    provider = MockPlacesProvider()
    results = provider.search_places("cafe", "Ahmedabad")
    assert len(results) > 0
    assert results[0]["city"] == "Ahmedabad"
    assert "place_id" in results[0]


def test_mock_audit_provider():
    provider = MockAuditProvider()
    res = provider.inspect_url("http://vastrapurheritagedining.example.com")
    assert res["reachable"] is True
    assert "performance_score" in res


def test_audit_service_recording(db_session, sample_business):
    log_entry = AuditService.record_transition(
        db=db_session,
        business_id=sample_business.id,
        action="TEST_ACTION",
        from_state="DISCOVERED",
        to_state="VERIFIED",
        agent_name="TestAgent",
        payload_snapshot={"test": "data"}
    )
    assert log_entry.id is not None
    assert log_entry.business_id == sample_business.id
    assert log_entry.action == "TEST_ACTION"

    # Query from DB
    retrieved_log = db_session.query(AuditLog).filter(AuditLog.id == log_entry.id).first()
    assert retrieved_log is not None
    assert retrieved_log.agent_name == "TestAgent"
