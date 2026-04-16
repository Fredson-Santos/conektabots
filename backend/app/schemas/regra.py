"""
Regra Schemas — Regras de Encaminhamento

Models:
    - RegraCreate/Update — criar/atualizar regra
    - RegraResponse — dados da regra
    - RegraOrigem/Destino/Filtro/Condicao — tabelas filhas
"""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional
from app.schemas.common import BaseResponse


# ═══════════════════════════════════════════════════════════════
# Regra Create/Update/Response
# ═══════════════════════════════════════════════════════════════

class RegraBase(BaseModel):
    """Base para Regra."""
    nome: str = Field(min_length=1, max_length=64, description="Nome da regra")
    bot_id: UUID
    marketplace_integracao_id: Optional[UUID] = None


class RegraCreate(RegraBase):
    """Criar nova regra."""
    substituto: Optional[str] = Field(default=None, max_length=255)
    filtro_midia: str = Field(
        default="todos",
        description="todos, foto, video, foto_video, documento, audio"
    )
    converter_link: bool = Field(default=False)
    
    # Nested lists para criar em uma requisição
    origens: list[str] = Field(default_factory=list, description="Canais de origem")
    destinos: list[str] = Field(default_factory=list, description="Canais de destino")
    filtros: Optional[list[dict]] = Field(default=None, description="[{tipo: 'incluir'|'bloquear', valor: 'palavra'}]")
    condicoes: Optional[list[str]] = Field(default=None, description="Condições obrigatórias")
    
    model_config = {"json_schema_extra": {
        "example": {
            "nome": "Reenviar para Suporte",
            "bot_id": "550e8400-e29b-41d4-a716-446655440000",
            "marketplace_integracao_id": None,
            "substituto": "[SUPORTE] ",
            "filtro_midia": "todos",
            "converter_link": False,
            "origens": ["@vendas", "@sales"],
            "destinos": ["@suporte"],
            "filtros": [
                {"tipo": "incluir", "valor": "problema"},
                {"tipo": "bloquear", "valor": "spam"}
            ],
            "condicoes": []
        }
    }}


class RegraUpdate(BaseModel):
    """Atualizar regra."""
    nome: Optional[str] = Field(default=None, max_length=64)
    substituto: Optional[str] = Field(default=None, max_length=255)
    filtro_midia: Optional[str] = Field(default=None)
    converter_link: Optional[bool] = Field(default=None)
    ativo: Optional[bool] = Field(default=None)


class RegraResponse(BaseResponse):
    """Resposta com dados da regra."""
    tenant_id: UUID
    bot_id: UUID
    marketplace_integracao_id: Optional[UUID] = None
    nome: str
    substituto: Optional[str] = None
    filtro_midia: str
    converter_link: bool
    ativo: bool
    
    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════
# Regra Child Models (Origem, Destino, Filtro, Condicao)
# ═══════════════════════════════════════════════════════════════

class RegraOrigemCreate(BaseModel):
    """Adicionar origem a uma regra."""
    origem: str = Field(max_length=255, description="Canal/grupo (@nome ou -ID)")


class RegraOrigemResponse(BaseResponse):
    """Dados de uma origem."""
    regra_id: UUID
    origem: str
    
    model_config = {"from_attributes": True}


class RegraDestinoCreate(BaseModel):
    """Adicionar destino a uma regra."""
    destino: str = Field(max_length=255)


class RegraDestinoResponse(BaseResponse):
    """Dados de um destino."""
    regra_id: UUID
    destino: str
    
    model_config = {"from_attributes": True}


class RegraFiltroCreate(BaseModel):
    """Adicionar filtro a uma regra."""
    tipo: str = Field(description="'incluir' ou 'bloquear'")
    valor: str = Field(max_length=255, description="Palavra-chave")


class RegraFiltroResponse(BaseResponse):
    """Dados de um filtro."""
    regra_id: UUID
    tipo: str
    valor: str
    
    model_config = {"from_attributes": True}


class RegraCondicaoCreate(BaseModel):
    """Adicionar condição a uma regra."""
    condicao: str = Field(max_length=255, description="Condição obrigatória")


class RegraCondicaoResponse(BaseResponse):
    """Dados de uma condição."""
    regra_id: UUID
    condicao: str
    
    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════
# Regra Full Response (com todos os children)
# ═══════════════════════════════════════════════════════════════

class RegraFullResponse(RegraResponse):
    """Resposta completa de uma regra (incluindo children)."""
    origens: list[RegraOrigemResponse] = Field(default_factory=list)
    destinos: list[RegraDestinoResponse] = Field(default_factory=list)
    filtros: list[RegraFiltroResponse] = Field(default_factory=list)
    condicoes: list[RegraCondicaoResponse] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════════
# Regra Statistics
# ═══════════════════════════════════════════════════════════════

class RegraStats(BaseModel):
    """Estatísticas de uma regra."""
    regra_id: UUID
    total_executions: int = Field(description="Total de vezes executada")
    successful: int = Field(description="Execuções bem-sucedidas")
    failed: int = Field(description="Execuções que falharam")
    success_rate: float
    last_execution: Optional[datetime] = None
    msgs_forwarded_today: int
    msgs_forwarded_this_week: int
    msgs_forwarded_this_month: int


# ═══════════════════════════════════════════════════════════════
# Regra Testing
# ═══════════════════════════════════════════════════════════════

class RegraTestExecution(BaseModel):
    """Testar execução de uma regra."""
    regra_id: UUID
    test_message: str = Field(max_length=500, description="Mensagem de teste")
    origem_channel: str = Field(description="Canal de origem simulado")


class RegraTestExecutionResponse(BaseModel):
    """Resultado do teste."""
    success: bool
    matched_rules: int = Field(description="Quantas regras foram acionadas")
    would_forward: bool = Field(description="Se a mensagem seria encaminhada")
    destinos: list[str] = Field(description="Para onde seria enviada")
    reasons: list[str] = Field(default_factory=list, description="Motivo se não foram encaminhadas")


# ═══════════════════════════════════════════════════════════════
# Regra Bulk Operations
# ═══════════════════════════════════════════════════════════════

class RegraBulkActivate(BaseModel):
    """Ativar múltiplas regras."""
    rule_ids: list[UUID]


class RegraBulkDeactivate(BaseModel):
    """Desativar múltiplas regras."""
    rule_ids: list[UUID]


class RegraBulkOperationResponse(BaseModel):
    """Resposta de operação em lote."""
    success: bool
    affected_count: int
    timestamp: datetime


# ═══════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "RegraCreate",
    "RegraUpdate",
    "RegraResponse",
    "RegraOrigemCreate",
    "RegraOrigemResponse",
    "RegraDestinoCreate",
    "RegraDestinoResponse",
    "RegraFiltroCreate",
    "RegraFiltroResponse",
    "RegraCondicaoCreate",
    "RegraCondicaoResponse",
    "RegraFullResponse",
    "RegraStats",
    "RegraTestExecution",
    "RegraTestExecutionResponse",
    "RegraBulkActivate",
    "RegraBulkDeactivate",
    "RegraBulkOperationResponse",
]
