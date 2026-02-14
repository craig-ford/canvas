from enum import Enum
from sqlalchemy import Column, Text, Date, ForeignKey, CheckConstraint, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from canvas.models import TimestampMixin, Base

class ProofPointStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    OBSERVED = "observed"
    STALLED = "stalled"

class ProofPoint(Base, TimestampMixin):
    __tablename__ = "proof_points"
    
    thesis_id = Column(UUID(as_uuid=True), ForeignKey("theses.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(ProofPointStatus, values_callable=lambda e: [x.value for x in e]), nullable=False, default=ProofPointStatus.NOT_STARTED, index=True)
    evidence_note = Column(Text, nullable=True)
    target_review_month = Column(Date, nullable=True)
    
    # Relationships
    thesis = relationship("Thesis", back_populates="proof_points")
    attachments = relationship("Attachment", back_populates="proof_point", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(description)) > 0", name="ck_proof_point_description_not_empty"),
    )