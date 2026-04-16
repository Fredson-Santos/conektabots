"""
Marketplace Models — Integrações com Marketplaces

Tabela:
    marketplace_integracao — Credenciais de marketplace criptografadas

Padrão:
    - Credenciais armazenadas como BYTEA (criptografadas via pgp_sym_encrypt)
    - NUNCA retornar credenciais_enc em API responses
    - Estratégia de cliente em worker/marketplace_clients/
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, LargeBinary
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.guid import GUID
from app.models.enums import MarketplaceTipo
import uuid
from datetime import datetime


class MarketplaceIntegracao(Base):
    """Integração com marketplace (credenciais criptografadas).
    
    Mapeia:
        - tenant: Qual organização
        - tipo: Qual marketplace (shopee, mercado_livre, etc)
        - credenciais_enc: JSON criptografado com keys do marketplace
    
    Exemplo de credenciais (antes de encriptar):
        {
            "app_id": "123456",
            "app_secret": "xyz789abc",
            "access_token": "token_aqui",
            "shop_id": "shop_999"  # Shopee
        }
    
    Encriptação:
        - Feita no banco via pgp_sym_encrypt() e ENCRYPTION_KEY
        - Descriptação em queries com pgp_sym_decrypt()
        - Python não tem acesso às credenciais (apenas o DB)
    
    Campos:
        id: UUID PK
        tenant_id: FK para Tenant (multi-tenancy)
        tipo: Enum MarketplaceTipo (shopee, mercado_livre, amazon, magalu, etc)
        nome: Nome legível para o usuário (ex: "Loja Shopee Brasil")
        credenciais_enc: BYTEA criptografado (NUNCA retornar em API)
        
        ativo: Flag de ativação
        criado_em, atualizado_em: Timestamps
        deletado_em: Soft delete
    
    Relationships:
        - tenant: Tenant (N:1)
        - regras: Regra que usam esta integração (1:N)
        - agendamentos: Agendamento que usam esta integração (1:N)
    
    Safety:
        - API responses devem excluir credenciais_enc
        - Queries para encriptar/descriptografar devem usar pgp_sym_encrypt
        - Rate limiting por marketplace para não ultrapassar quotas
    """
    __tablename__ = "marketplace_integracao"
    
    # ─────────────────────────────────────────────────────────────
    # Primary Key
    # ─────────────────────────────────────────────────────────────
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    
    # ─────────────────────────────────────────────────────────────
    # Multi-Tenancy
    # ─────────────────────────────────────────────────────────────
    tenant_id = Column(GUID, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # ─────────────────────────────────────────────────────────────
    # Marketplace Type & Configuration
    # ─────────────────────────────────────────────────────────────
    tipo = Column(String(30), nullable=False, index=True)
    # Exemplo de valores: "shopee", "mercado_livre", "amazon", "magalu", etc
    # Mapeado para MarketplaceTipo enum em app/models/enums.py
    
    # Nome legível para o usuário (ex: "Loja Shopee Brasil", "ML Pro")
    nome = Column(String(100), nullable=False)
    
    # ─────────────────────────────────────────────────────────────
    # Credenciais (CRIPTOGRAFADAS)
    # ─────────────────────────────────────────────────────────────
    # BYTEA encriptado via pgp_sym_encrypt() — NUNCA retornar em API responses
    # Conteúdo: JSON com app_id, app_secret, access_token, shop_id, etc
    # Ex: {"app_id": "123", "app_secret": "xyz", "access_token": "token_abc"}
    credenciais_enc = Column(LargeBinary, nullable=True)
    # nullable=True permite criar integração sem credenciais (add tudo depois)
    
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
    tenant = relationship(
        "Tenant",
        lazy="select",
        foreign_keys=[tenant_id],
    )
    
    # Regras que usam esta integração para encaminhamento
    regras = relationship(
        "Regra",
        lazy="select",
        foreign_keys="Regra.marketplace_integracao_id",
    )
    
    # Agendamentos que usam esta integração para envio
    agendamentos = relationship(
        "Agendamento",
        lazy="select",
        foreign_keys="Agendamento.marketplace_integracao_id",
    )
    
    # ─────────────────────────────────────────────────────────────
    # Methods
    # ─────────────────────────────────────────────────────────────
    
    def is_deleted(self) -> bool:
        """Verifica se integração foi soft-deleted."""
        return self.deletado_em is not None
    
    def is_active(self) -> bool:
        """Verifica se integração está ativa (não deletada e ativo=true)."""
        return self.ativo and not self.is_deleted()
    
    @property
    def is_configured(self) -> bool:
        """Verifica se credenciais foram configuradas (credenciais_enc não é NULL)."""
        return self.credenciais_enc is not None
    
    def get_marketplace_type(self) -> MarketplaceTipo:
        """Retorna o tipo como enum MarketplaceTipo."""
        try:
            return MarketplaceTipo(self.tipo)
        except ValueError:
            return None
    
    def __repr__(self):
        return f"<MarketplaceIntegracao(id={self.id}, tipo={self.tipo}, nome={self.nome!r})>"


__all__ = ["MarketplaceIntegracao"]

