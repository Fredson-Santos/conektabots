"""Shopee Marketplace Client Implementation.

Integrates with Shopee API for order and message handling.
"""

from typing import List, Dict, Any, Optional
import aiohttp
import json
from datetime import datetime

from worker.marketplace_clients.base import (
    BaseMarketplaceClient,
    MarketplaceMessage,
)


class ShopeeClient(BaseMarketplaceClient):
    """Shopee marketplace API client."""

    API_BASE = "https://partner.shopeemobile.com/api/v2"

    def __init__(self, credentials: Dict[str, Any]):
        """Initialize Shopee client.

        Args:
            credentials: Must contain 'access_token' and 'shop_id'
        """
        super().__init__(credentials)
        self.access_token = credentials.get("access_token")
        self.shop_id = credentials.get("shop_id")
        self.session: Optional[aiohttp.ClientSession] = None

    async def authenticate(self) -> bool:
        """Authenticate with Shopee API.

        Returns:
            True if credentials valid
        """
        if not self.access_token or not self.shop_id:
            return False

        # Test with a simple API call
        return await self.health_check()

    async def fetch_messages(
        self, shop_id: str, limit: int = 100
    ) -> List[MarketplaceMessage]:
        """Fetch messages from Shopee shop.

        Args:
            shop_id: Shopee shop ID
            limit: Max messages to fetch

        Returns:
            List of marketplace messages
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            # Shopee conversations API
            url = f"{self.API_BASE}/conversation/get_list"
            params = {
                "access_token": self.access_token,
                "shop_id": shop_id,
                "limit": limit,
            }

            async with self.session.get(url, params=params) as resp:
                if resp.status != 200:
                    return []

                data = await resp.json()
                conversations = data.get("data", {}).get("conversations", [])

                messages = []
                for conv in conversations:
                    for msg in conv.get("messages", []):
                        messages.append(
                            MarketplaceMessage(
                                id=msg.get("message_id"),
                                platform="shopee",
                                origem_id=shop_id,
                                sender_id=msg.get("from_id"),
                                sender_nome=msg.get("from_name", "Unknown"),
                                conteudo=msg.get("text", ""),
                                timestamp=msg.get("timestamp", 0),
                                metadata=msg,
                            )
                        )

                return messages
        except Exception as e:
            print(f"Shopee fetch_messages error: {e}")
            return []

    async def send_message(
        self, shop_id: str, recipient_id: str, message: str
    ) -> bool:
        """Send message on Shopee.

        Args:
            shop_id: Shop ID
            recipient_id: Recipient (user/buyer) ID
            message: Message text

        Returns:
            True if sent successfully
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            url = f"{self.API_BASE}/conversation/send_message"
            payload = {
                "access_token": self.access_token,
                "shop_id": shop_id,
                "to_id": recipient_id,
                "message": message,
            }

            async with self.session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("error", 0) == 0

            return False
        except Exception as e:
            print(f"Shopee send_message error: {e}")
            return False

    async def health_check(self) -> bool:
        """Check Shopee API connection.

        Returns:
            True if connected
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            url = f"{self.API_BASE}/shop/get_shop_info"
            params = {
                "access_token": self.access_token,
                "shop_id": self.shop_id,
            }

            async with self.session.get(url, params=params, timeout=5) as resp:
                return resp.status == 200

        except Exception:
            return False

    async def close(self) -> None:
        """Close session."""
        if self.session:
            await self.session.close()
