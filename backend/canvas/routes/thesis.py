from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from canvas.db import get_db_session
from canvas.auth.dependencies import get_current_user, require_role
from canvas.services.canvas_service import CanvasService
from canvas.models.user import User, UserRole
from canvas.models.thesis import Thesis
from canvas import success_response, list_response

class ThesisCreate(BaseModel):
    text: str = Field(..., min_length=1, description="Thesis statement")
    order: int = Field(..., ge=1, le=5, description="Display order 1-5")

class ThesisUpdate(BaseModel):
    text: str = Field(..., min_length=1, description="Updated thesis text")

class ThesesReorder(BaseModel):
    thesis_orders: List[Dict[str, Any]] = Field(..., description="List of {id, order} pairs")

router = APIRouter(prefix="/api", tags=["thesis"])
canvas_service = CanvasService()

@router.get("/canvases/{canvas_id}/theses")
async def get_theses(
    canvas_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get theses for canvas with authorization check"""
    canvas = await canvas_service.get_canvas_by_vbu_id_for_auth(canvas_id, current_user, db)
    theses = await canvas_service.get_theses_by_canvas(canvas_id, db)
    return list_response(theses, len(theses))

@router.post("/canvases/{canvas_id}/theses", status_code=201)
async def create_thesis(
    canvas_id: UUID,
    thesis_data: ThesisCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.GM])),
    db: AsyncSession = Depends(get_db_session)
):
    """Create thesis with max 5 constraint and order validation"""
    await canvas_service.verify_canvas_ownership(canvas_id, current_user, db)
    thesis = await canvas_service.create_thesis(canvas_id, thesis_data.text, thesis_data.order, db)
    return success_response(thesis, status_code=201)

@router.patch("/theses/{thesis_id}")
async def update_thesis(
    thesis_id: UUID,
    thesis_data: ThesisUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.GM])),
    db: AsyncSession = Depends(get_db_session)
):
    """Update thesis text with ownership verification"""
    await canvas_service.verify_thesis_ownership(thesis_id, current_user, db)
    thesis = await canvas_service.update_thesis(thesis_id, thesis_data.text, db)
    return success_response(thesis)

@router.delete("/theses/{thesis_id}", status_code=204)
async def delete_thesis(
    thesis_id: UUID,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.GM])),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete thesis with cascade to proof points"""
    await canvas_service.verify_thesis_ownership(thesis_id, current_user, db)
    await canvas_service.delete_thesis(thesis_id, db)

@router.put("/canvases/{canvas_id}/theses/reorder")
async def reorder_theses(
    canvas_id: UUID,
    reorder_data: ThesesReorder,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.GM])),
    db: AsyncSession = Depends(get_db_session)
):
    """Reorder theses with order constraint validation"""
    await canvas_service.verify_canvas_ownership(canvas_id, current_user, db)
    try:
        theses = await canvas_service.reorder_theses(canvas_id, reorder_data.thesis_orders, db)
    except Exception as e:
        if "IntegrityError" in type(e).__name__ or "CheckViolation" in str(e):
            raise HTTPException(status_code=422, detail="Order values must be between 1 and 5")
        raise
    return success_response(theses)