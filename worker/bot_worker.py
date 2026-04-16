"""Bot Worker — Main Worker Process.

Coordinates message fetching, processing, and sending.
Runs marketplace polling, rule evaluation, scheduling, and bot communication.
"""

import asyncio
import logging
from typing import Dict, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from telethon import TelegramClient
from telethon.sessions import StringSession

from app.core.config import settings
from app.models.bot import Bot
from app.models.marketplace import MarketplaceIntegracao
from app.models.regra import Regra
from app.models.agendamento import Agendamento
from worker.marketplace_clients.factory import MarketplaceClientFactory
from worker.message_processor import MessageProcessor
from worker.queue_manager import QueueManager
from worker.scheduler import Scheduler


logger = logging.getLogger(__name__)


class BotWorker:
    """Main worker process for ConektaBots."""

    def __init__(self):
        """Initialize worker."""
        self.engine = None
        self.session_maker = None
        self.clients: Dict[UUID, TelegramClient] = {}  # bot_id -> TelegramClient
        self.marketplace_clients = {}  # marketplace_id -> MarketplaceClient
        self.queue_manager = None
        self.scheduler = None
        self.processor = MessageProcessor()
        self.running = False

    async def initialize(self) -> None:
        """Initialize async database session and clients."""
        # Setup database
        database_url = settings.DATABASE_URL.replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        self.engine = create_async_engine(database_url, pool_size=10, max_overflow=0)
        self.session_maker = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

        logger.info("Worker initialized")

    async def start(self) -> None:
        """Start worker and all background tasks."""
        if self.running:
            logger.warning("Worker already running")
            return

        await self.initialize()
        self.running = True

        logger.info("Starting worker...")

        # Create session
        async with self.session_maker() as session:
            self.queue_manager = QueueManager(session)
            self.scheduler = Scheduler(session)

            # Start background tasks
            tasks = [
                asyncio.create_task(self.scheduler.start_scheduler()),
                asyncio.create_task(self._polling_loop(session)),
                asyncio.create_task(self._queue_processing_loop()),
            ]

            try:
                await asyncio.gather(*tasks)
            except asyncio.CancelledError:
                logger.info("Worker tasks cancelled")
            except Exception as e:
                logger.error(f"Worker error: {e}")
            finally:
                await self.stop()

    async def stop(self) -> None:
        """Stop worker and cleanup."""
        self.running = False
        await self.scheduler.stop_scheduler()

        # Close all clients
        for client in self.clients.values():
            try:
                await client.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting client: {e}")

        for client in self.marketplace_clients.values():
            try:
                await client.close()
            except Exception as e:
                logger.error(f"Error closing marketplace client: {e}")

        if self.engine:
            await self.engine.dispose()

        logger.info("Worker stopped")

    async def _polling_loop(self, session: AsyncSession) -> None:
        """Poll marketplaces for new messages."""
        while self.running:
            try:
                # Get all active bots and their integrations
                stmt = select(Bot).where(Bot.ativo == True)
                result = await session.execute(stmt)
                bots = result.scalars().all()

                for bot in bots:
                    # Get marketplace integrations for this bot
                    stmt = select(MarketplaceIntegracao).where(
                        MarketplaceIntegracao.tenant_id == bot.tenant_id,
                        MarketplaceIntegracao.ativo == True,
                    )
                    result = await session.execute(stmt)
                    integrations = result.scalars().all()

                    for integration in integrations:
                        # Fetch messages from marketplace
                        # TODO: Decrypt credentials and fetch
                        pass

                # Wait before next poll
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Polling loop error: {e}")
                await asyncio.sleep(30)

    async def _queue_processing_loop(self) -> None:
        """Process outgoing message queue."""
        while self.running:
            try:
                if self.queue_manager.get_queue_size() > 0:
                    sent = await self.queue_manager.process_queue(self.clients)
                    if sent > 0:
                        logger.info(f"Queue processor: sent {sent} messages")

                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Queue processing error: {e}")
                await asyncio.sleep(5)

    async def get_status(self) -> dict:
        """Get worker status.

        Returns:
            Status dict
        """
        return {
            "running": self.running,
            "telegram_clients": len(self.clients),
            "marketplace_clients": len(self.marketplace_clients),
            "queue_size": self.queue_manager.get_queue_size()
            if self.queue_manager
            else 0,
        }


# Singleton instance
_worker_instance: Optional[BotWorker] = None


async def get_worker() -> BotWorker:
    """Get or create worker instance.

    Returns:
        BotWorker instance
    """
    global _worker_instance
    if _worker_instance is None:
        _worker_instance = BotWorker()
    return _worker_instance
