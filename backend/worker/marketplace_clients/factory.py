"""Marketplace Client Factory.

Creates appropriate marketplace client based on integration type.
"""

from typing import Dict, Any
from worker.marketplace_clients.base import BaseMarketplaceClient
from worker.marketplace_clients.shopee import ShopeeClient


class MarketplaceClientFactory:
    """Factory for creating marketplace clients."""

    CLIENTS = {
        "shopee": ShopeeClient,
        # TODO: Add more clients
        # "mercado_livre": MercadoLivreClient,
        # "amazon": AmazonClient,
        # "magalu": MagaluClient,
    }

    @staticmethod
    def create_client(tipo: str, credentials: Dict[str, Any]) -> BaseMarketplaceClient:
        """Create marketplace client.

        Args:
            tipo: Integration type (shopee, mercado_livre, etc)
            credentials: API credentials

        Returns:
            Marketplace client instance

        Raises:
            ValueError if tipo not supported
        """
        client_class = MarketplaceClientFactory.CLIENTS.get(tipo)
        if not client_class:
            raise ValueError(f"Unknown marketplace type: {tipo}")

        return client_class(credentials)

    @staticmethod
    def get_supported_types() -> list[str]:
        """Get list of supported marketplace types.

        Returns:
            List of supported type strings
        """
        return list(MarketplaceClientFactory.CLIENTS.keys())
