"""
Main FastAPI application
Entry point for Rhiz Protocol API
"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db

# Import routers
from app.api import analytics, conviction, entities, graph


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    """Lifecycle manager for startup and shutdown"""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.app_env}")
    await init_db()
    print("Database initialized")

    yield

    # Shutdown
    print("Shutting down gracefully")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Rhiz Protocol API - The Relationship Layer of the Internet",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
async def root() -> dict[str, Any]:
    """Root endpoint"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
        "environment": settings.app_env,
    }


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/ready", tags=["health"])
async def readiness_check() -> dict[str, str]:
    """Readiness check endpoint"""
    # TODO: Check database and Redis connectivity
    return {"status": "ready"}


# Include API routers
app.include_router(graph.router, prefix="/api/v1/graph", tags=["graph"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(entities.router, prefix="/api/v1/entities", tags=["entities"])
app.include_router(conviction.router, tags=["conviction"])  # XRPC endpoints include prefix


@app.exception_handler(404)
async def not_found_handler(request: Any, exc: Any) -> JSONResponse:
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={"detail": "The requested resource was not found"},
    )


@app.exception_handler(500)
async def internal_error_handler(request: Any, exc: Any) -> JSONResponse:
    """Custom 500 handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level,
    )

