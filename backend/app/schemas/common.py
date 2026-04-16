"""
Common Schemas — DTOs reutilizáveis em toda a API

Padrão:
    - Todos os schemas herdam de BaseModel (Pydantic v2)
    - Campos com type hints explícitos
    - Validadores com field_validator para lógica customizada
    - Response models excluem campos sensíveis (_enc)
    - Create/Update models definem quais campos são obrigatórios/opcionais
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, Generic, TypeVar


# ═══════════════════════════════════════════════════════════════
# Response Wrapper Models
# ═══════════════════════════════════════════════════════════════

class SuccessResponse(BaseModel):
    """Resposta padrão de sucesso."""
    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    """Resposta padrão de erro."""
    success: bool = False
    error: str
    detail: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# Pagination Models
# ═══════════════════════════════════════════════════════════════

class PaginationParams(BaseModel):
    """Parâmetros de paginação."""
    skip: int = Field(default=0, ge=0, description="Número de registros a pular")
    limit: int = Field(default=20, ge=1, le=100, description="Número de registros a retornar")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {"skip": 0, "limit": 20}
    })


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Resposta paginada genérica."""
    total: int = Field(description="Total de registros")
    skip: int = Field(description="Registros pulados")
    limit: int = Field(description="Registros por página")
    items: list[T] = Field(description="Items da página")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "total": 42,
            "skip": 0,
            "limit": 20,
            "items": []
        }
    })


# ═══════════════════════════════════════════════════════════════
# Base Response Models (mixin for all responses)
# ═══════════════════════════════════════════════════════════════

class BaseResponse(BaseModel):
    """
    Base para todos os response models — inclui timestamps e IDs.
    Não inclui campos criptografados (_enc).
    """
    id: UUID
    criado_em: datetime
    atualizado_em: datetime
    deletado_em: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class BaseAudit(BaseModel):
    """Auditoria mínima (timestamps apenas)."""
    criado_em: datetime
    atualizado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# Tenant-scoped Response Model
# ═══════════════════════════════════════════════════════════════

class TenantInfo(BaseModel):
    """Informações mínimas de tenant (para nested responses)."""
    id: UUID
    nome: str
    slug: str
    plano: str
    ativo: bool
    
    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# Status & Flag Models
# ═══════════════════════════════════════════════════════════════

class StatusUpdate(BaseModel):
    """Modelo genérico para atualizar status."""
    ativo: bool = Field(description="Ativo ou inativo")


class SoftDeleteResponse(BaseModel):
    """Resposta após soft delete."""
    id: UUID
    deletado_em: datetime
    message: str = "Recurso deletado com sucesso"


# ═══════════════════════════════════════════════════════════════
# Bulk Operation Models
# ═══════════════════════════════════════════════════════════════

class BulkDeleteRequest(BaseModel):
    """Deletar múltiplos recursos."""
    ids: list[UUID] = Field(min_items=1, max_items=100)


class BulkDeleteResponse(BaseModel):
    """Resposta de bulk delete."""
    deleted_count: int
    ids: list[UUID]
    message: str = "Recursos deletados com sucesso"


class BulkUpdateRequest(BaseModel):
    """Atualizar múltiplos recursos."""
    ids: list[UUID] = Field(min_items=1, max_items=100)
    ativo: bool = Field(description="Novo status para todos os recursos")


class BulkUpdateResponse(BaseModel):
    """Resposta de bulk update."""
    updated_count: int
    ids: list[UUID]
    message: str = "Recursos atualizados com sucesso"


# ═══════════════════════════════════════════════════════════════
# Filter Models
# ═══════════════════════════════════════════════════════════════

class FilterParams(BaseModel):
    """Filtros genéricos para queries."""
    search: Optional[str] = Field(default=None, description="Busca por nome/descrição")
    ativo: Optional[bool] = Field(default=None, description="Filtrar por status")
    include_deleted: bool = Field(default=False, description="Incluir deletados (soft-deleted)")


# ═══════════════════════════════════════════════════════════════
# List Query Models
# ═══════════════════════════════════════════════════════════════

class ListQueryParams(BaseModel):
    """Parâmetros combinados para listar: paginação + filtros."""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)
    search: Optional[str] = Field(default=None)
    ativo: Optional[bool] = Field(default=None)
    include_deleted: bool = Field(default=False)
    sort_by: Optional[str] = Field(default="criado_em", description="Campo para ordenação")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "skip": 0,
            "limit": 20,
            "search": "bot principal",
            "ativo": True,
            "include_deleted": False,
            "sort_by": "criado_em",
            "sort_order": "desc"
        }
    })


# ═══════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "SuccessResponse",
    "ErrorResponse",
    "PaginationParams",
    "PaginatedResponse",
    "BaseResponse",
    "BaseAudit",
    "TenantInfo",
    "StatusUpdate",
    "SoftDeleteResponse",
    "BulkDeleteRequest",
    "BulkDeleteResponse",
    "BulkUpdateRequest",
    "BulkUpdateResponse",
    "FilterParams",
    "ListQueryParams",
]
