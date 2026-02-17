import pytest
from typing import Callable
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from canvas.auth.dependencies import get_current_user, require_role
from canvas.models.user import User, UserRole


class TestGetCurrentUserContract:
    """Test get_current_user dependency contract."""
    
    @pytest.mark.asyncio
    async def test_get_current_user_signature(self):
        """Test get_current_user has correct signature."""
        # Verify function exists and has correct parameters
        import inspect
        sig = inspect.signature(get_current_user)
        params = list(sig.parameters.keys())
        assert "credentials" in params
        assert "db" in params
        assert sig.return_annotation == User
    
    @pytest.mark.asyncio
    async def test_get_current_user_extracts_token(self):
        """Test get_current_user extracts token from Authorization header."""
        # Mock dependencies
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        db = AsyncMock(spec=AsyncSession)
        
        # Mock auth service to return valid payload and user
        with patch('canvas.auth.dependencies.auth_service') as mock_auth_service:
            mock_payload = {"sub": "123e4567-e89b-12d3-a456-426614174000"}
            mock_user = MagicMock(spec=User)
            mock_user.is_active = True
            
            # Make async methods return coroutines
            mock_auth_service.verify_token = AsyncMock(return_value=mock_payload)
            mock_auth_service.get_user_by_id = AsyncMock(return_value=mock_user)
            
            result = await get_current_user(credentials, db)
            assert result == mock_user
            mock_auth_service.verify_token.assert_called_once_with("valid_token")
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token_raises_401(self):
        """Test invalid tokens raise HTTPException 401."""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")
        db = AsyncMock(spec=AsyncSession)
        
        # Mock auth service to return None for invalid token
        with patch('canvas.auth.dependencies.auth_service') as mock_auth_service:
            mock_auth_service.verify_token = AsyncMock(return_value=None)
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials, db)
            
            assert exc_info.value.status_code == 401
            assert "Invalid token" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found_raises_401(self):
        """Test user not found raises HTTPException 401."""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        db = AsyncMock(spec=AsyncSession)
        
        # Mock auth service to return valid payload but no user
        with patch('canvas.auth.dependencies.auth_service') as mock_auth_service:
            mock_payload = {"sub": "123e4567-e89b-12d3-a456-426614174000"}
            mock_auth_service.verify_token = AsyncMock(return_value=mock_payload)
            mock_auth_service.get_user_by_id = AsyncMock(return_value=None)
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials, db)
            
            assert exc_info.value.status_code == 401
            assert "User not found" in exc_info.value.detail


class TestRequireRoleContract:
    """Test require_role dependency factory contract."""
    
    def test_require_role_signature(self):
        """Test require_role has correct signature."""
        import inspect
        sig = inspect.signature(require_role)
        # Check that it returns a callable that takes User and returns User
        assert "Callable" in str(sig.return_annotation)
    
    def test_require_role_accepts_multiple_roles(self):
        """Test require_role accepts variable number of UserRole arguments."""
        # Should not raise exception
        checker = require_role(UserRole.ADMIN)
        assert callable(checker)
        
        checker = require_role(UserRole.ADMIN, UserRole.GM)
        assert callable(checker)
    
    def test_require_role_checker_signature(self):
        """Test returned checker function has correct signature."""
        checker = require_role(UserRole.ADMIN)
        import inspect
        sig = inspect.signature(checker)
        params = list(sig.parameters.keys())
        assert "user" in params
        assert sig.return_annotation == User
    
    def test_require_role_authorized_user_passes(self):
        """Test authorized user passes role check."""
        checker = require_role(UserRole.ADMIN)
        
        # Mock user with admin role
        user = MagicMock(spec=User)
        user.role = UserRole.ADMIN
        
        # Should return the user without raising exception
        result = checker(user)
        assert result == user
    
    def test_require_role_unauthorized_user_raises_403(self):
        """Test unauthorized user raises HTTPException 403."""
        checker = require_role(UserRole.ADMIN)
        
        # Mock user with viewer role
        user = MagicMock(spec=User)
        user.role = UserRole.VIEWER
        
        with pytest.raises(HTTPException) as exc_info:
            checker(user)
        
        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in exc_info.value.detail
    
    def test_require_role_multiple_roles_any_passes(self):
        """Test user with any of multiple required roles passes."""
        checker = require_role(UserRole.ADMIN, UserRole.GM)
        
        # Mock user with GM role (one of the allowed roles)
        user = MagicMock(spec=User)
        user.role = UserRole.GM
        
        # Should return the user without raising exception
        result = checker(user)
        assert result == user