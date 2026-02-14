from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from canvas.db import get_db_session
from canvas.auth.dependencies import get_current_user, require_role
from canvas.models.user import User, UserRole
from canvas.models.vbu import VBU
from canvas.services.canvas_service import CanvasService
from canvas.pdf.service import PDFService
from canvas.schemas import VBUCreate, VBUUpdate, VBUResponse
from canvas import success_response, list_response

router = APIRouter(prefix="/api/vbus", tags=["vbu"])

@router.get("", response_model=dict)
async def list_vbus(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """List VBUs filtered by user role"""
    service = CanvasService()
    vbus = await service.list_vbus(current_user, db)
    
    # Apply pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_vbus = vbus[start:end]
    
    vbu_responses = [
        VBUResponse(
            id=vbu.id,
            name=vbu.name,
            gm_id=vbu.gm_id,
            gm_name=vbu.gm.name,
            created_at=vbu.created_at,
            updated_at=vbu.updated_at,
            updated_by=vbu.updated_by
        ) for vbu in paginated_vbus
    ]
    
    return list_response(vbu_responses, len(vbus), page, per_page)

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_vbu(
    vbu_data: VBUCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db_session)
):
    """Create VBU (admin only)"""
    service = CanvasService()
    vbu = await service.create_vbu(
        name=vbu_data.name,
        gm_id=vbu_data.gm_id,
        created_by=current_user.id,
        db=db
    )
    
    # Load gm relationship for response
    await db.refresh(vbu, ["gm"])
    
    vbu_response = VBUResponse(
        id=vbu.id,
        name=vbu.name,
        gm_id=vbu.gm_id,
        gm_name=vbu.gm.name,
        created_at=vbu.created_at,
        updated_at=vbu.updated_at,
        updated_by=vbu.updated_by
    )
    
    return success_response(vbu_response, status.HTTP_201_CREATED)

@router.get("/{vbu_id}", response_model=dict)
async def get_vbu(
    vbu_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get VBU by ID"""
    # Get VBU and check authorization
    result = await db.execute(
        select(VBU).options(selectinload(VBU.gm)).where(VBU.id == vbu_id)
    )
    vbu = result.scalar_one_or_none()
    if not vbu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="VBU not found")
    
    # Check GM ownership
    if current_user.role == UserRole.GM and vbu.gm_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    vbu_response = VBUResponse(
        id=vbu.id,
        name=vbu.name,
        gm_id=vbu.gm_id,
        gm_name=vbu.gm.name,
        created_at=vbu.created_at,
        updated_at=vbu.updated_at,
        updated_by=vbu.updated_by
    )
    
    return success_response(vbu_response)

@router.patch("/{vbu_id}", response_model=dict)
async def update_vbu(
    vbu_id: UUID,
    vbu_data: VBUUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update VBU (admin or GM owner)"""
    # Check VBU exists and authorization
    result = await db.execute(
        select(VBU).options(selectinload(VBU.gm)).where(VBU.id == vbu_id)
    )
    vbu = result.scalar_one_or_none()
    if not vbu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="VBU not found")
    
    # Check authorization
    if current_user.role == UserRole.GM and vbu.gm_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if current_user.role == UserRole.VIEWER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Admin can update all fields, GM can only update name
    service = CanvasService()
    updated_vbu = await service.update_vbu(
        vbu_id=vbu_id,
        name=vbu_data.name,
        gm_id=vbu_data.gm_id if current_user.role == UserRole.ADMIN else None,
        updated_by=current_user.id,
        db=db
    )
    
    # Load gm relationship for response
    await db.refresh(updated_vbu, ["gm"])
    
    vbu_response = VBUResponse(
        id=updated_vbu.id,
        name=updated_vbu.name,
        gm_id=updated_vbu.gm_id,
        gm_name=updated_vbu.gm.name,
        created_at=updated_vbu.created_at,
        updated_at=updated_vbu.updated_at,
        updated_by=updated_vbu.updated_by
    )
    
    return success_response(vbu_response)

@router.delete("/{vbu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vbu(
    vbu_id: UUID,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete VBU (admin only)"""
    service = CanvasService()
    await service.delete_vbu(vbu_id, db)

@router.get("/{vbu_id}/canvas/pdf")
async def export_canvas_pdf(
    vbu_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> Response:
    """Export canvas as PDF with role-based access control.
    
    Returns:
        PDF file with proper Content-Type and filename headers
        
    Raises:
        404: VBU not found or access denied
        500: PDF generation failed
    """
    # Get VBU and check authorization
    result = await db.execute(
        select(VBU).options(selectinload(VBU.canvas)).where(VBU.id == vbu_id)
    )
    vbu = result.scalar_one_or_none()
    if not vbu:
        raise HTTPException(status_code=404, detail="VBU not found")
    
    # Check GM ownership
    if current_user.role == UserRole.GM and vbu.gm_id != current_user.id:
        raise HTTPException(status_code=404, detail="VBU not found")
    
    if not vbu.canvas:
        raise HTTPException(status_code=404, detail="Canvas not found")
    
    try:
        pdf_service = PDFService(db)
        pdf_bytes = await pdf_service.export_canvas(vbu.canvas.id)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{vbu.name}_canvas.pdf"',
                "Content-Length": str(len(pdf_bytes))
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="PDF generation failed")