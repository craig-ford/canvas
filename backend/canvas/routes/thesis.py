from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from canvas.db import get_db_session
from canvas.auth.dependencies import get_current_user, require_role, verify_csrf
from canvas.services.canvas_service import CanvasService
from canvas.models.user import User, UserRole
from canvas.models.thesis import Thesis
from canvas.models.thesis_category import ThesisCategory
from canvas import success_response, list_response

class ThesisCreate(BaseModel):
    text: str = Field("", description="Thesis statement")
    order: int | None = Field(None, ge=1, le=5, description="Display order 1-5, auto-assigned if omitted")
    description: str | None = None
    category_id: UUID | None = None

class ThesisUpdate(BaseModel):
    text: str | None = Field(None)
    description: str | None = None
    category_id: UUID | None = None

class ThesesReorder(BaseModel):
    thesis_orders: List[Dict[str, Any]] = Field(..., description="List of {id, order} pairs")

router = APIRouter(prefix="/api", tags=["thesis"])
canvas_service = CanvasService()

@router.get("/thesis-categories")
async def list_categories(
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(ThesisCategory).order_by(ThesisCategory.name))
    cats = result.scalars().all()
    return list_response(
        [{"id": str(c.id), "name": c.name, "description": c.description, "color": c.color} for c in cats],
        len(cats),
    )

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
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.GM, UserRole.GROUP_LEADER])),
    db: AsyncSession = Depends(get_db_session),
    _: None = Depends(verify_csrf)
):
    """Create thesis with max 5 constraint and order validation"""
    await canvas_service.verify_canvas_ownership(canvas_id, current_user, db)
    thesis = await canvas_service.create_thesis(canvas_id, thesis_data.text, thesis_data.order, db, description=thesis_data.description, category_id=thesis_data.category_id)
    return success_response(thesis, status_code=201)

@router.patch("/theses/{thesis_id}")
async def update_thesis(
    thesis_id: UUID,
    thesis_data: ThesisUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.GM, UserRole.GROUP_LEADER])),
    db: AsyncSession = Depends(get_db_session),
    _: None = Depends(verify_csrf)
):
    """Update thesis text with ownership verification"""
    await canvas_service.verify_thesis_ownership(thesis_id, current_user, db)
    updates = thesis_data.model_dump(exclude_unset=True)
    thesis = await canvas_service.update_thesis(thesis_id, updates, db)
    return success_response(thesis)

@router.delete("/theses/{thesis_id}", status_code=204)
async def delete_thesis(
    thesis_id: UUID,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.GM, UserRole.GROUP_LEADER])),
    db: AsyncSession = Depends(get_db_session),
    _: None = Depends(verify_csrf)
):
    """Delete thesis with cascade to proof points"""
    await canvas_service.verify_thesis_ownership(thesis_id, current_user, db)
    await canvas_service.delete_thesis(thesis_id, db)

@router.put("/canvases/{canvas_id}/theses/reorder")
async def reorder_theses(
    canvas_id: UUID,
    reorder_data: ThesesReorder,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.GM, UserRole.GROUP_LEADER])),
    db: AsyncSession = Depends(get_db_session),
    _: None = Depends(verify_csrf)
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