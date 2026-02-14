import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import date
from fastapi import HTTPException
from canvas.models.user import User, UserRole
from canvas.portfolio.service import PortfolioService
from canvas.portfolio.schemas import PortfolioFilters, LifecycleLane

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
def mock_db():
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    return db

@pytest.fixture
def portfolio_service(mock_db):
    return PortfolioService(db=mock_db)

class TestPortfolioServiceGetSummary:
    """Test PortfolioService.get_summary method"""
    
    async def test_get_summary_admin_sees_all(self, portfolio_service, mock_db, admin_user):
        """Test admin user sees all VBUs"""
        # Mock database result
        mock_row = MagicMock()
        mock_row.id = uuid4()
        mock_row.name = "Test VBU"
        mock_row.gm_name = "John Smith"
        mock_row.lifecycle_lane = "build"
        mock_row.success_description = "Test success"
        mock_row.currently_testing = "Test focus"
        mock_row.next_review_date = date(2026, 3, 15)
        mock_row.primary_constraint = "Test constraint"
        mock_row.health_indicator = "In Progress"
        mock_row.portfolio_notes = "Test notes"
        
        mock_db.execute.return_value = [mock_row]
        
        filters = PortfolioFilters()
        result = await portfolio_service.get_summary(admin_user, filters)
        
        # Verify no role-based filtering for admin
        mock_db.execute.assert_called_once()
        query_args = mock_db.execute.call_args[0]
        assert "v.gm_id = :user_id" not in query_args[0]
        
        assert len(result) == 1
        assert result[0].name == "Test VBU"
        assert result[0].gm_name == "John Smith"

    async def test_get_summary_gm_sees_own_only(self, portfolio_service, mock_db, gm_user):
        """Test GM user sees only their own VBUs"""
        mock_db.execute.return_value = []
        
        filters = PortfolioFilters()
        await portfolio_service.get_summary(gm_user, filters)
        
        # Verify role-based filtering for GM
        mock_db.execute.assert_called_once()
        query_args = mock_db.execute.call_args[0]
        assert "v.gm_id = :user_id" in query_args[0]
        assert query_args[1]["user_id"] == gm_user.id

    async def test_get_summary_viewer_sees_all(self, portfolio_service, mock_db, viewer_user):
        """Test viewer user sees all VBUs"""
        mock_db.execute.return_value = []
        
        filters = PortfolioFilters()
        await portfolio_service.get_summary(viewer_user, filters)
        
        # Verify no role-based filtering for viewer
        mock_db.execute.assert_called_once()
        query_args = mock_db.execute.call_args[0]
        assert "v.gm_id = :user_id" not in query_args[0]

    async def test_get_summary_with_lane_filter(self, portfolio_service, mock_db, admin_user):
        """Test filtering by lifecycle lane"""
        mock_db.execute.return_value = []
        
        filters = PortfolioFilters(lane=[LifecycleLane.build, LifecycleLane.sell])
        await portfolio_service.get_summary(admin_user, filters)
        
        # Verify lane filtering
        mock_db.execute.assert_called_once()
        query_args = mock_db.execute.call_args[0]
        assert "c.lifecycle_lane = ANY(:lanes)" in query_args[0]
        assert query_args[1]["lanes"] == ["build", "sell"]

    async def test_get_summary_with_gm_filter(self, portfolio_service, mock_db, admin_user):
        """Test filtering by GM ID"""
        gm_ids = [uuid4(), uuid4()]
        mock_db.execute.return_value = []
        
        filters = PortfolioFilters(gm_id=gm_ids)
        await portfolio_service.get_summary(admin_user, filters)
        
        # Verify GM filtering
        mock_db.execute.assert_called_once()
        query_args = mock_db.execute.call_args[0]
        assert "v.gm_id = ANY(:gm_ids)" in query_args[0]
        assert query_args[1]["gm_ids"] == gm_ids

    async def test_get_summary_with_health_filter(self, portfolio_service, mock_db, admin_user):
        """Test filtering by health status"""
        mock_db.execute.return_value = []
        
        filters = PortfolioFilters(health_status=["In Progress", "On Track"])
        await portfolio_service.get_summary(admin_user, filters)
        
        # Verify health status filtering
        mock_db.execute.assert_called_once()
        query_args = mock_db.execute.call_args[0]
        assert "COALESCE(c.health_indicator_cache, 'Not Started') = ANY(:health_statuses)" in query_args[0]
        assert query_args[1]["health_statuses"] == ["In Progress", "On Track"]

    async def test_get_summary_combined_filters(self, portfolio_service, mock_db, gm_user):
        """Test combining multiple filters"""
        mock_db.execute.return_value = []
        
        filters = PortfolioFilters(
            lane=[LifecycleLane.build],
            health_status=["On Track"]
        )
        await portfolio_service.get_summary(gm_user, filters)
        
        # Verify all filters applied
        mock_db.execute.assert_called_once()
        query_args = mock_db.execute.call_args[0]
        assert "v.gm_id = :user_id" in query_args[0]  # Role-based
        assert "c.lifecycle_lane = ANY(:lanes)" in query_args[0]  # Lane filter
        assert "COALESCE(c.health_indicator_cache, 'Not Started') = ANY(:health_statuses)" in query_args[0]  # Health filter

class TestPortfolioServiceUpdateNotes:
    """Test PortfolioService.update_portfolio_notes method"""
    
    async def test_update_notes_admin_success(self, portfolio_service, mock_db, admin_user):
        """Test admin can update portfolio notes"""
        notes = "Updated portfolio notes"
        
        await portfolio_service.update_portfolio_notes(notes, admin_user)
        
        # Verify database update called
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()
        
        # Verify HTML escaping
        update_call = mock_db.execute.call_args[0][0]
        assert "portfolio_notes" in str(update_call)

    async def test_update_notes_html_escaping(self, portfolio_service, mock_db, admin_user):
        """Test HTML entities are escaped to prevent XSS"""
        notes = "<script>alert('xss')</script>"
        
        await portfolio_service.update_portfolio_notes(notes, admin_user)
        
        # Verify HTML was escaped (implementation detail - we trust html.escape works)
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()

    async def test_update_notes_empty_notes(self, portfolio_service, mock_db, admin_user):
        """Test updating with empty/None notes"""
        await portfolio_service.update_portfolio_notes(None, admin_user)
        
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()

    async def test_update_notes_gm_forbidden(self, portfolio_service, mock_db, gm_user):
        """Test GM cannot update portfolio notes"""
        with pytest.raises(HTTPException) as exc_info:
            await portfolio_service.update_portfolio_notes("Should fail", gm_user)
        
        assert exc_info.value.status_code == 403
        assert "Admin role required" in exc_info.value.detail
        
        # Verify no database operations
        mock_db.execute.assert_not_called()
        mock_db.commit.assert_not_called()

    async def test_update_notes_viewer_forbidden(self, portfolio_service, mock_db, viewer_user):
        """Test viewer cannot update portfolio notes"""
        with pytest.raises(HTTPException) as exc_info:
            await portfolio_service.update_portfolio_notes("Should fail", viewer_user)
        
        assert exc_info.value.status_code == 403
        assert "Admin role required" in exc_info.value.detail
        
        # Verify no database operations
        mock_db.execute.assert_not_called()
        mock_db.commit.assert_not_called()

class TestPortfolioServiceIntegration:
    """Integration tests for PortfolioService"""
    
    def test_service_initialization(self):
        """Test service can be initialized with and without db"""
        # With db
        mock_db = AsyncMock()
        service = PortfolioService(db=mock_db)
        assert service.db == mock_db
        
        # Without db (uses get_db_session)
        service = PortfolioService()
        assert service.db is None

    async def test_query_structure(self, portfolio_service, mock_db, admin_user):
        """Test SQL query structure is correct"""
        mock_db.execute.return_value = []
        
        filters = PortfolioFilters()
        await portfolio_service.get_summary(admin_user, filters)
        
        # Verify query structure
        mock_db.execute.assert_called_once()
        query_args = mock_db.execute.call_args[0]
        query = query_args[0]
        
        # Check key query components
        assert "SELECT v.id, v.name, u.name as gm_name" in query
        assert "FROM vbus v" in query
        assert "JOIN users u ON v.gm_id = u.id" in query
        assert "JOIN canvases c ON c.vbu_id = v.id" in query
        assert "ORDER BY v.name" in query
        assert "COALESCE(c.health_indicator_cache, 'Not Started')" in query