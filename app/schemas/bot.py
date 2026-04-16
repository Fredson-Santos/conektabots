"""
Bot Schemas — Contas Telegram

Models:
    - BotCreate — criar novo bot
    - BotUpdate — atualizar bot
    - BotResponse — dados do bot (sem credenciais)
    - BotCredentialUpdate — atualizar credenciais
"""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional
from app.schemas.common import BaseResponse


# ═══════════════════════════════════════════════════════════════
# Bot Create/Update
# ═══════════════════════════════════════════════════════════════

class BotBase(BaseModel):
    """Base para Bot."""
    nome: str = Field(min_length=1, max_length=64, description="Nome do bot/conta")
    tipo: str = Field(description="'user' ou 'bot'")


class BotCreate(BotBase):
    """Criar novo bot."""
    api_id: Optional[int] = Field(default=None, description="API ID (para tipo=user)")
    phone: Optional[str] = Field(default=None, description="Telefone (para tipo=user)")
    
    model_config = {"json_schema_extra": {
        "example": {
            "nome": "Bot Principal",
            "tipo": "user",
            "api_id": 29234512,
            "phone": "+5531999999999"
        }
    }}


class BotUpdate(BaseModel):
    """Atualizar bot (sem credenciais)."""
    nome: Optional[str] = Field(default=None, max_length=64)
    ativo: Optional[bool] = Field(default=None)
    
    model_config = {"json_schema_extra": {
        "example": {
            "nome": "Bot Principal - v2",
            "ativo": True
        }
    }}


class BotResponse(BaseResponse):
    """Resposta com dados do bot (SEM credenciais)."""
    tenant_id: UUID
    nome: str
    tipo: str
    api_id: Optional[int] = None
    phone: Optional[str] = None
    ativo: bool
    is_configured: bool = Field(
        description="True se bot tem credenciais configuradas"
    )
    
    model_config = {"from_attributes": True, "json_schema_extra": {
        "description": "⚠️ Nunca retorna api_hash, bot_token, session_string"
    }}


# ═══════════════════════════════════════════════════════════════
# Bot Credentials (Update only, no response)
# ═══════════════════════════════════════════════════════════════

class BotCredentialUpdateUser(BaseModel):
    """Atualizar credenciais de bot tipo=user."""
    api_hash: str = Field(description="Hash da API (obtido em my.telegram.org)")
    session_string: str = Field(description="Session string (serializada pelo Telethon)")
    
    model_config = {"json_schema_extra": {
        "example": {
            "api_hash": "abc123def456...",
            "session_string": "AQAAAAAAAAAAAAAAAAA..."
        },
        "description": "⚠️ Credenciais sensíveis - enviar apenas via HTTPS"
    }}


class BotCredentialUpdateBot(BaseModel):
    """Atualizar credenciais de bot tipo=bot."""
    bot_token: str = Field(
        description="Token do bot (formato: 123456:ABC-DEF...)"
    )
    
    model_config = {"json_schema_extra": {
        "example": {
            "bot_token": "123456789:ABCdefGHIjklmnoPQRstuvWXYZ1234567"
        },
        "description": "⚠️ Credenciais sensíveis - enviar apenas via HTTPS"
    }}


class BotCredentialClear(BaseModel):
    """Limpar credenciais de um bot."""
    confirm: bool = Field(
        description="Confirmação (deve ser true para limpar)"
    )
    
    model_config = {"json_schema_extra": {
        "example": {"confirm": True},
        "description": "⚠️ Esta ação não pode ser desfeita"
    }}


# ═══════════════════════════════════════════════════════════════
# Bot Status & Health
# ═══════════════════════════════════════════════════════════════

class BotHealthCheck(BaseModel):
    """Status de saúde de um bot."""
    bot_id: UUID
    nome: str
    online: bool
    last_activity: Optional[datetime] = None
    error_message: Optional[str] = None
    last_error_at: Optional[datetime] = None


class BotTestConnection(BaseModel):
    """Teste de conexão com Telegram."""
    success: bool
    message: str
    phone_or_username: Optional[str] = None
    verified_at: Optional[datetime] = None


# ═══════════════════════════════════════════════════════════════
# Bot Statistics
# ═══════════════════════════════════════════════════════════════

class BotStats(BaseModel):
    """Estatísticas de uso do bot."""
    bot_id: UUID
    total_msgs_sent: int = Field(description="Total de mensagens enviadas")
    total_msg_failures: int = Field(description="Total de mensagens falhadas")
    success_rate: float = Field(description="Percentagem de sucesso (0-100)")
    msgs_today: int
    msgs_this_week: int
    msgs_this_month: int
    active_rules: int = Field(description="Regras ativas usando este bot")
    active_schedules: int = Field(description="Agendamentos ativos")
    
    model_config = {"json_schema_extra": {
        "example": {
            "bot_id": "550e8400-e29b-41d4-a716-446655440000",
            "total_msgs_sent": 5234,
            "total_msg_failures": 12,
            "success_rate": 99.77,
            "msgs_today": 234,
            "msgs_this_week": 1234,
            "msgs_this_month": 5234,
            "active_rules": 5,
            "active_schedules": 3
        }
    }}


# ═══════════════════════════════════════════════════════════════
# Bot List with Filters
# ═══════════════════════════════════════════════════════════════

class BotListItem(BaseModel):
    """Item em lista de bots."""
    id: UUID
    nome: str
    tipo: str
    ativo: bool
    is_configured: bool
    criado_em: datetime
    last_used: Optional[datetime] = None


# ═══════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "BotCreate",
    "BotUpdate",
    "BotResponse",
    "BotCredentialUpdateUser",
    "BotCredentialUpdateBot",
    "BotCredentialClear",
    "BotHealthCheck",
    "BotTestConnection",
    "BotStats",
    "BotListItem",
]
