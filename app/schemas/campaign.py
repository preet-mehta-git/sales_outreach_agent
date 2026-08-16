from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CampaignCreate(BaseModel):
    name: str
    industry: str = "restaurant_cafe"
    city: str = "Ahmedabad"
    state: str = "Gujarat"
    country: str = "India"
    min_opportunity_score: int = Field(default=70, ge=0, le=100)
    priority_score: int = Field(default=80, ge=0, le=100)
    is_active: bool = True


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    industry: str
    city: str
    state: str
    country: str
    min_opportunity_score: int
    priority_score: int
    is_active: bool
    created_at: datetime
