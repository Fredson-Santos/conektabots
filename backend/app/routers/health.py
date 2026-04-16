"""Health Router — Health Check Endpoints.

GET /healthz — API health status
GET /health — Database health check
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_session


router = APIRouter(tags=["health"])


@router.get("/healthz")
async def health_check():
    """Quick health status (no DB call).

    Returns:
        Status OK
    """
    return {"status": "ok", "message": "ConektaBots API v2.0"}


@router.get("/health")
async def database_health(session: AsyncSession = Depends(get_session)):
    """Health check with database validation.

    Args:
        session: Database session

    Returns:
        Status and database connection info
    """
    try:
        result = await session.execute(text("SELECT 1"))
        result.scalar()

        return {
            "status": "ok",
            "database": "connected",
            "version": "2.0.0",
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e),
        }
