from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from canvas.db import get_db_session
from canvas.auth.dependencies import get_current_user, require_role
from canvas.services.canvas_service import CanvasService
from canvas.models.user import User, UserRole
from canvas.models.proof_point import ProofPoint, ProofPointStatus
from canvas import success_response, list_response

class ProofPointCreate(BaseModel):
    description: str = Field(..., min_length=1, description="Observable signal description")
    status: ProofPointStatus = ProofPointStatus.NOT_STARTED
    evidence_note: Optional[str] = None
    target_review_month: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}$", description="YYYY-MM format")

class ProofPointUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    status: Optional[ProofPointStatus] = None
    evidence_note: Optional[str] = None
    target_review_month: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}$", description="YYYY-MM format")

router = APIRouter(prefix="/api", tags=["proof_point"])
canvas_service = CanvasService()

@router.get("/theses/{thesis_id}/proof-points")
async def get_proof_points(
    thesis_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get proof points for thesis with attachments"""
    await canvas_service.verify_thesis_ownership(thesis_id, current_user, db)
    # BLOCKED: awaiting CanvasService.get_proof_points_by_thesis method
    proof_points = await canvas_service.get_proof_points_by_thesis(thesis_id, db)
    return list_response(proof_points, len(proof_points))

@router.post("/theses/{thesis_id}/proof-points", status_code=201)
async def create_proof_point(
    thesis_id: UUID,
    proof_point_data: ProofPointCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.GM])),
    db: AsyncSession = Depends(get_db_session)
):
    """Create proof point with status validation"""
    await canvas_service.verify_thesis_ownership(thesis_id, current_user, db)
    proof_point = await canvas_service.create_proof_point(
        thesis_id,
        proof_point_data.description,
        proof_point_data.status.value,
        proof_point_data.evidence_note,
        proof_point_data.target_review_month,
        db
    )
    return success_response(proof_point, status_code=201)

@router.patch("/proof-points/{proof_point_id}")
async def update_proof_point(
    proof_point_id: UUID,
    proof_point_data: ProofPointUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.GM])),
    db: AsyncSession = Depends(get_db_session)
):
    """Update proof point fields including status changes"""
    # BLOCKED: awaiting CanvasService.verify_proof_point_ownership method
    await canvas_service.verify_proof_point_ownership(proof_point_id, current_user, db)
    proof_point = await canvas_service.update_proof_point(
        proof_point_id,
        proof_point_data.description,
        proof_point_data.status.value if proof_point_data.status else None,
        proof_point_data.evidence_note,
        proof_point_data.target_review_month,
        db
    )
    return success_response(proof_point)

@router.delete("/proof-points/{proof_point_id}", status_code=204)
async def delete_proof_point(
    proof_point_id: UUID,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.GM])),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete proof point with cascade to attachments"""
    # BLOCKED: awaiting CanvasService.verify_proof_point_ownership method
    await canvas_service.verify_proof_point_ownership(proof_point_id, current_user, db)
    await canvas_service.delete_proof_point(proof_point_id, db)