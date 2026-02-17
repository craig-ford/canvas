from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID
from canvas.models.canvas import CurrentlyTestingType

class CommitmentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    order: int = Field(..., ge=1, le=3)

class ReviewCreateSchema(BaseModel):
    review_date: date
    what_moved: Optional[str] = Field(None, max_length=5000)
    what_learned: Optional[str] = Field(None, max_length=5000)
    what_threatens: Optional[str] = Field(None, max_length=5000)
    currently_testing_type: str = Field(..., pattern=f"^({'|'.join([e.value for e in CurrentlyTestingType])})$")
    currently_testing_id: UUID
    commitments: List[CommitmentCreate] = Field(..., min_length=1, max_length=3)
    attachment_ids: List[UUID] = Field(default_factory=list, max_length=10)
    
    @field_validator('review_date')
    @classmethod
    def review_date_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError('Review date cannot be in the future')
        return v
    
    @field_validator('commitments')
    @classmethod
    def unique_commitment_orders(cls, v: List[CommitmentCreate]) -> List[CommitmentCreate]:
        orders = [c.order for c in v]
        if len(orders) != len(set(orders)):
            raise ValueError('Commitment orders must be unique')
        return v

class CommitmentResponse(BaseModel):
    id: UUID
    text: str
    order: int
    model_config = {"from_attributes": True}

class AttachmentResponse(BaseModel):
    id: UUID
    filename: str
    label: Optional[str] = None
    size_bytes: int
    model_config = {"from_attributes": True}

class ReviewResponse(BaseModel):
    id: UUID
    canvas_id: UUID
    review_date: date
    what_moved: Optional[str] = None
    what_learned: Optional[str] = None
    what_threatens: Optional[str] = None
    currently_testing_type: Optional[str] = None
    currently_testing_id: Optional[UUID] = None
    created_by: UUID
    created_at: datetime
    commitments: List[CommitmentResponse]
    attachments: List[AttachmentResponse]
    
    model_config = {"from_attributes": True}
