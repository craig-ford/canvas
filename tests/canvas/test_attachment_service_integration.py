import pytest
import pytest_asyncio
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
    """Create temporary upload directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def attachment_service(temp_upload_dir):
    """Create AttachmentService with temp directory."""
    settings = Settings(
        database_url="postgresql+asyncpg://canvas:canvas_dev@db:5432/canvas_test",
        cors_origins=["*"],
        secret_key="test",
        upload_dir=str(temp_upload_dir),
        max_upload_size_mb=10
    )
    return AttachmentService(settings)


def _make_upload_file(filename: str, content: bytes, content_type: str) -> UploadFile:
    """Create UploadFile with proper headers for content_type."""
    from starlette.datastructures import Headers
    headers = Headers({"content-type": content_type})
    return UploadFile(file=io.BytesIO(content), size=len(content), filename=filename, headers=headers)


@pytest.fixture
def sample_png_file():
    """Create sample PNG file."""
    content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
    return _make_upload_file("test.png", content, "image/png")


class TestAttachmentServiceIntegration:
    """Integration tests for AttachmentService with real filesystem."""

    @pytest.mark.asyncio
    async def test_upload_valid_file(
        self, db_session: AsyncSession, sample_user: User,
        attachment_service: AttachmentService, sample_png_file: UploadFile,
        sample_vbu, sample_proof_point
    ):
        """Test successful file upload creates attachment record and saves file."""
        attachment = await attachment_service.upload(
            file=sample_png_file,
            vbu_id=sample_vbu.id,
            entity_type="proof_point",
            entity_id=sample_proof_point.id,
            uploaded_by=sample_user.id,
            db=db_session,
            label="Test image"
        )

        assert attachment.filename == "test.png"
        assert attachment.content_type == "image/png"
        assert attachment.label == "Test image"
        assert attachment.uploaded_by == sample_user.id

    @pytest.mark.asyncio
    async def test_upload_file_too_large(
        self, db_session: AsyncSession, sample_user: User,
        attachment_service: AttachmentService, sample_vbu, sample_proof_point
    ):
        """Test file size validation rejects files over max size."""
        large_content = b'x' * (11 * 1024 * 1024)
        large_file = _make_upload_file("large.png", large_content, "image/png")

        with pytest.raises(HTTPException) as exc_info:
            await attachment_service.upload(
                file=large_file,
                vbu_id=sample_vbu.id,
                entity_type="proof_point",
                entity_id=sample_proof_point.id,
                uploaded_by=sample_user.id,
                db=db_session
            )

        assert exc_info.value.status_code == 413

    @pytest.mark.asyncio
    async def test_upload_invalid_content_type(
        self, db_session: AsyncSession, sample_user: User,
        attachment_service: AttachmentService, sample_vbu, sample_proof_point
    ):
        """Test content type validation rejects unsupported types."""
        invalid_file = _make_upload_file("test.exe", b"content", "application/x-executable")

        with pytest.raises(HTTPException) as exc_info:
            await attachment_service.upload(
                file=invalid_file,
                vbu_id=sample_vbu.id,
                entity_type="proof_point",
                entity_id=sample_proof_point.id,
                uploaded_by=sample_user.id,
                db=db_session
            )

        assert exc_info.value.status_code == 415

    @pytest.mark.asyncio
    async def test_download_nonexistent_file(self, db_session: AsyncSession, attachment_service: AttachmentService):
        """Test download of non-existent attachment raises 404."""
        with pytest.raises(HTTPException) as exc_info:
            await attachment_service.download(uuid4(), db_session)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_download_existing_file(
        self, db_session: AsyncSession, sample_user: User,
        attachment_service: AttachmentService, sample_png_file: UploadFile,
        sample_vbu, sample_proof_point
    ):
        """Test file download returns FileResponse with correct metadata."""
        attachment = await attachment_service.upload(
            file=sample_png_file,
            vbu_id=sample_vbu.id,
            entity_type="proof_point",
            entity_id=sample_proof_point.id,
            uploaded_by=sample_user.id,
            db=db_session
        )

        response = await attachment_service.download(attachment.id, db_session)
        assert response.media_type == "image/png"
        assert response.filename == "test.png"

    @pytest.mark.asyncio
    async def test_delete_existing_file(
        self, db_session: AsyncSession, sample_user: User,
        attachment_service: AttachmentService, sample_png_file: UploadFile,
        sample_vbu, sample_proof_point
    ):
        """Test file deletion removes both filesystem file and database record."""
        attachment = await attachment_service.upload(
            file=sample_png_file,
            vbu_id=sample_vbu.id,
            entity_type="proof_point",
            entity_id=sample_proof_point.id,
            uploaded_by=sample_user.id,
            db=db_session
        )

        storage_path = Path(attachment.storage_path)
        assert storage_path.exists()

        await attachment_service.delete(attachment.id, db_session)

        assert not storage_path.exists()
        result = await db_session.get(Attachment, attachment.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_storage_path_generation(
        self, db_session: AsyncSession, sample_user: User,
        attachment_service: AttachmentService, sample_png_file: UploadFile,
        sample_vbu, sample_proof_point
    ):
        """Test storage path follows expected directory structure."""
        attachment = await attachment_service.upload(
            file=sample_png_file,
            vbu_id=sample_vbu.id,
            entity_type="proof_point",
            entity_id=sample_proof_point.id,
            uploaded_by=sample_user.id,
            db=db_session
        )

        expected_prefix = str(Path(attachment_service.upload_dir) / str(sample_vbu.id) / "proof_point")
        assert str(attachment.storage_path).startswith(expected_prefix)
        assert attachment.storage_path.endswith(".png")
