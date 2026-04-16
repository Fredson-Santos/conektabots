"""Regra Service — Forwarding Rule Management.

Handles rule CRUD with normalized children (origem, destino, filtro, condicao).
"""

from datetime import datetime
from uuid import UUID
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.regra import (
    Regra,
    RegraOrigem,
    RegraDestino,
    RegraFiltro,
    RegraCondicao,
)
from app.schemas.regra import (
    RegraCreate,
    RegraUpdate,
    RegraResponse,
    RegraFullResponse,
)


class RegraService:
    """Manage forwarding rules."""

    def __init__(self, session: AsyncSession):
        """Initialize regra service.

        Args:
            session: Database session
        """
        self.session = session

    async def create(
        self, tenant_id: UUID, regra_in: RegraCreate
    ) -> RegraFullResponse:
        """Create new rule with children.

        Args:
            tenant_id: Tenant UUID
            regra_in: Rule creation data

        Returns:
            Created rule response with nested children
        """
        # Create rule
        regra = Regra(
            tenant_id=tenant_id,
            nome=regra_in.nome,
            bot_id=regra_in.bot_id,
            marketplace_id=regra_in.marketplace_id,
            ativo=True,
        )
        self.session.add(regra)
        await self.session.flush()

        # Create origins
        for origem_in in (regra_in.origens or []):
            origem = RegraOrigem(
                regra_id=regra.id,
                tipo=origem_in.tipo,
                canal=origem_in.canal,
            )
            self.session.add(origem)

        # Create destinations
        for destino_in in (regra_in.destinos or []):
            destino = RegraDestino(
                regra_id=regra.id,
                tipo=destino_in.tipo,
                canal=destino_in.canal,
                chat_id=destino_in.chat_id,
            )
            self.session.add(destino)

        # Create filters
        for filtro_in in (regra_in.filtros or []):
            filtro = RegraFiltro(
                regra_id=regra.id,
                tipo=filtro_in.tipo,
                valor=filtro_in.valor,
            )
            self.session.add(filtro)

        # Create conditions
        for condicao_in in (regra_in.condicoes or []):
            condicao = RegraCondicao(
                regra_id=regra.id,
                tipo=condicao_in.tipo,
                operador=condicao_in.operador,
                valor=condicao_in.valor,
            )
            self.session.add(condicao)

        await self.session.commit()
        return await self.get_full(regra.id, tenant_id)

    async def get(
        self, regra_id: UUID, tenant_id: UUID
    ) -> Optional[RegraResponse]:
        """Get rule by ID (basic, without children).

        Args:
            regra_id: Rule UUID
            tenant_id: Tenant UUID

        Returns:
            Rule response or None
        """
        stmt = select(Regra).where(
            and_(Regra.id == regra_id, Regra.tenant_id == tenant_id)
        )
        result = await self.session.execute(stmt)
        regra = result.scalar_one_or_none()

        return RegraResponse.from_attributes(regra) if regra else None

    async def get_full(
        self, regra_id: UUID, tenant_id: UUID
    ) -> Optional[RegraFullResponse]:
        """Get rule with all nested children.

        Args:
            regra_id: Rule UUID
            tenant_id: Tenant UUID

        Returns:
            Full rule response with children
        """
        stmt = select(Regra).where(
            and_(Regra.id == regra_id, Regra.tenant_id == tenant_id)
        )
        result = await self.session.execute(stmt)
        regra = result.scalar_one_or_none()

        if not regra:
            return None

        return RegraFullResponse.from_attributes(regra)

    async def list_by_tenant(self, tenant_id: UUID) -> list[RegraResponse]:
        """List all rules of tenant.

        Args:
            tenant_id: Tenant UUID

        Returns:
            List of rule responses
        """
        stmt = select(Regra).where(Regra.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        regras = result.scalars().all()

        return [RegraResponse.from_attributes(r) for r in regras]

    async def list_by_bot(self, bot_id: UUID, tenant_id: UUID) -> list[RegraResponse]:
        """List rules for a specific bot.

        Args:
            bot_id: Bot UUID
            tenant_id: Tenant UUID

        Returns:
            List of rule responses
        """
        stmt = select(Regra).where(
            and_(Regra.bot_id == bot_id, Regra.tenant_id == tenant_id)
        )
        result = await self.session.execute(stmt)
        regras = result.scalars().all()

        return [RegraResponse.from_attributes(r) for r in regras]

    async def update(
        self, regra_id: UUID, tenant_id: UUID, regra_in: RegraUpdate
    ) -> Optional[RegraResponse]:
        """Update rule.

        Args:
            regra_id: Rule UUID
            tenant_id: Tenant UUID
            regra_in: Update data

        Returns:
            Updated rule response
        """
        stmt = select(Regra).where(
            and_(Regra.id == regra_id, Regra.tenant_id == tenant_id)
        )
        result = await self.session.execute(stmt)
        regra = result.scalar_one_or_none()

        if not regra:
            return None

        if regra_in.nome:
            regra.nome = regra_in.nome
        if regra_in.ativo is not None:
            regra.ativo = regra_in.ativo

        await self.session.commit()
        await self.session.refresh(regra)

        return RegraResponse.from_attributes(regra)

    async def delete(self, regra_id: UUID, tenant_id: UUID) -> None:
        """Soft delete rule.

        Args:
            regra_id: Rule UUID
            tenant_id: Tenant UUID
        """
        stmt = select(Regra).where(
            and_(Regra.id == regra_id, Regra.tenant_id == tenant_id)
        )
        result = await self.session.execute(stmt)
        regra = result.scalar_one_or_none()

        if regra:
            regra.deletado_em = datetime.utcnow()
            await self.session.commit()

    # ===================== Bulk Operations =====================

    async def activate_multiple(
        self, regra_ids: list[UUID], tenant_id: UUID
    ) -> None:
        """Activate multiple rules.

        Args:
            regra_ids: List of rule UUIDs
            tenant_id: Tenant UUID
        """
        stmt = select(Regra).where(
            and_(Regra.id.in_(regra_ids), Regra.tenant_id == tenant_id)
        )
        result = await self.session.execute(stmt)
        regras = result.scalars().all()

        for regra in regras:
            regra.ativo = True

        await self.session.commit()

    async def deactivate_multiple(
        self, regra_ids: list[UUID], tenant_id: UUID
    ) -> None:
        """Deactivate multiple rules.

        Args:
            regra_ids: List of rule UUIDs
            tenant_id: Tenant UUID
        """
        stmt = select(Regra).where(
            and_(Regra.id.in_(regra_ids), Regra.tenant_id == tenant_id)
        )
        result = await self.session.execute(stmt)
        regras = result.scalars().all()

        for regra in regras:
            regra.ativo = False

        await self.session.commit()
