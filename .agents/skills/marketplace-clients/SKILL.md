# SKILL: Marketplace Clients & Link Conversion

**Purpose**: Guidelines for implementing marketplace API clients, link conversion, credential management, and extensibility patterns.

**Used for**: Adding new marketplace integrations, implementing API clients, link/affiliate URL conversion, testing marketplace connections.

---

## Marketplace Client Architecture

### Base Interface (ABC)
```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class MarketplaceClient(ABC):
    """Abstract base class for marketplace API clients."""
    
    def __init__(self, credentials: Dict[str, str]):
        """
        Args:
            credentials: Dict with marketplace-specific keys
                (e.g., {"app_id": "...", "app_secret": "..."})
        """
        self.credentials = credentials
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if credentials are valid."""
        pass
    
    @abstractmethod
    async def convert_link(self, url: str, affiliate_id: str) -> str:
        """
        Convert regular URL to affiliate link.
        
        Args:
            url: Original product URL
            affiliate_id: Affiliate ID for commission tracking
        
        Returns:
            Affiliate URL
        """
        pass
    
    @abstractmethod
    async def get_product_info(self, url: str) -> Dict[str, Any]:
        """Fetch product metadata from marketplace API."""
        pass
```

### Factory Pattern
```python
from enum import Enum

class MarketplaceType(str, Enum):
    SHOPEE = "shopee"
    MERCADO_LIVRE = "mercado_livre"
    AMAZON = "amazon"
    MAGALU = "magalu"

class MarketplaceClientFactory:
    """Factory for creating marketplace clients."""
    
    _clients = {
        MarketplaceType.SHOPEE: "worker.marketplace_clients.shopee.ShopeeClient",
        MarketplaceType.MERCADO_LIVRE: "worker.marketplace_clients.mercado_livre.MercadoLivreClient",
        MarketplaceType.AMAZON: "worker.marketplace_clients.amazon.AmazonClient",
        MarketplaceType.MAGALU: "worker.marketplace_clients.magalu.MagaluClient",
    }
    
    @classmethod
    async def get_client(
        cls,
        marketplace_type: MarketplaceType,
        credentials: Dict[str, str]
    ) -> MarketplaceClient:
        """Dynamically load and instantiate client."""
        client_path = cls._clients.get(marketplace_type)
        
        if not client_path:
            raise ValueError(f"Unknown marketplace: {marketplace_type}")
        
        module_path, class_name = client_path.rsplit(".", 1)
        module = __import__(module_path, fromlist=[class_name])
        client_class = getattr(module, class_name)
        
        return client_class(credentials)
    
    @classmethod
    def register_client(
        cls,
        marketplace_type: MarketplaceType,
        client_path: str
    ):
        """Register new marketplace client dynamically."""
        cls._clients[marketplace_type] = client_path
```

---

## Example Implementation: Shopee

```python
import httpx
from typing import Dict, Any, Optional

class ShopeeClient(MarketplaceClient):
    """Shopee affiliate API integration."""
    
    BASE_URL = "https://api.k8.shopeepay.com"
    
    async def test_connection(self) -> bool:
        """Validate credentials with test request."""
        try:
            params = {
                "partner_id": self.credentials["partner_id"],
                "timestamp": int(datetime.utcnow().timestamp()),
            }
            params["sign"] = self._generate_signature(params)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/affiliate/api/v2/shop/get_shop_name",
                    params=params,
                    timeout=10
                )
            
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Shopee connection test failed: {e}")
            return False
    
    async def convert_link(self, url: str, affiliate_id: str) -> str:
        """Convert Shopee URL to affiliate link."""
        # Parse product ID from URL
        product_id = self._extract_product_id(url)
        
        if not product_id:
            return url  # Return original if parsing fails
        
        # Generate affiliate link with commission tracking
        affiliate_link = (
            f"https://shopee.com.br/product/"
            f"{product_id}"
            f"?d={affiliate_id}"  # Affiliate ID parameter
        )
        
        logger.info(f"Converted Shopee link: {url} → {affiliate_link}")
        return affiliate_link
    
    async def get_product_info(self, url: str) -> Dict[str, Any]:
        """Fetch product info from Shopee API."""
        try:
            product_id = self._extract_product_id(url)
            
            if not product_id:
                return {}
            
            # Call Shopee API
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/affiliate/api/v2/product/get_product",
                    params={"product_id": product_id},
                    timeout=10
                )
            
            data = response.json()
            
            return {
                "title": data.get("product_name"),
                "price": data.get("price"),
                "rating": data.get("rating_average"),
                "commission_rate": data.get("commission_rate", 0)
            }
        
        except Exception as e:
            logger.error(f"Failed to fetch Shopee product info: {e}")
            return {}
    
    def _generate_signature(self, params: Dict) -> str:
        """Generate HMAC-SHA256 signature for Shopee API."""
        import hmac
        import hashlib
        
        message = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        secret = self.credentials["secret"]
        
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _extract_product_id(self, url: str) -> Optional[str]:
        """Extract product ID from Shopee URL."""
        # Example: https://shopee.com.br/product/123456789/
        import re
        
        match = re.search(r'/(\d+)/?', url)
        return match.group(1) if match else None
```

---

## Service Integration

### Marketplace Service (High-Level)
```python
class MarketplaceService:
    async def create_integracao(
        self,
        tenant_id: UUID,
        marketplace_type: str,
        nome_exibicao: str,
        credenciais_dict: Dict[str, str]
    ) -> MarketplaceIntegracao:
        """Create new marketplace integration."""
        
        # Test credentials before saving
        try:
            client = await MarketplaceClientFactory.get_client(
                MarketplaceType(marketplace_type),
                credenciais_dict
            )
            
            if not await client.test_connection():
                raise ValueError("Credentials validation failed")
        
        except Exception as e:
            raise BadRequestError(f"Invalid credentials: {e}")
        
        # Encrypt credentials
        credenciais_enc = self.crypto_service.encrypt(
            json.dumps(credenciais_dict)
        )
        
        # Save to DB
        integracao = MarketplaceIntegracao(
            tenant_id=tenant_id,
            tipo=marketplace_type,
            nome_exibicao=nome_exibicao,
            credenciais_enc=credenciais_enc,
            ativo=True
        )
        
        await db.add(integracao)
        await db.commit()
        
        return integracao
    
    async def convert_link(
        self,
        integracao_id: UUID,
        url: str,
        affiliate_id: str
    ) -> str:
        """Convert URL using marketplace integration."""
        
        # Fetch integration
        integracao = await db.query(MarketplaceIntegracao).filter(
            MarketplaceIntegracao.id == integracao_id
        ).first()
        
        if not integracao:
            raise NotFoundError("Marketplace integration not found")
        
        # Decrypt credentials
        credenciais_dict = json.loads(
            self.crypto_service.decrypt(integracao.credenciais_enc)
        )
        
        # Get marketplace client
        client = await MarketplaceClientFactory.get_client(
            MarketplaceType(integracao.tipo),
            credenciais_dict
        )
        
        # Convert link
        affiliate_link = await client.convert_link(url, affiliate_id)
        
        return affiliate_link
```

---

## Testing Marketplace Clients

```python
import pytest

@pytest.mark.asyncio
async def test_shopee_convert_link():
    """Test Shopee link conversion."""
    credentials = {
        "partner_id": "test_partner",
        "secret": "test_secret"
    }
    
    client = ShopeeClient(credentials)
    
    # Mock HTTP response (use pytest-httpx or responses)
    url = "https://shopee.com.br/product/123456789/"
    affiliate_link = await client.convert_link(url, "affiliate_123")
    
    assert "d=affiliate_123" in affiliate_link
    assert "product" in affiliate_link

@pytest.mark.asyncio
async def test_shopee_test_connection():
    """Test Shopee connection validation."""
    credentials = {"partner_id": "...", "secret": "..."}
    client = ShopeeClient(credentials)
    
    # Mock HTTP for success
    is_valid = await client.test_connection()
    assert is_valid == True
```

---

## Adding New Marketplace

### Checklist
1. [ ] Create `worker/marketplace_clients/new_market.py`
2. [ ] Implement `NewMarketClient(MarketplaceClient)` class
   - [ ] `test_connection()`
   - [ ] `convert_link(url, affiliate_id)`
   - [ ] `get_product_info(url)`
3. [ ] Register in `MarketplaceClientFactory._clients`
4. [ ] Add enum value `MarketplaceType.NEW_MARKET`
5. [ ] Write tests in `tests/test_marketplace_clients.py`
6. [ ] Update documentation (`docs/MARKETPLACES.md`)
7. [ ] Test end-to-end in staging

### Template for New Marketplace
```python
from worker.marketplace_clients.base import MarketplaceClient

class NewMarketClient(MarketplaceClient):
    """New marketplace integration."""
    
    BASE_URL = "https://api.newmarket.com"
    
    async def test_connection(self) -> bool:
        try:
            # TODO: Implement connection test
            return True
        except Exception:
            return False
    
    async def convert_link(self, url: str, affiliate_id: str) -> str:
        # TODO: Implement link conversion logic
        return url
    
    async def get_product_info(self, url: str) -> Dict[str, Any]:
        # TODO: Fetch product metadata
        return {}
```

---

## Affiliate Link Formatting

### Standard Parameters per Marketplace
| Marketplace | Parameter | Example |
|---|---|---|
| Shopee | `d` | `https://shopee.com.br/product/123?d=aff_123` |
| ML | `utm_source` | `https://produto.mercadolivre.com.br?utm_source=aff_123` |
| Amazon | `tag` | `https://amazon.com.br/dp/ASIN?tag=aff_123` |
| Magalu | `ref` | `https://www.magazineluiza.com.br?ref=aff_123` |

---

## Error Handling

```python
class MarketplaceError(Exception):
    """Base exception for marketplace operations."""
    pass

class InvalidCredentialsError(MarketplaceError):
    """Credentials are invalid or expired."""
    pass

class LinkConversionError(MarketplaceError):
    """Failed to convert URL to affiliate link."""
    pass

class RateLimitError(MarketplaceError):
    """Marketplace API rate limit exceeded."""
    pass
```

---

## Common Mistakes ⚠️

❌ **Mistake 1**: Hard-coded credentials
```python
# BAD
class ShopeeClient:
    PARTNER_ID = "hardcoded_partner_id"

# GOOD
class ShopeeClient:
    def __init__(self, credentials: Dict[str, str]):
        self.partner_id = credentials["partner_id"]
```

❌ **Mistake 2**: No error handling for API calls
```python
# BAD
response = await client.get(url)
return response.json()

# GOOD
try:
    response = await client.get(url, timeout=10)
    return response.json()
except httpx.TimeoutException:
    raise MarketplaceError("API timeout")
except Exception as e:
    logger.error(f"API error: {e}")
    raise
```

❌ **Mistake 3**: Storing plaintext credentials
```python
# BAD
integracao.credenciais = json.dumps(creds)  # Plaintext!

# GOOD
integracao.credenciais_enc = crypto.encrypt(json.dumps(creds))
```

---

## Resources
- [List of Marketplace APIs](https://github.com/awesome-lists/awesome-affiliate-links)
- [httpx Documentation](https://www.python-httpx.org/)
- [Secure API Key Storage](https://owasp.org/www-community/Sensitive_Data_Exposure)

---

**Last Updated**: April 15, 2026  
**Status**: Active
