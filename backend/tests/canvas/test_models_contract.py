"""Contract tests for canvas management models."""

def test_vbu_model_contract():
    """VBU model has required fields and relationships."""
    from canvas.models.vbu import VBU
    
    assert hasattr(VBU, 'id')
    assert hasattr(VBU, 'name')
    assert hasattr(VBU, 'gm_id')
    assert hasattr(VBU, 'created_at')
    assert hasattr(VBU, 'updated_at')
    assert hasattr(VBU, 'updated_by')
    assert hasattr(VBU, 'canvas')
    
    # Check column constraints
    assert VBU.name.nullable is False
    assert VBU.gm_id.nullable is False
    assert VBU.updated_by.nullable is True
    # Check FK targets
    assert str(VBU.gm_id.foreign_keys.pop().column) == "users.id"
    assert str(VBU.updated_by.foreign_keys.pop().column) == "users.id"


def test_canvas_model_contract():
    """Canvas model has required fields and relationships."""
    from canvas.models.canvas import Canvas
    
    assert hasattr(Canvas, 'id')
    assert hasattr(Canvas, 'vbu_id')
    assert hasattr(Canvas, 'lifecycle_lane')
    assert hasattr(Canvas, 'currently_testing_type')
    assert hasattr(Canvas, 'currently_testing_id')
    assert hasattr(Canvas, 'theses')
    
    # Check FK constraint
    assert Canvas.vbu_id.nullable is False
    assert str(Canvas.vbu_id.foreign_keys.pop().column) == "vbus.id"
    # Check nullable fields
    assert Canvas.currently_testing_type.nullable is True
    assert Canvas.currently_testing_id.nullable is True


def test_thesis_model_contract():
    """Thesis model has required fields and relationships."""
    from canvas.models.thesis import Thesis
    
    assert hasattr(Thesis, 'id')
    assert hasattr(Thesis, 'canvas_id')
    assert hasattr(Thesis, 'order')
    assert hasattr(Thesis, 'text')
    assert hasattr(Thesis, 'proof_points')
    
    # Check constraints
    assert Thesis.canvas_id.nullable is False
    assert Thesis.order.nullable is False
    assert Thesis.text.nullable is False
    # Check FK target
    assert str(Thesis.canvas_id.foreign_keys.pop().column) == "canvases.id"


def test_proof_point_model_contract():
    """ProofPoint model has required fields and relationships."""
    from canvas.models.proof_point import ProofPoint
    
    assert hasattr(ProofPoint, 'id')
    assert hasattr(ProofPoint, 'thesis_id')
    assert hasattr(ProofPoint, 'description')
    assert hasattr(ProofPoint, 'status')
    assert hasattr(ProofPoint, 'attachments')
    
    # Check constraints
    assert ProofPoint.thesis_id.nullable is False
    assert ProofPoint.description.nullable is False
    assert ProofPoint.status.nullable is False
    # Check FK target
    assert str(ProofPoint.thesis_id.foreign_keys.pop().column) == "theses.id"


def test_attachment_model_contract():
    """Attachment model has required fields and relationships."""
    from canvas.models.attachment import Attachment
    
    assert hasattr(Attachment, 'id')
    assert hasattr(Attachment, 'proof_point_id')
    assert hasattr(Attachment, 'monthly_review_id')
    assert hasattr(Attachment, 'filename')
    assert hasattr(Attachment, 'storage_path')
    assert hasattr(Attachment, 'content_type')
    assert hasattr(Attachment, 'size_bytes')
    assert hasattr(Attachment, 'uploaded_by')
    
    # Check nullable constraints (polymorphic relationship)
    assert Attachment.proof_point_id.nullable is True
    assert Attachment.monthly_review_id.nullable is True
    # Check required fields
    assert Attachment.filename.nullable is False
    assert Attachment.storage_path.nullable is False
    assert Attachment.content_type.nullable is False
    assert Attachment.size_bytes.nullable is False
    assert Attachment.uploaded_by.nullable is False


def test_lifecycle_lane_enum():
    """LifecycleLane enum has required values."""
    from canvas.models.canvas import LifecycleLane
    
    assert hasattr(LifecycleLane, 'BUILD')
    assert hasattr(LifecycleLane, 'SELL')
    assert hasattr(LifecycleLane, 'MILK')
    assert hasattr(LifecycleLane, 'REFRAME')


def test_proof_point_status_enum():
    """ProofPointStatus enum has required values."""
    from canvas.models.proof_point import ProofPointStatus
    
    assert hasattr(ProofPointStatus, 'NOT_STARTED')
    assert hasattr(ProofPointStatus, 'IN_PROGRESS')
    assert hasattr(ProofPointStatus, 'OBSERVED')
    assert hasattr(ProofPointStatus, 'STALLED')


def test_currently_testing_type_enum():
    """CurrentlyTestingType enum has required values."""
    from canvas.models.canvas import CurrentlyTestingType
    
    assert hasattr(CurrentlyTestingType, 'THESIS')
    assert hasattr(CurrentlyTestingType, 'PROOF_POINT')