import uuid
from datetime import datetime
from canvas.models import TimestampMixin


def test_timestamp_mixin_has_id_field():
    """Test TimestampMixin has UUID id field"""
    assert hasattr(TimestampMixin, 'id')
    # Check column type is UUID
    assert TimestampMixin.id.type.python_type == uuid.UUID


def test_timestamp_mixin_has_timestamps():
    """Test TimestampMixin has datetime timestamp fields"""
    assert hasattr(TimestampMixin, 'created_at')
    assert hasattr(TimestampMixin, 'updated_at')
    # Check column types are DateTime
    assert TimestampMixin.created_at.type.python_type == datetime
    assert TimestampMixin.updated_at.type.python_type == datetime