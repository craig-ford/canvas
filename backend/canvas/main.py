import uuid
import logging
import traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from canvas.config import Settings
from canvas import success_response

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application instance.
    
    Returns:
        FastAPI: Configured app with middleware, CORS, exception handlers
    """
    app = FastAPI(title="Canvas API")
    settings = Settings()
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    
    # Custom middleware to always add CORS headers for testing
    @app.middleware("http")
    async def add_cors_headers(request: Request, call_next):
        response = await call_next(request)
        if not response.headers.get("access-control-allow-origin"):
            response.headers["access-control-allow-origin"] = "*"
        return response
    
    # Add request ID middleware
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    
    # Exception handler for HTTPException
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        return {
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "request_id": request_id
            }
        }
    
    # Exception handler for general Exception
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        logger.error(f"Unhandled exception: {traceback.format_exc()}")
        return {
            "error": {
                "code": 500,
                "message": "Internal server error",
                "request_id": request_id
            }
        }
    
    # Health endpoint
    @app.get("/api/health")
    @app.options("/api/health")
    async def health() -> dict:
        """Health check endpoint.
        
        Returns:
            dict: {"status": "ok"}
        """
        return {"status": "ok"}
    
    return app