from sqlalchemy import Column, Text, Integer, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from canvas.models import TimestampMixin, Base

class Thesis(Base, TimestampMixin):
    __tablename__ = "theses"
    
    canvas_id = Column(UUID(as_uuid=True), ForeignKey("canvases.id", ondelete="CASCADE"), nullable=False, index=True)
    order = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("thesis_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Relationships
    canvas = relationship("Canvas", back_populates="theses")
    proof_points = relationship("ProofPoint", back_populates="thesis", cascade="all, delete-orphan")
    category = relationship("ThesisCategory", lazy="joined")
    
    __table_args__ = (
        CheckConstraint('"order" BETWEEN 1 AND 5', name="ck_thesis_order_range"),
        UniqueConstraint("canvas_id", "order", name="uq_theses_canvas_order"),
    )
