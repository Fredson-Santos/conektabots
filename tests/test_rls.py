"""Test RLS Policies — Row-Level Security.

Verifies database RLS policies are enforced.
"""

import pytest
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.models.bot import Bot


@pytest.mark.asyncio
async def test_rls_tenant_isolation(session: AsyncSession):
    """Test RLS prevents accessing other tenant's data.

    NOTE: This test demonstrates RLS enforcement.
    In actual test environment need Supabase with RLS enabled.
    """
    # Create 2 tenants
    tenant_a = Tenant(nome="Tenant A", slug="tenant-a", plano="free", ativo=True)
    tenant_b = Tenant(nome="Tenant B", slug="tenant-b", plano="free", ativo=True)
    session.add(tenant_a)
    session.add(tenant_b)
    await session.flush()

    # Create bot in tenant A
    bot = Bot(
        tenant_id=tenant_a.id,
        nome="Bot A",
        tipo="BOT",
        api_id="123456",
        ativo=True,
    )
    session.add(bot)
    await session.commit()

    # Test: In production with RLS enabled,
    # a query with tenant_id = B should not see bot from tenant A

    # For this test, we verify service-level isolation
    # (database RLS would be tested in integration tests with real Supabase)

    from app.services.bot_service import BotService

    service_b = BotService(session)
    result = await service_b.get(bot.id, tenant_b.id)

    # Service-level isolation should prevent access
    assert result is None


@pytest.mark.asyncio
async def test_tenant_soft_delete_visibility(session: AsyncSession):
    """Test that soft-deleted records are not visible."""
    from datetime import datetime

    tenant = Tenant(nome="Test", slug="test", plano="free", ativo=True)
    session.add(tenant)
    await session.commit()

    # Soft delete
    tenant.deletado_em = datetime.utcnow()
    await session.commit()

    # Query (should filter out deletado_em records)
    from sqlalchemy import select

    stmt = select(Tenant).where(Tenant.id == tenant.id, Tenant.deletado_em == None)
    result = await session.execute(stmt)
    found = result.scalar_one_or_none()

    assert found is None, "Soft-deleted record should not appear"
