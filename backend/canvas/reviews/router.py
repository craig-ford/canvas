from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List
from canvas.auth.dependencies import get_current_user, require_role
from canvas.db import get_db_session
from canvas import success_response, list_response
from canvas.reviews.service import ReviewService
from canvas.reviews.schemas import ReviewCreateSchema, ReviewResponse
from canvas.models.canvas import Canvas
from canvas.models.vbu import VBU

router = APIRouter(prefix="/api", tags=["reviews"])

def check_csrf_token(request: Request) -> None:
    """Basic CSRF protection - check for custom header"""
    csrf_header = request.headers.get("X-CSRF-Token")
    if not csrf_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token required"
        )

async def verify_canvas_access(canvas_id: UUID, current_user, db: AsyncSession):
    """Verify user has access to canvas based on role"""
    result = await db.execute(
        select(Canvas).options(selectinload(Canvas.vbu)).where(Canvas.id == canvas_id)
    )
    canvas = result.scalar_one_or_none()
    if not canvas:
        raise HTTPException(status_code=404, detail="Canvas not found")
    
    if current_user.role == "admin":
        return canvas
    
    if current_user.role == "viewer" and current_user.vbu_id != canvas.vbu_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == "gm" and canvas.vbu.gm_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == "group_leader" and canvas.vbu.group_leader_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return canvas

@router.get("/canvases/{canvas_id}/reviews", response_model=dict)
async def list_reviews(
    canvas_id: UUID, 
    current_user=Depends(get_current_user), 
    db: AsyncSession = Depends(get_db_session)
):
    """List reviews for a canvas"""
    await verify_canvas_access(canvas_id, current_user, db)
    service = ReviewService(db)
    reviews = await service.list_reviews(canvas_id)
    return list_response([ReviewResponse.model_validate(review) for review in reviews], len(reviews))

@router.post("/canvases/{canvas_id}/reviews", response_model=dict, status_code=201)
async def create_review(
    canvas_id: UUID, 
    review_data: ReviewCreateSchema, 
    request: Request,
    current_user=Depends(require_role("admin", "gm", "group_leader")), 
    db: AsyncSession = Depends(get_db_session)
):
    """Create new review"""
    check_csrf_token(request)
    await verify_canvas_access(canvas_id, current_user, db)
    service = ReviewService(db)
    try:
        review = await service.create_review(canvas_id, review_data.model_dump(), current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return success_response(ReviewResponse.model_validate(review), 201)

@router.get("/reviews/{review_id}", response_model=dict)
async def get_review(
    review_id: UUID, 
    current_user=Depends(get_current_user), 
    db: AsyncSession = Depends(get_db_session)
):
    """Get single review detail"""
    service = ReviewService(db)
    review = await service.get_review(review_id)
    
    await verify_canvas_access(review.canvas_id, current_user, db)
    
    return success_response(ReviewResponse.model_validate(review))
