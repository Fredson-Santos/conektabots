"""Bots Router — Telegram Account Management.

POST /api/v1/bots — Create bot
GET /api/v1/bots — List bots
GET /api/v1/bots/{bot_id} — Get bot
PATCH /api/v1/bots/{bot_id} — Update bot
DELETE /api/v1/bots/{bot_id} — Delete bot
POST /api/v1/bots/{bot_id}/credentials/user — Update USER credentials
POST /api/v1/bots/{bot_id}/credentials/bot — Update BOT credentials
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_tenant
from app.schemas.bot import (
    BotCreate,
    BotUpdate,
    BotResponse,
    BotCredentialUpdateUser,
    BotCredentialUpdateBot,
)
from app.services.bot_service import BotService


router = APIRouter(prefix="/api/v1/bots", tags=["bots"])


@router.post("/", response_model=BotResponse, status_code=status.HTTP_201_CREATED)
async def create_bot(
    bot_in: BotCreate,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Create new Telegram bot/account.

    Args:
        bot_in: Bot creation data
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Created bot response (without credentials)
    """
    service = BotService(session)
    return await service.create(tenant_id, bot_in)


@router.get("/", response_model=list[BotResponse])
async def list_bots(
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """List all bots of current tenant.

    Args:
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        List of bot responses
    """
    service = BotService(session)
    return await service.list_by_tenant(tenant_id)


@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot(
    bot_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Get specific bot.

    Args:
        bot_id: Bot UUID
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Bot response or 404
    """
    service = BotService(session)
    bot = await service.get(bot_id, tenant_id)

    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot não encontrado",
        )

    return bot


@router.patch("/{bot_id}", response_model=BotResponse)
async def update_bot(
    bot_id: UUID,
    bot_in: BotUpdate,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Update bot metadata (nome, ativo).

    Args:
        bot_id: Bot UUID
        bot_in: Update data
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Updated bot response
    """
    service = BotService(session)
    bot = await service.update(bot_id, tenant_id, bot_in)

    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot não encontrado",
        )

    return bot


@router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bot(
    bot_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Delete (soft delete) bot.

    Args:
        bot_id: Bot UUID
        tenant_id: Injected current tenant
        session: Database session
    """
    service = BotService(session)
    await service.delete(bot_id, tenant_id)


# ===================== Credentials =====================


@router.post(
    "/{bot_id}/credentials/user", response_model=BotResponse
)
async def update_credentials_user(
    bot_id: UUID,
    cred_in: BotCredentialUpdateUser,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Update USER-type bot credentials (api_hash, session_string).

    Args:
        bot_id: Bot UUID
        cred_in: Credential data
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Updated bot response
    """
    service = BotService(session)
    bot = await service.update_credentials_user(bot_id, tenant_id, cred_in)

    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot não encontrado",
        )

    return bot


@router.post(
    "/{bot_id}/credentials/bot", response_model=BotResponse
)
async def update_credentials_bot(
    bot_id: UUID,
    cred_in: BotCredentialUpdateBot,
    tenant_id: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Update BOT-type bot credentials (bot_token).

    Args:
        bot_id: Bot UUID
        cred_in: Credential data
        tenant_id: Injected current tenant
        session: Database session

    Returns:
        Updated bot response
    """
    service = BotService(session)
    bot = await service.update_credentials_bot(bot_id, tenant_id, cred_in)

    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot não encontrado",
        )

    return bot

