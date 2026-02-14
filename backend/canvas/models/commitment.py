from sqlalchemy import Column, Text, Integer, ForeignKey, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from canvas.models import Base, TimestampMixin

class Commitment(Base, TimestampMixin):
    __tablename__ = "commitments"
    
    monthly_review_id = Column(UUID(as_uuid=True), ForeignKey("monthly_reviews.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    
    # Relationships
    monthly_review = relationship("MonthlyReview", back_populates="commitments")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("length(text) > 0 AND length(text) <= 1000", name="ck_commitments_text_length"),
        CheckConstraint("order >= 1 AND order <= 3", name="ck_commitments_order_range"),
        UniqueConstraint('monthly_review_id', 'order', name='uq_commitments_review_order'),
        Index('ix_commitments_review_id', 'monthly_review_id'),
    )