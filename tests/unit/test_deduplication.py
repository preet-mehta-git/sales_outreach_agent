from app.schemas.lead import BusinessCreate
from app.services.lead_service import LeadService
from app.services.deduplication import DeduplicationEngine


def test_deduplication_by_place_id(db_session):
    lead1 = BusinessCreate(
        name="Makarba Cafe",
        category="cafe",
        address="SG Highway",
        place_id="place_123"
    )
    LeadService.create_lead(db_session, lead1)

    lead2 = BusinessCreate(
        name="Different Name Cafe",
        category="cafe",
        address="Different Address",
        place_id="place_123"  # Same place_id
    )

    duplicate = DeduplicationEngine.find_duplicate(db_session, lead2)
    assert duplicate is not None
    assert duplicate.place_id == "place_123"


def test_deduplication_by_phone(db_session):
    lead1 = BusinessCreate(
        name="Vastrapur Diner",
        category="restaurant",
        address="Vastrapur",
        phone="+91 98765 43210"
    )
    LeadService.create_lead(db_session, lead1)

    lead2 = BusinessCreate(
        name="Vastrapur Lake Restaurant",
        category="restaurant",
        address="Near Lake",
        phone="9876543210"  # Same normalized digits
    )

    duplicate = DeduplicationEngine.find_duplicate(db_session, lead2)
    assert duplicate is not None


def test_deduplication_by_domain(db_session):
    lead1 = BusinessCreate(
        name="CG Road Cafe",
        category="cafe",
        address="CG Road",
        website_url="https://www.cgroadcafe.com/menu"
    )
    LeadService.create_lead(db_session, lead1)

    lead2 = BusinessCreate(
        name="New CG Cafe",
        category="cafe",
        address="Navrangpura",
        website_url="http://cgroadcafe.com"  # Same canonical domain
    )

    duplicate = DeduplicationEngine.find_duplicate(db_session, lead2)
    assert duplicate is not None


def test_deduplication_by_name_and_city(db_session):
    lead1 = BusinessCreate(
        name="The Heritage Kitchen & Cafe!",
        category="restaurant",
        address="Bodakdev",
        city="Ahmedabad"
    )
    LeadService.create_lead(db_session, lead1)

    lead2 = BusinessCreate(
        name="the heritage kitchen   cafe",  # Normalized match
        category="restaurant",
        address="New Address",
        city="AHMEDABAD"
    )

    duplicate = DeduplicationEngine.find_duplicate(db_session, lead2)
    assert duplicate is not None
