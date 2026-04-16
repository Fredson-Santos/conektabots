"""Marketplace Clients — Integration Implementations.

Shopee, Mercado Livre, Amazon, and other marketplace integrations.
"""

from worker.marketplace_clients.base import BaseMarketplaceClient, MarketplaceMessage
from worker.marketplace_clients.shopee import ShopeeClient
from worker.marketplace_clients.factory import MarketplaceClientFactory

__all__ = [
    "BaseMarketplaceClient",
    "MarketplaceMessage",
    "ShopeeClient",
    "MarketplaceClientFactory",
]
