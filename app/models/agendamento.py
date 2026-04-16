"""
Agendamento Models — Envio automático de mensagens em horários

Tabelas:
    agendamento — Config mãe de agendamento
    agendamento_origem — Canais de origem (N por agendamento)
    agendamento_destino — Canais de destino (N por agendamento)
    agendamento_horario — Horários de disparo (N por agendamento)
    agendamento_filtro — Palavras-chave (incluir/bloquear, N por agendamento)
    agendamento_condicao — Condições obrigatórias (N por agendamento)

Padrão:
    - Agendamento é o "root" — define a configuração
    - Tabelas filhas são N:1
    - Horários individuais em agendamento_horario (antes era string "12:30,19:45")
    - Soft delete em todas as tabelas
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Integer, Time
from app.core.guid import GUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import TipoEnvio, FiltroMidiaTipo, FiltroRegraType
import uuid
from datetime import datetime, time


class Agendamento(Base):
    """Agendamento de envio automático de mensagens em horários.
    
    Fluxo:
        1. No horário configurado (agendamento_horario):
           - Busca as mensagens na ORIGEM (chats configured)
           - Aplica filtros (mídia, palavras-chave, condições)
           - Encaminha para DESTINO
           - Pode converter links (ex: Shopee)
        2. Controla sequência de msgs com msg_id_atual
        3. Modo de envio: sequencial (1,2,3) ou aleatório
    
    Campos:
        id: UUID PK
        tenant_id: FK para Tenant (multi-tenancy)
        nome: Nome legível do agendamento
        bot_id: FK para Bot (qual conta executa)
        marketplace_integracao_id: FK para MarketplaceIntegracao (opcional, para converter links)
        
        msg_id_atual: Índice na sequência (para controlar onde parou)
        tipo_envio: Sequencial ou aleatório
        
        substituto: Texto para prepender na mensagem
        filtro_midia: Filtrar por tipo de mídia (todos, foto, vídeo, etc)
        
        ativo: Flag de ativação
        criado_em, atualizado_em: Timestamps
        deletado_em: Soft delete
    
    Relationships:
        - tenant: Tenant (N:1)
        - bot: Bot (N:1)
        - marketplace_integracao: MarketplaceIntegracao (N:1, nullable)
        - origens: AgendamentoOrigem (1:N)
        - destinos: AgendamentoDestino (1:N)
        - horarios: AgendamentoHorario (1:N)
        - filtros: AgendamentoFiltro (1:N)
        - condicoes: AgendamentoCondicao (1:N)
    """
    __tablename__ = "agendamento"
    
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
    
    # Controle de sequência (para tipo_envio=sequencial)
    msg_id_atual = Column(Integer, nullable=False, default=0)
    
    # Modo de envio (sequencial: 1,2,3... ou aleatório: random shuffle)
    tipo_envio = Column(String(20), nullable=False, default=TipoEnvio.SEQUENCIAL.value)
    
    # Texto para prepender na mensagem encaminhada
    substituto = Column(String(255), nullable=True)
    
    # Filtro de mídia (todos, foto, vídeo, documento, audio, foto_video)
    filtro_midia = Column(String(20), nullable=False, default=FiltroMidiaTipo.TODOS.value)
    
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
        "AgendamentoOrigem",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="AgendamentoOrigem.agendamento_id",
        back_populates="agendamento",
    )
    
    destinos = relationship(
        "AgendamentoDestino",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="AgendamentoDestino.agendamento_id",
        back_populates="agendamento",
    )
    
    horarios = relationship(
        "AgendamentoHorario",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="AgendamentoHorario.agendamento_id",
        back_populates="agendamento",
    )
    
    filtros = relationship(
        "AgendamentoFiltro",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="AgendamentoFiltro.agendamento_id",
        back_populates="agendamento",
    )
    
    condicoes = relationship(
        "AgendamentoCondicao",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="AgendamentoCondicao.agendamento_id",
        back_populates="agendamento",
    )
    
    # ─────────────────────────────────────────────────────────────
    # Methods
    # ─────────────────────────────────────────────────────────────
    
    def is_deleted(self) -> bool:
        """Verifica se agendamento foi soft-deleted."""
        return self.deletado_em is not None
    
    def is_active(self) -> bool:
        """Verifica se agendamento está ativo (não deletado e ativo=true)."""
        return self.ativo and not self.is_deleted()
    
    def __repr__(self):
        return f"<Agendamento(id={self.id}, nome={self.nome!r})>"


class AgendamentoOrigem(Base):
    """Canais/grupos de origem para um agendamento."""
    __tablename__ = "agendamento_origem"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(GUID, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    agendamento_id = Column(GUID, ForeignKey("agendamento.id", ondelete="CASCADE"), nullable=False, index=True)
    origem = Column(String(255), nullable=False)
    
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletado_em = Column(DateTime, nullable=True, index=True)
    
    agendamento = relationship("Agendamento", lazy="select", foreign_keys=[agendamento_id], back_populates="origens")
    
    def is_deleted(self) -> bool:
        return self.deletado_em is not None
    
    def __repr__(self):
        return f"<AgendamentoOrigem(agendamento_id={self.agendamento_id}, origem={self.origem!r})>"


class AgendamentoDestino(Base):
    """Canais/grupos de destino para um agendamento."""
    __tablename__ = "agendamento_destino"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(GUID, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    agendamento_id = Column(GUID, ForeignKey("agendamento.id", ondelete="CASCADE"), nullable=False, index=True)
    destino = Column(String(255), nullable=False)
    
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletado_em = Column(DateTime, nullable=True, index=True)
    
    agendamento = relationship("Agendamento", lazy="select", foreign_keys=[agendamento_id], back_populates="destinos")
    
    def is_deleted(self) -> bool:
        return self.deletado_em is not None
    
    def __repr__(self):
        return f"<AgendamentoDestino(agendamento_id={self.agendamento_id}, destino={self.destino!r})>"


class AgendamentoHorario(Base):
    """Horários de disparo para um agendamento.
    
    Exemplo:
        - agendamento_id: <uuid>
        - horario: TIME "12:30:00"
        - horario: TIME "19:45:00"
    
    Antes: armazenava como "12:30,19:45" (string)
    Agora: Normalizado em linhas separadas com tipo TIME
    
    UNIQUE(agendamento_id, horario) garante não haver duplicatas.
    """
    __tablename__ = "agendamento_horario"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(GUID, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    agendamento_id = Column(GUID, ForeignKey("agendamento.id", ondelete="CASCADE"), nullable=False, index=True)
    horario = Column(Time, nullable=False)  # TIME type
    
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletado_em = Column(DateTime, nullable=True, index=True)
    
    agendamento = relationship("Agendamento", lazy="select", foreign_keys=[agendamento_id], back_populates="horarios")
    
    def is_deleted(self) -> bool:
        return self.deletado_em is not None
    
    def __repr__(self):
        return f"<AgendamentoHorario(agendamento_id={self.agendamento_id}, horario={self.horario})>"


class AgendamentoFiltro(Base):
    """Filtros de palavras-chave (incluir/bloquear) para um agendamento."""
    __tablename__ = "agendamento_filtro"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(GUID, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    agendamento_id = Column(GUID, ForeignKey("agendamento.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo = Column(String(20), nullable=False, default=FiltroRegraType.INCLUIR.value)
    valor = Column(String(255), nullable=False)
    
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletado_em = Column(DateTime, nullable=True, index=True)
    
    agendamento = relationship("Agendamento", lazy="select", foreign_keys=[agendamento_id], back_populates="filtros")
    
    def is_deleted(self) -> bool:
        return self.deletado_em is not None
    
    def __repr__(self):
        return f"<AgendamentoFiltro(agendamento_id={self.agendamento_id}, tipo={self.tipo}, valor={self.valor!r})>"


class AgendamentoCondicao(Base):
    """Condições obrigatórias para um agendamento."""
    __tablename__ = "agendamento_condicao"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(GUID, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    agendamento_id = Column(GUID, ForeignKey("agendamento.id", ondelete="CASCADE"), nullable=False, index=True)
    condicao = Column(String(255), nullable=False)
    
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletado_em = Column(DateTime, nullable=True, index=True)
    
    agendamento = relationship("Agendamento", lazy="select", foreign_keys=[agendamento_id], back_populates="condicoes")
    
    def is_deleted(self) -> bool:
        return self.deletado_em is not None
    
    def __repr__(self):
        return f"<AgendamentoCondicao(agendamento_id={self.agendamento_id}, condicao={self.condicao!r})>"


__all__ = [
    "Agendamento",
    "AgendamentoOrigem",
    "AgendamentoDestino",
    "AgendamentoHorario",
    "AgendamentoFiltro",
    "AgendamentoCondicao",
]

