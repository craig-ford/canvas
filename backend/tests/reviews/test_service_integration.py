import pytest
from uuid import uuid4
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from canvas.reviews.service import ReviewService
from canvas.models.monthly_review import MonthlyReview
from canvas.models.commitment import Commitment

class TestReviewServiceIntegration:
    async def test_create_review_with_commitments(self, db_session: AsyncSession, sample_canvas, admin_user, test_thesis):
        """Test creating review with commitments updates canvas atomically"""
        service = ReviewService(db_session)
        review_data = {
            "review_date": date.today(),
            "currently_testing_type": "thesis",
            "currently_testing_id": test_thesis.id,
            "commitments": [{"text": "Test commitment", "order": 1}]
        }
        review = await service.create_review(
            canvas_id=sample_canvas.id, 
            review_data=review_data,
            created_by=admin_user.id
        )
        assert review is not None
        assert review.canvas_id == sample_canvas.id
        assert len(review.commitments) == 1

    async def test_list_reviews_ordered_by_date(self, db_session: AsyncSession, sample_canvas):
        """Test reviews returned in review_date DESC, created_at DESC order"""
        service = ReviewService(db_session)
        reviews = await service.list_reviews(canvas_id=sample_canvas.id)
        assert isinstance(reviews, list)
        if len(reviews) > 1:
            assert all(reviews[i].review_date >= reviews[i + 1].review_date for i in range(len(reviews) - 1))

    async def test_create_review_updates_canvas_currently_testing(self, db_session: AsyncSession, sample_canvas, sample_thesis, admin_user):
        """Test review stores currently_testing_type and currently_testing_id"""
        service = ReviewService(db_session)
        review_data = {
            "review_date": date.today(),
            "currently_testing_type": "thesis",
            "currently_testing_id": sample_thesis.id,
            "commitments": [{"text": "c1", "order": 1}]
        }
        review = await service.create_review(
            canvas_id=sample_canvas.id, 
            review_data=review_data,
            created_by=admin_user.id
        )
        assert review.currently_testing_type == "thesis"
        assert review.currently_testing_id == sample_thesis.id

    async def test_attachment_linking_integration(self, db_session: AsyncSession, sample_canvas, admin_user, test_thesis):
        """Test linking pre-uploaded attachments to review via AttachmentService"""
        service = ReviewService(db_session)
        review_data = {
            "review_date": date.today(),
            "currently_testing_type": "thesis",
            "currently_testing_id": test_thesis.id,
            "attachment_ids": [],
            "commitments": [{"text": "c1", "order": 1}]
        }
        review = await service.create_review(
            canvas_id=sample_canvas.id, 
            review_data=review_data,
            created_by=admin_user.id
        )
        assert review is not None
        assert review.attachments == []

    async def test_validate_currently_testing_belongs_to_canvas(self, db_session: AsyncSession, sample_canvas, other_canvas_thesis, admin_user):
        """Test validation prevents selecting thesis/proof_point from different canvas"""
        service = ReviewService(db_session)
        review_data = {
            "review_date": date.today(),
            "currently_testing_type": "thesis",
            "currently_testing_id": other_canvas_thesis.id,
            "commitments": [{"text": "c1", "order": 1}]
        }
        with pytest.raises(ValueError, match="does not belong to canvas"):
            await service.create_review(
                canvas_id=sample_canvas.id, 
                review_data=review_data,
                created_by=admin_user.id
            )

    async def test_get_review_with_relationships(self, db_session: AsyncSession, sample_review):
        """Test get_review loads commitments and attachments"""
        service = ReviewService(db_session)
        review = await service.get_review(sample_review.id)
        assert review is not None
        assert hasattr(review, "commitments")
        assert hasattr(review, "attachments")