"""Agendamentos Router — Scheduled Automation Management.

POST /api/v1/agendamentos — Create schedule
GET /api/v1/agendamentos — List schedules
GET /api/v1/agendamentos/{agendamento_id} — Get schedule with children
PATCH /api/v1/agendamentos/{agendamento_id} — Update schedule
DELETE /api/v1/agendamentos/{agendamento_id} — Delete schedule
POST /api/v1/agendamentos/{agendamento_id}/reset-sequence — Reset sequence counter
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_tenant
from app.schemas.agendamento import (
    AgendamentoCreate,
    AgendamentoUpdate,
    AgendamentoResponse,
    AgendamentoFullResponse,
)
from app.services.agendamento_service import AgendamentoService


router = APIRouter(prefix="/api/v1/agendamentos", tags=["agendamentos"])


@router.post(
    "/", response_model=AgendamentoFullResponse, status_code=status.HTTP_201_CREATED
)
async def create_agendamento(
    agendamento_in: AgendamentoCreate,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Create new scheduled automation with children.

    Args:
        agendamento_in: Schedule creation data (includes origens, destinos, horarios, filtros, condicoes)
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Created schedule response with all nested children
    """
    service = AgendamentoService(session)
    return await service.create(tenant_id, agendamento_in)


@router.get("/", response_model=list[AgendamentoResponse])
async def list_agendamentos(
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """List all scheduled automations of tenant.

    Args:
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        List of schedule responses (basic, without children)
    """
    service = AgendamentoService(session)
    return await service.list_by_tenant(tenant_id)


@router.get("/{agendamento_id}", response_model=AgendamentoFullResponse)
async def get_agendamento(
    agendamento_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Get specific schedule with all nested children.

    Args:
        agendamento_id: Schedule UUID
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Full schedule response with children (origens, destinos, horarios, filtros, condicoes)
    """
    service = AgendamentoService(session)
    agendamento = await service.get_full(agendamento_id, tenant_id)

    if not agendamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )

    return agendamento


@router.patch("/{agendamento_id}", response_model=AgendamentoResponse)
async def update_agendamento(
    agendamento_id: UUID,
    agendamento_in: AgendamentoUpdate,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Update schedule metadata (nome, tipo_envio, ativo).

    Args:
        agendamento_id: Schedule UUID
        agendamento_in: Update data
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Updated schedule response
    """
    service = AgendamentoService(session)
    agendamento = await service.update(agendamento_id, tenant_id, agendamento_in)

    if not agendamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )

    return agendamento


@router.delete("/{agendamento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agendamento(
    agendamento_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Delete (soft delete) schedule.

    Args:
        agendamento_id: Schedule UUID
        tenant_id: Injected current tenant
        session: Database session
    """
    service = AgendamentoService(session)
    await service.delete(agendamento_id, tenant_id)


# ===================== Sequence Management =====================


@router.post("/{agendamento_id}/reset-sequence", status_code=status.HTTP_204_NO_CONTENT)
async def reset_sequence(
    agendamento_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Reset sequence counter (msg_id_atual) to 0.

    Only relevant for schedules with tipo_envio = 'sequencial'.

    Args:
        agendamento_id: Schedule UUID
        tenant_id: Injected current tenant
        session: Database session
    """
    service = AgendamentoService(session)
    await service.reset_sequence(agendamento_id, tenant_id)
