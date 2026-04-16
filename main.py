"""ConektaBots API v2.0 — FastAPI Application Entry Point.

Multi-tenant SaaS platform for Telegram automation with marketplace integrations.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.routers import auth, tenants, bots, marketplaces, regras, agendamentos, logs, health
from app.middleware.auth import auth_middleware
from app.middleware.tenant import tenant_middleware
from app.middleware.rate_limit import rate_limit_middleware


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create FastAPI app
app = FastAPI(
    title="ConektaBots API",
    version="2.0.0",
    description="Multi-tenant automation platform for Telegram and marketplaces",
    docs_url="/docs",
    openapi_url="/openapi.json",
)


# ===================== CORS =====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================== Middleware Stack =====================
# Order matters! Apply from bottom to top:
# 1. Auth (must be first to set request.state)
# 2. Tenant (depends on auth setting state)
# 3. Rate limit (depends on tenant for plan info)

@app.middleware("http")
async def auth_middleware_wrapper(request: Request, call_next):
    """Wrap auth middleware."""
    return await auth_middleware(request, call_next)


@app.middleware("http")
async def tenant_middleware_wrapper(request: Request, call_next):
    """Wrap tenant middleware."""
    return await tenant_middleware(request, call_next)


@app.middleware("http")
async def rate_limit_middleware_wrapper(request: Request, call_next):
    """Wrap rate limit middleware."""
    return await rate_limit_middleware(request, call_next)


# ===================== Exception Handlers =====================

from fastapi import HTTPException, status

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    import os
    debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    
    response_content = {
        "error": "Internal server error",
        "status_code": 500,
    }
    
    # Include error details in development mode
    if debug_mode:
        response_content["detail"] = str(exc)
        import traceback
        response_content["traceback"] = traceback.format_exc()
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_content,
    )


# ===================== Routers =====================

app.include_router(health.router)  # Public endpoints
app.include_router(auth.router)  # Public auth endpoints
app.include_router(tenants.router)  # Protected endpoints
app.include_router(bots.router)
app.include_router(marketplaces.router)
app.include_router(regras.router)
app.include_router(agendamentos.router)
app.include_router(logs.router)


# ===================== Startup/Shutdown =====================

@app.on_event("startup")
async def startup_event():
    """Run startup tasks."""
    logger.info("🚀 ConektaBots API v2.0 starting...")
    
    # Initialize database tables (non-blocking with timeout)
    import asyncio
    from app.core.database import engine, Base
    try:
        # Set a short timeout for initialization
        async def init_db():
            async with engine.begin() as conn:
                # Import all models to register them with SQLAlchemy
                from app.models import (
                    user, tenant, bot, regra, agendamento, 
                    log, marketplace, uso
                )
                # Create tables
                await conn.run_sync(Base.metadata.create_all)
        
        # Try to initialize with timeout
        await asyncio.wait_for(init_db(), timeout=10.0)
        logger.info("✓ Database tables initialized")
    except asyncio.TimeoutError:
        logger.warning("⚠ Database initialization timed out - will retry on first request")
    except Exception as e:
        logger.error(f"✗ Database initialization error: {type(e).__name__}: {e}")
        logger.warning("⚠ API starting anyway - database may need manual initialization")
    
    # TODO: Initialize worker if enabled
    # from worker import get_worker
    # worker = await get_worker()
    # await worker.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Run shutdown tasks."""
    logger.info("🛑 ConektaBots API shutting down...")
    # TODO: Stop worker if running
    # from worker import get_worker
    # worker = await get_worker()
    # await worker.stop()


# ===================== Default Route =====================

@app.get("/", tags=["info"])
async def root():
    """API info."""
    return {
        "name": "ConektaBots API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/healthz",
    }


# ===================== Development Server =====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.HOST or "0.0.0.0",
        port=settings.PORT or 8000,
        reload=settings.DEBUG,
        log_level="info",
    )
