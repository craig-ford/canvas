from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
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
        result = await self.db.execute(
            select(MonthlyReview)
            .where(MonthlyReview.canvas_id == canvas_id)
            .order_by(MonthlyReview.review_date.desc(), MonthlyReview.created_at.desc())
            .options(selectinload(MonthlyReview.commitments), selectinload(MonthlyReview.attachments))
        )
        return result.scalars().all()
    
    async def create_review(self, canvas_id: UUID, review_data: Dict[str, Any], created_by: UUID) -> MonthlyReview:
        """Create review with commitments, update canvas currently_testing atomically"""
        try:
            # Validate currently_testing selection belongs to canvas
            if review_data.get('currently_testing_type') and review_data.get('currently_testing_id'):
                await self._validate_currently_testing(
                    canvas_id,
                    review_data['currently_testing_type'],
                    review_data['currently_testing_id']
                )

            # Create review
            review = MonthlyReview(
                canvas_id=canvas_id,
                review_date=review_data['review_date'],
                what_moved=review_data.get('what_moved'),
                what_learned=review_data.get('what_learned'),
                what_threatens=review_data.get('what_threatens'),
                currently_testing_type=review_data.get('currently_testing_type'),
                currently_testing_id=review_data.get('currently_testing_id'),
                created_by=created_by
            )
            self.db.add(review)
            await self.db.flush()

            # Create commitments
            for commitment_data in review_data['commitments']:
                commitment = Commitment(
                    monthly_review_id=review.id,
                    text=commitment_data['text'],
                    order=commitment_data['order']
                )
                self.db.add(commitment)

            # Link attachments
            if review_data.get('attachment_ids'):
                await self._link_attachments(review.id, review_data['attachment_ids'])

            await self.db.commit()
            
            # Use eager loading instead of refresh to avoid N+1 queries
            result = await self.db.execute(
                select(MonthlyReview)
                .where(MonthlyReview.id == review.id)
                .options(selectinload(MonthlyReview.commitments), selectinload(MonthlyReview.attachments))
            )
            return result.scalar_one()
        except IntegrityError as e:
            if "uq_monthly_reviews_canvas_date" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Review already exists for this canvas and date"
                )
            raise
    
    async def get_review(self, review_id: UUID) -> MonthlyReview:
        """Get single review with commitments and attachments"""
        result = await self.db.execute(
            select(MonthlyReview)
            .where(MonthlyReview.id == review_id)
            .options(selectinload(MonthlyReview.commitments), selectinload(MonthlyReview.attachments))
        )
        review = result.scalar_one_or_none()
        if not review:
            raise HTTPException(404, "Review not found")
        return review
        
    async def get_canvas_options(self, canvas_id: UUID) -> Dict[str, Any]:
        """Get theses and proof points for currently testing selection"""
        # Get theses with their proof points
        result = await self.db.execute(
            select(Thesis)
            .where(Thesis.canvas_id == canvas_id)
            .order_by(Thesis.order)
            .options(selectinload(Thesis.proof_points))
        )
        theses = result.scalars().all()
        
        options = []
        for thesis in theses:
            thesis_option = {
                "id": thesis.id,
                "type": "thesis",
                "text": thesis.text,
                "proof_points": [
                    {
                        "id": pp.id,
                        "type": "proof_point", 
                        "description": pp.description
                    }
                    for pp in thesis.proof_points
                ]
            }
            options.append(thesis_option)
        
        return {"options": options}
    
    async def _validate_currently_testing(self, canvas_id: UUID, testing_type: str, testing_id: UUID) -> None:
        """Validate selected thesis/proof point belongs to canvas"""
        if not testing_type or not testing_id:
            return
            
        if testing_type == "thesis":
            result = await self.db.execute(
                select(Thesis).where(Thesis.id == testing_id, Thesis.canvas_id == canvas_id)
            )
        else:  # proof_point
            result = await self.db.execute(
                select(ProofPoint)
                .join(Thesis)
                .where(ProofPoint.id == testing_id, Thesis.canvas_id == canvas_id)
            )
        
        if not result.scalar_one_or_none():
            raise ValueError("Selected thesis/proof point does not belong to canvas")
    
    async def _link_attachments(self, review_id: UUID, attachment_ids: List[UUID]) -> None:
        """Link pre-uploaded attachments to review"""
        if attachment_ids:
            await self.db.execute(
                update(Attachment)
                .where(Attachment.id.in_(attachment_ids))
                .values(monthly_review_id=review_id)
            )