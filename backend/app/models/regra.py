"""
Regra Models — Encaminhamento automático de mensagens

Tabelas:
    regra — Config mãe de encaminhamento
    regra_origem — Canais/grupos de origem (N por regra)
    regra_destino — Canais/grupos de destino (N por regra)
    regra_filtro — Palavras-chave (incluir/bloquear, N por regra)
    regra_condicao — Condições obrigatórias (N por regra)

Padrão:
    - Regra é o "root" — define a configuração
    - Tabelas filhas ("_origem", "_destino", "_filtro", "_condicao") são N:1
    - Soft delete em todas as tabelas
    - Índices em chaves únicas (regra_id, origem) para evitar duplicatas
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.guid import GUID
from app.models.enums import FiltroMidiaTipo, FiltroRegraType
import uuid
from datetime import datetime


class Regra(Base):
    """Regra de encaminhamento automático de mensagens.
    
    Fluxo:
        1. Mensagem chega em um dos canais de ORIGEM
        2. Regra verifica:
           - Filtro de mídia (foto, vídeo, documento, etc)
           - Palavras-chave (incluir/bloquear)
           - Condições obrigatórias
        3. Se passar, encaminha para DESTINO
        4. Pode converter links de afiliado (ex: Shopee)
    
    Campos:
        id: UUID PK
        tenant_id: FK para Tenant (multi-tenancy)
        nome: Nome legível da regra
        bot_id: FK para Bot (qual conta executa)
        marketplace_integracao_id: FK para MarketplaceIntegracao (opcional, para converter links)
        
        substituto: Texto para prepender na mensagem encaminhada (ex: "Promoção: " + msg)
        filtro_midia: Filtrar por tipo de mídia (todos, foto, vídeo, etc)
        converter_link: Ativar conversão de links de afiliado
        
        ativo: Flag de ativação
        criado_em, atualizado_em: Timestamps
        deletado_em: Soft delete
    
    Relationships:
        - tenant: Tenant (N:1)
        - bot: Bot (N:1)
        - marketplace_integracao: MarketplaceIntegracao (N:1, nullable)
        - origens: RegraOrigem (1:N)
        - destinos: RegraDestino (1:N)
        - filtros: RegraFiltro (1:N)
        - condicoes: RegraCondicao (1:N)
    """
    __tablename__ = "regra"
    
    # ─────────────────────────────────────────────────────────────
    # Primary Key
    # ─────────────────────────────────────────────────────────────
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    
    # ─────────────────────────────────────────────────────────────
    # Multi-Tenancy & References
    # ─────────────────────────────────────────────────────────────
    tenant_id = Column(GUID, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    bot_id = Column(GUID, ForeignKey("bot.id", ondelete="CASCADE"), nullable=False, index=True)
    marketplace_integracao_id = Column(GUID, ForeignKey("marketplace_integracao.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # ─────────────────────────────────────────────────────────────
    # Core Configuration
    # ─────────────────────────────────────────────────────────────
    nome = Column(String(64), nullable=False, index=True)
    
    # Texto para prepender (ex: "[PROMO] " + mensagem)
    substituto = Column(String(255), nullable=True)
    
    # Filtro de mídia (todos, foto, vídeo, documento, audio, foto_video)
    filtro_midia = Column(String(20), nullable=False, default=FiltroMidiaTipo.TODOS.value)
    
    # Converter links de afiliado? (ex: Shopee, AliExpress)
    converter_link = Column(Boolean, nullable=False, default=False)
    
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
    tenant = relationship("Tenant", lazy="select", foreign_keys=[tenant_id])
    bot = relationship("Bot", lazy="select", foreign_keys=[bot_id])
    marketplace_integracao = relationship("MarketplaceIntegracao", lazy="select", foreign_keys=[marketplace_integracao_id])
    
    origens = relationship(
        "RegraOrigem",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="RegraOrigem.regra_id",
        back_populates="regra",
    )
    
    destinos = relationship(
        "RegraDestino",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="RegraDestino.regra_id",
        back_populates="regra",
    )
    
    filtros = relationship(
        "RegraFiltro",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="RegraFiltro.regra_id",
        back_populates="regra",
    )
    
    condicoes = relationship(
        "RegraCondicao",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="RegraCondicao.regra_id",
        back_populates="regra",
    )
    
    # ─────────────────────────────────────────────────────────────
    # Methods
    # ─────────────────────────────────────────────────────────────
    
    def is_deleted(self) -> bool:
        """Verifica se regra foi soft-deleted."""
        return self.deletado_em is not None
    
    def is_active(self) -> bool:
        """Verifica se regra está ativa (não deletada e ativo=true)."""
        return self.ativo and not self.is_deleted()
    
    def __repr__(self):
        return f"<Regra(id={self.id}, nome={self.nome!r})>"


class RegraOrigem(Base):
    """Canais/grupos de origem para uma regra.
    
    Exemplo:
        - regra_id: <uuid da regra>
        - origem: "-1001234567890"  (ID de grupo Telegram)
        - origem: "@canal_vendas"   (username de canal)
    
    UNIQUE(regra_id, origem) garante não haver duplicatas.
    """
    __tablename__ = "regra_origem"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(GUID, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    regra_id = Column(GUID, ForeignKey("regra.id", ondelete="CASCADE"), nullable=False, index=True)
    origem = Column(String(255), nullable=False)
    
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletado_em = Column(DateTime, nullable=True, index=True)
    
    regra = relationship("Regra", lazy="select", foreign_keys=[regra_id], back_populates="origens")
    
    def is_deleted(self) -> bool:
        return self.deletado_em is not None
    
    def __repr__(self):
        return f"<RegraOrigem(regra_id={self.regra_id}, origem={self.origem!r})>"


class RegraDestino(Base):
    """Canais/grupos de destino para encaminhamento.
    
    Exemplo:
        - regra_id: <uuid da regra>
        - destino: "-1009876543210"  (ID de grupo Telegram)
        - destino: "@vendas_geral"   (username de canal)
    
    UNIQUE(regra_id, destino) garante não haver duplicatas.
    """
    __tablename__ = "regra_destino"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(GUID, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    regra_id = Column(GUID, ForeignKey("regra.id", ondelete="CASCADE"), nullable=False, index=True)
    destino = Column(String(255), nullable=False)
    
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletado_em = Column(DateTime, nullable=True, index=True)
    
    regra = relationship("Regra", lazy="select", foreign_keys=[regra_id], back_populates="destinos")
    
    def is_deleted(self) -> bool:
        return self.deletado_em is not None
    
    def __repr__(self):
        return f"<RegraDestino(regra_id={self.regra_id}, destino={self.destino!r})>"


class RegraFiltro(Base):
    """Filtros de palavras-chave (incluir/bloquear).
    
    Tipos:
        - tipo="incluir": Whitelist — mensagem só passa se contiver a palavra
        - tipo="bloquear": Blacklist — mensagem é pulada se contiver a palavra
    
    Processamento:
        Se há filtros INCLUIR: Mensagem deve conter TODAS as palavras incluir
        Se há filtros BLOQUEAR: Mensagem não pode conter NENHUMA das palavras bloquear
        Se há ambos: Passa no INCLUIR E passa no BLOQUEAR
    
    UNIQUE(regra_id, tipo, valor) garante não haver duplicatas.
    """
    __tablename__ = "regra_filtro"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(GUID, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    regra_id = Column(GUID, ForeignKey("regra.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo = Column(String(20), nullable=False, default=FiltroRegraType.INCLUIR.value)
    valor = Column(String(255), nullable=False)
    
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletado_em = Column(DateTime, nullable=True, index=True)
    
    regra = relationship("Regra", lazy="select", foreign_keys=[regra_id], back_populates="filtros")
    
    def is_deleted(self) -> bool:
        return self.deletado_em is not None
    
    def __repr__(self):
        return f"<RegraFiltro(regra_id={self.regra_id}, tipo={self.tipo}, valor={self.valor!r})>"


class RegraCondicao(Base):
    """Condições obrigatórias.
    
    Exemplo:
        - condicao: "deve ter emoji"
        - condicao: "deve ter preço"
        - condicao: "deve ser no horário comercial"
    
    Interpretação:
        Mensagem só é encaminhada se CONTEM TODAS as condições.
    
    UNIQUE(regra_id, condicao) garante não haver duplicatas.
    """
    __tablename__ = "regra_condicao"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(GUID, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    regra_id = Column(GUID, ForeignKey("regra.id", ondelete="CASCADE"), nullable=False, index=True)
    condicao = Column(String(255), nullable=False)
    
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletado_em = Column(DateTime, nullable=True, index=True)
    
    regra = relationship("Regra", lazy="select", foreign_keys=[regra_id], back_populates="condicoes")
    
    def is_deleted(self) -> bool:
        return self.deletado_em is not None
    
    def __repr__(self):
        return f"<RegraCondicao(regra_id={self.regra_id}, condicao={self.condicao!r})>"


__all__ = ["Regra", "RegraOrigem", "RegraDestino", "RegraFiltro", "RegraCondicao"]

