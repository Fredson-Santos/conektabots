"""Log Service — Execution History & Analytics.

Handles log queries, filtering, pagination, and statistics.
"""

from datetime import datetime, timedelta
from uuid import UUID
from typing import Optional
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.log import LogExecucao
from app.schemas.log import LogExecucaoResponse, LogFilter, LogStats


class LogService:
    """Query and analyze execution logs."""

    def __init__(self, session: AsyncSession):
        """Initialize log service.

        Args:
            session: Database session
        """
        self.session = session

    async def list_logs(
        self,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[LogFilter] = None,
    ) -> tuple[list[LogExecucaoResponse], int]:
        """List logs with pagination and filters.

        Args:
            tenant_id: Tenant UUID
            skip: Pagination offset
            limit: Pagination limit
            filters: Log filters

        Returns:
            Tuple of (logs, total_count)
        """
        query = select(LogExecucao).where(LogExecucao.tenant_id == tenant_id)

        # Apply filters
        if filters:
            if filters.bot_id:
                query = query.where(LogExecucao.bot_id == filters.bot_id)
            if filters.status:
                query = query.where(LogExecucao.status == filters.status)
            if filters.date_from:
                query = query.where(LogExecucao.criado_em >= filters.date_from)
            if filters.date_to:
                query = query.where(LogExecucao.criado_em <= filters.date_to)
            if filters.search:
                query = query.where(
                    or_(
                        LogExecucao.mensagem.ilike(f"%{filters.search}%"),
                        LogExecucao.origem.ilike(f"%{filters.search}%"),
                        LogExecucao.destino.ilike(f"%{filters.search}%"),
                    )
                )

        # Count total
        count_result = await self.session.execute(
            select(func.count()).select_from(LogExecucao).where(
                query.whereclause
            )
        )
        total = count_result.scalar()

        # Fetch paginated results
        query = query.order_by(desc(LogExecucao.criado_em)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        logs = result.scalars().all()

        return [LogExecucaoResponse.from_attributes(l) for l in logs], total

    async def get_log(
        self, log_id: UUID, tenant_id: UUID
    ) -> Optional[LogExecucaoResponse]:
        """Get specific log entry.

        Args:
            log_id: Log UUID
            tenant_id: Tenant UUID

        Returns:
            Log response or None
        """
        stmt = select(LogExecucao).where(
            and_(LogExecucao.id == log_id, LogExecucao.tenant_id == tenant_id)
        )
        result = await self.session.execute(stmt)
        log = result.scalar_one_or_none()

        return LogExecucaoResponse.from_attributes(log) if log else None

    # ===================== Statistics =====================

    async def get_stats(
        self, tenant_id: UUID, days: int = 30
    ) -> LogStats:
        """Get log statistics for tenant.

        Args:
            tenant_id: Tenant UUID
            days: Number of days to include in stats

        Returns:
            Stats object
        """
        date_threshold = datetime.utcnow() - timedelta(days=days)

        query = select(LogExecucao).where(
            and_(
                LogExecucao.tenant_id == tenant_id,
                LogExecucao.criado_em >= date_threshold,
            )
        )
        result = await self.session.execute(query)
        logs = result.scalars().all()

        total = len(logs)
        successful = sum(1 for l in logs if l.status == "sucesso")
        failed = sum(1 for l in logs if l.status == "erro")
        warnings = sum(1 for l in logs if l.status == "aviso")

        success_rate = (successful / total * 100) if total > 0 else 0

        return LogStats(
            total_executions=total,
            successful=successful,
            failed=failed,
            warnings=warnings,
            success_rate=success_rate,
        )

    async def get_stats_by_bot(
        self, bot_id: UUID, tenant_id: UUID, days: int = 30
    ) -> LogStats:
        """Get statistics for specific bot.

        Args:
            bot_id: Bot UUID
            tenant_id: Tenant UUID
            days: Number of days to include

        Returns:
            Stats object
        """
        date_threshold = datetime.utcnow() - timedelta(days=days)

        query = select(LogExecucao).where(
            and_(
                LogExecucao.bot_id == bot_id,
                LogExecucao.tenant_id == tenant_id,
                LogExecucao.criado_em >= date_threshold,
            )
        )
        result = await self.session.execute(query)
        logs = result.scalars().all()

        total = len(logs)
        successful = sum(1 for l in logs if l.status == "sucesso")
        failed = sum(1 for l in logs if l.status == "erro")
        warnings = sum(1 for l in logs if l.status == "aviso")

        success_rate = (successful / total * 100) if total > 0 else 0

        return LogStats(
            total_executions=total,
            successful=successful,
            failed=failed,
            warnings=warnings,
            success_rate=success_rate,
        )

    async def get_stats_by_status(
        self, tenant_id: UUID, days: int = 30
    ) -> dict[str, int]:
        """Get log count by status.

        Args:
            tenant_id: Tenant UUID
            days: Number of days to include

        Returns:
            Dictionary of status counts
        """
        date_threshold = datetime.utcnow() - timedelta(days=days)

        query = select(LogExecucao).where(
            and_(
                LogExecucao.tenant_id == tenant_id,
                LogExecucao.criado_em >= date_threshold,
            )
        )
        result = await self.session.execute(query)
        logs = result.scalars().all()

        counts = {
            "sucesso": sum(1 for l in logs if l.status == "sucesso"),
            "erro": sum(1 for l in logs if l.status == "erro"),
            "aviso": sum(1 for l in logs if l.status == "aviso"),
        }

        return counts

    async def get_top_errors(
        self, tenant_id: UUID, limit: int = 10, days: int = 30
    ) -> list[dict]:
        """Get most common error messages.

        Args:
            tenant_id: Tenant UUID
            limit: Number of errors to return
            days: Number of days to include

        Returns:
            List of error dicts with message and count
        """
        date_threshold = datetime.utcnow() - timedelta(days=days)

        query = select(LogExecucao).where(
            and_(
                LogExecucao.tenant_id == tenant_id,
                LogExecucao.status == "erro",
                LogExecucao.criado_em >= date_threshold,
            )
        )
        result = await self.session.execute(query)
        logs = result.scalars().all()

        # Count errors
        error_counts = {}
        for log in logs:
            if log.mensagem:
                error_counts[log.mensagem] = error_counts.get(log.mensagem, 0) + 1

        # Sort and return top errors
        sorted_errors = sorted(
            error_counts.items(), key=lambda x: x[1], reverse=True
        )[:limit]

        return [
            {"message": msg, "count": count} for msg, count in sorted_errors
        ]

    # ===================== Cleanup =====================

    async def cleanup_old_logs(self, days: int = 90) -> int:
        """Delete logs older than specified days.

        Args:
            days: Delete logs older than this many days

        Returns:
            Number of deleted logs
        """
        threshold = datetime.utcnow() - timedelta(days=days)

        query = select(LogExecucao).where(LogExecucao.criado_em < threshold)
        result = await self.session.execute(query)
        old_logs = result.scalars().all()

        count = len(old_logs)
        for log in old_logs:
            await self.session.delete(log)

        await self.session.commit()
        return count
