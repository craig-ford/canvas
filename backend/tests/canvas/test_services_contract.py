import inspect
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
from canvas.services.canvas_service import CanvasService as ActualCanvasService
from canvas.services.attachment_service import AttachmentService as ActualAttachmentService

class CanvasService:
    """Canvas management service interface"""
    
    async def create_vbu(self, name: str, gm_id: UUID, created_by: UUID, db: AsyncSession) -> VBU:
        """Create new VBU with associated canvas"""
        pass
    
    async def update_vbu(self, vbu_id: UUID, name: Optional[str], gm_id: Optional[UUID], updated_by: UUID, db: AsyncSession) -> VBU:
        """Update VBU details"""
        pass
    
    async def delete_vbu(self, vbu_id: UUID, db: AsyncSession) -> None:
        """Delete VBU and cascade to canvas"""
        pass
    
    async def list_vbus(self, current_user: User, db: AsyncSession) -> List[VBU]:
        """List VBUs filtered by user role"""
        pass
    
    async def get_canvas_by_vbu(self, vbu_id: UUID, db: AsyncSession) -> Canvas:
        """Get canvas with nested theses and proof points"""
        pass
    
    async def update_canvas(self, vbu_id: UUID, canvas_data: dict, updated_by: UUID, db: AsyncSession) -> Canvas:
        """Update canvas fields"""
        pass
    
    async def create_thesis(self, canvas_id: UUID, text: str, order: int, db: AsyncSession) -> Thesis:
        """Create thesis with order validation"""
        pass
    
    async def update_thesis(self, thesis_id: UUID, text: str, db: AsyncSession) -> Thesis:
        """Update thesis text"""
        pass
    
    async def delete_thesis(self, thesis_id: UUID, db: AsyncSession) -> None:
        """Delete thesis and cascade to proof points"""
        pass
    
    async def reorder_theses(self, canvas_id: UUID, thesis_orders: List[dict], db: AsyncSession) -> List[Thesis]:
        """Reorder theses with constraint validation"""
        pass
    
    async def create_proof_point(self, thesis_id: UUID, description: str, status: str, evidence_note: Optional[str], target_review_month: Optional[str], db: AsyncSession) -> ProofPoint:
        """Create proof point"""
        pass
    
    async def update_proof_point(self, proof_point_id: UUID, description: Optional[str], status: Optional[str], evidence_note: Optional[str], target_review_month: Optional[str], db: AsyncSession) -> ProofPoint:
        """Update proof point fields"""
        pass
    
    async def delete_proof_point(self, proof_point_id: UUID, db: AsyncSession) -> None:
        """Delete proof point and cascade to attachments"""
        pass

class AttachmentService:
    """File attachment service interface (cross-cutting contract)"""
    
    async def upload(self, file: UploadFile, vbu_id: UUID, entity_type: str, entity_id: UUID, uploaded_by: UUID, db: AsyncSession, label: Optional[str] = None) -> Attachment:
        """Upload file with validation and storage"""
        pass
    
    async def download(self, attachment_id: UUID, db: AsyncSession) -> FileResponse:
        """Download file with authorization check"""
        pass
    
    async def delete(self, attachment_id: UUID, db: AsyncSession) -> None:
        """Delete file from storage and database"""
        pass

def test_canvas_service_interface():
    """Verify CanvasService has all required methods with correct signatures"""
    # Verify all required methods exist
    assert hasattr(ActualCanvasService, 'create_vbu')
    assert hasattr(ActualCanvasService, 'update_vbu')
    assert hasattr(ActualCanvasService, 'delete_vbu')
    assert hasattr(ActualCanvasService, 'list_vbus')
    assert hasattr(ActualCanvasService, 'get_canvas_by_vbu')
    assert hasattr(ActualCanvasService, 'update_canvas')
    assert hasattr(ActualCanvasService, 'create_thesis')
    assert hasattr(ActualCanvasService, 'update_thesis')
    assert hasattr(ActualCanvasService, 'delete_thesis')
    assert hasattr(ActualCanvasService, 'reorder_theses')
    assert hasattr(ActualCanvasService, 'create_proof_point')
    assert hasattr(ActualCanvasService, 'update_proof_point')
    assert hasattr(ActualCanvasService, 'delete_proof_point')
    
    # Verify method signatures match interface
    create_vbu_sig = inspect.signature(ActualCanvasService.create_vbu)
    assert len(create_vbu_sig.parameters) == 5  # self, name, gm_id, created_by, db
    assert 'name' in create_vbu_sig.parameters
    assert 'gm_id' in create_vbu_sig.parameters
    assert 'created_by' in create_vbu_sig.parameters
    assert 'db' in create_vbu_sig.parameters

def test_attachment_service_interface():
    """Verify AttachmentService has all required methods with correct signatures"""
    # Verify all required methods exist
    assert hasattr(ActualAttachmentService, 'upload')
    assert hasattr(ActualAttachmentService, 'download')
    assert hasattr(ActualAttachmentService, 'delete')
    
    # Verify method signatures match interface
    upload_sig = inspect.signature(ActualAttachmentService.upload)
    assert len(upload_sig.parameters) == 8  # self, file, vbu_id, entity_type, entity_id, uploaded_by, db, label
    assert 'file' in upload_sig.parameters
    assert 'vbu_id' in upload_sig.parameters
    assert 'entity_type' in upload_sig.parameters
    assert 'entity_id' in upload_sig.parameters
    assert 'uploaded_by' in upload_sig.parameters
    assert 'db' in upload_sig.parameters
    assert 'label' in upload_sig.parameters