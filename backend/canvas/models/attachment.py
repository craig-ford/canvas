from sqlalchemy import Column, String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from canvas.models import TimestampMixin, Base

class Attachment(Base, TimestampMixin):
    __tablename__ = "attachments"
    
    proof_point_id = Column(UUID(as_uuid=True), ForeignKey("proof_points.id", ondelete="CASCADE"), nullable=True, index=True)
    monthly_review_id = Column(UUID(as_uuid=True), ForeignKey("monthly_reviews.id", ondelete="CASCADE"), nullable=True, index=True)
    filename = Column(String(255), nullable=False)
    storage_path = Column(String(1024), nullable=False, unique=True)
    content_type = Column(String(128), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    label = Column(String(255), nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    
    # Relationships
    proof_point = relationship("ProofPoint", back_populates="attachments")
    
    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(filename)) > 0", name="ck_attachment_filename_not_empty"),
        CheckConstraint("LENGTH(TRIM(storage_path)) > 0", name="ck_attachment_storage_path_not_empty"),
        CheckConstraint("size_bytes BETWEEN 1 AND 10485760", name="ck_attachment_size_range"),
        CheckConstraint("label IS NULL OR LENGTH(TRIM(label)) > 0", name="ck_attachment_label_not_empty"),
        CheckConstraint("content_type IN ('image/jpeg','image/png','image/gif','application/pdf','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','application/vnd.openxmlformats-officedocument.wordprocessingml.document','application/vnd.openxmlformats-officedocument.presentationml.presentation')", name="ck_attachment_content_type"),
        CheckConstraint("(proof_point_id IS NULL) != (monthly_review_id IS NULL)", name="ck_attachment_exactly_one_parent"),
    )