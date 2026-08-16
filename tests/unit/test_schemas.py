import pytest
from pydantic import ValidationError
from app.schemas.lead import BusinessCreate, Provenance
from app.schemas.enums import ConfidenceLevel, VerificationStatus


def test_business_create_schema_valid():
    lead_data = BusinessCreate(
        name="Vastrapur Bistro",
        category="restaurant",
        address="Near Vastrapur Lake",
        city="Ahmedabad",
        rating=4.5,
        review_count=350
    )
    assert lead_data.name == "Vastrapur Bistro"
    assert lead_data.city == "Ahmedabad"
    assert lead_data.rating == 4.5


def test_business_create_invalid_rating():
    with pytest.raises(ValidationError):
        BusinessCreate(
            name="Invalid Rating Cafe",
            category="cafe",
            address="CG Road",
            rating=6.0  # Must be <= 5.0
        )


def test_provenance_schema():
    provenance = Provenance(
        field="phone",
        value="+91 98765 00000",
        source="Google Places API",
        confidence=ConfidenceLevel.HIGH,
        verification_status=VerificationStatus.VERIFIED
    )
    assert provenance.source == "Google Places API"
    assert provenance.confidence == ConfidenceLevel.HIGH
