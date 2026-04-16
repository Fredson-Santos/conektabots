"""Regras Router — Forwarding Rules Management.

POST /api/v1/regras — Create rule
GET /api/v1/regras — List rules
GET /api/v1/regras/{regra_id} — Get rule with children
PATCH /api/v1/regras/{regra_id} — Update rule
DELETE /api/v1/regras/{regra_id} — Delete rule
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_tenant
from app.schemas.regra import (
    RegraCreate,
    RegraUpdate,
    RegraResponse,
    RegraFullResponse,
)
from app.services.regra_service import RegraService


router = APIRouter(prefix="/api/v1/regras", tags=["regras"])


@router.post("/", response_model=RegraFullResponse, status_code=status.HTTP_201_CREATED)
async def create_regra(
    regra_in: RegraCreate,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Create new forwarding rule with children.

    Args:
        regra_in: Rule creation data (includes origens, destinos, filtros, condicoes)
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Created rule response with all nested children
    """
    service = RegraService(session)
    return await service.create(tenant_id, regra_in)


@router.get("/", response_model=list[RegraResponse])
async def list_regras(
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """List all forwarding rules of tenant.

    Args:
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        List of rule responses (basic, without children)
    """
    service = RegraService(session)
    return await service.list_by_tenant(tenant_id)


@router.get("/{regra_id}", response_model=RegraFullResponse)
async def get_regra(
    regra_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Get specific rule with all nested children.

    Args:
        regra_id: Rule UUID
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Full rule response with children (origens, destinos, filtros, condicoes)
    """
    service = RegraService(session)
    regra = await service.get_full(regra_id, tenant_id)

    if not regra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra não encontrada",
        )

    return regra


@router.patch("/{regra_id}", response_model=RegraResponse)
async def update_regra(
    regra_id: UUID,
    regra_in: RegraUpdate,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Update rule metadata (nome, ativo).

    Args:
        regra_id: Rule UUID
        regra_in: Update data
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Updated rule response
    """
    service = RegraService(session)
    regra = await service.update(regra_id, tenant_id, regra_in)

    if not regra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra não encontrada",
        )

    return regra


@router.delete("/{regra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_regra(
    regra_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Delete (soft delete) rule.

    Args:
        regra_id: Rule UUID
        tenant_id: Injected current tenant
        session: Database session
    """
    service = RegraService(session)
    await service.delete(regra_id, tenant_id)
