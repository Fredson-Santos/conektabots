"""
Models — SQLAlchemy ORM models para ConektaBots SaaS

Estrutura:
    enums.py — Tipos enumerados (PlanoTipo, BotTipo, etc)
    user.py — User (autenticação local)
    tenant.py — Tenant + TenantMember (multi-tenancy)
    marketplace.py — Integrações com marketplaces
    bot.py — Contas Telegram
    regra.py — Regras de encaminhamento + filhas
    agendamento.py — Agendamentos + filhas
    log.py — Log de execução
    uso.py — Controle de uso (rate limiting)
"""

# ═══════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════
from .enums import (
    PlanoTipo,
    BotTipo,
    TipoEnvio,
    LogStatus,
    MarketplaceTipo,
    MembroRole,
    FiltroMidiaTipo,
    FiltroRegraType,
    PLAN_LIMITS,
)

# ═══════════════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════════════
from .user import User

# ═══════════════════════════════════════════════════════════════
# MULTI-TENANCY
# ═══════════════════════════════════════════════════════════════
from .tenant import Tenant, TenantMember

# ═══════════════════════════════════════════════════════════════
# MARKETPLACE INTEGRATIONS
# ═══════════════════════════════════════════════════════════════
from .marketplace import MarketplaceIntegracao

# ═══════════════════════════════════════════════════════════════
# BOT & ACCOUNTS
# ═══════════════════════════════════════════════════════════════
from .bot import Bot

# ═══════════════════════════════════════════════════════════════
# RULES & FORWARDING
# ═══════════════════════════════════════════════════════════════
from .regra import Regra, RegraOrigem, RegraDestino, RegraFiltro, RegraCondicao

# ═══════════════════════════════════════════════════════════════
# SCHEDULES & AUTOMATION
# ═══════════════════════════════════════════════════════════════
from .agendamento import (
    Agendamento,
    AgendamentoOrigem,
    AgendamentoDestino,
    AgendamentoHorario,
    AgendamentoFiltro,
    AgendamentoCondicao,
)

# ═══════════════════════════════════════════════════════════════
# LOGGING & USAGE
# ═══════════════════════════════════════════════════════════════
from .log import LogExecucao
from .uso import UsoMensal

# ═══════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    "PlanoTipo",
    "BotTipo",
    "TipoEnvio",
    "LogStatus",
    "MarketplaceTipo",
    "MembroRole",
    "FiltroMidiaTipo",
    "FiltroRegraType",
    "PLAN_LIMITS",
    # Authentication
    "User",
    # Multi-Tenancy
    "Tenant",
    "TenantMember",
    # Marketplace
    "MarketplaceIntegracao",
    # Accounts
    "Bot",
    # Rules
    "Regra",
    "RegraOrigem",
    "RegraDestino",
    "RegraFiltro",
    "RegraCondicao",
    # Schedules
    "Agendamento",
    "AgendamentoOrigem",
    "AgendamentoDestino",
    "AgendamentoHorario",
    "AgendamentoFiltro",
    "AgendamentoCondicao",
    # Logging
    "LogExecucao",
    "UsoMensal",
]
