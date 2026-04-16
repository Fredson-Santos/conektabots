"""
Uso Schemas — Controle de Uso e Rate Limiting

Models:
    - UsoResponse — dados de uso mensal
    - UsoStats — estatísticas de consumo
"""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional
from app.schemas.common import BaseResponse


# ═══════════════════════════════════════════════════════════════
# Uso Mensal Response
# ═══════════════════════════════════════════════════════════════

class UsoMensalResponse(BaseResponse):
    """Dados de uso de um mês."""
    tenant_id: UUID
    ano_mes: str = Field(description="YYYYMM (ex: '202604')")
    msgs_enviadas: int = Field(description="Mensagens bem-sucedidas")
    msgs_failed: int = Field(description="Mensagens falhadas")
    total_msgs: int = Field(description="Total (enviadas + falhadas)")
    success_rate: float = Field(description="Porcentagem 0-100")
    
    model_config = {"from_attributes": True, "json_schema_extra": {
        "example": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
            "ano_mes": "202604",
            "msgs_enviadas": 12345,
            "msgs_failed": 50,
            "total_msgs": 12395,
            "success_rate": 99.60,
            "criado_em": "2026-04-01T00:00:00Z",
            "atualizado_em": "2026-04-14T23:59:59Z",
            "deletado_em": None
        }
    }}


# ═══════════════════════════════════════════════════════════════
# Usage Stats & Limits
# ═══════════════════════════════════════════════════════════════

class UsoStats(BaseModel):
    """Estatísticas de uso do tenant."""
    tenant_id: UUID
    current_month: str = Field(description="YYYYMM")
    msgs_this_month: int
    msgs_limit_this_month: Optional[int] = Field(default=None, description="Limite (None = ilimitado)")
    usage_percentage: float = Field(
        description="Porcentagem de uso do limite (0-100, None se ilimitado)"
    )
    msgs_today: int
    msgs_last_hour: int
    rate_limit: int = Field(description="Msgs/hora permitido")
    rate_limit_exceeded: bool


class UsoQuota(BaseModel):
    """Informações de quota do tenant."""
    plano: str
    total_limit_msgs_month: Optional[int] = None
    total_limit_msgs_hour: int
    current_usage_this_month: int
    current_usage_this_hour: int
    remaining_this_month: Optional[int] = None
    blocks_remaining_month: bool = Field(
        description="Se atingiu limite do mês"
    )
    blocks_this_hour: bool = Field(
        description="Se vai ultrapassar limite/hora agora"
    )
    reset_at: Optional[datetime] = Field(
        default=None,
        description="Quando o rate_limit reinicia (próxima hora ou próximo mês)"
    )


# ═══════════════════════════════════════════════════════════════
# Usage History
# ═══════════════════════════════════════════════════════════════

class UsoHistorico(BaseModel):
    """Um mês de histórico de uso."""
    ano_mes: str
    msgs_enviadas: int
    msgs_failed: int
    success_rate: float


class UsoHistoricoResponse(BaseModel):
    """Histórico dos últimos N meses."""
    tenant_id: UUID
    historico: list[UsoHistorico] = Field(
        description="Últimos 12 meses de uso"
    )
    total_this_year: int
    average_per_month: float


# ═══════════════════════════════════════════════════════════════
# Usage Breakdown
# ═══════════════════════════════════════════════════════════════

class UsoByBot(BaseModel):
    """Uso por bot."""
    bot_id: UUID
    bot_name: str
    msgs_sent: int
    msgs_failed: int
    percentage_of_total: float


class UsoByChannel(BaseModel):
    """Uso por canal."""
    channel: str
    msgs_sent: int
    percentage_of_total: float


class UsoBreakdown(BaseModel):
    """Detalhamento de uso."""
    month: str
    total_msgs: int
    by_bot: list[UsoByBot]
    by_channel: list[UsoByChannel]
    top_users: list[dict] = Field(
        description="Usuários que mais causaram uso"
    )


# ═══════════════════════════════════════════════════════════════
# Rate Limiting
# ═══════════════════════════════════════════════════════════════

class RateLimitStatus(BaseModel):
    """Status de rate limit."""
    tenant_id: UUID
    msgs_per_hour_limit: int
    current_hour_usage: int
    requests_remaining: int
    reset_at: datetime


class RateLimitWarning(BaseModel):
    """Aviso de rate limit próximo."""
    threshold_percentage: int = Field(
        description="Porcentagem do limite (ex: 80)"
    )
    current_percentage: float
    will_be_blocked: bool
    requests_before_block: Optional[int] = None


# ═══════════════════════════════════════════════════════════════
# Plan Upgrade/Downgrade
# ═══════════════════════════════════════════════════════════════

class PlanUpgrade(BaseModel):
    """Informações de upgrade de plano."""
    current_plan: str
    new_plan: str
    current_usage: int
    new_limit_msgs_month: Optional[int] = None
    new_limit_msgs_hour: int
    monthly_cost: float
    upgrade_fee: Optional[float] = None
    effective_date: datetime


class PlanUpgradePreview(BaseModel):
    """Preview antes de fazer upgrade."""
    plan_name: str
    description: str
    price: float
    features: list[str]
    limite_bots: int
    limite_regras: int
    limite_agendamentos: int
    limite_msgs_hora: int


# ═══════════════════════════════════════════════════════════════
# Overage & Billing
# ═══════════════════════════════════════════════════════════════

class OverageCharge(BaseModel):
    """Cobrança por uso excedente."""
    month: str
    plan: str
    base_cost: float
    msgs_over_limit: int
    overage_cost: float
    total_cost: float


class OverageHistory(BaseModel):
    """Histórico de cobranças por overage."""
    tenant_id: UUID
    overages: list[OverageCharge]
    total_overage_charges: float


# ═══════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "UsoMensalResponse",
    "UsoStats",
    "UsoQuota",
    "UsoHistorico",
    "UsoHistoricoResponse",
    "UsoByBot",
    "UsoByChannel",
    "UsoBreakdown",
    "RateLimitStatus",
    "RateLimitWarning",
    "PlanUpgrade",
    "PlanUpgradePreview",
    "OverageCharge",
    "OverageHistory",
]
