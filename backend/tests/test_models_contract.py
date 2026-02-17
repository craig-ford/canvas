import uuid
from datetime import datetime
from canvas.models import TimestampMixin


def test_timestamp_mixin_has_id_field():
    """Test TimestampMixin has UUID id field"""
    assert hasattr(TimestampMixin, 'id')
    # Check column type is UUID
    assert TimestampMixin.id.type.python_type == uuid.UUID
    # Check it's primary key
    assert TimestampMixin.id.primary_key is True
    # Check default is uuid4 function
    assert TimestampMixin.id.default.arg.__name__ == 'uuid4'


def test_timestamp_mixin_has_timestamps():
    """Test TimestampMixin has datetime timestamp fields"""
    assert hasattr(TimestampMixin, 'created_at')
    assert hasattr(TimestampMixin, 'updated_at')
    # Check column types are DateTime
    assert TimestampMixin.created_at.type.python_type == datetime
    assert TimestampMixin.updated_at.type.python_type == datetime
    # Check timezone=True
    assert TimestampMixin.created_at.type.timezone is True
    assert TimestampMixin.updated_at.type.timezone is True
    # Check nullable=False
    assert TimestampMixin.created_at.nullable is False
    assert TimestampMixin.updated_at.nullable is False