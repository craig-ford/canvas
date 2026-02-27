from enum import Enum
from sqlalchemy import Column, Text, Date, ForeignKey, CheckConstraint, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from canvas.models import TimestampMixin, Base

class ProofPointStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    OBSERVED = "observed"
    NOT_OBSERVED = "not_observed"
    STALLED = "stalled"

    @property
    def score(self) -> int | None:
        """Observation score: 1 for observed, 0 for not_observed, None otherwise."""
        return {self.OBSERVED: 1, self.NOT_OBSERVED: 0}.get(self)

class ProofPoint(Base, TimestampMixin):
    __tablename__ = "proof_points"
    
    thesis_id = Column(UUID(as_uuid=True), ForeignKey("theses.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(SQLEnum(ProofPointStatus, values_callable=lambda e: [x.value for x in e]), nullable=False, default=ProofPointStatus.NOT_STARTED, index=True)
    evidence_note = Column(Text, nullable=True)
    target_review_month = Column(Date, nullable=True)
    
    # Relationships
    thesis = relationship("Thesis", back_populates="proof_points")
    attachments = relationship("Attachment", back_populates="proof_point", cascade="all, delete-orphan")