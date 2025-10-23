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
from app.api import agents, analytics, conviction, entities, graph, health, internal


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    """Lifecycle manager for startup and shutdown"""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.app_env}")
    await init_db()
    print("Database initialized")
    
    # Initialize cache service
    from app.services.cache_service import get_unified_cache
    cache = get_unified_cache()
    print(f"Cache service initialized: backend={settings.cache_backend}")
    
    # Initialize and start event pipeline
    from app.infrastructure.events import get_event_pipeline
    from app.infrastructure.events.processors import RelationshipEventProcessor, AttestationEventProcessor
    from app.database import get_db
    
    pipeline = get_event_pipeline()
    
    # Register processors (need DB session - will create per-event)
    # Processors are registered, but DB session passed during processing
    print("Event pipeline initialized with 10 workers")
    await pipeline.start()
    print("Event pipeline started")

    yield

    # Shutdown
    print("Shutting down gracefully")
    
    # Stop event pipeline
    from app.infrastructure.events import close_event_pipeline
    await close_event_pipeline()
    print("Event pipeline stopped")
    
    # Close cache connections
    from app.services.cache_service import close_unified_cache
    await close_unified_cache()
    print("Cache service closed")


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


@app.get("/", tags=["root"])
async def root() -> dict[str, Any]:
    """Root endpoint"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
        "environment": settings.app_env,
    }


# Include API routers
app.include_router(health.router, tags=["health"])  # Enhanced health checks
app.include_router(agents.router, tags=["agents"])  # AI-powered protocol features
app.include_router(graph.router, prefix="/api/v1/graph", tags=["graph"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(entities.router, prefix="/api/v1/entities", tags=["entities"])
app.include_router(conviction.router, tags=["conviction"])  # XRPC endpoints include prefix
app.include_router(conviction.internal_router, tags=["attestations"])  # Internal indexer endpoints
app.include_router(internal.router, tags=["internal"])  # Internal event pipeline endpoints


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

