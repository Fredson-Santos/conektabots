"""
Tenant Schemas — Organizações e Membros

Models:
    - TenantCreate — criar novo tenant
    - TenantUpdate — atualizar tenant
    - TenantResponse — dados do tenant
    - TenantMemberAdd — adicionar membro
    - TenantMemberResponse — dados do membro
"""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional
from app.schemas.common import BaseResponse


# ═══════════════════════════════════════════════════════════════
# Tenant Create/Update/Response
# ═══════════════════════════════════════════════════════════════

class TenantBase(BaseModel):
    """Base model para Tenant."""
    nome: str = Field(min_length=1, max_length=100, description="Nome da organização")
    slug: str = Field(
        min_length=1,
        max_length=100,
        description="URL-safe identifier (ex: minha-empresa)"
    )


class TenantCreate(TenantBase):
    """Criar novo tenant."""
    plano: str = Field(default="free", description="free, starter, pro, enterprise")
    
    model_config = {"json_schema_extra": {
        "example": {
            "nome": "Minha Empresa LTDA",
            "slug": "minha-empresa",
            "plano": "free"
        }
    }}


class TenantUpdate(BaseModel):
    """Atualizar tenant (apenas fields editáveis)."""
    nome: Optional[str] = Field(default=None, max_length=100)
    
    model_config = {"json_schema_extra": {
        "example": {
            "nome": "Minha Empresa - Novo nome"
        }
    }}


class TenantUpgradePlan(BaseModel):
    """Upgrade de plano."""
    new_plan: str = Field(description="free, starter, pro, enterprise")
    
    model_config = {"json_schema_extra": {
        "example": {"new_plan": "pro"}
    }}


class TenantResponse(BaseResponse):
    """Resposta com dados do tenant."""
    nome: str
    slug: str
    plano: str
    ativo: bool
    limite_bots: int
    limite_regras: int
    limite_agendamentos: int
    limite_msgs_hora: int
    
    model_config = {"from_attributes": True}


class TenantLimitsResponse(BaseModel):
    """Limites e uso atual do tenant."""
    limite_bots: int
    bots_usados: int
    limite_regras: int
    regras_usadas: int
    limite_agendamentos: int
    agendamentos_usados: int
    limite_msgs_hora: int
    msgs_ultima_hora: int
    
    model_config = {"json_schema_extra": {
        "example": {
            "limite_bots": 20,
            "bots_usados": 5,
            "limite_regras": 50,
            "regras_usadas": 12,
            "limite_agendamentos": 30,
            "agendamentos_usados": 8,
            "limite_msgs_hora": 1000,
            "msgs_ultima_hora": 234
        }
    }}


# ═══════════════════════════════════════════════════════════════
# Tenant Member (RBAC)
# ═══════════════════════════════════════════════════════════════

class TenantMemberBase(BaseModel):
    """Base model para TenantMember."""
    role: str = Field(description="owner, admin, editor, viewer")


class TenantMemberAdd(TenantMemberBase):
    """Adicionar membro ao tenant."""
    email: str = Field(description="Email do usuário (deve existir)")
    
    model_config = {"json_schema_extra": {
        "example": {
            "email": "collaborator@example.com",
            "role": "editor"
        }
    }}


class TenantMemberUpdate(BaseModel):
    """Atualizar role de um membro."""
    role: str = Field(description="owner, admin, editor, viewer")
    
    model_config = {"json_schema_extra": {
        "example": {"role": "admin"}
    }}


class TenantMemberResponse(BaseResponse):
    """Dados de um membro no tenant."""
    user_id: UUID
    role: str
    user_email: Optional[str] = Field(default=None, description="Email do usuário (nested)")
    user_name: Optional[str] = Field(default=None, description="Nome completo do usuário")
    
    model_config = {"from_attributes": True}


class TenantMemberListResponse(BaseModel):
    """Listar membros do tenant."""
    id: UUID
    user_id: UUID
    email: str
    name: str
    role: str
    criado_em: datetime
    ativo: bool


# ═══════════════════════════════════════════════════════════════
# Tenant Settings
# ═══════════════════════════════════════════════════════════════

class TenantSettingsResponse(BaseModel):
    """Configurações do tenant."""
    plano: str
    ativo: bool
    limite_bots: int
    limite_regras: int
    limite_agendamentos: int
    limite_msgs_hora: int
    rate_limit_enabled: bool
    notifications_enabled: bool
    webhook_url: Optional[str] = None


class TenantNotificationSettings(BaseModel):
    """Configurações de notificação."""
    email_on_error: bool = Field(default=True)
    email_on_milestone: bool = Field(default=True)
    email_on_limit: bool = Field(default=True)
    discord_webhook: Optional[str] = Field(default=None)
    slack_webhook: Optional[str] = Field(default=None)


# ═══════════════════════════════════════════════════════════════
# Tenant Billing (future)
# ═══════════════════════════════════════════════════════════════

class TenantBillingInfo(BaseModel):
    """Informações de billing."""
    plan: str
    monthly_cost: float
    usage_msgs: int
    overage_msgs: int
    overage_cost: float
    next_billing_date: datetime


# ═══════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "TenantCreate",
    "TenantUpdate",
    "TenantUpgradePlan",
    "TenantResponse",
    "TenantLimitsResponse",
    "TenantMemberAdd",
    "TenantMemberUpdate",
    "TenantMemberResponse",
    "TenantMemberListResponse",
    "TenantSettingsResponse",
    "TenantNotificationSettings",
    "TenantBillingInfo",
]
