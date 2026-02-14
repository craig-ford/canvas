from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import date
from enum import Enum

class LifecycleLane(str, Enum):
    build = "build"
    sell = "sell"
    milk = "milk"
    reframe = "reframe"

class VBUSummary(BaseModel):
    id: UUID
    name: str
    gm_name: str
    lifecycle_lane: LifecycleLane
    success_description: Optional[str]
    currently_testing: Optional[str]
    next_review_date: Optional[date]
    primary_constraint: Optional[str]
    health_indicator: str
    portfolio_notes: Optional[str]

class PortfolioFilters(BaseModel):
    lane: Optional[List[LifecycleLane]] = None
    gm_id: Optional[List[UUID]] = None
    health_status: Optional[List[str]] = None

class PortfolioNotesRequest(BaseModel):
    notes: Optional[str] = Field(None, max_length=10000)