from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from canvas.models.monthly_review import MonthlyReview
from canvas.models.commitment import Commitment
from canvas.models.canvas import Canvas
from canvas.models.thesis import Thesis
from canvas.models.proof_point import ProofPoint
from canvas.models.attachment import Attachment

class ReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_reviews(self, canvas_id: UUID) -> List[MonthlyReview]:
        """List reviews for canvas, ordered by review_date DESC, created_at DESC"""
        ...
    
    async def create_review(self, canvas_id: UUID, review_data: Dict[str, Any], created_by: UUID) -> MonthlyReview:
        """Create review with commitments, update canvas currently_testing atomically"""
        ...
    
    async def get_review(self, review_id: UUID) -> MonthlyReview:
        """Get single review with commitments and attachments"""
        ...
        
    async def get_canvas_options(self, canvas_id: UUID) -> Dict[str, Any]:
        """Get theses and proof points for currently testing selection"""
        ...
    
    async def _validate_currently_testing(self, canvas_id: UUID, testing_type: str, testing_id: UUID) -> None:
        """Validate selected thesis/proof point belongs to canvas"""
        ...
    
    async def _link_attachments(self, review_id: UUID, attachment_ids: List[UUID]) -> None:
        """Link pre-uploaded attachments to review"""
        ...