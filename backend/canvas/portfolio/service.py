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
                case(
                    (Canvas.currently_testing_type == 'thesis', 
                     select(Thesis.text).where(Thesis.id == Canvas.currently_testing_id).scalar_subquery()),
                    (Canvas.currently_testing_type == 'proof_point',
                     select(ProofPoint.description).where(ProofPoint.id == Canvas.currently_testing_id).scalar_subquery()),
                    else_=None
                ).label('currently_testing'),
                select(func.min(MonthlyReview.review_date + timedelta(days=30)))
                .where(MonthlyReview.canvas_id == Canvas.id)
                .scalar_subquery()
                .label('next_review_date')
            )
            .select_from(VBU)
            .join(User, VBU.gm_id == User.id)
            .join(Canvas, Canvas.vbu_id == VBU.id)
        )
        
        # Apply filters using parameterized conditions
        conditions = []
        
        # Role-based filtering
        if user.role == "gm":
            conditions.append(VBU.gm_id == user.id)
        
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