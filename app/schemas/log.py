"""
Log Schemas — Histórico de Execução e Auditoria

Models:
    - LogResponse — dados do log
    - LogFilter — filtros para buscar logs
"""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional
from app.schemas.common import BaseResponse


# ═══════════════════════════════════════════════════════════════
# Log Response
# ═══════════════════════════════════════════════════════════════

class LogExecucaoResponse(BaseResponse):
    """Dados de um log de execução."""
    tenant_id: UUID
    bot_id: UUID
    origem: str = Field(description="Canal de origem")
    destino: str = Field(description="Canal de destino")
    status: str = Field(description="sucesso, erro, aviso")
    mensagem: Optional[str] = None
    data_hora: datetime
    
    model_config = {"from_attributes": True, "json_schema_extra": {
        "example": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
            "bot_id": "550e8400-e29b-41d4-a716-446655440002",
            "origem": "@vendas",
            "destino": "@suporte",
            "status": "sucesso",
            "mensagem": "Message forwarded successfully",
            "data_hora": "2026-04-14T14:30:00Z",
            "criado_em": "2026-04-14T14:30:00Z",
            "atualizado_em": "2026-04-14T14:30:00Z",
            "deletado_em": None
        }
    }}


# ═══════════════════════════════════════════════════════════════
# Log Filters & Queries
# ═══════════════════════════════════════════════════════════════

class LogFilter(BaseModel):
    """Filtros para buscar logs."""
    bot_id: Optional[UUID] = None
    status: Optional[str] = Field(default=None, description="sucesso, erro, aviso")
    origem: Optional[str] = None
    destino: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = Field(default=None, max_length=255)
    
    model_config = {"json_schema_extra": {
        "example": {
            "bot_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "erro",
            "date_from": "2026-04-01T00:00:00Z",
            "date_to": "2026-04-14T23:59:59Z"
        }
    }}


# ═══════════════════════════════════════════════════════════════
# Log Statistics & Analytics
# ═══════════════════════════════════════════════════════════════

class LogStats(BaseModel):
    """Estatísticas agregadas de logs."""
    total_executions: int
    successful: int
    failed: int
    warnings: int
    success_rate: float = Field(description="Porcentagem 0-100")
    failure_rate: float
    warning_rate: float
    date_from: datetime
    date_to: datetime


class LogStatsByBot(BaseModel):
    """Estatísticas por bot."""
    bot_id: UUID
    bot_name: str
    total_executions: int
    successful: int
    failed: int
    success_rate: float
    last_execution: Optional[datetime] = None


class LogStatsByChannel(BaseModel):
    """Estatísticas por canal (origem/destino)."""
    channel: str
    direction: str = Field(description="'origem' ou 'destino'")
    total_executions: int
    successful: int
    failed: int
    success_rate: float


class LogStatsByStatus(BaseModel):
    """Contagem por status."""
    status: str
    count: int
    percentage: float


class LogStatsSummary(BaseModel):
    """Resumo de estatísticas."""
    date_range: str = Field(description="Data/período (ex: 'Últimas 24h')")
    total_msgs: int
    by_status: dict[str, int] = Field(description="{'sucesso': 100, 'erro': 5, 'aviso': 2}")
    success_rate: float
    top_errors: list[str] = Field(max_items=5)
    top_channels: list[dict] = Field(description="Canais mais usados")


# ═══════════════════════════════════════════════════════════════
# Log Export
# ═══════════════════════════════════════════════════════════════

class LogExportRequest(BaseModel):
    """Requisitar export de logs."""
    format: str = Field(description="csv, json, xlsx")
    date_from: datetime
    date_to: datetime
    bot_ids: Optional[list[UUID]] = None


class LogExportResponse(BaseModel):
    """Link para download de export."""
    success: bool
    download_url: str
    format: str
    expires_at: datetime
    file_size: int = Field(description="Bytes")


# ═══════════════════════════════════════════════════════════════
# Error Analysis
# ═══════════════════════════════════════════════════════════════

class ErrorAnalysis(BaseModel):
    """Análise de erros."""
    error_type: str = Field(description="Tipo de erro (ex: 'rate_limit', 'connection_timeout')")
    count: int
    first_occurrence: datetime
    last_occurrence: datetime
    affected_bots: int
    affected_channels: int


class ErrorTrend(BaseModel):
    """Tendência de erros ao longo do tempo."""
    date: datetime
    error_count: int
    warning_count: int
    success_count: int


# ═══════════════════════════════════════════════════════════════
# Audit Trail (for compliance)
# ═══════════════════════════════════════════════════════════════

class AuditLog(BaseModel):
    """Log de auditoria (actions de usuários)."""
    id: UUID
    user_id: UUID
    action: str = Field(description="create, update, delete, etc")
    resource_type: str = Field(description="bot, regra, agendamento, etc")
    resource_id: UUID
    changes: Optional[dict] = None
    ip_address: Optional[str] = None
    timestamp: datetime


# ═══════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "LogExecucaoResponse",
    "LogFilter",
    "LogStats",
    "LogStatsByBot",
    "LogStatsByChannel",
    "LogStatsByStatus",
    "LogStatsSummary",
    "LogExportRequest",
    "LogExportResponse",
    "ErrorAnalysis",
    "ErrorTrend",
    "AuditLog",
]
