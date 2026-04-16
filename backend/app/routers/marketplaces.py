"""Marketplaces Router — Marketplace Integration Management.

POST /api/v1/marketplaces — Create integration
GET /api/v1/marketplaces — List integrations
GET /api/v1/marketplaces/{marketplace_id} — Get integration
PATCH /api/v1/marketplaces/{marketplace_id} — Update integration
DELETE /api/v1/marketplaces/{marketplace_id} — Delete integration
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_tenant
from app.schemas.marketplace import (
    MarketplaceIntegracaoCreate,
    MarketplaceIntegracaoUpdate,
    MarketplaceIntegracaoResponse,
)
from app.services.marketplace_service import MarketplaceService


router = APIRouter(prefix="/api/v1/marketplaces", tags=["marketplaces"])


@router.post(
    "/", response_model=MarketplaceIntegracaoResponse, status_code=status.HTTP_201_CREATED
)
async def create_marketplace(
    marketplace_in: MarketplaceIntegracaoCreate,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Create new marketplace integration.

    Args:
        marketplace_in: Integration data
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Created integration response (without credentials)
    """
    service = MarketplaceService(session)
    return await service.create(tenant_id, marketplace_in)


@router.get("/", response_model=list[MarketplaceIntegracaoResponse])
async def list_integrations(
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """List all marketplace integrations of tenant.

    Args:
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        List of integration responses
    """
    service = MarketplaceService(session)
    return await service.list_by_tenant(tenant_id)


@router.get("/{marketplace_id}", response_model=MarketplaceIntegracaoResponse)
async def get_marketplace(
    marketplace_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Get specific marketplace integration.

    Args:
        marketplace_id: Integration UUID
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Integration response or 404
    """
    service = MarketplaceService(session)
    marketplace = await service.get(marketplace_id, tenant_id)

    if not marketplace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integração não encontrada",
        )

    return marketplace


@router.patch("/{marketplace_id}", response_model=MarketplaceIntegracaoResponse)
async def update_marketplace(
    marketplace_id: UUID,
    marketplace_in: MarketplaceIntegracaoUpdate,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Update marketplace integration.

    Args:
        marketplace_id: Integration UUID
        marketplace_in: Update data
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Updated integration response
    """
    service = MarketplaceService(session)
    marketplace = await service.update(marketplace_id, tenant_id, marketplace_in)

    if not marketplace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integração não encontrada",
        )

    return marketplace


@router.delete("/{marketplace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_marketplace(
    marketplace_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Delete (soft delete) marketplace integration.

    Args:
        marketplace_id: Integration UUID
        tenant_id: Injected current tenant
        session: Database session
    """
    service = MarketplaceService(session)
    await service.delete(marketplace_id, tenant_id)
