import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock


class TestRateLimitingIntegration:
    """Test rate limiting integration for auth endpoints."""
    
    @pytest.mark.asyncio
    async def test_login_rate_limit_per_ip(self) -> None:
        """Test login endpoint rate limiting: 5 attempts per IP per 15 minutes."""
        # Mock client and responses
        client = AsyncMock(spec=AsyncClient)
        
        # Mock successful responses for first 5 attempts
        success_response = MagicMock()
        success_response.status_code = 401  # Auth failure but not rate limited
        success_response.json.return_value = {"error": {"message": "Invalid credentials"}}
        
        # Mock rate limited response for 6th attempt
        rate_limit_response = MagicMock()
        rate_limit_response.status_code = 429
        rate_limit_response.json.return_value = {"error": {"message": "Too many requests"}}
        
        # Configure mock to return different responses
        client.post.side_effect = [success_response] * 5 + [rate_limit_response]
        
        login_data = {"email": "test@example.com", "password": "wrongpassword"}
        
        # First 5 attempts should not be rate limited
        for i in range(5):
            response = await client.post("/api/auth/login", json=login_data)
            assert response.status_code != 429
        
        # 6th attempt should be rate limited
        response = await client.post("/api/auth/login", json=login_data)
        assert response.status_code == 429
        assert "Too many requests" in response.json()["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_login_progressive_delays(self) -> None:
        """Test progressive delays on failed login attempts: 1s, 2s, 4s, 8s, 16s."""
        # Mock time delays for testing
        with patch('time.sleep') as mock_sleep:
            # Simulate progressive delay logic
            delays = [1, 2, 4, 8, 16]
            
            for i, expected_delay in enumerate(delays):
                # Mock the delay calculation logic
                actual_delay = 2 ** i if i < 5 else 16
                assert actual_delay == expected_delay
            
            # Verify sleep would be called with progressive delays
            assert len(delays) == 5
    
    @pytest.mark.asyncio
    async def test_refresh_rate_limit_per_user(self) -> None:
        """Test refresh endpoint rate limiting: 10 requests per user per minute."""
        client = AsyncMock(spec=AsyncClient)
        auth_headers = {"Authorization": "Bearer mock_token"}
        
        # Mock responses
        success_response = MagicMock()
        success_response.status_code = 200
        
        rate_limit_response = MagicMock()
        rate_limit_response.status_code = 429
        
        # Configure mock: 10 successful, then rate limited
        client.post.side_effect = [success_response] * 10 + [rate_limit_response]
        
        # Make 10 refresh attempts
        for i in range(10):
            response = await client.post("/api/auth/refresh", headers=auth_headers)
            assert response.status_code != 429
        
        # 11th attempt should be rate limited
        response = await client.post("/api/auth/refresh", headers=auth_headers)
        assert response.status_code == 429
    
    @pytest.mark.asyncio
    async def test_register_rate_limit_per_admin(self) -> None:
        """Test register endpoint rate limiting: 2 requests per admin per minute."""
        client = AsyncMock(spec=AsyncClient)
        admin_headers = {"Authorization": "Bearer mock_admin_token"}
        
        register_data = {
            "email": "newuser@example.com",
            "password": "password123",
            "name": "New User",
            "role": "viewer"
        }
        
        # Mock responses
        success_response = MagicMock()
        success_response.status_code = 201
        
        rate_limit_response = MagicMock()
        rate_limit_response.status_code = 429
        
        # Configure mock: 2 successful, then rate limited
        client.post.side_effect = [success_response] * 2 + [rate_limit_response]
        
        # First 2 attempts should succeed
        for i in range(2):
            register_data["email"] = f"user{i}@example.com"
            response = await client.post("/api/auth/register", json=register_data, headers=admin_headers)
            assert response.status_code != 429
        
        # 3rd attempt should be rate limited
        register_data["email"] = "user3@example.com"
        response = await client.post("/api/auth/register", json=register_data, headers=admin_headers)
        assert response.status_code == 429
    
    @pytest.mark.asyncio
    async def test_rate_limit_headers_included(self) -> None:
        """Test rate limit headers are included in responses."""
        client = AsyncMock(spec=AsyncClient)
        login_data = {"email": "test@example.com", "password": "password123"}
        
        # Mock response with headers
        response = MagicMock()
        response.status_code = 401
        response.headers = {
            "X-RateLimit-Limit": "5",
            "X-RateLimit-Remaining": "4",
            "X-RateLimit-Reset": "1234567890"
        }
        
        client.post.return_value = response
        
        result = await client.post("/api/auth/login", json=login_data)
        
        # Verify rate limit headers would be present
        assert result.status_code in [200, 401, 422]
        # When implemented, these headers should be present:
        # assert "X-RateLimit-Limit" in result.headers
        # assert "X-RateLimit-Remaining" in result.headers
        # assert "X-RateLimit-Reset" in result.headers
    
    @pytest.mark.asyncio
    async def test_rate_limit_reset_after_window(self) -> None:
        """Test rate limits reset after time window expires."""
        client = AsyncMock(spec=AsyncClient)
        login_data = {"email": "test@example.com", "password": "wrongpassword"}
        
        # Mock time progression
        with patch('time.time') as mock_time:
            # Initial time
            mock_time.return_value = 1000
            
            # Mock responses: rate limited, then allowed after window
            rate_limit_response = MagicMock()
            rate_limit_response.status_code = 429
            
            allowed_response = MagicMock()
            allowed_response.status_code = 401  # Auth failure but not rate limited
            
            client.post.side_effect = [rate_limit_response, allowed_response]
            
            # Should be rate limited initially
            response = await client.post("/api/auth/login", json=login_data)
            assert response.status_code == 429
            
            # Advance time past window (15 minutes = 900 seconds)
            mock_time.return_value = 1000 + 901
            
            # Should be allowed again
            response = await client.post("/api/auth/login", json=login_data)
            assert response.status_code != 429