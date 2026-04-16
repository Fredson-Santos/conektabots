"""
Tenant Models — Organização/Empresa e Membros

Tabelas:
    tenant — Documento raiz do multi-tenancy
    tenant_member — Associação entre usuário Supabase Auth e tenant com RBAC

Padrão:
    - Tenant é o "root" de isolamento
    - Cada tenant_id em outras tabelas REFERENCES public.tenant(id) ON DELETE CASCADE
    - TenantMember liga auth.users (Supabase Auth) a um tenant com um role
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.types import String as StringType
from app.core.database import Base
from app.core.guid import GUID
from app.models.enums import PlanoTipo, MembroRole
import uuid
from datetime import datetime


class Tenant(Base):
    """Organização/Empresa — Raiz do multi-tenancy.
    
    Campos:
        id: UUID PK
        nome: Nome legível (ex: "Minha Empresa LTDA")
        slug: Identificador URL-safe único (ex: "minha-empresa")
        plano: Enum PlanoTipo (free, starter, pro, enterprise)
        
        Limites por plano (desnormalizados para performance):
        - limite_bots: Quantidade máxima de bots ativos
        - limite_regras: Quantidade máxima de regras ativas
        - limite_agendamentos: Quantidade máxima de agendamentos ativos
        - limite_msgs_hora: Taxa limit de mensagens por hora
        
        ativo: Soft flag (true = pode usar, false = suspenso)
        criado_em, atualizado_em: Timestamps
        deletado_em: Soft delete marker
    
    Relationships:
        - members: TenantMember (1:N)
        - bots: Bot (1:N, cascade delete)
        - regras: Regra (1:N, cascade delete)
        - agendamentos: Agendamento (1:N, cascade delete)
        - marketplace_integracoes: MarketplaceIntegracao (1:N, cascade delete)
    """
    __tablename__ = "tenant"
    
    # ─────────────────────────────────────────────────────────────
    # Primary Key & Identity
    # ─────────────────────────────────────────────────────────────
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    
    # ─────────────────────────────────────────────────────────────
    # Core Fields
    # ─────────────────────────────────────────────────────────────
    nome = Column(String(100), nullable=False, index=True)
    # Índice UNIQUE no slug para lookups rápidos por URL (ex: GET /api/minha-empresa/bots)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    
    # ─────────────────────────────────────────────────────────────
    # Plano & Limites
    # ─────────────────────────────────────────────────────────────
    # Tipo da assinatura (referência para PLAN_LIMITS em enums.py)
    plano = Column(String(20), nullable=False, default=PlanoTipo.FREE.value, index=True)
    
    # Limites desnormalizados (snapshot do plan_limits no momento da upgrade)
    # Útil para não perder histórico se plano for modificado
    limite_bots = Column(Integer, nullable=False, default=2)
    limite_regras = Column(Integer, nullable=False, default=5)
    limite_agendamentos = Column(Integer, nullable=False, default=5)
    limite_msgs_hora = Column(Integer, nullable=False, default=50)
    
    # ─────────────────────────────────────────────────────────────
    # Status & Audit
    # ─────────────────────────────────────────────────────────────
    ativo = Column(Boolean, nullable=False, default=True, index=True)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletado_em = Column(DateTime, nullable=True, index=True)  # Soft delete
    
    # ─────────────────────────────────────────────────────────────
    # Relationships (lazy="select" para async)
    # ─────────────────────────────────────────────────────────────
    members = relationship(
        "TenantMember",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="TenantMember.tenant_id",
        back_populates="tenant",
    )
    
    bots = relationship(
        "Bot",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="Bot.tenant_id",
    )
    
    regras = relationship(
        "Regra",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="Regra.tenant_id",
    )
    
    agendamentos = relationship(
        "Agendamento",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="Agendamento.tenant_id",
    )
    
    marketplace_integracoes = relationship(
        "MarketplaceIntegracao",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="MarketplaceIntegracao.tenant_id",
    )
    
    # ─────────────────────────────────────────────────────────────
    # Methods
    # ─────────────────────────────────────────────────────────────
    
    def is_deleted(self) -> bool:
        """Verifica se tenant foi soft-deleted."""
        return self.deletado_em is not None
    
    def is_active(self) -> bool:
        """Verifica se tenant está ativo (não deletado e ativo=true)."""
        return self.ativo and not self.is_deleted()
    
    def get_limit(self, limit_name: str) -> int:
        """Retorna um limite específico do plano.
        
        Args:
            limit_name: 'bots', 'regras', 'agendamentos', ou 'msgs_hora'
            
        Returns:
            Valor do limite (ex: 2 para free plan)
        """
        limits = {
            "bots": self.limite_bots,
            "regras": self.limite_regras,
            "agendamentos": self.limite_agendamentos,
            "msgs_hora": self.limite_msgs_hora,
        }
        return limits.get(limit_name, 0)
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, nome={self.nome!r}, plano={self.plano})>"


class TenantMember(Base):
    """Associação entre Usuário Supabase Auth e um Tenant com RBAC.
    
    Liga:
        1. user_id (UUID do Supabase Auth)
        2. tenant_id (UUID do Tenant)
        3. role (MembroRole: owner, admin, editor, viewer)
    
    Permission Model:
        - Um usuário pode estar em múltiplos tenants
        - Em cada tenant, o usuário tem um role específico
        - Role define o que o usuário pode fazer naquele tenant
        - RLS policies no Supabase garantem isolamento
    
    Campos:
        id: UUID PK
        tenant_id: FK para Tenant
        user_id: UUID do Supabase Auth (não é FK pois não está em auth.users)
        role: MembroRole enum (owner, admin, editor, viewer)
        
        criado_em, atualizado_em: Timestamps
        deletado_em: Soft delete (remover membro mantendo histórico)
    
    Constraints:
        - UNIQUE(tenant_id, user_id) — um usuário só pode estar 1x em um tenant
        - Cascade delete em tenant_id
    """
    __tablename__ = "tenant_member"
    
    # ─────────────────────────────────────────────────────────────
    # Primary Key
    # ─────────────────────────────────────────────────────────────
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    
    # ─────────────────────────────────────────────────────────────
    # Foreign Keys & User Reference
    # ─────────────────────────────────────────────────────────────
    # FK para tenant (cascade delete)
    tenant_id = Column(GUID, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # FK para user (cascade delete)
    user_id = Column(GUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # ─────────────────────────────────────────────────────────────
    # RBAC Role
    # ─────────────────────────────────────────────────────────────
    role = Column(String(20), nullable=False, default=MembroRole.VIEWER.value, index=True)
    
    # ─────────────────────────────────────────────────────────────
    # Audit & Lifecycle
    # ─────────────────────────────────────────────────────────────
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletado_em = Column(DateTime, nullable=True, index=True)  # Soft delete = remove member
    
    # ─────────────────────────────────────────────────────────────
    # Relationships
    # ─────────────────────────────────────────────────────────────
    tenant = relationship(
        "Tenant",
        lazy="select",
        foreign_keys=[tenant_id],
        back_populates="members",
    )
    
    user = relationship(
        "User",
        lazy="select",
        foreign_keys=[user_id],
        back_populates="tenant_members",
    )
    
    # ─────────────────────────────────────────────────────────────
    # Constraints
    # ─────────────────────────────────────────────────────────────
    # UNIQUE via __table_args__ (um usuário só pode estar 1x em um tenant)
    __table_args__ = (
        # UNIQUE(tenant_id, user_id)
        # Comment: Garante que não haja duplicação — um user só pode ter 1 role por tenant
    )
    
    # ─────────────────────────────────────────────────────────────
    # Methods
    # ─────────────────────────────────────────────────────────────
    
    def is_deleted(self) -> bool:
        """Verifica se membro foi soft-deleted (removido do tenant)."""
        return self.deletado_em is not None
    
    def is_active(self) -> bool:
        """Verifica se membro está ativo no tenant."""
        return not self.is_deleted()
    
    def get_role(self) -> MembroRole:
        """Retorna o role como MembroRole enum."""
        return MembroRole(self.role)
    
    def has_permission(self, required_role: MembroRole) -> bool:
        """Verifica se este membro tem permissão >= required_role.
        
        Args:
            required_role: Role requerida (ex: MembroRole.ADMIN)
            
        Returns:
            True se self.role >= required_role (em hierarquia)
        """
        return self.get_role().has_permission(required_role)
    
    def __repr__(self):
        return f"<TenantMember(tenant_id={self.tenant_id}, user_id={self.user_id}, role={self.role})>"


__all__ = ["Tenant", "TenantMember"]

