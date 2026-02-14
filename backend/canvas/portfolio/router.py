from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from canvas.auth.dependencies import get_current_user, require_role
from canvas.models.user import User
from canvas import success_response, list_response
from .schemas import PortfolioFilters, PortfolioNotesRequest
from .service import PortfolioService

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])
portfolio_service = PortfolioService()

@router.get("/summary")
async def get_portfolio_summary(
    lane: Optional[str] = Query(None, description="Comma-separated lifecycle lanes"),
    gm_id: Optional[str] = Query(None, description="Comma-separated GM UUIDs"),
    health_status: Optional[str] = Query(None, description="Comma-separated health statuses"),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get portfolio summary with filtering"""
    filters = PortfolioFilters(
        lane=lane.split(",") if lane else None,
        gm_id=[UUID(id.strip()) for id in gm_id.split(",")] if gm_id else None,
        health_status=health_status.split(",") if health_status else None
    )
    
    summary = await portfolio_service.get_summary(current_user, filters)
    return list_response(summary, len(summary))

@router.patch("/notes")
async def update_portfolio_notes(
    request: PortfolioNotesRequest,
    current_user: User = Depends(require_role("admin"))
) -> dict:
    """Update portfolio notes (admin only)"""
    await portfolio_service.update_portfolio_notes(request.notes, current_user)
    return success_response({
        "notes": request.notes,
        "updated_at": "2026-02-13T14:00:00Z"
    })