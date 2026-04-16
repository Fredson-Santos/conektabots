"""
Database Configuration — SQLAlchemy Async

Gerencia:
    - Conexão assíncrona ao PostgreSQL
    - Session factory para DI em FastAPI
    - Base metaclass para registrar modelos
    - Init/close lifecycle

Padrão:
    - async_session_maker: sessionmaker para criar sessions
    - get_session(): dependency para FastAPI routes
    - init_db(): criar/verificar tabelas (startup)
    - close_db(): cleanup (shutdown)
    
    Todos os modelos devem herdar de Base para serem registrados
    automaticamente no Base.metadata.create_all()
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import UUID
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════════════════════════
# DATABASE URL
# ═══════════════════════════════════════════════════════════════

database_url = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://fred:evYMr4UQguPaFWr@100.79.53.49:5432/conekta_dev"  # PostgreSQL
)

# Converter postgresql:// para postgresql+asyncpg://
if database_url.startswith("postgresql://") and not database_url.startswith("postgresql+asyncpg://"):
    async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    async_database_url = database_url

# Log connection info
_host = async_database_url.split("@")[1].split("/")[0] if "@" in async_database_url else "localhost"
_db = async_database_url.split("/")[-1] if "/" in async_database_url else "conekta_dev"
print(f"[DB] PostgreSQL | Host: {_host} | Database: {_db}")

# ═══════════════════════════════════════════════════════════════
# ENGINE & SESSION FACTORY
# ═══════════════════════════════════════════════════════════════

# PostgreSQL com pool configuration
engine = create_async_engine(
    async_database_url,
    echo=False,  # Mudar para True para debug SQL
    future=True,
    pool_size=20,           # Conexões simultâneas
    max_overflow=0,         # Não criar conexões extras além de pool_size
    pool_pre_ping=True,     # Verificar se conexão está viva antes de usar
    pool_recycle=3600,      # Reciclar conexão a cada hora
)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Não expirar objetos após commit
    autocommit=False,
    autoflush=False,
)

# ═══════════════════════════════════════════════════════════════
# BASE DECLARATIVE
# ═══════════════════════════════════════════════════════════════

Base = declarative_base()

# Nota: Cada modelo deve fazer: class MyModel(Base)
# Isso registra automaticamente em Base.metadata


# ═══════════════════════════════════════════════════════════════
# DEPENDENCY INJECTION
# ═══════════════════════════════════════════════════════════════

async def get_session():
    """
    Dependency Injection para FastAPI routes.
    
    Usage:
        from fastapi import Depends
        from app.core.database import get_session
        
        @app.get("/bots")
        async def list_bots(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(Bot))
            return result.scalars().all()
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


# ═══════════════════════════════════════════════════════════════
# LIFECYCLE MANAGEMENT
# ═══════════════════════════════════════════════════════════════

async def init_db():
    """
    Inicializar banco de dados (criar tabelas).
    
    Chamado no startup da aplicação:
        app.add_event_handler("startup", init_db)
    
    Importa todos os modelos para registrá-los no Base.metadata
    """
    # ─────────────────────────────────────────────────────────────
    # IMPORT ALL MODELS (para registrar no Base.metadata)
    # ─────────────────────────────────────────────────────────────
    # Deve importar DEPOIS de definir Base
    from app.models import (  # noqa: F401
        # Enums (não são tabelas)
        PlanoTipo,
        BotTipo,
        TipoEnvio,
        LogStatus,
        MarketplaceTipo,
        MembroRole,
        FiltroMidiaTipo,
        FiltroRegraType,
        # Multi-Tenancy
        Tenant,
        TenantMember,
        # Marketplace
        MarketplaceIntegracao,
        # Accounts
        Bot,
        # Rules & Forwarding
        Regra,
        RegraOrigem,
        RegraDestino,
        RegraFiltro,
        RegraCondicao,
        # Schedules & Automation
        Agendamento,
        AgendamentoOrigem,
        AgendamentoDestino,
        AgendamentoHorario,
        AgendamentoFiltro,
        AgendamentoCondicao,
        # Logging & Usage
        LogExecucao,
        UsoMensal,
    )
    
    # ─────────────────────────────────────────────────────────────
    # CREATE ALL TABLES
    # ─────────────────────────────────────────────────────────────
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("[DB] ✅ Todas as tabelas criadas/verificadas")


async def close_db():
    """
    Fechar conexão com o banco de dados.
    
    Chamado no shutdown da aplicação:
        app.add_event_handler("shutdown", close_db)
    """
    await engine.dispose()
    print("[DB] ✅ Conexão fechada")


# ═══════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "engine",
    "Base",
    "async_session_maker",
    "get_session",
    "init_db",
    "close_db",
]
