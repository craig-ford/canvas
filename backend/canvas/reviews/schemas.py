from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID

class CommitmentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    order: int = Field(..., ge=1, le=3)

class ReviewCreateSchema(BaseModel):
    review_date: date
    what_moved: Optional[str] = Field(None, max_length=5000)
    what_learned: Optional[str] = Field(None, max_length=5000)
    what_threatens: Optional[str] = Field(None, max_length=5000)
    currently_testing_type: str = Field(..., regex="^(thesis|proof_point)$")
    currently_testing_id: UUID
    commitments: List[CommitmentCreate] = Field(..., min_items=1, max_items=3)
    attachment_ids: List[UUID] = Field(default_factory=list, max_items=10)
    
    @validator('review_date')
    def review_date_not_future(cls, v):
        if v > date.today():
            raise ValueError('Review date cannot be in the future')
        return v
    
    @validator('commitments')
    def unique_commitment_orders(cls, v):
        orders = [c.order for c in v]
        if len(orders) != len(set(orders)):
            raise ValueError('Commitment orders must be unique')
        return v

class CommitmentResponse(BaseModel):
    id: UUID
    text: str
    order: int

class AttachmentResponse(BaseModel):
    id: UUID
    filename: str
    label: Optional[str]
    size_bytes: int

class ReviewResponse(BaseModel):
    id: UUID
    canvas_id: UUID
    review_date: date
    what_moved: Optional[str]
    what_learned: Optional[str]
    what_threatens: Optional[str]
    currently_testing_type: Optional[str]
    currently_testing_id: Optional[UUID]
    created_by: UUID
    created_at: datetime
    commitments: List[CommitmentResponse]
    attachments: List[AttachmentResponse]
    
    class Config:
        from_attributes = True