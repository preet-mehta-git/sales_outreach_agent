from datetime import datetime, timedelta, timezone
from app.db.session import SessionLocal, engine
from app.db.models import Base, Business, AuditLog
from app.services.cache_purger import CachePurgerService
from app.providers.places_provider import GooglePlacesProvider

Base.metadata.create_all(bind=engine)


def test_places_cache_purge_retains_place_id(db_session):
    # Create business created 35 days ago
    old_date = datetime.now(timezone.utc) - timedelta(days=35)
    biz = Business(
        name="Old Place Cafe",
        category="cafe",
        address="SG Highway",
        city="Ahmedabad",
        place_id="ch_old_place_123",
        created_at=old_date
    )
    db_session.add(biz)
    db_session.commit()

    res = CachePurgerService.run_compliance_purge(db_session, max_age_days=30)
    assert res["records_processed"] >= 1

    # Place ID must be retained
    db_session.refresh(biz)
    assert biz.place_id == "ch_old_place_123"

    # Audit log created
    audit = db_session.query(AuditLog).filter_by(business_id=biz.id, action="GOOGLE_PLACES_30DAY_COMPLIANCE_PURGE").first()
    assert audit is not None


def test_places_provider_purge_helper(db_session):
    old_date = datetime.now(timezone.utc) - timedelta(days=40)
    biz = Business(
        name="Ancient Diner",
        category="diner",
        address="Navrangpura",
        city="Ahmedabad",
        place_id="ch_ancient_456",
        created_at=old_date
    )
    db_session.add(biz)
    db_session.commit()

    purged = GooglePlacesProvider.purge_expired_cache(db_session, max_age_days=30)
    assert purged >= 1
