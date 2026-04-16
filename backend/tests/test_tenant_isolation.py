"""Test Tenant Isolation — Multi-Tenant Security.

Verifies that tenants cannot see each other's data.
"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant, TenantMember
from app.models.bot import Bot


@pytest.mark.asyncio
async def test_tenant_isolation_bots(session: AsyncSession):
    """Test that tenant A cannot see tenant B's bots.

    Scenario:
    - Create 2 tenants
    - Add bot to tenant A
    - Verify tenant B cannot query bot
    """
    # Create tenants
    tenant_a = Tenant(nome="Tenant A", slug="tenant-a", plano="free", ativo=True)
    tenant_b = Tenant(nome="Tenant B", slug="tenant-b", plano="free", ativo=True)
    session.add(tenant_a)
    session.add(tenant_b)
    await session.flush()

    # Create bot in tenant A
    bot_a = Bot(
        tenant_id=tenant_a.id,
        nome="Bot A",
        tipo="BOT",
        api_id="123456",
        ativo=True,
    )
    session.add(bot_a)
    await session.commit()

    # Tenant B tries to query bot A (should fail due to RLS)
    # In production, RLS prevents this at database level
    # For testing: verify service-level isolation

    from app.services.bot_service import BotService

    service_b = BotService(session)
    bot = await service_b.get(bot_a.id, tenant_b.id)

    assert bot is None, "Tenant B should not see Bot A"


@pytest.mark.asyncio
async def test_tenant_member_isolation(session: AsyncSession):
    """Test that members are scoped to tenant."""
    from app.models.user import User
    import uuid
    
    tenant_a = Tenant(nome="Tenant A", slug="tenant-a", plano="free", ativo=True)
    tenant_b = Tenant(nome="Tenant B", slug="tenant-b", plano="free", ativo=True)
    session.add(tenant_a)
    session.add(tenant_b)
    await session.flush()

    # Create users
    user_a = User(
        email="user@tenant-a.com",
        senha_hash="hash",
        nome="User A",
        ativo=True,
    )
    user_b = User(
        email="user@tenant-b.com",
        senha_hash="hash",
        nome="User B",
        ativo=True,
    )
    session.add(user_a)
    session.add(user_b)
    await session.flush()

    # Add members to tenants
    member_a = TenantMember(
        tenant_id=tenant_a.id,
        user_id=user_a.id,
        role="owner",
    )
    member_b = TenantMember(
        tenant_id=tenant_b.id,
        user_id=user_b.id,
        role="owner",
    )
    session.add(member_a)
    session.add(member_b)
    await session.commit()

    # List members of tenant A
    from sqlalchemy import select

    stmt = select(TenantMember).where(TenantMember.tenant_id == tenant_a.id)
    result = await session.execute(stmt)
    members_a = result.scalars().all()

    assert len(members_a) == 1, "Tenant A should have only 1 member"
    assert members_a[0].user_id == user_a.id
