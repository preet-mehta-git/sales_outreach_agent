import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.schemas.enums import (
    WorkflowState, WebsiteStatus, VerificationStatus, ConfidenceLevel, OutreachStatus,
    EntityType, EntityVerificationStatus, WebsiteVerificationStatus, WebsiteClassification, OutreachReadiness,
    DemoAccessStatus, ContactTargetStatus, ManualReviewStatus, QualificationStatus, DemoReadiness
)



def generate_uuid() -> str:
    return str(uuid.uuid4())


class Campaign(Base):
    __tablename__ = "campaigns"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str] = mapped_column(String(100), default="restaurant_cafe")
    city: Mapped[str] = mapped_column(String(100), default="Ahmedabad")
    state: Mapped[str] = mapped_column(String(100), default="Gujarat")
    country: Mapped[str] = mapped_column(String(100), default="India")
    min_opportunity_score: Mapped[int] = mapped_column(Integer, default=70)
    priority_score: Mapped[int] = mapped_column(Integer, default=80)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    businesses: Mapped[list["Business"]] = relationship("Business", back_populates="campaign", cascade="all, delete-orphan")


class Business(Base):
    __tablename__ = "businesses"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    campaign_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(100), default="Ahmedabad", index=True)
    state: Mapped[str] = mapped_column(String(100), default="Gujarat")
    country: Mapped[str] = mapped_column(String(100), default="India")
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    place_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    website_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    website_status: Mapped[WebsiteStatus] = mapped_column(
        SQLEnum(WebsiteStatus), default=WebsiteStatus.WEBSITE_UNVERIFIED
    )
    verification_status: Mapped[VerificationStatus] = mapped_column(
        SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED
    )
    workflow_state: Mapped[WorkflowState] = mapped_column(
        SQLEnum(WorkflowState), default=WorkflowState.DISCOVERED, index=True
    )
    opportunity_score: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    
    # Phase 11 Extensions: Entity Verification
    entity_type: Mapped[EntityType | None] = mapped_column(SQLEnum(EntityType), default=EntityType.UNCERTAIN, nullable=True)
    entity_verification_status: Mapped[EntityVerificationStatus | None] = mapped_column(SQLEnum(EntityVerificationStatus), default=EntityVerificationStatus.MANUAL_REVIEW, nullable=True)
    entity_verification_confidence: Mapped[float | None] = mapped_column(Float, default=0.0, nullable=True)
    entity_verification_evidence: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)

    # Phase 11 Extensions: Website Discovery (Source A + B)
    website_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    website_verification_status: Mapped[WebsiteVerificationStatus | None] = mapped_column(SQLEnum(WebsiteVerificationStatus), default=WebsiteVerificationStatus.WEBSITE_FOUND_UNVERIFIED, nullable=True)
    website_confidence: Mapped[float | None] = mapped_column(Float, default=0.0, nullable=True)
    website_evidence: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    website_classification: Mapped[WebsiteClassification | None] = mapped_column(SQLEnum(WebsiteClassification), nullable=True)

    # Phase 11 Extensions: Purchase Signals & Outreach Readiness
    purchase_signal_evidence: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    outreach_readiness: Mapped[OutreachReadiness | None] = mapped_column(SQLEnum(OutreachReadiness), default=OutreachReadiness.NOT_READY, nullable=True)
    outreach_readiness_reasons: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)

    # Phase 11.1 Extensions: Contact Target Status & Public Demo Verification
    contact_target_status: Mapped[ContactTargetStatus | None] = mapped_column(SQLEnum(ContactTargetStatus), default=ContactTargetStatus.NOT_FOUND, nullable=True)
    contact_target_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_target_confidence: Mapped[float | None] = mapped_column(Float, default=0.0, nullable=True)

    local_preview_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    public_demo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    demo_access_status: Mapped[DemoAccessStatus | None] = mapped_column(SQLEnum(DemoAccessStatus), default=DemoAccessStatus.NOT_GENERATED, nullable=True)
    demo_http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    demo_last_verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # Phase 11.2 Extensions: Manual Review Status & Demo Readiness
    manual_review_status: Mapped[ManualReviewStatus | None] = mapped_column(SQLEnum(ManualReviewStatus), default=ManualReviewStatus.NO_REVIEW_REQUIRED, nullable=True)
    manual_review_reasons: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    demo_readiness: Mapped[DemoReadiness | None] = mapped_column(SQLEnum(DemoReadiness), default=DemoReadiness.NOT_GENERATED, nullable=True)


    # Suppression flag
    is_suppressed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    
    campaign: Mapped["Campaign | None"] = relationship("Campaign", back_populates="businesses")
    website_audit: Mapped["WebsiteAudit | None"] = relationship("WebsiteAudit", back_populates="business", uselist=False, cascade="all, delete-orphan")
    score_details: Mapped["OpportunityScoreRecord | None"] = relationship("OpportunityScoreRecord", back_populates="business", uselist=False, cascade="all, delete-orphan")
    decision_maker: Mapped["DecisionMakerRecord | None"] = relationship("DecisionMakerRecord", back_populates="business", uselist=False, cascade="all, delete-orphan")
    outreach_draft: Mapped["OutreachDraft | None"] = relationship("OutreachDraft", back_populates="business", uselist=False, cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="business", cascade="all, delete-orphan")


class WebsiteAudit(Base):
    __tablename__ = "website_audits"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id"), nullable=False, unique=True)
    
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    performance_score: Mapped[float] = mapped_column(Float, default=0.0)
    mobile_score: Mapped[float] = mapped_column(Float, default=0.0)
    design_score: Mapped[float] = mapped_column(Float, default=0.0)
    info_score: Mapped[float] = mapped_column(Float, default=0.0)
    conversion_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    missing_elements: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    raw_metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    audited_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    business: Mapped["Business"] = relationship("Business", back_populates="website_audit")


class OpportunityScoreRecord(Base):
    __tablename__ = "opportunity_scores"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id"), nullable=False, unique=True)
    
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    digital_gap_score: Mapped[float] = mapped_column(Float, default=0.0)
    traction_score: Mapped[float] = mapped_column(Float, default=0.0)
    commercial_score: Mapped[float] = mapped_column(Float, default=0.0)
    contactability_score: Mapped[float] = mapped_column(Float, default=0.0)
    purchase_signals_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    is_disqualified: Mapped[bool] = mapped_column(Boolean, default=False)
    disqualification_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    calculated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    business: Mapped["Business"] = relationship("Business", back_populates="score_details")


class DecisionMakerRecord(Base):
    __tablename__ = "decision_makers"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id"), nullable=False, unique=True)
    
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    confidence: Mapped[ConfidenceLevel] = mapped_column(SQLEnum(ConfidenceLevel), default=ConfidenceLevel.NOT_FOUND)
    evidence: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    business: Mapped["Business"] = relationship("Business", back_populates="decision_maker")


# Model Alias for DecisionMakerRecord
DecisionMaker = DecisionMakerRecord


class OutreachDraft(Base):
    __tablename__ = "outreach_drafts"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id"), nullable=False, unique=True)
    
    email_subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    email_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    whatsapp_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    demo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[OutreachStatus] = mapped_column(SQLEnum(OutreachStatus), default=OutreachStatus.AWAITING_APPROVAL)
    
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    business: Mapped["Business"] = relationship("Business", back_populates="outreach_draft")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("businesses.id"), nullable=True)
    
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    from_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    agent_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    payload_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    
    business: Mapped["Business | None"] = relationship("Business", back_populates="audit_logs")


class AgentRun(Base):
    __tablename__ = "agent_runs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    agent_version: Mapped[str] = mapped_column(String(50), nullable=False)
    lead_id: Mapped[str] = mapped_column(String(36), nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0)
    input_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    output_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    errors: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
