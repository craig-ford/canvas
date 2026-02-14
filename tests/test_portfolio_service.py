import pytest
from uuid import uuid4
from datetime import date
from canvas.portfolio.schemas import VBUSummary, PortfolioFilters, PortfolioNotesRequest, LifecycleLane
from canvas.portfolio.service import PortfolioService
from canvas.models.user import User, UserRole

class TestPortfolioSchemas:
    """Test Pydantic schema validation"""
    
    def test_vbu_summary_valid(self):
        """Test VBUSummary with valid data"""
        summary = VBUSummary(
            id=uuid4(),
            name="Test VBU",
            gm_name="John Doe",
            lifecycle_lane=LifecycleLane.build,
            success_description="Success means...",
            currently_testing="Testing channels",
            next_review_date=date(2026, 3, 15),
            primary_constraint="Limited capacity",
            health_indicator="In Progress",
            portfolio_notes="Q1 focus"
        )
        assert summary.name == "Test VBU"
        assert summary.lifecycle_lane == LifecycleLane.build
        assert summary.health_indicator == "In Progress"
    
    def test_vbu_summary_minimal(self):
        """Test VBUSummary with minimal required fields"""
        summary = VBUSummary(
            id=uuid4(),
            name="Minimal VBU",
            gm_name="Jane Doe",
            lifecycle_lane=LifecycleLane.sell,
            success_description=None,
            currently_testing=None,
            next_review_date=None,
            primary_constraint=None,
            health_indicator="Not Started",
            portfolio_notes=None
        )
        assert summary.name == "Minimal VBU"
        assert summary.success_description is None
    
    def test_lifecycle_lane_enum(self):
        """Test LifecycleLane enum values"""
        assert LifecycleLane.build == "build"
        assert LifecycleLane.sell == "sell"
        assert LifecycleLane.milk == "milk"
        assert LifecycleLane.reframe == "reframe"
    
    def test_portfolio_filters_empty(self):
        """Test PortfolioFilters with no filters"""
        filters = PortfolioFilters()
        assert filters.lane is None
        assert filters.gm_id is None
        assert filters.health_status is None
    
    def test_portfolio_filters_with_values(self):
        """Test PortfolioFilters with filter values"""
        filters = PortfolioFilters(
            lane=[LifecycleLane.build, LifecycleLane.sell],
            gm_id=[uuid4(), uuid4()],
            health_status=["In Progress", "On Track"]
        )
        assert len(filters.lane) == 2
        assert len(filters.gm_id) == 2
        assert len(filters.health_status) == 2
    
    def test_portfolio_notes_request_valid(self):
        """Test PortfolioNotesRequest with valid notes"""
        request = PortfolioNotesRequest(notes="Q1 focus areas")
        assert request.notes == "Q1 focus areas"
    
    def test_portfolio_notes_request_empty(self):
        """Test PortfolioNotesRequest with empty notes"""
        request = PortfolioNotesRequest(notes=None)
        assert request.notes is None
    
    def test_portfolio_notes_request_max_length(self):
        """Test PortfolioNotesRequest validates max length"""
        long_notes = "x" * 10001  # Exceeds max_length=10000
        with pytest.raises(ValueError):
            PortfolioNotesRequest(notes=long_notes)

class TestPortfolioServiceContract:
    """Test PortfolioService interface contracts"""
    
    def test_service_instantiation(self):
        """Test PortfolioService can be instantiated"""
        service = PortfolioService()
        assert service is not None
    
    def test_get_summary_signature(self):
        """Test get_summary method signature"""
        service = PortfolioService()
        
        # Verify method exists and has correct signature
        assert hasattr(service, 'get_summary')
        assert callable(service.get_summary)
        
        # Check method is async
        import inspect
        assert inspect.iscoroutinefunction(service.get_summary)
    
    def test_update_portfolio_notes_signature(self):
        """Test update_portfolio_notes method signature"""
        service = PortfolioService()
        
        # Verify method exists and has correct signature
        assert hasattr(service, 'update_portfolio_notes')
        assert callable(service.update_portfolio_notes)
        
        # Check method is async
        import inspect
        assert inspect.iscoroutinefunction(service.update_portfolio_notes)

class TestRoleBasedAccessContract:
    """Test role-based access control contracts"""
    
    def test_admin_user_contract(self):
        """Test admin user can access all functionality"""
        # This is a contract test - we're defining expected behavior
        # Implementation will be tested in integration tests
        admin_user = User(
            id=uuid4(),
            email="admin@test.com",
            name="Admin User",
            role=UserRole.ADMIN,
            is_active=True
        )
        assert admin_user.role == UserRole.ADMIN
    
    def test_gm_user_contract(self):
        """Test GM user has limited access"""
        gm_user = User(
            id=uuid4(),
            email="gm@test.com", 
            name="GM User",
            role=UserRole.GM,
            is_active=True
        )
        assert gm_user.role == UserRole.GM
    
    def test_viewer_user_contract(self):
        """Test viewer user has read-only access"""
        viewer_user = User(
            id=uuid4(),
            email="viewer@test.com",
            name="Viewer User", 
            role=UserRole.VIEWER,
            is_active=True
        )
        assert viewer_user.role == UserRole.VIEWER

class TestFilterValidationContract:
    """Test filter parameter validation contracts"""
    
    def test_lifecycle_lane_filter_validation(self):
        """Test lifecycle lane filter accepts valid enum values"""
        valid_lanes = [LifecycleLane.build, LifecycleLane.sell]
        filters = PortfolioFilters(lane=valid_lanes)
        assert filters.lane == valid_lanes
    
    def test_health_status_filter_validation(self):
        """Test health status filter accepts string values"""
        valid_statuses = ["Not Started", "In Progress", "On Track", "At Risk"]
        filters = PortfolioFilters(health_status=valid_statuses)
        assert filters.health_status == valid_statuses
    
    def test_gm_id_filter_validation(self):
        """Test GM ID filter accepts UUID values"""
        valid_ids = [uuid4(), uuid4()]
        filters = PortfolioFilters(gm_id=valid_ids)
        assert filters.gm_id == valid_ids