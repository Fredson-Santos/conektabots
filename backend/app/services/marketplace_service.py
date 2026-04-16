"""Marketplace Service — Marketplace Integration Management.

Handles marketplace CRUD (Shopee, Mercado Livre, Amazon, etc).
Encrypts integration credentials.
"""

from datetime import datetime
import json
from uuid import UUID
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.marketplace import MarketplaceIntegracao
from app.schemas.marketplace import (
    MarketplaceIntegracaoCreate,
    MarketplaceIntegracaoUpdate,
    MarketplaceIntegracaoResponse,
)
from app.services.crypto_service import CryptoService


class MarketplaceService:
    """Manage marketplace integrations."""

    def __init__(self, session: AsyncSession):
        """Initialize marketplace service.

        Args:
            session: Database session
        """
        self.session = session
        self.crypto = CryptoService(session)

    async def create(
        self, tenant_id: UUID, marketplace_in: MarketplaceIntegracaoCreate
    ) -> MarketplaceIntegracaoResponse:
        """Create new marketplace integration.

        Args:
            tenant_id: Tenant UUID
            marketplace_in: Integration creation data

        Returns:
            Created integration response (without credentials)
        """
        # Encrypt credentials if provided
        credenciais_enc = None
        if marketplace_in.credenciais:
            credenciais_json = json.dumps(marketplace_in.credenciais, ensure_ascii=False)
            credenciais_enc = await self.crypto.encrypt(credenciais_json)

        integration = MarketplaceIntegracao(
            tenant_id=tenant_id,
            tipo=marketplace_in.tipo,
            nome=marketplace_in.nome,
            credenciais_enc=credenciais_enc,
            ativo=True,
        )
        self.session.add(integration)
        await self.session.commit()
        await self.session.refresh(integration)

        return MarketplaceIntegracaoResponse.model_validate(
            integration, from_attributes=True
        )

    async def get(
        self, marketplace_id: UUID, tenant_id: UUID
    ) -> Optional[MarketplaceIntegracaoResponse]:
        """Get marketplace integration by ID.

        Args:
            marketplace_id: Integration UUID
            tenant_id: Tenant UUID (for isolation)

        Returns:
            Integration response or None
        """
        stmt = select(MarketplaceIntegracao).where(
            and_(
                MarketplaceIntegracao.id == marketplace_id,
                MarketplaceIntegracao.tenant_id == tenant_id,
            )
        )
        result = await self.session.execute(stmt)
        integration = result.scalar_one_or_none()

        return (
            MarketplaceIntegracaoResponse.model_validate(
                integration, from_attributes=True
            )
            if integration
            else None
        )

    async def list_by_tenant(self, tenant_id: UUID) -> list[MarketplaceIntegracaoResponse]:
        """List all integrations of tenant.

        Args:
            tenant_id: Tenant UUID

        Returns:
            List of integration responses
        """
        stmt = select(MarketplaceIntegracao).where(
            MarketplaceIntegracao.tenant_id == tenant_id
        )
        result = await self.session.execute(stmt)
        integrations = result.scalars().all()

        return [
            MarketplaceIntegracaoResponse.model_validate(m, from_attributes=True)
            for m in integrations
        ]

    async def list_by_tipo(self, tenant_id: UUID, tipo: str) -> list[MarketplaceIntegracaoResponse]:
        """List integrations by type.

        Args:
            tenant_id: Tenant UUID
            tipo: Marketplace type (shopee, mercado_livre, amazon, etc)

        Returns:
            List of integration responses
        """
        stmt = select(MarketplaceIntegracao).where(
            and_(
                MarketplaceIntegracao.tenant_id == tenant_id,
                MarketplaceIntegracao.tipo == tipo,
            )
        )
        result = await self.session.execute(stmt)
        integrations = result.scalars().all()

        return [
            MarketplaceIntegracaoResponse.model_validate(m, from_attributes=True)
            for m in integrations
        ]

    async def update(
        self,
        marketplace_id: UUID,
        tenant_id: UUID,
        marketplace_in: MarketplaceIntegracaoUpdate,
    ) -> Optional[MarketplaceIntegracaoResponse]:
        """Update marketplace integration.

        Args:
            marketplace_id: Integration UUID
            tenant_id: Tenant UUID
            marketplace_in: Update data

        Returns:
            Updated integration response
        """
        stmt = select(MarketplaceIntegracao).where(
            and_(
                MarketplaceIntegracao.id == marketplace_id,
                MarketplaceIntegracao.tenant_id == tenant_id,
            )
        )
        result = await self.session.execute(stmt)
        integration = result.scalar_one_or_none()

        if not integration:
            return None

        if marketplace_in.nome:
            integration.nome = marketplace_in.nome
        if marketplace_in.credenciais:
            credenciais_json = json.dumps(marketplace_in.credenciais, ensure_ascii=False)
            integration.credenciais_enc = await self.crypto.encrypt(
                credenciais_json
            )
        if marketplace_in.ativo is not None:
            integration.ativo = marketplace_in.ativo

        await self.session.commit()
        await self.session.refresh(integration)

        return MarketplaceIntegracaoResponse.model_validate(
            integration, from_attributes=True
        )

    async def delete(self, marketplace_id: UUID, tenant_id: UUID) -> None:
        """Soft delete marketplace integration.

        Args:
            marketplace_id: Integration UUID
            tenant_id: Tenant UUID
        """
        stmt = select(MarketplaceIntegracao).where(
            and_(
                MarketplaceIntegracao.id == marketplace_id,
                MarketplaceIntegracao.tenant_id == tenant_id,
            )
        )
        result = await self.session.execute(stmt)
        integration = result.scalar_one_or_none()

        if integration:
            integration.deletado_em = datetime.utcnow()
            await self.session.commit()

    # ===================== Credential Management =====================

    async def get_credentials(
        self, marketplace_id: UUID, tenant_id: UUID
    ) -> Optional[dict]:
        """Get decrypted credentials for integration.

        Args:
            marketplace_id: Integration UUID
            tenant_id: Tenant UUID

        Returns:
            Decrypted credentials dict or None
        """
        stmt = select(MarketplaceIntegracao).where(
            and_(
                MarketplaceIntegracao.id == marketplace_id,
                MarketplaceIntegracao.tenant_id == tenant_id,
            )
        )
        result = await self.session.execute(stmt)
        integration = result.scalar_one_or_none()

        if not integration or not integration.credenciais_enc:
            return None

        # Decrypt credentials
        decrypted = await self.crypto.decrypt(integration.credenciais_enc)
        if decrypted:
            import json

            return json.loads(decrypted)

        return None

    async def clear_credentials(self, marketplace_id: UUID, tenant_id: UUID) -> None:
        """Clear credentials from integration (destructive).

        Args:
            marketplace_id: Integration UUID
            tenant_id: Tenant UUID
        """
        stmt = select(MarketplaceIntegracao).where(
            and_(
                MarketplaceIntegracao.id == marketplace_id,
                MarketplaceIntegracao.tenant_id == tenant_id,
            )
        )
        result = await self.session.execute(stmt)
        integration = result.scalar_one_or_none()

        if integration:
            integration.credenciais_enc = None
            await self.session.commit()
