"""Tenants Router — Tenant & Membership Management.

GET /api/v1/tenants/{tenant_id} — Get tenant
PATCH /api/v1/tenants/{tenant_id} — Update tenant
GET /api/v1/tenants/{tenant_id}/limits — Get usage limits
GET /api/v1/tenants/{tenant_id}/members — List members
POST /api/v1/tenants/{tenant_id}/members — Add member
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user, get_current_tenant
from app.schemas.tenant import (
    TenantResponse,
    TenantUpdate,
    TenantLimitsResponse,
    TenantMemberAdd,
    TenantMemberResponse,
    TenantMemberUpdate,
)
from app.services.tenant_service import TenantService


router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    current_tenant: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Get tenant details.

    Args:
        tenant_id: Tenant UUID
        current_tenant: Injected current tenant (for isolation check)
        session: Database session

    Returns:
        Tenant response
    """
    # Verify tenant isolation
    if tenant_id != current_tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado",
        )

    service = TenantService(session)
    tenant = await service.get(tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant não encontrado",
        )

    return tenant


@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    tenant_in: TenantUpdate,
    current_tenant: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Update tenant (nome, plano, etc).

    Args:
        tenant_id: Tenant UUID
        tenant_in: Update data
        current_tenant: Injected current tenant
        session: Database session

    Returns:
        Updated tenant response
    """
    # Verify tenant isolation
    if tenant_id != current_tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado",
        )

    service = TenantService(session)
    tenant = await service.update(tenant_id, tenant_in)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant não encontrado",
        )

    return tenant


@router.get("/{tenant_id}/limits", response_model=TenantLimitsResponse)
async def get_tenant_limits(
    tenant_id: UUID,
    current_tenant: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Get tenant usage limits and current usage.

    Args:
        tenant_id: Tenant UUID
        current_tenant: Injected current tenant
        session: Database session

    Returns:
        Tenant limits response
    """
    # Verify tenant isolation
    if tenant_id != current_tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado",
        )

    service = TenantService(session)
    return await service.get_limits(tenant_id)


# ===================== Members =====================


@router.get("/{tenant_id}/members", response_model=list[TenantMemberResponse])
async def list_members(
    tenant_id: UUID,
    current_tenant: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """List all members of tenant.

    Args:
        tenant_id: Tenant UUID
        current_tenant: Injected current tenant
        session: Database session

    Returns:
        List of member responses
    """
    # Verify tenant isolation
    if tenant_id != current_tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado",
        )

    service = TenantService(session)
    return await service.list_members(tenant_id)


@router.post(
    "/{tenant_id}/members",
    response_model=TenantMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_member(
    tenant_id: UUID,
    member_in: TenantMemberAdd,
    current_tenant: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Add new member to tenant.

    Args:
        tenant_id: Tenant UUID
        member_in: Member data
        current_tenant: Injected current tenant
        session: Database session

    Returns:
        Created member response
    """
    # Verify tenant isolation
    if tenant_id != current_tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado",
        )

    service = TenantService(session)

    try:
        return await service.add_member(tenant_id, member_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.patch("/{tenant_id}/members/{member_id}", response_model=TenantMemberResponse)
async def update_member(
    tenant_id: UUID,
    member_id: UUID,
    member_in: TenantMemberUpdate,
    current_tenant: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Update tenant member role or status.

    Args:
        tenant_id: Tenant UUID
        member_id: Member UUID
        member_in: Update data
        current_tenant: Injected current tenant
        session: Database session

    Returns:
        Updated member response
    """
    # Verify tenant isolation
    if tenant_id != current_tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado",
        )

    service = TenantService(session)
    member = await service.update_member(tenant_id, member_id, member_in)

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membro não encontrado",
        )

    return member


@router.delete("/{tenant_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    tenant_id: UUID,
    member_id: UUID,
    current_tenant: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Remove member from tenant.

    Args:
        tenant_id: Tenant UUID
        member_id: Member UUID
        current_tenant: Injected current tenant
        session: Database session
    """
    # Verify tenant isolation
    if tenant_id != current_tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado",
        )

    service = TenantService(session)
    await service.remove_member(tenant_id, member_id)
