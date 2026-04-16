"""User Model — Local User Management

Tabela:
    user — Usuários do sistema com autenticação local
    
Nota:
    Armazena credentials locais (email + senha hash)
    Integra com TenantMember para RBAC
"""

from sqlalchemy import Column, String, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.guid import GUID
import uuid
from datetime import datetime


class User(Base):
    """Usuário com autenticação local.
    
    Campos:
        id: UUID PK
        email: Email único para login
        senha_hash: Senha hasheada com bcrypt
        nome: Nome completo do usuário
        ativo: Se usuário pode fazer login
        
        criado_em, atualizado_em: Timestamps
        deletado_em: Soft delete
        
    Relationships:
        - tenant_members: TenantMember (1:N)
            Ligação entre User e tenants que usuario faz parte
    """
    __tablename__ = "user"
    
    # ─────────────────────────────────────────────────────────────
    # Primary Key
    # ─────────────────────────────────────────────────────────────
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    
    # ─────────────────────────────────────────────────────────────
    # Authentication
    # ─────────────────────────────────────────────────────────────
    # Email como identificador único (índice para login)
    email = Column(String(255), nullable=False, unique=True, index=True)
    
    # Senha hasheada com bcrypt (nunca armazenar plain text!)
    senha_hash = Column(String(255), nullable=False)
    
    # ─────────────────────────────────────────────────────────────
    # Profile
    # ─────────────────────────────────────────────────────────────
    # Nome completo
    nome = Column(String(255), nullable=False)
    
    # ─────────────────────────────────────────────────────────────
    # Status & Audit
    # ─────────────────────────────────────────────────────────────
    ativo = Column(Boolean, nullable=False, default=True, index=True)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletado_em = Column(DateTime, nullable=True, index=True)  # Soft delete
    
    # ─────────────────────────────────────────────────────────────
    # Relationships
    # ─────────────────────────────────────────────────────────────
    tenant_members = relationship(
        "TenantMember",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="TenantMember.user_id",
        back_populates="user",
    )
    
    # ─────────────────────────────────────────────────────────────
    # Methods
    # ─────────────────────────────────────────────────────────────
    
    def is_deleted(self) -> bool:
        """Verifica se usuário foi soft-deleted."""
        return self.deletado_em is not None
    
    def is_active(self) -> bool:
        """Verifica se usuário está ativo (não deletado e ativo=true)."""
        return self.ativo and not self.is_deleted()
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email!r}, nome={self.nome!r})>"

