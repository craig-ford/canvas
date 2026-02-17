# TODO: ARCHITECTURAL DEBT - This service violates SRP by handling VBU, Canvas, Thesis, and ProofPoint operations
# Future refactor: Split into VBUService, CanvasService, ThesisService, ProofPointService
# Each service should handle only its domain entity and related operations
# This is functional code that works correctly but should be refactored for maintainability

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, update, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from canvas.models.user import User, UserRole
from canvas.models.vbu import VBU
from canvas.models.canvas import Canvas, LifecycleLane
from canvas.models.thesis import Thesis
from canvas.models.proof_point import ProofPoint, ProofPointStatus

class CanvasService:
    async def create_vbu(self, name: str, gm_id: UUID, created_by: UUID, db: AsyncSession) -> VBU:
        """Create VBU with auto-created canvas"""
        # Verify GM exists
        gm_result = await db.execute(select(User).where(User.id == gm_id))
        if not gm_result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid gm_id: user not found")
        
        vbu = VBU(name=name.strip(), gm_id=gm_id, updated_by=created_by)
        db.add(vbu)
        await db.flush()
        
        canvas = Canvas(vbu_id=vbu.id, lifecycle_lane=LifecycleLane.BUILD, updated_by=created_by)
        db.add(canvas)
        await db.commit()
        await db.refresh(vbu)
        return vbu

    async def update_vbu(self, vbu_id: UUID, name: Optional[str], gm_id: Optional[UUID], updated_by: UUID, db: AsyncSession) -> VBU:
        """Update VBU details"""
        result = await db.execute(select(VBU).where(VBU.id == vbu_id))
        vbu = result.scalar_one_or_none()
        if not vbu:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="VBU not found")
        
        if name is not None:
            vbu.name = name.strip()
        if gm_id is not None:
            vbu.gm_id = gm_id
        vbu.updated_by = updated_by
        await db.commit()
        await db.refresh(vbu)
        return vbu

    async def delete_vbu(self, vbu_id: UUID, db: AsyncSession) -> None:
        """Delete VBU and cascade to canvas"""
        result = await db.execute(select(VBU).where(VBU.id == vbu_id))
        vbu = result.scalar_one_or_none()
        if not vbu:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="VBU not found")
        
        await db.delete(vbu)
        await db.commit()

    async def list_vbus(self, current_user: User, db: AsyncSession) -> List[VBU]:
        """List VBUs filtered by user role with eager loading"""
        query = select(VBU).options(
            selectinload(VBU.gm),
            selectinload(VBU.canvas).selectinload(Canvas.theses).selectinload(Thesis.proof_points)
        )
        if current_user.role == UserRole.GM:
            query = query.where(VBU.gm_id == current_user.id)
        
        result = await db.execute(query.order_by(VBU.name))
        return list(result.scalars().all())

    async def list_vbus_paginated(self, current_user: User, page: int, per_page: int, db: AsyncSession) -> tuple[List[VBU], int]:
        """List VBUs with pagination and role-based filtering"""
        from sqlalchemy import func
        
        # Build query with role-based filtering
        query = select(VBU).options(selectinload(VBU.gm))
        count_query = select(func.count(VBU.id))
        
        if current_user.role == UserRole.GM:
            query = query.where(VBU.gm_id == current_user.id)
            count_query = count_query.where(VBU.gm_id == current_user.id)
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * per_page
        paginated_query = query.order_by(VBU.name).offset(offset).limit(per_page)
        
        result = await db.execute(paginated_query)
        vbus = list(result.scalars().all())
        
        return vbus, total

    async def get_canvas_by_vbu(self, vbu_id: UUID, db: AsyncSession) -> Canvas:
        """Get canvas with nested theses and proof points"""
        result = await db.execute(
            select(Canvas)
            .options(
                selectinload(Canvas.theses).selectinload(Thesis.proof_points)
            )
            .where(Canvas.vbu_id == vbu_id)
        )
        canvas = result.scalar_one_or_none()
        if not canvas:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canvas not found")
        return canvas

    async def update_canvas(self, vbu_id: UUID, canvas_data: Dict[str, Any], updated_by: UUID, db: AsyncSession) -> Canvas:
        """Update canvas fields"""
        result = await db.execute(select(Canvas).where(Canvas.vbu_id == vbu_id))
        canvas = result.scalar_one_or_none()
        if not canvas:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canvas not found")
        
        # Validate product_name not empty if provided
        if "product_name" in canvas_data and not canvas_data["product_name"].strip():
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="product_name cannot be empty")
        
        for field, value in canvas_data.items():
            if hasattr(canvas, field):
                setattr(canvas, field, value)
        canvas.updated_by = updated_by
        await db.commit()
        await db.refresh(canvas)
        return canvas

    async def create_thesis(self, canvas_id: UUID, text: str, order: int, db: AsyncSession) -> Thesis:
        """Create thesis with order validation"""
        result = await db.execute(select(Thesis).where(Thesis.canvas_id == canvas_id))
        existing = list(result.scalars().all())
        if len(existing) >= 5:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Maximum 5 theses per canvas")
        
        # Check for duplicate order
        if any(t.order == order for t in existing):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Thesis with order {order} already exists")
        
        thesis = Thesis(canvas_id=canvas_id, text=text.strip(), order=order)
        db.add(thesis)
        await db.commit()
        await db.refresh(thesis)
        return thesis

    async def update_thesis(self, thesis_id: UUID, text: str, db: AsyncSession) -> Thesis:
        """Update thesis text"""
        result = await db.execute(select(Thesis).where(Thesis.id == thesis_id))
        thesis = result.scalar_one_or_none()
        if not thesis:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thesis not found")
        
        thesis.text = text.strip()
        await db.commit()
        await db.refresh(thesis)
        return thesis

    async def delete_thesis(self, thesis_id: UUID, db: AsyncSession) -> None:
        """Delete thesis and cascade to proof points"""
        result = await db.execute(select(Thesis).where(Thesis.id == thesis_id))
        thesis = result.scalar_one_or_none()
        if not thesis:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thesis not found")
        
        await db.delete(thesis)
        await db.commit()

    async def reorder_theses(self, canvas_id: UUID, thesis_orders: List[Dict[str, Any]], db: AsyncSession) -> List[Thesis]:
        """Reorder theses — drop and recreate constraint to allow reorder"""
        if not thesis_orders:
            result = await db.execute(
                select(Thesis).where(Thesis.canvas_id == canvas_id).order_by(Thesis.order)
            )
            return list(result.scalars().all())

        await db.execute(text("ALTER TABLE theses DROP CONSTRAINT IF EXISTS uq_theses_canvas_order"))
        for item in thesis_orders:
            await db.execute(
                update(Thesis)
                .where(Thesis.id == item["id"])
                .values(order=item["order"])
            )
        await db.execute(text(
            'ALTER TABLE theses ADD CONSTRAINT uq_theses_canvas_order UNIQUE (canvas_id, "order") DEFERRABLE INITIALLY IMMEDIATE'
        ))
        await db.commit()
        db.expire_all()

        result = await db.execute(
            select(Thesis)
            .where(Thesis.canvas_id == canvas_id)
            .order_by(Thesis.order)
        )
        return list(result.scalars().all())

    async def create_proof_point(self, thesis_id: UUID, description: str, status: str, evidence_note: Optional[str], target_review_month: Optional[str], db: AsyncSession) -> ProofPoint:
        """Create proof point"""
        target_date = None
        if target_review_month:
            year, month = target_review_month.split('-')
            target_date = datetime(int(year), int(month), 1).date()
        
        proof_point = ProofPoint(
            thesis_id=thesis_id,
            description=description.strip(),
            status=ProofPointStatus(status),
            evidence_note=evidence_note,
            target_review_month=target_date
        )
        db.add(proof_point)
        await db.commit()
        await db.refresh(proof_point)
        return proof_point

    async def update_proof_point(self, proof_point_id: UUID, description: Optional[str], status: Optional[str], evidence_note: Optional[str], target_review_month: Optional[str], db: AsyncSession) -> ProofPoint:
        """Update proof point fields"""
        result = await db.execute(select(ProofPoint).where(ProofPoint.id == proof_point_id))
        proof_point = result.scalar_one_or_none()
        if not proof_point:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proof point not found")
        
        if description is not None:
            proof_point.description = description.strip()
        if status is not None:
            proof_point.status = ProofPointStatus(status)
        if evidence_note is not None:
            proof_point.evidence_note = evidence_note
        if target_review_month is not None:
            year, month = target_review_month.split('-')
            proof_point.target_review_month = datetime(int(year), int(month), 1).date()
        
        await db.commit()
        await db.refresh(proof_point)
        return proof_point

    async def delete_proof_point(self, proof_point_id: UUID, db: AsyncSession) -> None:
        """Delete proof point and cascade to attachments"""
        result = await db.execute(select(ProofPoint).where(ProofPoint.id == proof_point_id))
        proof_point = result.scalar_one_or_none()
        if not proof_point:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proof point not found")
        
        await db.delete(proof_point)
        await db.commit()

    async def get_canvas_by_vbu_id_for_auth(self, canvas_id: UUID, current_user: User, db: AsyncSession) -> Canvas:
        """Get canvas with authorization check"""
        result = await db.execute(
            select(Canvas)
            .options(
                selectinload(Canvas.theses).selectinload(Thesis.proof_points)
            )
            .join(VBU, Canvas.vbu_id == VBU.id)
            .where(Canvas.id == canvas_id)
        )
        canvas = result.scalar_one_or_none()
        if not canvas:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canvas not found")
        
        # Authorization check
        if current_user.role == UserRole.GM:
            vbu_result = await db.execute(select(VBU).where(VBU.id == canvas.vbu_id))
            vbu = vbu_result.scalar_one()
            if vbu.gm_id != current_user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        return canvas

    async def get_theses_by_canvas(self, canvas_id: UUID, db: AsyncSession) -> List[Thesis]:
        """Get theses for canvas ordered by order"""
        result = await db.execute(
            select(Thesis)
            .where(Thesis.canvas_id == canvas_id)
            .order_by(Thesis.order)
        )
        return list(result.scalars().all())

    async def verify_canvas_ownership(self, canvas_id: UUID, current_user: User, db: AsyncSession) -> None:
        """Verify user can modify canvas"""
        if current_user.role == UserRole.ADMIN:
            return
        
        result = await db.execute(
            select(Canvas)
            .join(VBU, Canvas.vbu_id == VBU.id)
            .where(Canvas.id == canvas_id)
        )
        canvas = result.scalar_one_or_none()
        if not canvas:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canvas not found")
        
        vbu_result = await db.execute(select(VBU).where(VBU.id == canvas.vbu_id))
        vbu = vbu_result.scalar_one()
        if vbu.gm_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    async def verify_thesis_ownership(self, thesis_id: UUID, current_user: User, db: AsyncSession) -> None:
        """Verify user can modify thesis"""
        if current_user.role == UserRole.ADMIN:
            return
        
        result = await db.execute(
            select(VBU.gm_id)
            .select_from(Thesis)
            .join(Canvas, Thesis.canvas_id == Canvas.id)
            .join(VBU, Canvas.vbu_id == VBU.id)
            .where(Thesis.id == thesis_id)
        )
        gm_id = result.scalar_one_or_none()
        if not gm_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thesis not found")
        
        if gm_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    async def verify_proof_point_ownership(self, proof_point_id: UUID, current_user: User, db: AsyncSession) -> None:
        """Verify user can modify proof point via thesis→canvas→VBU ownership chain"""
        if current_user.role == UserRole.ADMIN:
            return

        result = await db.execute(
            select(VBU.gm_id)
            .select_from(ProofPoint)
            .join(Thesis, ProofPoint.thesis_id == Thesis.id)
            .join(Canvas, Thesis.canvas_id == Canvas.id)
            .join(VBU, Canvas.vbu_id == VBU.id)
            .where(ProofPoint.id == proof_point_id)
        )
        gm_id = result.scalar_one_or_none()
        if not gm_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proof point not found")

        if gm_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    async def get_proof_points_by_thesis(self, thesis_id: UUID, db: AsyncSession) -> List[ProofPoint]:
        """Get proof points for a thesis ordered by creation date"""
        result = await db.execute(
            select(ProofPoint)
            .where(ProofPoint.thesis_id == thesis_id)
            .order_by(ProofPoint.created_at)
        )
        return list(result.scalars().all())
