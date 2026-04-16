"""Test Rate Limiting — Usage Quotas & Billing.

Verifies rate limiting by plan and quota enforcement.
"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.models.uso import UsoMensal
from app.services.quota_service import QuotaService


@pytest.mark.asyncio
async def test_free_plan_limit(session: AsyncSession):
    """Test free plan has 1000 msg/month limit."""
    tenant = Tenant(nome="Free User", slug="free-user", plano="free", ativo=True)
    session.add(tenant)
    await session.commit()

    service = QuotaService(session)
    limit = await service.get_tenant_limit(tenant.id)

    assert limit == 1000


@pytest.mark.asyncio
async def test_pro_plan_limit(session: AsyncSession):
    """Test pro plan has 100000 msg/month limit."""
    tenant = Tenant(nome="Pro User", slug="pro-user", plano="pro", ativo=True)
    session.add(tenant)
    await session.commit()

    service = QuotaService(session)
    limit = await service.get_tenant_limit(tenant.id)

    assert limit == 100000


@pytest.mark.asyncio
async def test_enterprise_unlimited(session: AsyncSession):
    """Test enterprise plan is unlimited."""
    tenant = Tenant(
        nome="Enterprise", slug="enterprise", plano="enterprise", ativo=True
    )
    session.add(tenant)
    await session.commit()

    service = QuotaService(session)
    limit = await service.get_tenant_limit(tenant.id)

    assert limit is None


@pytest.mark.asyncio
async def test_can_send_under_limit(session: AsyncSession):
    """Test message sending allowed under quota."""
    tenant = Tenant(nome="Test", slug="test", plano="free", ativo=True)
    session.add(tenant)
    await session.commit()

    service = QuotaService(session)

    # Add 500 messages to this month
    now = __import__("datetime").datetime.utcnow()
    ano_mes = f"{now.year:04d}-{now.month:02d}"
    uso = UsoMensal(
        tenant_id=tenant.id,
        ano_mes=ano_mes,
        msgs_enviadas=500,
        msgs_failed=0,
    )
    session.add(uso)
    await session.commit()

    # Should be able to send
    can_send, msg = await service.can_send_message(tenant.id)
    assert can_send is True


@pytest.mark.asyncio
async def test_cannot_send_over_limit(session: AsyncSession):
    """Test message sending blocked over quota."""
    tenant = Tenant(nome="Test", slug="test", plano="free", ativo=True)
    session.add(tenant)
    await session.commit()

    # Add 1000 messages (reached limit)
    now = __import__("datetime").datetime.utcnow()
    ano_mes = f"{now.year:04d}-{now.month:02d}"
    uso = UsoMensal(
        tenant_id=tenant.id,
        ano_mes=ano_mes,
        msgs_enviadas=1000,
        msgs_failed=0,
    )
    session.add(uso)
    await session.commit()

    service = QuotaService(session)

    # Should not be able to send
    can_send, msg = await service.can_send_message(tenant.id)
    assert can_send is False
    assert "excedida" in msg.lower()
