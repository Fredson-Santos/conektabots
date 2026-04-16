"""Agendamento Service — Scheduled Automation Management.

Handles schedule CRUD with normalized children (origem, destino, horario, filtro, condicao).
"""

from datetime import datetime, time
from uuid import UUID
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agendamento import (
    Agendamento,
    AgendamentoOrigem,
    AgendamentoDestino,
    AgendamentoHorario,
    AgendamentoFiltro,
    AgendamentoCondicao,
)
from app.schemas.agendamento import (
    AgendamentoCreate,
    AgendamentoUpdate,
    AgendamentoResponse,
    AgendamentoFullResponse,
    AgendamentoHorarioCreate,
)


class AgendamentoService:
    """Manage scheduled automations."""

    def __init__(self, session: AsyncSession):
        """Initialize agendamento service.

        Args:
            session: Database session
        """
        self.session = session

    async def create(
        self, tenant_id: UUID, agendamento_in: AgendamentoCreate
    ) -> AgendamentoFullResponse:
        """Create new schedule with children.

        Args:
            tenant_id: Tenant UUID
            agendamento_in: Schedule creation data

        Returns:
            Created schedule response with nested children
        """
        # Create schedule
        agendamento = Agendamento(
            tenant_id=tenant_id,
            nome=agendamento_in.nome,
            bot_id=agendamento_in.bot_id,
            marketplace_id=agendamento_in.marketplace_id,
            tipo_envio=agendamento_in.tipo_envio or "sequencial",
            ativo=True,
        )
        self.session.add(agendamento)
        await self.session.flush()

        # Create origins
        for origem_in in (agendamento_in.origens or []):
            origem = AgendamentoOrigem(
                agendamento_id=agendamento.id,
                tipo=origem_in.tipo,
                canal=origem_in.canal,
            )
            self.session.add(origem)

        # Create destinations
        for destino_in in (agendamento_in.destinos or []):
            destino = AgendamentoDestino(
                agendamento_id=agendamento.id,
                tipo=destino_in.tipo,
                canal=destino_in.canal,
                chat_id=destino_in.chat_id,
            )
            self.session.add(destino)

        # Create horarios
        for horario_in in (agendamento_in.horarios or []):
            # Parse HH:MM string to time object
            hora_parts = horario_in.horario.split(":")
            horario_time = time(int(hora_parts[0]), int(hora_parts[1]))

            horario = AgendamentoHorario(
                agendamento_id=agendamento.id,
                horario=horario_time,
            )
            self.session.add(horario)

        # Create filters
        for filtro_in in (agendamento_in.filtros or []):
            filtro = AgendamentoFiltro(
                agendamento_id=agendamento.id,
                tipo=filtro_in.tipo,
                valor=filtro_in.valor,
            )
            self.session.add(filtro)

        # Create conditions
        for condicao_in in (agendamento_in.condicoes or []):
            condicao = AgendamentoCondicao(
                agendamento_id=agendamento.id,
                tipo=condicao_in.tipo,
                operador=condicao_in.operador,
                valor=condicao_in.valor,
            )
            self.session.add(condicao)

        await self.session.commit()
        return await self.get_full(agendamento.id, tenant_id)

    async def get(
        self, agendamento_id: UUID, tenant_id: UUID
    ) -> Optional[AgendamentoResponse]:
        """Get schedule by ID (basic, without children).

        Args:
            agendamento_id: Schedule UUID
            tenant_id: Tenant UUID

        Returns:
            Schedule response or None
        """
        stmt = select(Agendamento).where(
            and_(Agendamento.id == agendamento_id, Agendamento.tenant_id == tenant_id)
        )
        result = await self.session.execute(stmt)
        agendamento = result.scalar_one_or_none()

        return (
            AgendamentoResponse.from_attributes(agendamento) if agendamento else None
        )

    async def get_full(
        self, agendamento_id: UUID, tenant_id: UUID
    ) -> Optional[AgendamentoFullResponse]:
        """Get schedule with all nested children.

        Args:
            agendamento_id: Schedule UUID
            tenant_id: Tenant UUID

        Returns:
            Full schedule response with children
        """
        stmt = select(Agendamento).where(
            and_(Agendamento.id == agendamento_id, Agendamento.tenant_id == tenant_id)
        )
        result = await self.session.execute(stmt)
        agendamento = result.scalar_one_or_none()

        if not agendamento:
            return None

        return AgendamentoFullResponse.from_attributes(agendamento)

    async def list_by_tenant(self, tenant_id: UUID) -> list[AgendamentoResponse]:
        """List all schedules of tenant.

        Args:
            tenant_id: Tenant UUID

        Returns:
            List of schedule responses
        """
        stmt = select(Agendamento).where(Agendamento.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        agendamentos = result.scalars().all()

        return [AgendamentoResponse.from_attributes(a) for a in agendamentos]

    async def list_by_bot(
        self, bot_id: UUID, tenant_id: UUID
    ) -> list[AgendamentoResponse]:
        """List schedules for a specific bot.

        Args:
            bot_id: Bot UUID
            tenant_id: Tenant UUID

        Returns:
            List of schedule responses
        """
        stmt = select(Agendamento).where(
            and_(Agendamento.bot_id == bot_id, Agendamento.tenant_id == tenant_id)
        )
        result = await self.session.execute(stmt)
        agendamentos = result.scalars().all()

        return [AgendamentoResponse.from_attributes(a) for a in agendamentos]

    async def update(
        self, agendamento_id: UUID, tenant_id: UUID, agendamento_in: AgendamentoUpdate
    ) -> Optional[AgendamentoResponse]:
        """Update schedule.

        Args:
            agendamento_id: Schedule UUID
            tenant_id: Tenant UUID
            agendamento_in: Update data

        Returns:
            Updated schedule response
        """
        stmt = select(Agendamento).where(
            and_(
                Agendamento.id == agendamento_id, Agendamento.tenant_id == tenant_id
            )
        )
        result = await self.session.execute(stmt)
        agendamento = result.scalar_one_or_none()

        if not agendamento:
            return None

        if agendamento_in.nome:
            agendamento.nome = agendamento_in.nome
        if agendamento_in.tipo_envio:
            agendamento.tipo_envio = agendamento_in.tipo_envio
        if agendamento_in.ativo is not None:
            agendamento.ativo = agendamento_in.ativo

        await self.session.commit()
        await self.session.refresh(agendamento)

        return AgendamentoResponse.from_attributes(agendamento)

    async def delete(self, agendamento_id: UUID, tenant_id: UUID) -> None:
        """Soft delete schedule.

        Args:
            agendamento_id: Schedule UUID
            tenant_id: Tenant UUID
        """
        stmt = select(Agendamento).where(
            and_(
                Agendamento.id == agendamento_id, Agendamento.tenant_id == tenant_id
            )
        )
        result = await self.session.execute(stmt)
        agendamento = result.scalar_one_or_none()

        if agendamento:
            agendamento.deletado_em = datetime.utcnow()
            await self.session.commit()

    # ===================== Sequence Management =====================

    async def reset_sequence(self, agendamento_id: UUID, tenant_id: UUID) -> None:
        """Reset sequence counter (msg_id_atual) for sequencial mode.

        Args:
            agendamento_id: Schedule UUID
            tenant_id: Tenant UUID
        """
        stmt = select(Agendamento).where(
            and_(
                Agendamento.id == agendamento_id, Agendamento.tenant_id == tenant_id
            )
        )
        result = await self.session.execute(stmt)
        agendamento = result.scalar_one_or_none()

        if agendamento:
            agendamento.msg_id_atual = 0
            await self.session.commit()

    # ===================== Bulk Operations =====================

    async def activate_multiple(
        self, agendamento_ids: list[UUID], tenant_id: UUID
    ) -> None:
        """Activate multiple schedules.

        Args:
            agendamento_ids: List of schedule UUIDs
            tenant_id: Tenant UUID
        """
        stmt = select(Agendamento).where(
            and_(
                Agendamento.id.in_(agendamento_ids),
                Agendamento.tenant_id == tenant_id,
            )
        )
        result = await self.session.execute(stmt)
        agendamentos = result.scalars().all()

        for agendamento in agendamentos:
            agendamento.ativo = True

        await self.session.commit()

    async def deactivate_multiple(
        self, agendamento_ids: list[UUID], tenant_id: UUID
    ) -> None:
        """Deactivate multiple schedules.

        Args:
            agendamento_ids: List of schedule UUIDs
            tenant_id: Tenant UUID
        """
        stmt = select(Agendamento).where(
            and_(
                Agendamento.id.in_(agendamento_ids),
                Agendamento.tenant_id == tenant_id,
            )
        )
        result = await self.session.execute(stmt)
        agendamentos = result.scalars().all()

        for agendamento in agendamentos:
            agendamento.ativo = False

        await self.session.commit()
