from typing import Generic, TypeVar, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from app.schemas.enums import ConfidenceLevel


T = TypeVar("T")


class AgentInput(BaseModel):
    lead_id: str | None = None
    campaign_id: str | None = None
    workflow_run_id: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    custom_params: dict[str, Any] = Field(default_factory=dict)


class AgentOutput(BaseModel, Generic[T]):
    agent_name: str
    agent_version: str
    lead_id: str | None = None
    success: bool
    data: T | None = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    evidence: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: float = 0.0
