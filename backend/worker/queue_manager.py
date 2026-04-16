"""Queue Manager — Message Distribution Queue.

Manages outgoing message queue and delivery.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from telethon import TelegramClient


logger = logging.getLogger(__name__)


@dataclass
class QueuedMessage:
    """Message in outgoing queue."""

    id: str
    tenant_id: UUID
    bot_id: UUID
    destino_chat_id: int
    mensagem: str
    criado_em: datetime
    tentativas: int = 0
    max_tentativas: int = 3


class QueueManager:
    """Manage message queue and delivery."""

    def __init__(self, session: AsyncSession):
        """Initialize queue manager.

        Args:
            session: Database session
        """
        self.session = session
        self.queue: list[QueuedMessage] = []
        self.processing = False

    async def add_to_queue(
        self,
        tenant_id: UUID,
        bot_id: UUID,
        destino_chat_id: int,
        mensagem: str,
    ) -> str:
        """Add message to outgoing queue.

        Args:
            tenant_id: Tenant UUID
            bot_id: Bot UUID
            destino_chat_id: Destination chat ID
            mensagem: Message text

        Returns:
            Queue item ID
        """
        import uuid

        item_id = str(uuid.uuid4())
        queued = QueuedMessage(
            id=item_id,
            tenant_id=tenant_id,
            bot_id=bot_id,
            destino_chat_id=destino_chat_id,
            mensagem=mensagem,
            criado_em=datetime.utcnow(),
        )

        self.queue.append(queued)
        logger.info(f"Queued message {item_id} for bot {bot_id} to {destino_chat_id}")

        return item_id

    async def process_queue(self, clients: Dict[UUID, TelegramClient]) -> int:
        """Process and send all queued messages.

        Args:
            clients: Dict of bot_id -> TelegramClient

        Returns:
            Number of messages sent successfully
        """
        if self.processing or not self.queue:
            return 0

        self.processing = True
        sent_count = 0

        try:
            while self.queue:
                item = self.queue.pop(0)

                # Get client
                client = clients.get(item.bot_id)
                if not client:
                    logger.warning(
                        f"No client for bot {item.bot_id}, requeueing message"
                    )
                    self.queue.append(item)
                    continue

                # Try to send
                try:
                    await client.send_message(
                        entity=item.destino_chat_id,
                        message=item.mensagem,
                    )
                    sent_count += 1
                    logger.info(
                        f"Sent message {item.id} to {item.destino_chat_id}"
                    )
                except Exception as e:
                    item.tentativas += 1
                    if item.tentativas < item.max_tentativas:
                        self.queue.append(item)  # Requeue
                        logger.warning(
                            f"Failed to send {item.id} (attempt {item.tentativas}): {e}"
                        )
                    else:
                        logger.error(f"Max retries exceeded for message {item.id}")

                # Rate limiting - don't spam
                await asyncio.sleep(0.5)

        finally:
            self.processing = False

        return sent_count

    def get_queue_size(self) -> int:
        """Get current queue size.

        Returns:
            Number of pending messages
        """
        return len(self.queue)

    async def clear_queue(self) -> None:
        """Clear entire queue (for maintenance).

        WARNING: Messages will be lost!
        """
        self.queue.clear()
        logger.warning("Queue cleared - pending messages lost!")
