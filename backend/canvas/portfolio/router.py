from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from canvas.auth.dependencies import get_current_user, require_role, verify_csrf
from canvas.models.user import User
from canvas.db import get_db_session
from canvas import success_response, list_response
from .schemas import PortfolioFilters, PortfolioNotesRequest, LifecycleLane
from .service import PortfolioService

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

@router.get("/summary")
async def get_portfolio_summary(
    lane: Optional[str] = Query(None, description="Comma-separated lifecycle lanes"),
    gm_id: Optional[str] = Query(None, description="Comma-separated GM UUIDs"),
    health_status: Optional[str] = Query(None, description="Comma-separated health statuses"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """Get portfolio summary with filtering"""
    try:
        # Parse and validate filters
        filters = PortfolioFilters()
        
        if lane:
            try:
                filters.lane = [LifecycleLane(l.strip()) for l in lane.split(",")]
            except ValueError as e:
                raise HTTPException(
                    status_code=422, 
                    detail=f"Invalid lifecycle lane. Valid values: {[e.value for e in LifecycleLane]}"
                )
        
        if gm_id:
            try:
                filters.gm_id = [UUID(id.strip()) for id in gm_id.split(",")]
            except ValueError:
                raise HTTPException(status_code=422, detail="Invalid GM ID format")
        
        if health_status:
            valid_statuses = ["Not Started", "In Progress", "On Track", "At Risk"]
            statuses = [s.strip() for s in health_status.split(",")]
            for status in statuses:
                if status not in valid_statuses:
                    raise HTTPException(
                        status_code=422, 
                        detail=f"Invalid health status: {status}. Valid values: {valid_statuses}"
                    )
            filters.health_status = statuses
        
        # Get portfolio summary
        portfolio_service = PortfolioService(db)
        summary = await portfolio_service.get_summary(current_user, filters)
        
        return list_response(
            data=[s.model_dump() for s in summary], 
            total=len(summary),
            page=1,
            per_page=25
        )
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.patch("/notes")
async def update_portfolio_notes(
    request: PortfolioNotesRequest,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db_session),
    _: None = Depends(verify_csrf)
) -> dict:
    """Update portfolio notes (admin only)"""
    portfolio_service = PortfolioService(db)
    await portfolio_service.update_portfolio_notes(request.notes, current_user)
    
    return success_response({
        "notes": request.notes,
        "updated_at": datetime.now(timezone.utc).isoformat()
    })