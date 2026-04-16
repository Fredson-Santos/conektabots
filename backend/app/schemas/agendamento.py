"""
Agendamento Schemas — Envios Automáticos Agendados

Models:
    - AgendamentoCreate/Update — criar/atualizar agendamento
    - AgendamentoResponse — dados do agendamento
    - AgendamentoHorario — horários de envio
"""

from pydantic import BaseModel, Field
from datetime import datetime, time
from uuid import UUID
from typing import Optional
from app.schemas.common import BaseResponse


# ═══════════════════════════════════════════════════════════════
# Agendamento Create/Update/Response
# ═══════════════════════════════════════════════════════════════

class AgendamentoBase(BaseModel):
    """Base para Agendamento."""
    nome: str = Field(min_length=1, max_length=64)
    bot_id: UUID
    marketplace_integracao_id: Optional[UUID] = None


class AgendamentoCreate(AgendamentoBase):
    """Criar novo agendamento."""
    msg_id_atual: int = Field(default=0, description="Índice na sequência")
    tipo_envio: str = Field(default="sequencial", description="sequencial ou aleatorio")
    substituto: Optional[str] = Field(default=None, max_length=255)
    filtro_midia: str = Field(default="todos")
    
    # Nested lists
    origens: list[str] = Field(default_factory=list)
    destinos: list[str] = Field(default_factory=list)
    horarios: list[str] = Field(
        default_factory=list,
        description="Lista de horários HH:MM (ex: ['12:30', '19:45'])"
    )
    filtros: Optional[list[dict]] = Field(default=None)
    condicoes: Optional[list[str]] = Field(default=None)
    
    model_config = {"json_schema_extra": {
        "example": {
            "nome": "Promotions Matinais",
            "bot_id": "550e8400-e29b-41d4-a716-446655440000",
            "tipo_envio": "sequencial",
            "substituto": "[PROMO] ",
            "filtro_midia": "todos",
            "origens": ["@produtos"],
            "destinos": ["@vendas"],
            "horarios": ["08:00", "12:00", "18:00"],
            "filtros": [],
            "condicoes": []
        }
    }}


class AgendamentoUpdate(BaseModel):
    """Atualizar agendamento."""
    nome: Optional[str] = Field(default=None, max_length=64)
    tipo_envio: Optional[str] = Field(default=None)
    substituto: Optional[str] = Field(default=None, max_length=255)
    filtro_midia: Optional[str] = Field(default=None)
    ativo: Optional[bool] = Field(default=None)


class AgendamentoResponse(BaseResponse):
    """Resposta com dados do agendamento."""
    tenant_id: UUID
    bot_id: UUID
    marketplace_integracao_id: Optional[UUID] = None
    nome: str
    msg_id_atual: int
    tipo_envio: str
    substituto: Optional[str] = None
    filtro_midia: str
    ativo: bool
    
    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════
# Agendamento Child Models (Origem, Destino, Horario, etc)
# ═══════════════════════════════════════════════════════════════

class AgendamentoOrigemCreate(BaseModel):
    """Adicionar origem."""
    origem: str = Field(max_length=255)


class AgendamentoOrigemResponse(BaseResponse):
    """Dados de uma origem."""
    agendamento_id: UUID
    origem: str
    
    model_config = {"from_attributes": True}


class AgendamentoDestinoCreate(BaseModel):
    """Adicionar destino."""
    destino: str = Field(max_length=255)


class AgendamentoDestinoResponse(BaseResponse):
    """Dados de um destino."""
    agendamento_id: UUID
    destino: str
    
    model_config = {"from_attributes": True}


class AgendamentoHorarioCreate(BaseModel):
    """Adicionar horário de envio."""
    horario: str = Field(
        description="Horário em formato HH:MM (ex: 14:30)",
        pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$"
    )


class AgendamentoHorarioResponse(BaseResponse):
    """Dados de um horário."""
    agendamento_id: UUID
    horario: time
    
    model_config = {"from_attributes": True}


class AgendamentoFiltroCreate(BaseModel):
    """Adicionar filtro."""
    tipo: str = Field(description="'incluir' ou 'bloquear'")
    valor: str = Field(max_length=255)


class AgendamentoFiltroResponse(BaseResponse):
    """Dados de um filtro."""
    agendamento_id: UUID
    tipo: str
    valor: str
    
    model_config = {"from_attributes": True}


class AgendamentoCondicaoCreate(BaseModel):
    """Adicionar condição."""
    condicao: str = Field(max_length=255)


class AgendamentoCondicaoResponse(BaseResponse):
    """Dados de uma condição."""
    agendamento_id: UUID
    condicao: str
    
    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════
# Agendamento Full Response
# ═══════════════════════════════════════════════════════════════

class AgendamentoFullResponse(AgendamentoResponse):
    """Resposta completa (com children)."""
    origens: list[AgendamentoOrigemResponse] = Field(default_factory=list)
    destinos: list[AgendamentoDestinoResponse] = Field(default_factory=list)
    horarios: list[AgendamentoHorarioResponse] = Field(default_factory=list)
    filtros: list[AgendamentoFiltroResponse] = Field(default_factory=list)
    condicoes: list[AgendamentoCondicaoResponse] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════════
# Agendamento Statistics
# ═══════════════════════════════════════════════════════════════

class AgendamentoStats(BaseModel):
    """Estatísticas de um agendamento."""
    agendamento_id: UUID
    total_executions: int = Field(description="Vezes executado")
    successful: int
    failed: int
    success_rate: float
    next_execution: Optional[datetime] = None
    last_execution: Optional[datetime] = None
    msgs_sent_today: int
    msgs_sent_this_week: int
    msgs_sent_this_month: int


# ═══════════════════════════════════════════════════════════════
# Agendamento Testing
# ═══════════════════════════════════════════════════════════════

class AgendamentoTestExecution(BaseModel):
    """Testar execução de agendamento."""
    agendamento_id: UUID
    test_message: str = Field(max_length=500)
    origem_channel: str


class AgendamentoTestExecutionResponse(BaseModel):
    """Resultado do teste."""
    success: bool
    matched_agendamentos: int
    would_send: bool
    destinos: list[str]
    reasons: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════════
# Agendamento Execution Control
# ═══════════════════════════════════════════════════════════════

class AgendamentoNextExecution(BaseModel):
    """Próxima execução programada."""
    agendamento_id: UUID
    nome: str
    next_execution_time: datetime
    horarios_today: list[time] = Field(description="Horários restantes hoje")
    frequency: str


class AgendamentoResetSequence(BaseModel):
    """Resetar sequência (msg_id_atual = 0)."""
    agendamento_id: UUID
    confirm: bool = Field(description="Confirmação")


class AgendamentoResetSequenceResponse(BaseModel):
    """Resposta de reset."""
    success: bool
    msg_id_atual: int = 0
    message: str


# ═══════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "AgendamentoCreate",
    "AgendamentoUpdate",
    "AgendamentoResponse",
    "AgendamentoOrigemCreate",
    "AgendamentoOrigemResponse",
    "AgendamentoDestinoCreate",
    "AgendamentoDestinoResponse",
    "AgendamentoHorarioCreate",
    "AgendamentoHorarioResponse",
    "AgendamentoFiltroCreate",
    "AgendamentoFiltroResponse",
    "AgendamentoCondicaoCreate",
    "AgendamentoCondicaoResponse",
    "AgendamentoFullResponse",
    "AgendamentoStats",
    "AgendamentoTestExecution",
    "AgendamentoTestExecutionResponse",
    "AgendamentoNextExecution",
    "AgendamentoResetSequence",
    "AgendamentoResetSequenceResponse",
]
