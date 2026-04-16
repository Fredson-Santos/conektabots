"""
Auth Schemas — Autenticação e Autorização

Models:
    - LoginRequest — credenciais
    - TokenResponse — JWT tokens (access + refresh)
    - UserCreate — registrar novo usuário
    - UserResponse — dados do usuário
    - RefreshTokenRequest — refresh token
"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Optional


# ═══════════════════════════════════════════════════════════════
# Login & Registration
# ═══════════════════════════════════════════════════════════════

class LoginRequest(BaseModel):
    """Login com email/password."""
    email: EmailStr = Field(description="Email do usuário")
    password: str = Field(min_length=8, description="Senha (mínimo 8 caracteres)")
    
    model_config = {"json_schema_extra": {
        "example": {
            "email": "user@example.com",
            "password": "SecurePassword123!"
        }
    }}


class LoginResponse(BaseModel):
    """Resposta de login bem-sucedida."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = Field(description="Segundos até expiração (1800 = 30min)")
    
    model_config = {"json_schema_extra": {
        "example": {
            "access_token": "eyJhbGciOiJIUzI1NiIs...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
            "token_type": "Bearer",
            "expires_in": 1800
        }
    }}


class RegisterRequest(BaseModel):
    """Registrar novo usuário."""
    email: EmailStr
    password: str = Field(
        min_length=8,
        description="Mínimo 8 caracteres, incluir maiúsculas, minúsculas, números e símbolos"
    )
    password_confirm: str = Field(description="Confirmação de senha")
    first_name: str = Field(description="Nome")
    last_name: str = Field(description="Sobrenome")
    
    model_config = {"json_schema_extra": {
        "example": {
            "email": "newuser@example.com",
            "password": "SecurePassword123!",
            "password_confirm": "SecurePassword123!",
            "first_name": "João",
            "last_name": "Silva"
        }
    }}


# ═══════════════════════════════════════════════════════════════
# Token Management
# ═══════════════════════════════════════════════════════════════

class TokenResponse(BaseModel):
    """Resposta padrão com tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    user_id: UUID
    tenant_id: UUID
    role: str = Field(description="Role no tenant: owner, admin, editor, viewer")
    expires_in: int = Field(default=1800, description="Segundos")


class RefreshTokenRequest(BaseModel):
    """Requisição para renovar access token."""
    refresh_token: str = Field(description="Refresh token válido")


class RefreshTokenResponse(BaseModel):
    """Nova credential após refresh."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 1800


# ═══════════════════════════════════════════════════════════════
# User Profile (Current User)
# ═══════════════════════════════════════════════════════════════

class UserResponse(BaseModel):
    """Dados do usuário autenticado."""
    id: UUID
    email: str
    first_name: str
    last_name: str
    full_name: str = Field(description="Concatenado: first_name last_name")
    current_tenant_id: UUID
    role: str = Field(description="Role no tenant atual")
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
    
    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    """Atualizar perfil do usuário."""
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    
    model_config = {"json_schema_extra": {
        "example": {
            "first_name": "João",
            "last_name": "Silva"
        }
    }}


class ChangePasswordRequest(BaseModel):
    """Alterar senha."""
    current_password: str = Field(description="Senha atual")
    new_password: str = Field(
        min_length=8,
        description="Nova senha (mínimo 8 caracteres)"
    )
    new_password_confirm: str = Field(description="Confirmação de nova senha")
    
    model_config = {"json_schema_extra": {
        "example": {
            "current_password": "OldPassword123!",
            "new_password": "NewPassword456!",
            "new_password_confirm": "NewPassword456!"
        }
    }}


# ═══════════════════════════════════════════════════════════════
# Permission Management (RBAC)
# ═══════════════════════════════════════════════════════════════

class PermissionCheck(BaseModel):
    """Verificação de permissão."""
    resource: str = Field(description="Recurso (ex: 'bot', 'regra')")
    action: str = Field(description="Ação (ex: 'create', 'edit', 'delete')")
    has_permission: bool


class RoleInfo(BaseModel):
    """Informações sobre um role."""
    role: str = Field(description="owner, admin, editor, viewer")
    level: int = Field(description="Nível hierárquico (4, 3, 2, 1)")
    description: str
    permissions: list[str] = Field(description="Permissões incluídas neste role")


# ═══════════════════════════════════════════════════════════════
# API Key Management (optional)
# ═══════════════════════════════════════════════════════════════

class APIKeyCreate(BaseModel):
    """Criar nova API key."""
    name: str = Field(description="Nome descritivo da chave")
    expires_in_days: Optional[int] = Field(default=None, description="Dias até expiração (None = nunca)")


class APIKeyResponse(BaseModel):
    """Resposta com API key criada."""
    id: UUID
    name: str
    key: str = Field(description="Chave real (mostrada UMA VEZ)")
    created_at: datetime
    expires_at: Optional[datetime] = None


class APIKeyListResponse(BaseModel):
    """Listar API keys (sem mostrar a chave completa)."""
    id: UUID
    name: str
    key_preview: str = Field(description="Primeiros 4 caracteres + últimos 4")
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    ativo: bool


# ═══════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "LoginRequest",
    "LoginResponse",
    "RegisterRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "RefreshTokenResponse",
    "UserResponse",
    "UserUpdateRequest",
    "ChangePasswordRequest",
    "PermissionCheck",
    "RoleInfo",
    "APIKeyCreate",
    "APIKeyResponse",
    "APIKeyListResponse",
]
