"""
Uso Model — Controle de Uso Mensal e Rate Limiting

Tabela:
    uso_mensal — Contador de mensagens enviadas por tenant/mês

Padrão:
    - Registra quantas mensagens cada tenant enviou neste mês
    - Facilita rate limiting (limite_msgs_hora) e auditoria
    - Resets no dia 1º de cada mês
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, Date, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.guid import GUID
import uuid
from datetime import datetime, date


class UsoMensal(Base):
    """Controle de uso mensal por tenant.
    
    Registro de consumo de mensagens para:
        1. Rate limiting — impedir tenant de ultrapassar limite_msgs_hora
        2. Auditoria — "Quantas msgs o tenant X usou em abril?"
        3. Billing — "Cobrar por msgs excedentes?"
    
    Campos:
        id: UUID PK
        tenant_id: FK para Tenant (multi-tenancy)
        ano_mes: YYYYMM string (ex: "202604" para abril/2026)
        msgs_enviadas: Counter de mensagens enviadas no mês
        msgs_failed: Counter de mensagens que falharam
        
        criado_em, atualizado_em: Timestamps
        deletado_em: Soft delete (rare)
    
    Relationships:
        - tenant: Tenant (N:1)
    
    Usage:
        1. Cada vez que uma mensagem é enviada:
           - Increment msgs_enviadas
           - Se status=erro, increment msgs_failed
        2. Rate limiting:
           - Verificar limite_msgs_hora do tenant
           - COUNT logs da última hora e comparar
        3. Dashboard:
           - Mostrar msgs_enviadas do mês atual
           - Mostrar taxa de sucesso (msgs_enviadas - msgs_failed) / msgs_enviadas
    
    ORM Pattern:
        # Buscar uso de um tenant no mês
        uso = (
            await session.execute(
                select(UsoMensal)
                .where(UsoMensal.tenant_id == tenant_id)
                .where(UsoMensal.ano_mes == current_month)
            )
        ).scalar_one_or_none()
        
        # Incrementar
        if uso:
            uso.msgs_enviadas += 1
        else:
            uso = UsoMensal(tenant_id=tenant_id, ano_mes=current_month, msgs_enviadas=1)
            session.add(uso)
    
    Índices:
        - (tenant_id, ano_mes) — query principal
        - (ano_mes) — queries por período
    """
    __tablename__ = "uso_mensal"
    
    # ─────────────────────────────────────────────────────────────
    # Primary Key
    # ─────────────────────────────────────────────────────────────
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    
    # ─────────────────────────────────────────────────────────────
    # Multi-Tenancy
    # ─────────────────────────────────────────────────────────────
    tenant_id = Column(GUID, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # ─────────────────────────────────────────────────────────────
    # Time Period & Counters
    # ─────────────────────────────────────────────────────────────
    # Período YYYYMM (ex: "202604" = abril/2026)
    # String para facilitar queries e comparações
    # Alternativa: usar DATE para 1º do mês? Decidir com team
    ano_mes = Column(String(6), nullable=False, index=True)  # "202604"
    
    # Contador de mensagens enviadas com sucesso neste mês
    msgs_enviadas = Column(Integer, nullable=False, default=0)
    
    # Contador de mensagens que falharam (status=erro)
    msgs_failed = Column(Integer, nullable=False, default=0)
    
    # ─────────────────────────────────────────────────────────────
    # Audit Timestamps
    # ─────────────────────────────────────────────────────────────
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletado_em = Column(DateTime, nullable=True, index=True)
    
    # ─────────────────────────────────────────────────────────────
    # Relationships
    # ─────────────────────────────────────────────────────────────
    tenant = relationship("Tenant", lazy="select", foreign_keys=[tenant_id])
    
    # ─────────────────────────────────────────────────────────────
    # Table Arguments (Additional Indexes)
    # ─────────────────────────────────────────────────────────────
    __table_args__ = (
        # Índice composto para queries rápidas (tenant_id + mês)
        Index("idx_uso_tenant_mes", tenant_id, ano_mes, unique=True),
        # Índice para queries por período (analytics)
        Index("idx_uso_mes", ano_mes),
    )
    
    # ─────────────────────────────────────────────────────────────
    # Methods
    # ─────────────────────────────────────────────────────────────
    
    def is_deleted(self) -> bool:
        """Verifica se registro foi soft-deleted (rare)."""
        return self.deletado_em is not None
    
    def total_msgs(self) -> int:
        """Total de mensagens (sucesso + falhas)."""
        return self.msgs_enviadas + self.msgs_failed
    
    def taxa_sucesso(self) -> float:
        """Taxa de sucesso em porcento (0-100).
        
        Returns:
            Percentual de mensagens bem-sucedidas (0.0 a 100.0)
            
        Example:
            >>> uso.msgs_enviadas = 95
            >>> uso.msgs_failed = 5
            >>> uso.taxa_sucesso()
            95.0
        """
        total = self.total_msgs()
        if total == 0:
            return 0.0
        return (self.msgs_enviadas / total) * 100.0
    
    def taxa_falha(self) -> float:
        """Taxa de falha em porcento (0-100)."""
        return 100.0 - self.taxa_sucesso()
    
    @staticmethod
    def get_current_month_str() -> str:
        """Retorna string do mês atual em format YYYYMM.
        
        Returns:
            String YYYYMM (ex: "202604")
        """
        today = datetime.now()
        return f"{today.year}{today.month:02d}"
    
    def __repr__(self):
        return f"<UsoMensal(tenant_id={self.tenant_id}, ano_mes={self.ano_mes}, msgs_enviadas={self.msgs_enviadas})>"


__all__ = ["UsoMensal"]

