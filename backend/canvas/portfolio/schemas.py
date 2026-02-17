from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import date
from canvas.models.canvas import LifecycleLane

class VBUSummary(BaseModel):
    id: UUID
    name: str = Field(..., max_length=255)
    gm_name: str = Field(..., max_length=255)
    lifecycle_lane: LifecycleLane
    success_description: Optional[str] = Field(None, max_length=10000)
    currently_testing: Optional[str] = Field(None, max_length=1000)
    next_review_date: Optional[date]
    primary_constraint: Optional[str] = Field(None, max_length=10000)
    health_indicator: str = Field(..., max_length=50)
    portfolio_notes: Optional[str] = Field(None, max_length=10000)

class PortfolioFilters(BaseModel):
    lane: Optional[List[LifecycleLane]] = None
    gm_id: Optional[List[UUID]] = None
    health_status: Optional[List[str]] = None

class PortfolioNotesRequest(BaseModel):
    notes: Optional[str] = Field(None, max_length=10000)