"""Bot Service — Telegram Account Management.

Handles bot (Telegram USER/BOT account) CRUD.
Encrypts sensitive credentials (api_hash, bot_token, session_string).
"""

from datetime import datetime
from uuid import UUID
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bot import Bot
from app.schemas.bot import (
    BotCreate,
    BotUpdate,
    BotResponse,
    BotCredentialUpdateUser,
    BotCredentialUpdateBot,
)
from app.services.crypto_service import CryptoService


class BotService:
    """Manage Telegram bots/accounts."""

    def __init__(self, session: AsyncSession):
        """Initialize bot service.

        Args:
            session: Database session
        """
        self.session = session
        self.crypto = CryptoService(session)

    async def create(self, tenant_id: UUID, bot_in: BotCreate) -> BotResponse:
        """Create new bot.

        Args:
            tenant_id: Tenant UUID
            bot_in: Bot creation data

        Returns:
            Created bot response (without credentials)
        """
        # Encrypt sensitive fields if provided
        encrypted = {}
        if bot_in.api_hash:
            encrypted["api_hash_enc"] = await self.crypto.encrypt(bot_in.api_hash)
        if bot_in.session_string:
            encrypted["session_string_enc"] = await self.crypto.encrypt(
                bot_in.session_string
            )
        if bot_in.bot_token:
            encrypted["bot_token_enc"] = await self.crypto.encrypt(bot_in.bot_token)

        bot = Bot(
            tenant_id=tenant_id,
            nome=bot_in.nome,
            tipo=bot_in.tipo or "USER",
            api_id=bot_in.api_id,
            phone=bot_in.phone,
            ativo=True,
            **encrypted,
        )
        self.session.add(bot)
        await self.session.commit()
        await self.session.refresh(bot)

        return BotResponse.from_attributes(bot)

    async def get(self, bot_id: UUID, tenant_id: UUID) -> Optional[BotResponse]:
        """Get bot by ID.

        Args:
            bot_id: Bot UUID
            tenant_id: Tenant UUID (for isolation)

        Returns:
            Bot response or None
        """
        stmt = select(Bot).where(and_(Bot.id == bot_id, Bot.tenant_id == tenant_id))
        result = await self.session.execute(stmt)
        bot = result.scalar_one_or_none()

        return BotResponse.from_attributes(bot) if bot else None

    async def list_by_tenant(self, tenant_id: UUID) -> list[BotResponse]:
        """List all bots of tenant.

        Args:
            tenant_id: Tenant UUID

        Returns:
            List of bot responses
        """
        stmt = select(Bot).where(Bot.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        bots = result.scalars().all()

        return [BotResponse.from_attributes(b) for b in bots]

    async def update(
        self, bot_id: UUID, tenant_id: UUID, bot_in: BotUpdate
    ) -> Optional[BotResponse]:
        """Update bot metadata.

        Args:
            bot_id: Bot UUID
            tenant_id: Tenant UUID
            bot_in: Update data

        Returns:
            Updated bot response
        """
        stmt = select(Bot).where(and_(Bot.id == bot_id, Bot.tenant_id == tenant_id))
        result = await self.session.execute(stmt)
        bot = result.scalar_one_or_none()

        if not bot:
            return None

        if bot_in.nome:
            bot.nome = bot_in.nome
        if bot_in.ativo is not None:
            bot.ativo = bot_in.ativo

        await self.session.commit()
        await self.session.refresh(bot)

        return BotResponse.from_attributes(bot)

    async def delete(self, bot_id: UUID, tenant_id: UUID) -> None:
        """Soft delete bot.

        Args:
            bot_id: Bot UUID
            tenant_id: Tenant UUID
        """
        stmt = select(Bot).where(and_(Bot.id == bot_id, Bot.tenant_id == tenant_id))
        result = await self.session.execute(stmt)
        bot = result.scalar_one_or_none()

        if bot:
            bot.deletado_em = datetime.utcnow()
            await self.session.commit()

    # ===================== Credential Management =====================

    async def update_credentials_user(
        self, bot_id: UUID, tenant_id: UUID, cred_in: BotCredentialUpdateUser
    ) -> BotResponse:
        """Update USER-type bot credentials (api_hash, session_string).

        Args:
            bot_id: Bot UUID
            tenant_id: Tenant UUID
            cred_in: Credential update data

        Returns:
            Updated bot response
        """
        stmt = select(Bot).where(and_(Bot.id == bot_id, Bot.tenant_id == tenant_id))
        result = await self.session.execute(stmt)
        bot = result.scalar_one_or_none()

        if not bot:
            return None

        # Encrypt and update
        if cred_in.api_hash:
            bot.api_hash_enc = await self.crypto.encrypt(cred_in.api_hash)
        if cred_in.session_string:
            bot.session_string_enc = await self.crypto.encrypt(cred_in.session_string)

        await self.session.commit()
        await self.session.refresh(bot)

        return BotResponse.from_attributes(bot)

    async def update_credentials_bot(
        self, bot_id: UUID, tenant_id: UUID, cred_in: BotCredentialUpdateBot
    ) -> BotResponse:
        """Update BOT-type bot credentials (bot_token).

        Args:
            bot_id: Bot UUID
            tenant_id: Tenant UUID
            cred_in: Credential update data

        Returns:
            Updated bot response
        """
        stmt = select(Bot).where(and_(Bot.id == bot_id, Bot.tenant_id == tenant_id))
        result = await self.session.execute(stmt)
        bot = result.scalar_one_or_none()

        if not bot:
            return None

        # Encrypt and update
        if cred_in.bot_token:
            bot.bot_token_enc = await self.crypto.encrypt(cred_in.bot_token)

        await self.session.commit()
        await self.session.refresh(bot)

        return BotResponse.from_attributes(bot)

    async def clear_credentials(self, bot_id: UUID, tenant_id: UUID) -> BotResponse:
        """Clear all credentials from bot (destructive).

        Args:
            bot_id: Bot UUID
            tenant_id: Tenant UUID

        Returns:
            Bot response with cleared credentials
        """
        stmt = select(Bot).where(and_(Bot.id == bot_id, Bot.tenant_id == tenant_id))
        result = await self.session.execute(stmt)
        bot = result.scalar_one_or_none()

        if bot:
            bot.api_hash_enc = None
            bot.bot_token_enc = None
            bot.session_string_enc = None
            await self.session.commit()
            await self.session.refresh(bot)

        return BotResponse.from_attributes(bot)
