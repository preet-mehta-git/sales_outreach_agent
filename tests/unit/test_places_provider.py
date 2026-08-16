from datetime import datetime, timedelta, timezone
from app.providers.places_provider import GooglePlacesProvider
from app.db.models import Business, AuditLog
from app.schemas.enums import WorkflowState


def test_places_provider_mock_fallback():
    provider = GooglePlacesProvider(api_key="mock_key")
    results = provider.search_places("cafe", "Ahmedabad", limit=2)
    assert len(results) == 2
    assert results[0]["city"] == "Ahmedabad"

    details = provider.get_place_details("ch_ahmedabad_001")
    assert details["place_id"] == "ch_ahmedabad_001"
    assert "name" in details


def test_purge_expired_cache_policy(db_session):
    # Add older record (> 30 days)
    old_date = datetime.now(timezone.utc) - timedelta(days=35)
    old_lead = Business(
        name="Old Cached Cafe",
        category="cafe",
        address="Old Address",
        city="Ahmedabad",
        place_id="old_place_999",
        workflow_state=WorkflowState.VERIFIED,
        created_at=old_date
    )
    db_session.add(old_lead)
    db_session.commit()

    # Execute cache purge check
    purged_count = GooglePlacesProvider.purge_expired_cache(db_session, max_age_days=30)
    assert purged_count == 1

    # Verify audit log recorded for cache purge
    audit_logs = db_session.query(AuditLog).filter(AuditLog.action == "GOOGLE_PLACES_CACHE_PURGED").all()
    assert len(audit_logs) == 1
    assert audit_logs[0].business_id == old_lead.id
