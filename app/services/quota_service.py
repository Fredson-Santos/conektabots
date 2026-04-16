"""Quota Service — Rate Limiting & Usage Tracking.

Manages usage quotas per tenant and plan, rate limiting, and billing.
"""

from datetime import datetime
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.uso import UsoMensal
from app.models.tenant import Tenant


class QuotaService:
    """Manage usage quotas and rate limiting."""

    # Plano limits (mensagens por mês)
    PLAN_LIMITS = {
        "free": 1000,
        "starter": 10000,
        "pro": 100000,
        "enterprise": None,  # Unlimited
    }

    def __init__(self, session: AsyncSession):
        """Initialize quota service.

        Args:
            session: Database session
        """
        self.session = session

    async def get_tenant_limit(self, tenant_id: UUID) -> int:
        """Get message limit for tenant based on plan.

        Args:
            tenant_id: Tenant UUID

        Returns:
            Message limit (None = unlimited)
        """
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await self.session.execute(stmt)
        tenant = result.scalar_one_or_none()

        if not tenant:
            return 0

        return self.PLAN_LIMITS.get(tenant.plano, 0)

    async def get_monthly_usage(self, tenant_id: UUID) -> int:
        """Get current month's message usage.

        Args:
            tenant_id: Tenant UUID

        Returns:
            Number of messages sent this month
        """
        now = datetime.utcnow()
        ano_mes = f"{now.year:04d}-{now.month:02d}"

        stmt = select(UsoMensal).where(
            and_(UsoMensal.tenant_id == tenant_id, UsoMensal.ano_mes == ano_mes)
        )
        result = await self.session.execute(stmt)
        uso = result.scalar_one_or_none()

        return uso.msgs_enviadas if uso else 0

    async def can_send_message(self, tenant_id: UUID) -> tuple[bool, str]:
        """Check if tenant can send message based on quota.

        Args:
            tenant_id: Tenant UUID

        Returns:
            Tuple of (can_send, reason)
        """
        limit = await self.get_tenant_limit(tenant_id)
        if limit is None:  # Unlimited
            return True, "OK"

        usage = await self.get_monthly_usage(tenant_id)

        if usage >= limit:
            return False, f"Quota excedida: {usage}/{limit} mensagens"

        # Warn if approaching limit
        if usage >= limit * 0.8:
            return True, f"Aviso: {usage}/{limit} mensagens (80% de limite)"

        return True, "OK"

    async def increment_usage(
        self, tenant_id: UUID, increment: int = 1
    ) -> None:
        """Increment message count for current month.

        NOTE: This is called by database trigger `incrementar_uso_msgs()`
        in production. For local testing, can be called manually.

        Args:
            tenant_id: Tenant UUID
            increment: Number of messages to add (default 1)
        """
        now = datetime.utcnow()
        ano_mes = f"{now.year:04d}-{now.month:02d}"

        stmt = select(UsoMensal).where(
            and_(UsoMensal.tenant_id == tenant_id, UsoMensal.ano_mes == ano_mes)
        )
        result = await self.session.execute(stmt)
        uso = result.scalar_one_or_none()

        if uso:
            uso.msgs_enviadas += increment
        else:
            # Create new monthly record
            uso = UsoMensal(
                tenant_id=tenant_id,
                ano_mes=ano_mes,
                msgs_enviadas=increment,
                msgs_falhadas=0,
            )
            self.session.add(uso)

        await self.session.flush()

    async def get_usage_percentage(self, tenant_id: UUID) -> float:
        """Get usage as percentage of limit.

        Args:
            tenant_id: Tenant UUID

        Returns:
            Usage percentage (0-100, None for unlimited)
        """
        limit = await self.get_tenant_limit(tenant_id)
        if limit is None:
            return None

        usage = await self.get_monthly_usage(tenant_id)
        return (usage / limit) * 100 if limit > 0 else 0

    async def get_quota_info(self, tenant_id: UUID) -> dict:
        """Get comprehensive quota information.

        Args:
            tenant_id: Tenant UUID

        Returns:
            Dict with limit, usage, percentage, reset_date
        """
        limit = await self.get_tenant_limit(tenant_id)
        usage = await self.get_monthly_usage(tenant_id)
        percentage = await self.get_usage_percentage(tenant_id)

        # Next reset is 1st of next month
        now = datetime.utcnow()
        if now.month == 12:
            reset = datetime(now.year + 1, 1, 1)
        else:
            reset = datetime(now.year, now.month + 1, 1)

        return {
            "limit": limit,
            "usage": usage,
            "percentage": percentage,
            "reset_at": reset,
            "unlimited": limit is None,
        }
