from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from canvas.db import get_db_session
from canvas.auth.dependencies import get_current_user, verify_csrf
from canvas.models.user import User, UserRole
from canvas.models.vbu import VBU
from canvas.services.canvas_service import CanvasService
from canvas.schemas import CanvasUpdate, CanvasResponse, ThesisResponse, ProofPointResponse, AttachmentResponse
from canvas import success_response

router = APIRouter(prefix="/api/vbus", tags=["canvas"])

@router.get("/{vbu_id}/canvas", response_model=dict)
async def get_canvas(
    vbu_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get canvas with nested theses and proof points"""
    # Check VBU exists and authorization
    result = await db.execute(select(VBU).where(VBU.id == vbu_id))
    vbu = result.scalar_one_or_none()
    if not vbu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="VBU not found")
    
    # Check GM ownership
    if current_user.role == UserRole.GM and vbu.gm_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Check group leader ownership
    if current_user.role == UserRole.GROUP_LEADER and vbu.group_leader_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Check viewer scoping
    if current_user.role == UserRole.VIEWER and current_user.vbu_id != vbu_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    service = CanvasService()
    canvas = await service.get_canvas_by_vbu(vbu_id, db)
    
    # Build nested response with theses and proof points
    theses_data = []
    for thesis in sorted(canvas.theses, key=lambda t: t.order):
        proof_points_data = [
            ProofPointResponse(
                id=pp.id,
                description=pp.description,
                notes=pp.notes,
                status=pp.status,
                evidence_note=pp.evidence_note,
                target_review_month=pp.target_review_month,
                attachments=[
                    AttachmentResponse(
                        id=a.id,
                        filename=a.filename,
                        content_type=a.content_type,
                        size_bytes=a.size_bytes,
                        label=a.label,
                        uploaded_by=a.uploaded_by,
                        created_at=a.created_at
                    ) for a in pp.attachments
                ],
                created_at=pp.created_at,
                updated_at=pp.updated_at
            ) for pp in thesis.proof_points
        ]
        
        theses_data.append(ThesisResponse(
            id=thesis.id,
            order=thesis.order,
            text=thesis.text,
            description=thesis.description,
            category_id=thesis.category_id,
            category_name=thesis.category.name if thesis.category else None,
            category_color=thesis.category.color if thesis.category else None,
            proof_points=proof_points_data,
            created_at=thesis.created_at,
            updated_at=thesis.updated_at
        ))
    
    # Filter portfolio_notes for non-admin/non-group-leader users
    portfolio_notes = canvas.portfolio_notes if current_user.role in (UserRole.ADMIN, UserRole.GROUP_LEADER) else None
    
    canvas_response = CanvasResponse(
        id=canvas.id,
        vbu_id=canvas.vbu_id,
        product_name=canvas.product_name,
        lifecycle_lane=canvas.lifecycle_lane,
        success_description=canvas.success_description,
        future_state_intent=canvas.future_state_intent,
        primary_focus=canvas.primary_focus,
        resist_doing=canvas.resist_doing,
        good_discipline=canvas.good_discipline,
        primary_constraint=canvas.primary_constraint,
        currently_testing_type=canvas.currently_testing_type,
        currently_testing_id=canvas.currently_testing_id,
        portfolio_notes=portfolio_notes,
        health_indicator=canvas.health_indicator_cache,
        theses=theses_data,
        created_at=canvas.created_at,
        updated_at=canvas.updated_at,
        updated_by=canvas.updated_by
    )
    
    return success_response(canvas_response)

@router.put("/{vbu_id}/canvas", response_model=dict)
async def update_canvas(
    vbu_id: UUID,
    canvas_data: CanvasUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    _: None = Depends(verify_csrf)
):
    """Update canvas fields"""
    # Check VBU exists and authorization
    result = await db.execute(select(VBU).where(VBU.id == vbu_id))
    vbu = result.scalar_one_or_none()
    if not vbu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="VBU not found")
    
    # Check authorization for updates
    if current_user.role == UserRole.GM and vbu.gm_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if current_user.role == UserRole.GROUP_LEADER and vbu.group_leader_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if current_user.role == UserRole.VIEWER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Filter update data based on role
    update_data = canvas_data.model_dump(exclude_unset=True)
    
    # Remove portfolio_notes for non-admin/non-group-leader users
    if current_user.role not in (UserRole.ADMIN, UserRole.GROUP_LEADER) and "portfolio_notes" in update_data:
        del update_data["portfolio_notes"]
    
    # Map health_indicator to DB column name
    if "health_indicator" in update_data:
        update_data["health_indicator_cache"] = update_data.pop("health_indicator")
    
    service = CanvasService()
    updated_canvas = await service.update_canvas(
        vbu_id=vbu_id,
        canvas_data=update_data,
        updated_by=current_user.id,
        db=db
    )
    
    # Build response (without nested data for update)
    portfolio_notes = updated_canvas.portfolio_notes if current_user.role == UserRole.ADMIN else None
    
    canvas_response = CanvasResponse(
        id=updated_canvas.id,
        vbu_id=updated_canvas.vbu_id,
        product_name=updated_canvas.product_name,
        lifecycle_lane=updated_canvas.lifecycle_lane,
        success_description=updated_canvas.success_description,
        future_state_intent=updated_canvas.future_state_intent,
        primary_focus=updated_canvas.primary_focus,
        resist_doing=updated_canvas.resist_doing,
        good_discipline=updated_canvas.good_discipline,
        primary_constraint=updated_canvas.primary_constraint,
        currently_testing_type=updated_canvas.currently_testing_type,
        currently_testing_id=updated_canvas.currently_testing_id,
        portfolio_notes=portfolio_notes,
        health_indicator=updated_canvas.health_indicator_cache,
        theses=[],  # Empty for update response
        created_at=updated_canvas.created_at,
        updated_at=updated_canvas.updated_at,
        updated_by=updated_canvas.updated_by
    )
    
    return success_response(canvas_response)