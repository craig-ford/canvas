from typing import Optional, List
from uuid import UUID
from fastapi import UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from canvas.models.user import User
from canvas.models.vbu import VBU
from canvas.models.canvas import Canvas
from canvas.models.thesis import Thesis
from canvas.models.proof_point import ProofPoint
from canvas.models.attachment import Attachment

class CanvasService:
    """Canvas management service interface"""
    
    async def create_vbu(self, name: str, gm_id: UUID, created_by: UUID, db: AsyncSession) -> VBU:
        """Create new VBU with associated canvas"""
        ...
    
    async def update_vbu(self, vbu_id: UUID, name: Optional[str], gm_id: Optional[UUID], updated_by: UUID, db: AsyncSession) -> VBU:
        """Update VBU details"""
        ...
    
    async def delete_vbu(self, vbu_id: UUID, db: AsyncSession) -> None:
        """Delete VBU and cascade to canvas"""
        ...
    
    async def list_vbus(self, current_user: User, db: AsyncSession) -> List[VBU]:
        """List VBUs filtered by user role"""
        ...
    
    async def get_canvas_by_vbu(self, vbu_id: UUID, db: AsyncSession) -> Canvas:
        """Get canvas with nested theses and proof points"""
        ...
    
    async def update_canvas(self, vbu_id: UUID, canvas_data: dict, updated_by: UUID, db: AsyncSession) -> Canvas:
        """Update canvas fields"""
        ...
    
    async def create_thesis(self, canvas_id: UUID, text: str, order: int, db: AsyncSession) -> Thesis:
        """Create thesis with order validation"""
        ...
    
    async def update_thesis(self, thesis_id: UUID, text: str, db: AsyncSession) -> Thesis:
        """Update thesis text"""
        ...
    
    async def delete_thesis(self, thesis_id: UUID, db: AsyncSession) -> None:
        """Delete thesis and cascade to proof points"""
        ...
    
    async def reorder_theses(self, canvas_id: UUID, thesis_orders: List[dict], db: AsyncSession) -> List[Thesis]:
        """Reorder theses with constraint validation"""
        ...
    
    async def create_proof_point(self, thesis_id: UUID, description: str, status: str, evidence_note: Optional[str], target_review_month: Optional[str], db: AsyncSession) -> ProofPoint:
        """Create proof point"""
        ...
    
    async def update_proof_point(self, proof_point_id: UUID, description: Optional[str], status: Optional[str], evidence_note: Optional[str], target_review_month: Optional[str], db: AsyncSession) -> ProofPoint:
        """Update proof point fields"""
        ...
    
    async def delete_proof_point(self, proof_point_id: UUID, db: AsyncSession) -> None:
        """Delete proof point and cascade to attachments"""
        ...

class AttachmentService:
    """File attachment service interface (cross-cutting contract)"""
    
    async def upload(self, file: UploadFile, vbu_id: UUID, entity_type: str, entity_id: UUID, uploaded_by: UUID, db: AsyncSession, label: Optional[str] = None) -> Attachment:
        """Upload file with validation and storage"""
        ...
    
    async def download(self, attachment_id: UUID, db: AsyncSession) -> FileResponse:
        """Download file with authorization check"""
        ...
    
    async def delete(self, attachment_id: UUID, db: AsyncSession) -> None:
        """Delete file from storage and database"""
        ...

def test_canvas_service_interface():
    """Verify CanvasService has all required methods"""
    assert hasattr(CanvasService, 'create_vbu')
    assert hasattr(CanvasService, 'update_vbu')
    assert hasattr(CanvasService, 'delete_vbu')
    assert hasattr(CanvasService, 'list_vbus')
    assert hasattr(CanvasService, 'get_canvas_by_vbu')
    assert hasattr(CanvasService, 'update_canvas')
    assert hasattr(CanvasService, 'create_thesis')
    assert hasattr(CanvasService, 'update_thesis')
    assert hasattr(CanvasService, 'delete_thesis')
    assert hasattr(CanvasService, 'reorder_theses')
    assert hasattr(CanvasService, 'create_proof_point')
    assert hasattr(CanvasService, 'update_proof_point')
    assert hasattr(CanvasService, 'delete_proof_point')

def test_attachment_service_interface():
    """Verify AttachmentService has all required methods"""
    assert hasattr(AttachmentService, 'upload')
    assert hasattr(AttachmentService, 'download')
    assert hasattr(AttachmentService, 'delete')