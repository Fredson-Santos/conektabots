"""Logs Router — Execution History & Analytics.

GET /api/v1/logs — List logs with pagination and filters
GET /api/v1/logs/{log_id} — Get specific log
GET /api/v1/logs/stats/summary — Get statistics summary
GET /api/v1/logs/stats/by-bot/{bot_id} — Get stats for specific bot
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_tenant
from app.schemas.log import LogExecucaoResponse, LogFilter, LogStats
from app.schemas.common import PaginatedResponse
from app.services.log_service import LogService


router = APIRouter(prefix="/api/v1/logs", tags=["logs"])


@router.get("/", response_model=PaginatedResponse)
async def list_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    bot_id: UUID | None = Query(None),
    status: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    search: str | None = Query(None),
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """List execution logs with pagination and filters.

    Args:
        skip: Pagination offset
        limit: Pagination limit (max 100)
        bot_id: Filter by bot UUID
        status: Filter by status (sucesso, erro, aviso)
        date_from: Filter by date (ISO format)
        date_to: Filter by date (ISO format)
        search: Search in message/origem/destino
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Paginated log list
    """
    filters = LogFilter(
        bot_id=bot_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )

    service = LogService(session)
    logs, total = await service.list_logs(tenant_id, skip, limit, filters)

    return PaginatedResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=logs,
    )


@router.get("/{log_id}", response_model=LogExecucaoResponse)
async def get_log(
    log_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Get specific log entry.

    Args:
        log_id: Log UUID
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Log response or 404
    """
    service = LogService(session)
    log = await service.get_log(log_id, tenant_id)

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log não encontrado",
        )

    return log


# ===================== Statistics =====================


@router.get("/stats/summary", response_model=LogStats)
async def get_stats_summary(
    days: int = Query(30, ge=1, le=365),
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Get execution statistics summary for tenant.

    Args:
        days: Number of days to include (default 30)
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Statistics object
    """
    service = LogService(session)
    return await service.get_stats(tenant_id, days)


@router.get("/stats/by-bot/{bot_id}", response_model=LogStats)
async def get_stats_by_bot(
    bot_id: UUID,
    days: int = Query(30, ge=1, le=365),
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Get execution statistics for specific bot.

    Args:
        bot_id: Bot UUID
        days: Number of days to include (default 30)
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Statistics object
    """
    service = LogService(session)
    return await service.get_stats_by_bot(bot_id, tenant_id, days)


@router.get("/stats/by-status", response_model=dict)
async def get_stats_by_status(
    days: int = Query(30, ge=1, le=365),
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Get log count breakdown by status.

    Args:
        days: Number of days to include (default 30)
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Dict with status counts
    """
    service = LogService(session)
    return await service.get_stats_by_status(tenant_id, days)


@router.get("/errors/top", response_model=list[dict])
async def get_top_errors(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(30, ge=1, le=365),
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Get most common error messages.

    Args:
        limit: Number of errors to return
        days: Number of days to include
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        List of top errors with counts
    """
    service = LogService(session)
    return await service.get_top_errors(tenant_id, limit, days)
