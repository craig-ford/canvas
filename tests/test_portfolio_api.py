import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from canvas.models.user import User, UserRole
from canvas.portfolio.schemas import VBUSummary, LifecycleLane

@pytest.fixture
def admin_user():
    return User(
        id=uuid4(),
        email="admin@test.com",
        name="Admin User",
        role=UserRole.admin,
        is_active=True
    )

@pytest.fixture
def gm_user():
    return User(
        id=uuid4(),
        email="gm@test.com", 
        name="GM User",
        role=UserRole.gm,
        is_active=True
    )

@pytest.fixture
def viewer_user():
    return User(
        id=uuid4(),
        email="viewer@test.com",
        name="Viewer User", 
        role=UserRole.viewer,
        is_active=True
    )

@pytest.fixture
def sample_vbu_summary():
    return VBUSummary(
        id=uuid4(),
        name="Test VBU",
        gm_name="John Smith",
        lifecycle_lane=LifecycleLane.build,
        success_description="Test success",
        currently_testing="Test focus",
        next_review_date=None,
        primary_constraint="Test constraint",
        health_indicator="In Progress",
        portfolio_notes="Test notes"
    )

class TestPortfolioSummaryEndpoint:
    """Test GET /api/portfolio/summary endpoint"""
    
    @patch('canvas.portfolio.router.portfolio_service.get_summary')
    def test_get_summary_success(self, mock_get_summary, client, admin_user, sample_vbu_summary):
        """Test successful portfolio summary retrieval"""
        mock_get_summary.return_value = [sample_vbu_summary]
        
        with patch('canvas.auth.dependencies.get_current_user', return_value=admin_user):
            response = client.get("/api/portfolio/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert len(data["data"]) == 1
        assert data["meta"]["total"] == 1
        assert "timestamp" in data["meta"]

    @patch('canvas.portfolio.router.portfolio_service.get_summary')
    def test_get_summary_with_filters(self, mock_get_summary, client, admin_user, sample_vbu_summary):
        """Test portfolio summary with query filters"""
        mock_get_summary.return_value = [sample_vbu_summary]
        
        with patch('canvas.auth.dependencies.get_current_user', return_value=admin_user):
            response = client.get(
                "/api/portfolio/summary?lane=build,sell&health_status=In Progress,On Track"
            )
        
        assert response.status_code == 200
        # Verify filters were parsed correctly
        mock_get_summary.assert_called_once()
        args = mock_get_summary.call_args[0]
        filters = args[1]
        assert filters.lane == ["build", "sell"]
        assert filters.health_status == ["In Progress", "On Track"]

    @patch('canvas.portfolio.router.portfolio_service.get_summary')
    def test_get_summary_gm_access(self, mock_get_summary, client, gm_user, sample_vbu_summary):
        """Test GM can access portfolio summary"""
        mock_get_summary.return_value = [sample_vbu_summary]
        
        with patch('canvas.auth.dependencies.get_current_user', return_value=gm_user):
            response = client.get("/api/portfolio/summary")
        
        assert response.status_code == 200
        mock_get_summary.assert_called_once_with(gm_user, pytest.any)

    @patch('canvas.portfolio.router.portfolio_service.get_summary')
    def test_get_summary_viewer_access(self, mock_get_summary, client, viewer_user, sample_vbu_summary):
        """Test viewer can access portfolio summary"""
        mock_get_summary.return_value = [sample_vbu_summary]
        
        with patch('canvas.auth.dependencies.get_current_user', return_value=viewer_user):
            response = client.get("/api/portfolio/summary")
        
        assert response.status_code == 200
        mock_get_summary.assert_called_once_with(viewer_user, pytest.any)

    def test_get_summary_unauthorized(self, client):
        """Test unauthorized access returns 401"""
        response = client.get("/api/portfolio/summary")
        assert response.status_code == 401

    @patch('canvas.portfolio.router.portfolio_service.get_summary')
    def test_get_summary_invalid_uuid_filter(self, mock_get_summary, client, admin_user):
        """Test invalid UUID in gm_id filter returns 422"""
        with patch('canvas.auth.dependencies.get_current_user', return_value=admin_user):
            response = client.get("/api/portfolio/summary?gm_id=invalid-uuid")
        
        assert response.status_code == 422

class TestPortfolioNotesEndpoint:
    """Test PATCH /api/portfolio/notes endpoint"""
    
    @patch('canvas.portfolio.router.portfolio_service.update_portfolio_notes')
    def test_update_notes_admin_success(self, mock_update_notes, client, admin_user):
        """Test admin can update portfolio notes"""
        mock_update_notes.return_value = None
        
        with patch('canvas.auth.dependencies.require_role') as mock_require_role:
            mock_require_role.return_value = lambda: admin_user
            response = client.patch(
                "/api/portfolio/notes",
                json={"notes": "Updated portfolio notes"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["notes"] == "Updated portfolio notes"
        assert "updated_at" in data["data"]
        mock_update_notes.assert_called_once_with("Updated portfolio notes", admin_user)

    @patch('canvas.portfolio.router.portfolio_service.update_portfolio_notes')
    def test_update_notes_empty_notes(self, mock_update_notes, client, admin_user):
        """Test updating with empty notes"""
        mock_update_notes.return_value = None
        
        with patch('canvas.auth.dependencies.require_role') as mock_require_role:
            mock_require_role.return_value = lambda: admin_user
            response = client.patch(
                "/api/portfolio/notes",
                json={"notes": None}
            )
        
        assert response.status_code == 200
        mock_update_notes.assert_called_once_with(None, admin_user)

    def test_update_notes_gm_forbidden(self, client, gm_user):
        """Test GM cannot update portfolio notes"""
        with patch('canvas.auth.dependencies.require_role') as mock_require_role:
            mock_require_role.side_effect = Exception("Forbidden")
            response = client.patch(
                "/api/portfolio/notes",
                json={"notes": "Should not work"}
            )
        
        assert response.status_code != 200

    def test_update_notes_viewer_forbidden(self, client, viewer_user):
        """Test viewer cannot update portfolio notes"""
        with patch('canvas.auth.dependencies.require_role') as mock_require_role:
            mock_require_role.side_effect = Exception("Forbidden")
            response = client.patch(
                "/api/portfolio/notes",
                json={"notes": "Should not work"}
            )
        
        assert response.status_code != 200

    def test_update_notes_unauthorized(self, client):
        """Test unauthorized access returns 401"""
        response = client.patch(
            "/api/portfolio/notes",
            json={"notes": "Should not work"}
        )
        assert response.status_code == 401

    @patch('canvas.portfolio.router.portfolio_service.update_portfolio_notes')
    def test_update_notes_too_long(self, mock_update_notes, client, admin_user):
        """Test notes exceeding max length returns 422"""
        long_notes = "x" * 10001  # Exceeds 10000 char limit
        
        with patch('canvas.auth.dependencies.require_role') as mock_require_role:
            mock_require_role.return_value = lambda: admin_user
            response = client.patch(
                "/api/portfolio/notes",
                json={"notes": long_notes}
            )
        
        assert response.status_code == 422

class TestPortfolioRouterIntegration:
    """Integration tests for portfolio router"""
    
    def test_router_prefix_and_tags(self):
        """Test router has correct prefix and tags"""
        from canvas.portfolio.router import router
        assert router.prefix == "/api/portfolio"
        assert "portfolio" in router.tags

    def test_endpoints_exist(self):
        """Test required endpoints are defined"""
        from canvas.portfolio.router import router
        
        routes = {route.path for route in router.routes}
        assert "/summary" in routes
        assert "/notes" in routes
        
        # Check HTTP methods
        summary_route = next(r for r in router.routes if r.path == "/summary")
        notes_route = next(r for r in router.routes if r.path == "/notes")
        
        assert "GET" in summary_route.methods
        assert "PATCH" in notes_route.methods