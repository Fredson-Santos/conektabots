"""Tenant Service — Multi-Tenant Management.

Handles tenant CRUD, membership, settings, and billing.
"""

from datetime import datetime
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant, TenantMember
from app.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantLimitsResponse,
    TenantMemberAdd,
    TenantMemberUpdate,
    TenantMemberResponse,
)
from app.services.auth_service import AuthService
from app.services.quota_service import QuotaService


class TenantService:
    """Manage tenants and memberships."""

    def __init__(self, session: AsyncSession):
        """Initialize tenant service.

        Args:
            session: Database session
        """
        self.session = session
        self.auth_service = AuthService(session)
        self.quota_service = QuotaService(session)

    async def create(self, tenant_in: TenantCreate) -> TenantResponse:
        """Create new tenant.

        Args:
            tenant_in: Tenant creation data

        Returns:
            Created tenant response

        Raises:
            ValueError if slug already exists
        """
        # Check slug uniqueness
        stmt = select(Tenant).where(Tenant.slug == tenant_in.slug.lower())
        existing = await self.session.execute(stmt)
        if existing.scalar_one_or_none():
            raise ValueError(f"Slug '{tenant_in.slug}' já existe")

        tenant = Tenant(
            nome=tenant_in.nome,
            slug=tenant_in.slug.lower(),
            plano=tenant_in.plano or "free",
            ativo=True,
        )
        self.session.add(tenant)
        await self.session.commit()
        await self.session.refresh(tenant)

        return TenantResponse.from_attributes(tenant)

    async def get(self, tenant_id: UUID) -> TenantResponse:
        """Get tenant by ID.

        Args:
            tenant_id: Tenant UUID

        Returns:
            Tenant response or None
        """
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await self.session.execute(stmt)
        tenant = result.scalar_one_or_none()

        return TenantResponse.from_attributes(tenant) if tenant else None

    async def update(self, tenant_id: UUID, tenant_in: TenantUpdate) -> TenantResponse:
        """Update tenant.

        Args:
            tenant_id: Tenant UUID
            tenant_in: Update data

        Returns:
            Updated tenant response
        """
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await self.session.execute(stmt)
        tenant = result.scalar_one_or_none()

        if not tenant:
            return None

        # Update fields
        if tenant_in.nome:
            tenant.nome = tenant_in.nome
        if tenant_in.plano:
            tenant.plano = tenant_in.plano
        if tenant_in.ativo is not None:
            tenant.ativo = tenant_in.ativo

        await self.session.commit()
        await self.session.refresh(tenant)

        return TenantResponse.from_attributes(tenant)

    async def delete(self, tenant_id: UUID) -> None:
        """Soft delete tenant (set deletado_em).

        Args:
            tenant_id: Tenant UUID
        """
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await self.session.execute(stmt)
        tenant = result.scalar_one_or_none()

        if tenant:
            tenant.deletado_em = datetime.utcnow()
            await self.session.commit()

    async def get_limits(self, tenant_id: UUID) -> TenantLimitsResponse:
        """Get tenant usage limits.

        Args:
            tenant_id: Tenant UUID

        Returns:
            Limits response
        """
        quota_info = await self.quota_service.get_quota_info(tenant_id)

        return TenantLimitsResponse(
            limite_bots=10,  # TODO: Make configurable by plan
            bots_usados=0,  # TODO: Count from DB
            limite_regras=100,
            regras_usadas=0,
            limite_agendamentos=50,
            agendamentos_usados=0,
            limite_msgs_mes=quota_info["limit"],
            msgs_enviadas_mes=quota_info["usage"],
            reset_at=quota_info["reset_at"],
        )

    # ===================== Member Management =====================

    async def add_member(
        self, tenant_id: UUID, member_in: TenantMemberAdd
    ) -> TenantMemberResponse:
        """Add member to tenant.

        Args:
            tenant_id: Tenant UUID
            member_in: Member add data

        Returns:
            Created member response
        """
        # Check if member already exists
        stmt = select(TenantMember).where(
            and_(TenantMember.tenant_id == tenant_id, TenantMember.email == member_in.email)
        )
        existing = await self.session.execute(stmt)
        if existing.scalar_one_or_none():
            raise ValueError(f"Membro com email '{member_in.email}' já existe")

        member = TenantMember(
            tenant_id=tenant_id,
            email=member_in.email,
            role=member_in.role,
            ativo=True,
        )
        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)

        return TenantMemberResponse.from_attributes(member)

    async def list_members(self, tenant_id: UUID) -> list[TenantMemberResponse]:
        """List all members of tenant.

        Args:
            tenant_id: Tenant UUID

        Returns:
            List of member responses
        """
        stmt = select(TenantMember).where(TenantMember.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        members = result.scalars().all()

        return [TenantMemberResponse.from_attributes(m) for m in members]

    async def update_member(
        self, tenant_id: UUID, member_id: UUID, member_in: TenantMemberUpdate
    ) -> TenantMemberResponse:
        """Update tenant member.

        Args:
            tenant_id: Tenant UUID
            member_id: Member UUID
            member_in: Update data

        Returns:
            Updated member response
        """
        stmt = select(TenantMember).where(
            and_(
                TenantMember.id == member_id, TenantMember.tenant_id == tenant_id
            )
        )
        result = await self.session.execute(stmt)
        member = result.scalar_one_or_none()

        if not member:
            return None

        if member_in.role:
            member.role = member_in.role
        if member_in.ativo is not None:
            member.ativo = member_in.ativo

        await self.session.commit()
        await self.session.refresh(member)

        return TenantMemberResponse.from_attributes(member)

    async def remove_member(self, tenant_id: UUID, member_id: UUID) -> None:
        """Remove member from tenant.

        Args:
            tenant_id: Tenant UUID
            member_id: Member UUID
        """
        stmt = select(TenantMember).where(
            and_(
                TenantMember.id == member_id, TenantMember.tenant_id == tenant_id
            )
        )
        result = await self.session.execute(stmt)
        member = result.scalar_one_or_none()

        if member:
            await self.session.delete(member)
            await self.session.commit()
