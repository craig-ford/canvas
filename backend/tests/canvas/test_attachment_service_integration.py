import pytest
import tempfile
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from canvas.services.attachment_service import AttachmentService
from canvas.models.attachment import Attachment
from canvas.models.user import User
from canvas.config import Settings
import io


@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def attachment_service(temp_upload_dir):
    """Create AttachmentService with temp directory"""
    settings = Settings(
        database_url="sqlite:///:memory:",
        cors_origins=["*"],
        secret_key="test",
        upload_dir=str(temp_upload_dir),
        max_upload_size_mb=10
    )
    return AttachmentService(settings)


@pytest.fixture
def sample_user():
    """Create sample user"""
    return User(
        id=uuid4(),
        email="test@example.com",
        name="Test User",
        role="gm"
    )


@pytest.fixture
def sample_png_file():
    """Create sample PNG file"""
    content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
    return UploadFile(filename="test.png", file=io.BytesIO(content), content_type="image/png")


class TestAttachmentServiceIntegration:
    """Integration tests for AttachmentService with real filesystem"""
    
    async def test_upload_valid_file(self, db_session: AsyncSession, sample_user: User, attachment_service: AttachmentService, sample_png_file: UploadFile):
        """Test successful file upload with validation"""
        vbu_id = uuid4()
        entity_id = uuid4()
        
        attachment = await attachment_service.upload(
            file=sample_png_file,
            vbu_id=vbu_id,
            entity_type="proof_point",
            entity_id=entity_id,
            uploaded_by=sample_user.id,
            db=db_session,
            label="Test image"
        )
        
        assert attachment.filename == "test.png"
        assert attachment.content_type == "image/png"
        assert attachment.label == "Test image"
        assert attachment.uploaded_by == sample_user.id
        assert attachment.proof_point_id == entity_id
        assert attachment.storage_path.startswith(f"/uploads/{vbu_id}/proof_point/")
        assert Path(attachment.storage_path).exists()
    
    async def test_upload_file_too_large(self, db_session: AsyncSession, sample_user: User, attachment_service: AttachmentService):
        """Test file size validation (max 10MB)"""
        large_content = b'x' * (11 * 1024 * 1024)  # 11MB
        large_file = UploadFile(filename="large.png", file=io.BytesIO(large_content), content_type="image/png")
        
        with pytest.raises(HTTPException) as exc_info:
            await attachment_service.upload(
                file=large_file,
                vbu_id=uuid4(),
                entity_type="proof_point",
                entity_id=uuid4(),
                uploaded_by=sample_user.id,
                db=db_session
            )
        
        assert exc_info.value.status_code == 413
        assert "FILE_TOO_LARGE" in str(exc_info.value.detail)
    
    async def test_upload_invalid_content_type(self, db_session: AsyncSession, sample_user: User, attachment_service: AttachmentService):
        """Test content type validation"""
        invalid_file = UploadFile(filename="test.exe", file=io.BytesIO(b"content"), content_type="application/x-executable")
        
        with pytest.raises(HTTPException) as exc_info:
            await attachment_service.upload(
                file=invalid_file,
                vbu_id=uuid4(),
                entity_type="proof_point",
                entity_id=uuid4(),
                uploaded_by=sample_user.id,
                db=db_session
            )
        
        assert exc_info.value.status_code == 415
        assert "UNSUPPORTED_TYPE" in str(exc_info.value.detail)
    
    async def test_download_existing_file(self, db_session: AsyncSession, sample_user: User, attachment_service: AttachmentService, sample_png_file: UploadFile):
        """Test file download with proper headers"""
        attachment = await attachment_service.upload(
            file=sample_png_file,
            vbu_id=uuid4(),
            entity_type="proof_point",
            entity_id=uuid4(),
            uploaded_by=sample_user.id,
            db=db_session
        )
        
        response = await attachment_service.download(attachment.id, db_session)
        
        assert response.path == attachment.storage_path
        assert response.media_type == "image/png"
        assert response.filename == "test.png"
    
    async def test_download_nonexistent_file(self, db_session: AsyncSession, attachment_service: AttachmentService):
        """Test download of non-existent attachment"""
        with pytest.raises(HTTPException) as exc_info:
            await attachment_service.download(uuid4(), db_session)
        
        assert exc_info.value.status_code == 404
    
    async def test_delete_existing_file(self, db_session: AsyncSession, sample_user: User, attachment_service: AttachmentService, sample_png_file: UploadFile):
        """Test file deletion from filesystem and database"""
        attachment = await attachment_service.upload(
            file=sample_png_file,
            vbu_id=uuid4(),
            entity_type="proof_point",
            entity_id=uuid4(),
            uploaded_by=sample_user.id,
            db=db_session
        )
        
        storage_path = Path(attachment.storage_path)
        assert storage_path.exists()
        
        await attachment_service.delete(attachment.id, db_session)
        
        assert not storage_path.exists()
        # Verify database record is deleted
        result = await db_session.get(Attachment, attachment.id)
        assert result is None
    
    async def test_storage_path_generation(self, db_session: AsyncSession, sample_user: User, attachment_service: AttachmentService, sample_png_file: UploadFile):
        """Test storage path follows pattern: /uploads/{vbu_id}/{entity_type}/{uuid}.{ext}"""
        vbu_id = uuid4()
        
        attachment = await attachment_service.upload(
            file=sample_png_file,
            vbu_id=vbu_id,
            entity_type="proof_point",
            entity_id=uuid4(),
            uploaded_by=sample_user.id,
            db=db_session
        )
        
        expected_prefix = f"/uploads/{vbu_id}/proof_point/"
        assert attachment.storage_path.startswith(expected_prefix)
        assert attachment.storage_path.endswith(".png")
        # Verify UUID format in filename
        filename = Path(attachment.storage_path).stem
        assert len(filename) == 36  # UUID length with hyphens