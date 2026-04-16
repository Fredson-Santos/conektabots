"""Test Marketplace Service — CRUD and credential handling.

Verifies marketplace integrations support optional encrypted credentials,
tenant isolation, and update flows.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.marketplace import (
    MarketplaceIntegracaoCreate,
    MarketplaceIntegracaoUpdate,
)
from app.services.marketplace_service import MarketplaceService


async def _fake_encrypt(_: str) -> bytes:
    return b"encrypted-credentials"


@pytest.mark.asyncio
async def test_create_marketplace_with_credentials(session: AsyncSession, tenant_a):
    """Creating a marketplace with credentials should mark it configured."""
    service = MarketplaceService(session)
    service.crypto.encrypt = _fake_encrypt

    request = MarketplaceIntegracaoCreate(
        tipo="shopee",
        nome="Loja Shopee",
        credenciais={
            "shop_id": "123456",
            "app_id": "app-001",
            "app_secret": "super-secret",
        },
    )

    response = await service.create(tenant_a.id, request)

    assert response.nome == "Loja Shopee"
    assert response.tipo == "shopee"
    assert response.tenant_id == tenant_a.id
    assert response.is_configured is True


@pytest.mark.asyncio
async def test_update_marketplace_can_toggle_active_and_replace_credentials(
    session: AsyncSession,
    tenant_a,
):
    """Updating a marketplace should allow safe field replacement."""
    service = MarketplaceService(session)
    service.crypto.encrypt = _fake_encrypt

    created = await service.create(
        tenant_a.id,
        MarketplaceIntegracaoCreate(
            tipo="mercado_livre",
            nome="Integração ML",
            credenciais={
                "app_id": "app-001",
                "app_secret": "initial-secret",
                "access_token": "token-1",
                "user_id": "user-1",
            },
        ),
    )

    updated = await service.update(
        created.id,
        tenant_a.id,
        MarketplaceIntegracaoUpdate(
            nome="Integração ML Atualizada",
            ativo=False,
            credenciais={
                "app_id": "app-002",
                "app_secret": "rotated-secret",
                "access_token": "token-2",
                "user_id": "user-2",
            },
        ),
    )

    assert updated is not None
    assert updated.nome == "Integração ML Atualizada"
    assert updated.ativo is False
    assert updated.is_configured is True
