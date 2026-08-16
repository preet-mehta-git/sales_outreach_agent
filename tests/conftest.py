import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.models import Business, Campaign
from app.schemas.enums import WorkflowState, WebsiteStatus, VerificationStatus


@pytest.fixture(scope="function")
def db_session():
    """In-memory SQLite database session for isolated testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_business(db_session):
    """Sample business lead fixture."""
    business = Business(
        name="Makarba Social Cafe",
        category="cafe",
        address="SG Highway, Makarba, Ahmedabad, Gujarat 380051",
        city="Ahmedabad",
        state="Gujarat",
        country="India",
        phone="+91 98765 43210",
        rating=4.6,
        review_count=1250,
        place_id="ch_ahmedabad_001",
        website_status=WebsiteStatus.NO_WEBSITE,
        verification_status=VerificationStatus.VERIFIED,
        workflow_state=WorkflowState.DISCOVERED
    )
    db_session.add(business)
    db_session.commit()
    db_session.refresh(business)
    return business
