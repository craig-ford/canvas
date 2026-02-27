import os
import uuid
import re
from pathlib import Path
from typing import Optional
from uuid import UUID
from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from canvas.models.attachment import Attachment
from canvas.config import Settings


class AttachmentService:
    """File attachment service with validation and storage"""
    
    def __init__(self, settings: Settings):
        self.upload_dir = Path(settings.upload_dir)
        self.max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
        self.allowed_types = {
            "image/png", "image/jpeg", "image/gif",
            "application/pdf", "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        }
    
    async def upload(self, file: UploadFile, vbu_id: Optional[UUID], entity_type: str, entity_id: Optional[UUID], uploaded_by: UUID, db: AsyncSession, label: Optional[str] = None) -> Attachment:
        """Upload file with validation and storage"""
        self._validate_file(file)
        
        # Sanitize filename to prevent path traversal
        safe_filename = self._sanitize_filename(file.filename)
        storage_subdir = str(vbu_id) if vbu_id else "standalone"
        storage_path = self._generate_storage_path(storage_subdir, entity_type, safe_filename)
        await self._save_file(file, storage_path)
        
        # Determine which field to set based on entity_type
        proof_point_id = entity_id if entity_type == "proof_point" else None
        monthly_review_id = entity_id if entity_type == "monthly_review" else None
        
        attachment = Attachment(
            proof_point_id=proof_point_id,
            monthly_review_id=monthly_review_id,
            filename=safe_filename,
            storage_path=str(storage_path),
            content_type=file.content_type,
            size_bytes=file.size,
            label=label,
            uploaded_by=uploaded_by
        )
        
        db.add(attachment)
        await db.commit()
        await db.refresh(attachment)
        
        return attachment
    
    async def download(self, attachment_id: UUID, db: AsyncSession) -> FileResponse:
        """Download file with authorization check"""
        result = await db.execute(select(Attachment).where(Attachment.id == attachment_id))
        attachment = result.scalar_one_or_none()
        
        if not attachment:
            raise HTTPException(status_code=404, detail="Attachment not found")
        
        storage_path = Path(attachment.storage_path)
        if not storage_path.exists():
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        return FileResponse(
            path=str(storage_path),
            media_type=attachment.content_type,
            filename=attachment.filename
        )
    
    async def delete(self, attachment_id: UUID, db: AsyncSession) -> None:
        """Delete file from storage and database"""
        result = await db.execute(select(Attachment).where(Attachment.id == attachment_id))
        attachment = result.scalar_one_or_none()
        
        if not attachment:
            raise HTTPException(status_code=404, detail="Attachment not found")
        
        # Delete file from filesystem
        storage_path = Path(attachment.storage_path)
        if storage_path.exists():
            storage_path.unlink()
        
        # Delete database record
        await db.delete(attachment)
        await db.commit()
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validate file size and content type"""
        if file.size > self.max_size_bytes:
            raise HTTPException(
                status_code=413,
                detail={"code": "FILE_TOO_LARGE", "message": f"File size exceeds {self.max_size_bytes // (1024*1024)}MB limit"}
            )
        
        if file.content_type not in self.allowed_types:
            raise HTTPException(
                status_code=415,
                detail={"code": "UNSUPPORTED_TYPE", "message": f"Content type {file.content_type} not allowed"}
            )
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal attacks"""
        if not filename:
            return "unnamed_file"
        
        # Remove path separators and dangerous characters
        safe_name = re.sub(r'[^\w\-_\.]', '_', filename)
        safe_name = safe_name.replace('..', '_')
        safe_name = safe_name.strip('.')
        
        # Ensure filename is not empty after sanitization
        if not safe_name or safe_name == '_':
            safe_name = "unnamed_file"
        
        return safe_name
    
    def _generate_storage_path(self, vbu_id: str, entity_type: str, filename: str) -> Path:
        """Generate storage path: /uploads/{vbu_id}/{entity_type}/{uuid}.{ext}"""
        file_uuid = uuid.uuid4()
        file_ext = Path(filename).suffix
        storage_filename = f"{file_uuid}{file_ext}"
        
        storage_path = self.upload_dir / str(vbu_id) / entity_type / storage_filename
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        return storage_path
    
    async def _save_file(self, file: UploadFile, storage_path: Path) -> None:
        """Save uploaded file to disk atomically"""
        temp_path = storage_path.with_suffix(storage_path.suffix + ".tmp")
        
        try:
            with open(temp_path, "wb") as temp_file:
                content = await file.read()
                temp_file.write(content)
            
            temp_path.rename(storage_path)
        except Exception:
            if temp_path.exists():
                temp_path.unlink()
            raise