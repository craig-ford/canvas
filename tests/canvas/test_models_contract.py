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


def test_canvas_model_contract():
    """Canvas model has required fields and relationships."""
    from canvas.models.canvas import Canvas
    
    assert hasattr(Canvas, 'id')
    assert hasattr(Canvas, 'vbu_id')
    assert hasattr(Canvas, 'lifecycle_lane')
    assert hasattr(Canvas, 'currently_testing_type')
    assert hasattr(Canvas, 'currently_testing_id')
    assert hasattr(Canvas, 'theses')


def test_thesis_model_contract():
    """Thesis model has required fields and relationships."""
    from canvas.models.thesis import Thesis
    
    assert hasattr(Thesis, 'id')
    assert hasattr(Thesis, 'canvas_id')
    assert hasattr(Thesis, 'order')
    assert hasattr(Thesis, 'text')
    assert hasattr(Thesis, 'proof_points')


def test_proof_point_model_contract():
    """ProofPoint model has required fields and relationships."""
    from canvas.models.proof_point import ProofPoint
    
    assert hasattr(ProofPoint, 'id')
    assert hasattr(ProofPoint, 'thesis_id')
    assert hasattr(ProofPoint, 'description')
    assert hasattr(ProofPoint, 'status')
    assert hasattr(ProofPoint, 'attachments')


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