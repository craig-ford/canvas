from sqlalchemy import Column, Date, Text, ForeignKey, Enum, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from canvas.models import Base, TimestampMixin
from canvas.models.canvas import CurrentlyTestingType

class MonthlyReview(Base, TimestampMixin):
    __tablename__ = "monthly_reviews"
    
    canvas_id = Column(UUID(as_uuid=True), ForeignKey("canvases.id", ondelete="CASCADE"), nullable=False)
    review_date = Column(Date, nullable=False)
    what_moved = Column(Text, nullable=True)
    what_learned = Column(Text, nullable=True)
    what_threatens = Column(Text, nullable=True)
    currently_testing_type = Column(Enum(CurrentlyTestingType, values_callable=lambda e: [x.value for x in e]), nullable=True)
    currently_testing_id = Column(UUID(as_uuid=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    
    # Relationships
    canvas = relationship("Canvas", back_populates="monthly_reviews")
    commitments = relationship("Commitment", back_populates="monthly_review", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="monthly_review", cascade="all, delete-orphan")
    created_by_user = relationship("User")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('canvas_id', 'review_date', name='uq_monthly_reviews_canvas_date'),
        CheckConstraint("currently_testing_type IN ('thesis', 'proof_point') OR currently_testing_type IS NULL"),
        Index('ix_monthly_reviews_canvas_id', 'canvas_id'),
        Index('ix_monthly_reviews_review_date', 'review_date'),
        Index('ix_monthly_reviews_created_by', 'created_by'),
    )