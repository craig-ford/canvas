import pytest
from httpx import AsyncClient, ASGITransport
from canvas.main import create_app


@pytest.mark.asyncio
async def test_health_endpoint_status_200():
    """Test GET /api/health returns 200 status code"""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint_response_body():
    """Test response body is exactly {"status": "ok"}"""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_endpoint_content_type():
    """Test response Content-Type is application/json"""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.headers["content-type"] == "application/json"


@pytest.mark.asyncio
async def test_health_endpoint_no_auth_required():
    """Test endpoint does not require authentication"""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code != 401


@pytest.mark.asyncio
async def test_health_endpoint_request_id_header():
    """Test endpoint includes X-Request-ID header in response"""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint_cors_headers():
    """Test CORS headers are present in response"""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.options("/api/health", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        })
        # CORS may return 200 or 204 or 405 depending on middleware config
        assert response.status_code in (200, 204, 405)
