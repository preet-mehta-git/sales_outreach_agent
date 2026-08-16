from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.enums import WorkflowState, WebsiteStatus, VerificationStatus, ConfidenceLevel


class Provenance(BaseModel):
    field: str
    value: str | None = None
    source: str
    source_ref: str | None = None
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    verification_status: VerificationStatus = VerificationStatus.VERIFIED


class BusinessCreate(BaseModel):
    name: str
    category: str  # e.g., "restaurant", "cafe", "fine_dining", "bakery"
    address: str
    city: str = "Ahmedabad"
    state: str = "Gujarat"
    country: str = "India"
    phone: str | None = None
    email: str | None = None
    place_id: str | None = None
    rating: float | None = Field(default=None, ge=0.0, le=5.0)
    review_count: int | None = Field(default=None, ge=0)
    website_url: str | None = None
    source_name: str = "Google Places API"


class DecisionMakerInfo(BaseModel):
    name: str | None = None
    title: str | None = None  # e.g. "Owner", "Founder", "Manager"
    contact_email: str | None = None
    contact_phone: str | None = None
    confidence: ConfidenceLevel = ConfidenceLevel.NOT_FOUND
    evidence: list[str] = Field(default_factory=list)


class BusinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    category: str
    address: str
    city: str
    phone: str | None = None
    email: str | None = None
    rating: float | None = None
    review_count: int | None = None
    website_url: str | None = None
    website_status: WebsiteStatus = WebsiteStatus.WEBSITE_UNVERIFIED
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    workflow_state: WorkflowState = WorkflowState.DISCOVERED
    opportunity_score: float | None = None
    created_at: datetime
    updated_at: datetime
