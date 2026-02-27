from typing import List
import html
from datetime import timedelta
from fastapi import HTTPException
from sqlalchemy import select, update, func, case, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from canvas.models.user import User
from canvas.models.vbu import VBU
from canvas.models.canvas import Canvas
from canvas.models.thesis import Thesis
from canvas.models.proof_point import ProofPoint
from canvas.models.monthly_review import MonthlyReview
from canvas.db import get_db_session
from .schemas import VBUSummary, PortfolioFilters

class PortfolioService:
    def __init__(self, db: AsyncSession = None):
        self.db = db
    
    async def get_summary(self, user: User, filters: PortfolioFilters) -> List[VBUSummary]:
        """Get portfolio summary with role-based filtering and health computation"""
        if not self.db:
            async with get_db_session() as db:
                return await self._get_summary_impl(db, user, filters)
        return await self._get_summary_impl(self.db, user, filters)
    
    async def _get_summary_impl(self, db: AsyncSession, user: User, filters: PortfolioFilters) -> List[VBUSummary]:
        # Build query using SQLAlchemy ORM
        # Create lateral subqueries for better performance
        currently_testing_subq = (
            select(
                case(
                    (Canvas.currently_testing_type == 'thesis', Thesis.text),
                    (Canvas.currently_testing_type == 'proof_point', ProofPoint.description),
                    else_=None
                ).label('currently_testing_text'),
                Canvas.id.label('canvas_id')
            )
            .select_from(Canvas)
            .outerjoin(Thesis, and_(Canvas.currently_testing_type == 'thesis', Canvas.currently_testing_id == Thesis.id))
            .outerjoin(ProofPoint, and_(Canvas.currently_testing_type == 'proof_point', Canvas.currently_testing_id == ProofPoint.id))
        ).lateral('ct')
        
        next_review_subq = (
            select(
                func.min(MonthlyReview.review_date + timedelta(days=30)).label('next_review_date'),
                MonthlyReview.canvas_id
            )
            .group_by(MonthlyReview.canvas_id)
        ).lateral('nr')
        
        query = (
            select(
                VBU.id,
                VBU.name,
                User.name.label('gm_name'),
                Canvas.lifecycle_lane,
                Canvas.success_description,
                Canvas.primary_constraint,
                Canvas.portfolio_notes,
                func.coalesce(Canvas.health_indicator_cache, 'Not Started').label('health_indicator'),
                currently_testing_subq.c.currently_testing_text.label('currently_testing'),
                next_review_subq.c.next_review_date
            )
            .select_from(VBU)
            .join(User, VBU.gm_id == User.id)
            .join(Canvas, Canvas.vbu_id == VBU.id)
            .outerjoin(currently_testing_subq, Canvas.id == currently_testing_subq.c.canvas_id)
            .outerjoin(next_review_subq, Canvas.id == next_review_subq.c.canvas_id)
        )
        
        # Apply filters using parameterized conditions
        conditions = []
        
        # Role-based filtering
        if user.role == "gm":
            conditions.append(VBU.gm_id == user.id)
        elif user.role == "group_leader":
            conditions.append(VBU.group_leader_id == user.id)
        elif user.role == "viewer" and user.vbu_id:
            conditions.append(VBU.id == user.vbu_id)
        
        # Lane filtering
        if filters.lane:
            conditions.append(Canvas.lifecycle_lane.in_([lane.value for lane in filters.lane]))
        
        # GM filtering
        if filters.gm_id:
            conditions.append(VBU.gm_id.in_(filters.gm_id))
        
        # Health status filtering
        if filters.health_status:
            conditions.append(
                func.coalesce(Canvas.health_indicator_cache, 'Not Started').in_(filters.health_status)
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Add pagination limit
        query = query.order_by(VBU.name).limit(1000)
        
        result = await db.execute(query)
        return [VBUSummary(
            id=row.id,
            name=row.name,
            gm_name=row.gm_name,
            lifecycle_lane=row.lifecycle_lane,
            success_description=row.success_description,
            currently_testing=row.currently_testing,
            next_review_date=row.next_review_date,
            primary_constraint=row.primary_constraint,
            health_indicator=row.health_indicator,
            portfolio_notes=row.portfolio_notes
        ) for row in result]
    
    async def update_portfolio_notes(self, notes: str, user: User) -> None:
        """Update portfolio notes (admin only)"""
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin role required")
        
        # HTML entity encoding for XSS prevention
        sanitized_notes = html.escape(notes) if notes else None
        
        if not self.db:
            async with get_db_session() as db:
                await self._update_notes_impl(db, sanitized_notes, user)
        else:
            await self._update_notes_impl(self.db, sanitized_notes, user)
    
    async def _update_notes_impl(self, db: AsyncSession, sanitized_notes: str, user: User) -> None:
        # Update all canvases with new portfolio notes
        await db.execute(
            update(Canvas).values(
                portfolio_notes=sanitized_notes,
                updated_at=func.now(),
                updated_by=user.id
            )
        )
        await db.commit()

    async def get_thesis_health(self, user: User) -> list[dict]:
        """Get thesis-level health across all VBUs the user can see.
        
        For each thesis, computes an observation ratio from scored proof points
        (observed=1, not_observed=0). A thesis is 'strengthening' if ratio > 0.5,
        'weakening' if ratio < 0.5, 'neutral' if exactly 0.5 or no scored points.
        """
        if not self.db:
            async with get_db_session() as db:
                return await self._get_thesis_health_impl(db, user)
        return await self._get_thesis_health_impl(self.db, user)

    async def _get_thesis_health_impl(self, db: AsyncSession, user: User) -> list[dict]:
        query = (
            select(VBU, Canvas, Thesis)
            .join(Canvas, Canvas.vbu_id == VBU.id)
            .join(Thesis, Thesis.canvas_id == Canvas.id)
            .options(selectinload(Thesis.proof_points), selectinload(Thesis.category))
            .order_by(VBU.name, Thesis.order)
        )

        if user.role == "gm":
            query = query.where(VBU.gm_id == user.id)
        elif user.role == "group_leader":
            query = query.where(VBU.group_leader_id == user.id)
        elif user.role == "viewer" and user.vbu_id:
            query = query.where(VBU.id == user.vbu_id)

        result = await db.execute(query)
        rows = result.unique().all()

        out = []
        for vbu, canvas, thesis in rows:
            scores = [pp.status.score for pp in thesis.proof_points if pp.status.score is not None]
            total = len(scores)
            observed = sum(scores) if scores else 0
            ratio = observed / total if total else None

            if ratio is None:
                signal = "neutral"
            elif ratio > 0.5:
                signal = "strengthening"
            elif ratio < 0.5:
                signal = "weakening"
            else:
                signal = "neutral"

            out.append({
                "vbu_id": str(vbu.id),
                "vbu_name": vbu.name,
                "thesis_id": str(thesis.id),
                "thesis_order": thesis.order,
                "thesis_text": thesis.text,
                "category_name": thesis.category.name if thesis.category else None,
                "category_color": thesis.category.color if thesis.category else None,
                "observed": observed,
                "not_observed": total - observed,
                "total_scored": total,
                "total_proof_points": len(thesis.proof_points),
                "signal": signal,
                "proof_points": [
                    {"id": str(pp.id), "status": pp.status.value, "description": pp.description}
                    for pp in thesis.proof_points
                ],
            })
        return out