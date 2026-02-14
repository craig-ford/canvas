"""Pydantic schemas for canvas management API."""

from datetime import date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from canvas.models.canvas import LifecycleLane, CurrentlyTestingType
from canvas.models.proof_point import ProofPointStatus


# Request schemas
class VBUCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="VBU name")
    gm_id: UUID = Field(..., description="General Manager user ID")


class VBUUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    gm_id: Optional[UUID] = None


class CanvasUpdate(BaseModel):
    product_name: Optional[str] = Field(None, max_length=255)
    lifecycle_lane: Optional[LifecycleLane] = None
    success_description: Optional[str] = None
    future_state_intent: Optional[str] = None
    primary_focus: Optional[str] = Field(None, max_length=255)
    resist_doing: Optional[str] = None
    good_discipline: Optional[str] = None
    primary_constraint: Optional[str] = None
    currently_testing_type: Optional[CurrentlyTestingType] = None
    currently_testing_id: Optional[UUID] = None
    portfolio_notes: Optional[str] = None


class ThesisCreate(BaseModel):
    text: str = Field(..., min_length=1, description="Thesis statement")
    order: int = Field(..., ge=1, le=5, description="Display order 1-5")


class ThesisUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1)


class ProofPointCreate(BaseModel):
    description: str = Field(..., min_length=1, description="Observable signal description")
    status: ProofPointStatus = ProofPointStatus.NOT_STARTED
    evidence_note: Optional[str] = None
    target_review_month: Optional[date] = None


class ProofPointUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    status: Optional[ProofPointStatus] = None
    evidence_note: Optional[str] = None
    target_review_month: Optional[date] = None