"""
Marketplace Schemas — Integrações com Marketplaces

Models:
    - MarketplaceIntegracaoCreate — criar integração
    - MarketplaceIntegracaoUpdate — atualizar
    - MarketplaceIntegracaoResponse — dados (sem credenciais)
    - MarketplaceCredentialUpdate — atualizar credenciais
"""

from pydantic import BaseModel, Field, JsonValue
from datetime import datetime
from uuid import UUID
from typing import Optional
from app.schemas.common import BaseResponse


# ═══════════════════════════════════════════════════════════════
# Marketplace Integration Create/Update
# ═══════════════════════════════════════════════════════════════

class MarketplaceIntegracaoBase(BaseModel):
    """Base para MarketplaceIntegracao."""
    tipo: str = Field(
        description="shopee, mercado_livre, amazon, magalu, americanas, aliexpress, shein"
    )
    nome: str = Field(min_length=1, max_length=100, description="Nome descritivo")


class MarketplaceIntegracaoCreate(MarketplaceIntegracaoBase):
    """Criar nova integração."""
    model_config = {"json_schema_extra": {
        "example": {
            "tipo": "shopee",
            "nome": "Loja Shopee Brasil"
        }
    }}


class MarketplaceIntegracaoUpdate(BaseModel):
    """Atualizar integração (sem credenciais)."""
    nome: Optional[str] = Field(default=None, max_length=100)
    ativo: Optional[bool] = Field(default=None)
    
    model_config = {"json_schema_extra": {
        "example": {
            "nome": "Loja Shopee - Novo nome",
            "ativo": True
        }
    }}


class MarketplaceIntegracaoResponse(BaseResponse):
    """Resposta com dados da integração (SEM credenciais)."""
    tenant_id: UUID
    tipo: str
    nome: str
    ativo: bool
    is_configured: bool = Field(
        description="True se credenciais foram configuradas"
    )
    
    model_config = {"from_attributes": True, "json_schema_extra": {
        "description": "⚠️ Nunca retorna credenciais_enc"
    }}


# ═══════════════════════════════════════════════════════════════
# Marketplace Credentials (Update only)
# ═══════════════════════════════════════════════════════════════

class ShopeeCredentials(BaseModel):
    """Credenciais Shopee."""
    shop_id: str = Field(description="Shop ID (numérico)")
    app_id: str = Field(description="App ID da aplicação")
    app_secret: str = Field(description="App Secret")
    access_token: Optional[str] = Field(default=None, description="Access token atual")


class MercadoLivreCredentials(BaseModel):
    """Credenciais Mercado Livre."""
    app_id: str
    app_secret: str
    access_token: str
    user_id: str = Field(description="User ID (numérico)")


class AmazonCredentials(BaseModel):
    """Credenciais Amazon."""
    aws_access_key: str
    aws_secret_key: str
    seller_id: str
    region: str = Field(default="us-east-1")


class AliExpressCredentials(BaseModel):
    """Credenciais AliExpress."""
    app_key: str
    app_secret: str
    api_gateway: str


class MarketplaceCredentialUpdate(BaseModel):
    """Atualizar credenciais de uma integração.
    
    ⚠️ Use a API específica para cada marketplace:
        - POST /marketplaces/{id}/credentials/shopee
        - POST /marketplaces/{id}/credentials/mercado_livre
        - etc
    """
    credentials: dict = Field(description="Credenciais específicas do marketplace")
    
    model_config = {"json_schema_extra": {
        "example": {
            "credentials": {
                "shop_id": "123456",
                "app_id": "app_id_here",
                "app_secret": "app_secret_here",
                "access_token": "token_here"
            }
        },
        "description": "⚠️ Credenciais sensíveis - enviar apenas via HTTPS"
    }}


class MarketplaceCredentialClear(BaseModel):
    """Limpar credenciais."""
    confirm: bool = Field(description="Confirmação (deve ser true)")
    
    model_config = {"json_schema_extra": {
        "example": {"confirm": True},
        "description": "⚠️ Esta ação não pode ser desfeita"
    }}


# ═══════════════════════════════════════════════════════════════
# Marketplace Connection Testing
# ═══════════════════════════════════════════════════════════════

class MarketplaceTestConnection(BaseModel):
    """Teste de conexão com marketplace."""
    success: bool
    message: str
    shop_name: Optional[str] = None
    verified_at: Optional[datetime] = None
    error_details: Optional[str] = None


class MarketplaceHealthCheck(BaseModel):
    """Status de saúde da integração."""
    integration_id: UUID
    tipo: str
    online: bool
    last_sync: Optional[datetime] = None
    last_error: Optional[str] = None
    last_error_at: Optional[datetime] = None


# ═══════════════════════════════════════════════════════════════
# Marketplace Statistics
# ═══════════════════════════════════════════════════════════════

class MarketplaceStats(BaseModel):
    """Estatísticas de uso da integração."""
    integration_id: UUID
    tipo: str
    total_msgs_sent: int = Field(description="Total de msgs encaminhadas")
    total_msg_failures: int
    success_rate: float
    msgs_today: int
    msgs_this_week: int
    msgs_this_month: int
    associated_rules: int = Field(description="Regras usando esta integração")
    associated_schedules: int = Field(description="Agendamentos usando esta integração")


# ═══════════════════════════════════════════════════════════════
# Marketplace Catalog (Products, Categories, etc)
# ═══════════════════════════════════════════════════════════════

class MarketplaceProduct(BaseModel):
    """Produto no marketplace."""
    product_id: str
    name: str
    price: float
    currency: str = "BRL"
    link: str
    image_url: Optional[str] = None


class MarketplaceCategorySync(BaseModel):
    """Sincronizar categorias do marketplace."""
    integration_id: UUID
    force_refresh: bool = Field(default=False)


class MarketplaceCategorySyncResponse(BaseModel):
    """Resposta de sincronização."""
    success: bool
    categories_synced: int
    timestamp: datetime


# ═══════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "MarketplaceIntegracaoCreate",
    "MarketplaceIntegracaoUpdate",
    "MarketplaceIntegracaoResponse",
    "ShopeeCredentials",
    "MercadoLivreCredentials",
    "AmazonCredentials",
    "AliExpressCredentials",
    "MarketplaceCredentialUpdate",
    "MarketplaceCredentialClear",
    "MarketplaceTestConnection",
    "MarketplaceHealthCheck",
    "MarketplaceStats",
    "MarketplaceProduct",
    "MarketplaceCategorySync",
    "MarketplaceCategorySyncResponse",
]
