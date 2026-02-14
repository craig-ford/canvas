import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TimestampMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


# Export all models and enums
from canvas.models.vbu import VBU
from canvas.models.canvas import Canvas, LifecycleLane, CurrentlyTestingType
from canvas.models.thesis import Thesis
from canvas.models.proof_point import ProofPoint, ProofPointStatus
from canvas.models.attachment import Attachment

__all__ = [
    "Base",
    "TimestampMixin",
    "VBU",
    "Canvas", "LifecycleLane", "CurrentlyTestingType",
    "Thesis",
    "ProofPoint", "ProofPointStatus",
    "Attachment",
]