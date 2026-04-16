"""
Log Model — Histórico de Execuções

Tabela:
    log_execucao — Log de cada execução de regra/agendamento

Padrão:
    - Registra cada vez que uma regra/agendamento executa
    - Armazena status (sucesso, erro, aviso), origem, destino, mensagem de erro
    - Facilita debugging e auditoria
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Index
from app.core.guid import GUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import LogStatus
import uuid
from datetime import datetime


class LogExecucao(Base):
    """Log de execução de regra ou agendamento.
    
    Registro de cada vez que:
        1. Uma regra tenta encaminhar uma mensagem
        2. Um agendamento executa em um horário programado
    
    Campos:
        id: UUID PK
        tenant_id: FK para Tenant (multi-tenancy)
        bot_id: FK para Bot (qual bot executou)
        origem: Origem da mensagem (ex: "@canal_vendas", "-1001234567890")
        destino: Destino do encaminhamento (ex: "@suporte")
        status: Log status (sucesso, erro, aviso)
        mensagem: Detalhes do status (ex: "Timeout ao enviar", "Rate limited")
        data_hora: Timestamp da execução
        
        criado_em, atualizado_em: Timestamps
        deletado_em: Soft delete (rare, but consistent)
    
    Relationships:
        - tenant: Tenant (N:1)
        - bot: Bot (N:1)
    
    Usage:
        - Auditoria: "Quantas mensagens foram enviadas hoje?"
        - Debugging: "Por que o agendamento falhou?"
        - Analytics: "Taxa de sucesso por bot"
        - Rate limiting: "Quantas messages nesta hora?"
    
    Índices:
        - (tenant_id, data_hora) — queries por tenant em período
        - (bot_id, data_hora) — queries por bot em período
        - (status) — filtrar por status
    """
    __tablename__ = "log_execucao"
    
    # ─────────────────────────────────────────────────────────────
    # Primary Key
    # ─────────────────────────────────────────────────────────────
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    
    # ─────────────────────────────────────────────────────────────
    # Multi-Tenancy & References
    # ─────────────────────────────────────────────────────────────
    tenant_id = Column(GUID, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    bot_id = Column(GUID, ForeignKey("bot.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # ─────────────────────────────────────────────────────────────
    # Execution Details
    # ─────────────────────────────────────────────────────────────
    # Canal/grupo de origem (ex: "@vendas", "-1001234567890")
    origem = Column(String(255), nullable=False, index=True)
    
    # Canal/grupo de destino (ex: "@suporte")
    destino = Column(String(255), nullable=False, index=True)
    
    # Status da execução (sucesso, erro, aviso)
    status = Column(String(20), nullable=False, index=True)  # LogStatus enum
    
    # Mensagem descritiva (ex: "Timeout ao enviar", "Rate limited", "Enviado com sucesso", "Bloqueado por filtro")
    mensagem = Column(String(500), nullable=True)
    
    # Timestamp da execução
    data_hora = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # ─────────────────────────────────────────────────────────────
    # Audit Timestamps
    # ─────────────────────────────────────────────────────────────
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletado_em = Column(DateTime, nullable=True, index=True)
    
    # ─────────────────────────────────────────────────────────────
    # Relationships
    # ─────────────────────────────────────────────────────────────
    tenant = relationship("Tenant", lazy="select", foreign_keys=[tenant_id])
    bot = relationship("Bot", lazy="select", foreign_keys=[bot_id])
    
    # ─────────────────────────────────────────────────────────────
    # Table Arguments (Additional Indexes)
    # ─────────────────────────────────────────────────────────────
    __table_args__ = (
        # Índice composto para queries rápidas por tenant + período
        Index("idx_log_tenant_data", tenant_id, data_hora),
        # Índice composto para queries por bot + período
        Index("idx_log_bot_data", bot_id, data_hora),
        # Índice para filtrar por status + período (analytics)
        Index("idx_log_status_data", status, data_hora),
    )
    
    # ─────────────────────────────────────────────────────────────
    # Methods
    # ─────────────────────────────────────────────────────────────
    
    def is_deleted(self) -> bool:
        """Verifica se log foi soft-deleted (rare)."""
        return self.deletado_em is not None
    
    def get_status(self) -> LogStatus:
        """Retorna o status como enum LogStatus."""
        try:
            return LogStatus(self.status)
        except ValueError:
            return None
    
    def is_success(self) -> bool:
        """Verifica se execução foi bem-sucedida."""
        return self.status == LogStatus.SUCESSO.value
    
    def is_error(self) -> bool:
        """Verifica se execução resultou em erro."""
        return self.status == LogStatus.ERRO.value
    
    def is_warning(self) -> bool:
        """Verifica se execução teve aviso."""
        return self.status == LogStatus.AVISO.value
    
    def __repr__(self):
        return f"<LogExecucao(bot_id={self.bot_id}, origem={self.origem!r}, destino={self.destino!r}, status={self.status})>"


__all__ = ["LogExecucao"]

