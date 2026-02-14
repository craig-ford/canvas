from typing import List
import html
from fastapi import HTTPException
from sqlalchemy import text, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from canvas.models.user import User
from canvas.models.canvas import Canvas
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
        where_conditions = ["1=1"]
        params = {}
        
        # Role-based filtering
        if user.role == "gm":
            where_conditions.append("v.gm_id = :user_id")
            params["user_id"] = user.id
        
        # Lane filtering
        if filters.lane:
            where_conditions.append("c.lifecycle_lane = ANY(:lanes)")
            params["lanes"] = [lane.value for lane in filters.lane]
        
        # GM filtering
        if filters.gm_id:
            where_conditions.append("v.gm_id = ANY(:gm_ids)")
            params["gm_ids"] = filters.gm_id
        
        # Health status filtering
        if filters.health_status:
            where_conditions.append("COALESCE(c.health_indicator_cache, 'Not Started') = ANY(:health_statuses)")
            params["health_statuses"] = filters.health_status
        
        query = f"""
        SELECT v.id, v.name, u.name as gm_name, c.lifecycle_lane,
               c.success_description, c.primary_constraint, c.portfolio_notes,
               COALESCE(c.health_indicator_cache, 'Not Started') as health_indicator,
               CASE 
                   WHEN c.currently_testing_type = 'thesis' THEN 
                       (SELECT t.text FROM theses t WHERE t.id = c.currently_testing_id)
                   WHEN c.currently_testing_type = 'proof_point' THEN
                       (SELECT pp.description FROM proof_points pp WHERE pp.id = c.currently_testing_id)
                   ELSE NULL
               END as currently_testing,
               (SELECT MIN(mr.review_date + INTERVAL '1 month') 
                FROM monthly_reviews mr WHERE mr.canvas_id = c.id) as next_review_date
        FROM vbus v
        JOIN users u ON v.gm_id = u.id  
        JOIN canvases c ON c.vbu_id = v.id
        WHERE {' AND '.join(where_conditions)}
        ORDER BY v.name
        """
        
        result = await db.execute(text(query), params)
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