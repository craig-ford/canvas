from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from canvas.db import get_db_session
from canvas.auth.dependencies import get_current_user, require_role
from canvas.models.user import User, UserRole
from canvas.models.attachment import Attachment
from canvas.models.proof_point import ProofPoint
from canvas.models.monthly_review import MonthlyReview
from canvas.models.thesis import Thesis
from canvas.models.canvas import Canvas
from canvas.models.vbu import VBU
from canvas.services.attachment_service import AttachmentService
from canvas import success_response

router = APIRouter(prefix="/api/attachments", tags=["attachments"])

def get_attachment_service() -> AttachmentService:
    from canvas.config import Settings
    return AttachmentService(Settings())

@router.post("", status_code=201)
async def upload_attachment(
    file: UploadFile = File(...),
    proof_point_id: Optional[UUID] = Form(None),
    monthly_review_id: Optional[UUID] = Form(None),
    label: Optional[str] = Form(None),
    current_user: User = Depends(require_role(["admin", "gm"])),
    db: AsyncSession = Depends(get_db_session),
    attachment_service: AttachmentService = Depends(get_attachment_service)
) -> dict:
    """Upload file attachment to proof point or monthly review"""
    # Validate exactly one parent is provided
    if not (proof_point_id or monthly_review_id) or (proof_point_id and monthly_review_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "VALIDATION_ERROR", "message": "Exactly one of proof_point_id or monthly_review_id must be provided"}
        )
    
    # Get VBU for authorization with single query
    vbu_id = None
    entity_type = None
    entity_id = None
    
    if proof_point_id:
        result = await db.execute(
            select(VBU.id, VBU.gm_id)
            .select_from(ProofPoint)
            .join(Thesis, ProofPoint.thesis_id == Thesis.id)
            .join(Canvas, Thesis.canvas_id == Canvas.id)
            .join(VBU, Canvas.vbu_id == VBU.id)
            .where(ProofPoint.id == proof_point_id)
        )
        row = result.first()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proof point not found")
        
        vbu_id = row.id
        entity_type = "proof_point"
        entity_id = proof_point_id
        
        # Check GM ownership
        if current_user.role == UserRole.GM and row.gm_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    elif monthly_review_id:
        result = await db.execute(
            select(VBU.id, VBU.gm_id)
            .select_from(MonthlyReview)
            .join(Canvas, MonthlyReview.canvas_id == Canvas.id)
            .join(VBU, Canvas.vbu_id == VBU.id)
            .where(MonthlyReview.id == monthly_review_id)
        )
        row = result.first()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monthly review not found")
        
        vbu_id = row.id
        entity_type = "monthly_review"
        entity_id = monthly_review_id
        
        # Check GM ownership
        if current_user.role == UserRole.GM and row.gm_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Upload file
    attachment = await attachment_service.upload(file, vbu_id, entity_type, entity_id, current_user.id, db, label)
    
    return success_response({
        "id": attachment.id,
        "filename": attachment.filename,
        "content_type": attachment.content_type,
        "size_bytes": attachment.size_bytes,
        "label": attachment.label,
        "uploaded_by": attachment.uploaded_by,
        "created_at": attachment.created_at
    })

@router.get("/{attachment_id}")
async def download_attachment(
    attachment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    attachment_service: AttachmentService = Depends(get_attachment_service)
) -> FileResponse:
    """Download attachment file with proper MIME headers"""
    # For admin, allow access to any attachment
    if current_user.role == UserRole.ADMIN:
        return await attachment_service.download(attachment_id, db)
    
    # For GM, check ownership with single query
    if current_user.role == UserRole.GM:
        # Check if attachment belongs to GM's VBU via proof point
        pp_result = await db.execute(
            select(VBU.gm_id)
            .select_from(Attachment)
            .join(ProofPoint, Attachment.proof_point_id == ProofPoint.id)
            .join(Thesis, ProofPoint.thesis_id == Thesis.id)
            .join(Canvas, Thesis.canvas_id == Canvas.id)
            .join(VBU, Canvas.vbu_id == VBU.id)
            .where(Attachment.id == attachment_id)
        )
        pp_row = pp_result.first()
        
        # Check if attachment belongs to GM's VBU via monthly review
        mr_result = await db.execute(
            select(VBU.gm_id)
            .select_from(Attachment)
            .join(MonthlyReview, Attachment.monthly_review_id == MonthlyReview.id)
            .join(Canvas, MonthlyReview.canvas_id == Canvas.id)
            .join(VBU, Canvas.vbu_id == VBU.id)
            .where(Attachment.id == attachment_id)
        )
        mr_row = mr_result.first()
        
        if not (pp_row or mr_row):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
        
        gm_id = pp_row.gm_id if pp_row else mr_row.gm_id
        if gm_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Viewer can access any attachment (no additional check needed)
    return await attachment_service.download(attachment_id, db)

@router.delete("/{attachment_id}", status_code=204)
async def delete_attachment(
    attachment_id: UUID,
    current_user: User = Depends(require_role(["admin", "gm"])),
    db: AsyncSession = Depends(get_db_session),
    attachment_service: AttachmentService = Depends(get_attachment_service)
) -> None:
    """Delete attachment file and database record"""
    # Get attachment with relationships for authorization
    result = await db.execute(
        select(Attachment)
        .options(
            selectinload(Attachment.proof_point).selectinload(ProofPoint.thesis).selectinload(Thesis.canvas).selectinload(Canvas.vbu)
        )
        .where(Attachment.id == attachment_id)
    )
    attachment = result.scalar_one_or_none()
    
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    
    # Check authorization
    vbu = None
    if attachment.proof_point:
        vbu = attachment.proof_point.thesis.canvas.vbu
    elif attachment.monthly_review_id:
        # Need to load monthly review relationship
        result = await db.execute(
            select(MonthlyReview)
            .options(selectinload(MonthlyReview.canvas).selectinload(Canvas.vbu))
            .where(MonthlyReview.id == attachment.monthly_review_id)
        )
        monthly_review = result.scalar_one_or_none()
        if monthly_review:
            vbu = monthly_review.canvas.vbu
    
    if not vbu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated VBU not found")
    
    # Check GM ownership
    if current_user.role == UserRole.GM and vbu.gm_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    await attachment_service.delete(attachment_id, db)