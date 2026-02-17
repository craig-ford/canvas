import uuid
import logging
import traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                    "request_id": request_id
                }
            }
        )
    
    # Exception handler for general Exception
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        logger.error(f"Unhandled exception: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": "Internal server error",
                    "request_id": request_id
                }
            }
        )
    
    # Health endpoint
    @app.get("/api/health")
    @app.options("/api/health")
    async def health() -> dict:
        """Health check endpoint.
        
        Returns:
            dict: {"status": "ok"}
        """
        return {"status": "ok"}
    
    # Register feature routers
    from canvas.auth.routes import router as auth_router
    from canvas.routes.vbu import router as vbu_router
    from canvas.routes.canvas import router as canvas_router
    from canvas.routes.thesis import router as thesis_router
    from canvas.routes.proof_point import router as proof_point_router
    from canvas.routes.attachment import router as attachment_router
    from canvas.portfolio.router import router as portfolio_router
    from canvas.reviews.router import router as reviews_router

    app.include_router(auth_router)
    app.include_router(vbu_router)
    app.include_router(canvas_router)
    app.include_router(thesis_router)
    app.include_router(proof_point_router)
    app.include_router(attachment_router)
    app.include_router(portfolio_router)
    app.include_router(reviews_router)

    return app