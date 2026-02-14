from sqlalchemy import Column, String, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from canvas.models import TimestampMixin, Base

class VBU(Base, TimestampMixin):
    __tablename__ = "vbus"
    
    name = Column(String(255), nullable=False)
    gm_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    gm = relationship("User", foreign_keys=[gm_id])
    canvas = relationship("Canvas", back_populates="vbu", uselist=False, cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(name)) > 0", name="ck_vbu_name_not_empty"),
    )