"""
Bot Models — Contas Telegram (User ou Bot)

Tabela:
    bot — Contas Telegram com credenciais criptografadas

Padrão:
    - api_hash, bot_token, session_string armazenados como BYTEA (criptografados)
    - NUNCA retornar campos _enc em API responses
    - Integração com Telethon (MTProto API)
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Integer, LargeBinary
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.guid import GUID
from app.models.enums import BotTipo
import uuid
from datetime import datetime


class Bot(Base):
    """Conta Telegram (User ou Bot).
    
    Dois tipos de autenticação MTProto:
        1. USER: Conta pessoal
           - Requer: api_id, api_hash, phone, session_string
           - Usa: Telethon com MTProto
           - Vantagem: Acesso completo, sem rate limit aparente
           
        2. BOT: Bot oficial
           - Requer: bot_token (do BotFather)
           - Usa: Bot API (HTTP)
           - Vantagem: Mais simples, menos overhead
    
    Campos:
        id: UUID PK
        tenant_id: FK para Tenant (multi-tenancy)
        nome: Nome legível da conta (ex: "Bot de Envios", "Suporte")
        api_id: Telegram API ID (para MTProto USER)
        tipo: Enum BotTipo (user ou bot)
        phone: Número de telefone (para MTProto USER)
        
        # Credenciais criptografadas (BYTEA)
        api_hash_enc: Hash da API (apenas para tipo=user)
        bot_token_enc: Token de bot (apenas para tipo=bot)
        session_string_enc: Session string serializada (apenas para tipo=user)
        
        ativo: Flag de ativação
        criado_em, atualizado_em: Timestamps
        deletado_em: Soft delete
    
    Relationships:
        - tenant: Tenant (N:1)
        - regras: Regra que usam este bot (1:N)
        - agendamentos: Agendamento que usam este bot (1:N)
        - logs: LogExecucao deste bot (1:N)
    
    Safety:
        - API responses devem excluir api_hash_enc, bot_token_enc, session_string_enc
        - Queries para encriptar devem usar pgp_sym_encrypt()
        - Worker.py autentica usando credenciais descriptografadas
        - Rate limiting por tenant (limite_msgs_hora)
    """
    __tablename__ = "bot"
    
    # ─────────────────────────────────────────────────────────────
    # Primary Key
    # ─────────────────────────────────────────────────────────────
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    
    # ─────────────────────────────────────────────────────────────
    # Multi-Tenancy
    # ─────────────────────────────────────────────────────────────
    tenant_id = Column(GUID, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # ─────────────────────────────────────────────────────────────
    # Basic Info
    # ─────────────────────────────────────────────────────────────
    # Nome que o usuário dá (ex: "Bot Principal", "Suporte")
    nome = Column(String(64), nullable=False, index=True)
    
    # Tipo de conta (user ou bot)
    tipo = Column(String(20), nullable=False, index=True)
    # Valores: "user" (MTProto user) ou "bot" (Bot API)
    
    # ─────────────────────────────────────────────────────────────
    # MTProto Configuration (para tipo="user")
    # ─────────────────────────────────────────────────────────────
    # Telegram API ID (obtido em my.telegram.org)
    api_id = Column(Integer, nullable=True)
    
    # Número de telefone da conta
    phone = Column(String(64), nullable=True)
    
    # ─────────────────────────────────────────────────────────────
    # Credenciais (CRIPTOGRAFADAS via pgp_sym_encrypt)
    # ─────────────────────────────────────────────────────────────
    
    # api_hash criptografado (para tipo="user")
    # NUNCA retornar em API responses
    api_hash_enc = Column(LargeBinary, nullable=True)
    
    # bot_token criptografado (para tipo="bot")
    # Format: "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    # NUNCA retornar em API responses
    bot_token_enc = Column(LargeBinary, nullable=True)
    
    # session_string criptografado (para tipo="user", Telethon serialized session)
    # NUNCA retornar em API responses
    session_string_enc = Column(LargeBinary, nullable=True)
    
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
    
    # Regras que usam este bot
    regras = relationship(
        "Regra",
        lazy="select",
        foreign_keys="Regra.bot_id",
    )
    
    # Agendamentos que usam este bot
    agendamentos = relationship(
        "Agendamento",
        lazy="select",
        foreign_keys="Agendamento.bot_id",
    )
    
    # Logs de execução deste bot
    logs = relationship(
        "LogExecucao",
        lazy="select",
        foreign_keys="LogExecucao.bot_id",
    )
    
    # ─────────────────────────────────────────────────────────────
    # Methods
    # ─────────────────────────────────────────────────────────────
    
    def is_deleted(self) -> bool:
        """Verifica se bot foi soft-deleted."""
        return self.deletado_em is not None
    
    def is_active(self) -> bool:
        """Verifica se bot está ativo (não deletado e ativo=true)."""
        return self.ativo and not self.is_deleted()
    
    def is_configured(self) -> bool:
        """Verifica se bot tem credenciais configuradas.
        
        Returns:
            True se:
                - tipo=user E tem api_hash, session_string
                - tipo=bot E tem bot_token
        """
        if self.tipo == "user":
            return self.api_hash_enc is not None and self.session_string_enc is not None
        elif self.tipo == "bot":
            return self.bot_token_enc is not None
        return False
    
    def get_bot_type(self) -> BotTipo:
        """Retorna o tipo como enum BotTipo."""
        try:
            return BotTipo(self.tipo)
        except ValueError:
            return None
    
    def __repr__(self):
        return f"<Bot(id={self.id}, nome={self.nome!r}, tipo={self.tipo})>"


__all__ = ["Bot"]

