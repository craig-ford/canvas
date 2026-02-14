from enum import Enum
from sqlalchemy import Column, String, Text, ForeignKey, CheckConstraint, Enum as SQLEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from canvas.models import TimestampMixin, Base

class LifecycleLane(str, Enum):
    BUILD = "build"
    SELL = "sell"
    MILK = "milk"
    REFRAME = "reframe"

class CurrentlyTestingType(str, Enum):
    THESIS = "thesis"
    PROOF_POINT = "proof_point"

class Canvas(Base, TimestampMixin):
    __tablename__ = "canvases"
    
    vbu_id = Column(UUID(as_uuid=True), ForeignKey("vbus.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    product_name = Column(String(255), nullable=True)
    lifecycle_lane = Column(SQLEnum(LifecycleLane, values_callable=lambda e: [x.value for x in e]), nullable=False, default=LifecycleLane.BUILD)
    success_description = Column(Text, nullable=True)
    future_state_intent = Column(Text, nullable=True)
    primary_focus = Column(String(255), nullable=True)
    resist_doing = Column(Text, nullable=True)
    good_discipline = Column(Text, nullable=True)
    primary_constraint = Column(Text, nullable=True)
    currently_testing_type = Column(SQLEnum(CurrentlyTestingType, values_callable=lambda e: [x.value for x in e]), nullable=True)
    currently_testing_id = Column(UUID(as_uuid=True), nullable=True)
    portfolio_notes = Column(Text, nullable=True)
    health_indicator_cache = Column(String(20), nullable=True)
    health_computed_at = Column(DateTime(timezone=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    vbu = relationship("VBU", back_populates="canvas")
    theses = relationship("Thesis", back_populates="canvas", cascade="all, delete-orphan", order_by="Thesis.order")
    monthly_reviews = relationship("MonthlyReview", back_populates="canvas", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("product_name IS NULL OR LENGTH(TRIM(product_name)) > 0", name="ck_canvas_product_name_not_empty"),
        CheckConstraint("(currently_testing_type IS NULL) = (currently_testing_id IS NULL)", name="ck_canvas_currently_testing_consistency"),
    )