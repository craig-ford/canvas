import pytest
from uuid import uuid4
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from canvas.models.monthly_review import MonthlyReview
from canvas.models.commitment import Commitment

class TestMonthlyReviewRelationships:
    async def test_monthly_review_canvas_relationship(self, db_session: AsyncSession, sample_canvas):
        """Test MonthlyReview belongs_to Canvas via canvas_id"""
        review = MonthlyReview(canvas_id=sample_canvas.id, review_date=date.today(), created_by=sample_canvas.vbu.gm_id)
        db_session.add(review)
        await db_session.flush()
        await db_session.refresh(review, ["canvas"])
        assert review.canvas.id == sample_canvas.id

    async def test_monthly_review_commitments_cascade_delete(self, db_session: AsyncSession, sample_review):
        """Test deleting review cascades to commitments"""
        review_id = sample_review.id
        assert len(sample_review.commitments) > 0
        await db_session.delete(sample_review)
        await db_session.flush()
        remaining = await db_session.execute(Commitment.__table__.select().where(Commitment.monthly_review_id == review_id))
        assert remaining.fetchall() == []

    async def test_commitment_monthly_review_relationship(self, db_session: AsyncSession, sample_review):
        """Test Commitment belongs_to MonthlyReview via monthly_review_id"""
        commitment = sample_review.commitments[0]
        assert commitment.monthly_review_id == sample_review.id

    async def test_unique_constraint_canvas_review_date(self, db_session: AsyncSession, sample_canvas):
        """Test unique constraint on (canvas_id, review_date)"""
        review1 = MonthlyReview(canvas_id=sample_canvas.id, review_date=date.today(), created_by=sample_canvas.vbu.gm_id)
        db_session.add(review1)
        await db_session.flush()
        review2 = MonthlyReview(canvas_id=sample_canvas.id, review_date=date.today(), created_by=sample_canvas.vbu.gm_id)
        db_session.add(review2)
        with pytest.raises(IntegrityError):
            await db_session.flush()

    async def test_commitment_order_uniqueness_per_review(self, db_session: AsyncSession, sample_review):
        """Test unique constraint on (monthly_review_id, order)"""
        dup = Commitment(monthly_review_id=sample_review.id, text="duplicate", order=1)
        db_session.add(dup)
        with pytest.raises(IntegrityError):
            await db_session.flush()

    async def test_commitment_order_check_constraint(self, db_session: AsyncSession, sample_review):
        """Test commitment order must be 1-3"""
        bad = Commitment(monthly_review_id=sample_review.id, text="bad order", order=0)
        db_session.add(bad)
        with pytest.raises(IntegrityError):
            await db_session.flush()

    async def test_commitment_text_not_null(self, db_session: AsyncSession, sample_review):
        """Test commitment text cannot be null or empty"""
        bad = Commitment(monthly_review_id=sample_review.id, text=None, order=2)
        db_session.add(bad)
        with pytest.raises(IntegrityError):
            await db_session.flush()

    async def test_monthly_review_created_by_foreign_key(self, db_session: AsyncSession, sample_canvas, sample_user):
        """Test MonthlyReview.created_by references users.id"""
        review = MonthlyReview(canvas_id=sample_canvas.id, review_date=date.today(), created_by=sample_user.id)
        db_session.add(review)
        await db_session.flush()
        assert review.created_by == sample_user.id