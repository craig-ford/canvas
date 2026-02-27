"""Pydantic schemas for canvas management API."""

from datetime import date, datetime
from typing import Optional, List
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
    health_indicator: Optional[str] = Field(None, pattern="^(Not Started|In Progress|On Track|At Risk)?$")


class ThesisCreate(BaseModel):
    text: str = Field("", description="Thesis statement")
    order: int = Field(..., ge=1, le=5, description="Display order 1-5")
    description: Optional[str] = None


class ThesisUpdate(BaseModel):
    text: Optional[str] = Field(None)
    description: Optional[str] = None


class ProofPointCreate(BaseModel):
    description: str = Field("", description="Observable signal description")
    status: ProofPointStatus = ProofPointStatus.NOT_STARTED
    evidence_note: Optional[str] = None
    target_review_month: Optional[date] = None


class ProofPointUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    status: Optional[ProofPointStatus] = None
    evidence_note: Optional[str] = None
    target_review_month: Optional[date] = None


# Response schemas
class AttachmentResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    size_bytes: int
    label: Optional[str]
    uploaded_by: UUID
    created_at: datetime


class ProofPointResponse(BaseModel):
    id: UUID
    description: str
    notes: Optional[str]
    status: ProofPointStatus
    evidence_note: Optional[str]
    target_review_month: Optional[date]
    attachments: List[AttachmentResponse]
    created_at: datetime
    updated_at: datetime


class ThesisResponse(BaseModel):
    id: UUID
    order: int
    text: str
    description: Optional[str]
    category_id: Optional[UUID]
    category_name: Optional[str]
    category_color: Optional[str]
    proof_points: List[ProofPointResponse]
    created_at: datetime
    updated_at: datetime


class CanvasResponse(BaseModel):
    id: UUID
    vbu_id: UUID
    product_name: Optional[str]
    lifecycle_lane: LifecycleLane
    success_description: Optional[str]
    future_state_intent: Optional[str]
    primary_focus: Optional[str]
    resist_doing: Optional[str]
    good_discipline: Optional[str]
    primary_constraint: Optional[str]
    currently_testing_type: Optional[CurrentlyTestingType]
    currently_testing_id: Optional[UUID]
    portfolio_notes: Optional[str]
    health_indicator: Optional[str]
    theses: List[ThesisResponse]
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[UUID]


# Response schemas
class VBUResponse(BaseModel):
    id: UUID
    name: str
    gm_id: UUID
    gm_name: str
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[UUID]