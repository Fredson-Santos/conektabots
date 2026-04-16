"""Base Marketplace Client — Abstract Interface.

All marketplace integrations inherit from this base class.
Defines common interface for message fetching and sending.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class MarketplaceMessage:
    """Standard message format from any marketplace."""

    id: str
    platform: str  # shopee, mercado_livre, amazon, etc
    origem_id: str  # Shop ID or seller account ID
    sender_id: str
    sender_nome: str
    conteudo: str
    timestamp: int  # Unix timestamp
    metadata: Dict[str, Any]  # Platform-specific data


class BaseMarketplaceClient(ABC):
    """Abstract base for marketplace clients."""

    def __init__(self, credentials: Dict[str, Any]):
        """Initialize marketplace client.

        Args:
            credentials: Authentication credentials (varies by platform)
        """
        self.credentials = credentials

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with marketplace API.

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def fetch_messages(
        self, shop_id: str, limit: int = 100
    ) -> List[MarketplaceMessage]:
        """Fetch new messages from marketplace.

        Args:
            shop_id: Shop or seller ID on marketplace
            limit: Maximum messages to fetch

        Returns:
            List of marketplace messages
        """
        pass

    @abstractmethod
    async def send_message(
        self, shop_id: str, recipient_id: str, message: str
    ) -> bool:
        """Send message through marketplace.

        Args:
            shop_id: Source shop ID
            recipient_id: Recipient ID on marketplace
            message: Message text

        Returns:
            True if sent successfully
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check API connection health.

        Returns:
            True if connected and working
        """
        pass

    async def close(self) -> None:
        """Close any open connections.

        Override if needed for resource cleanup.
        """
        pass
