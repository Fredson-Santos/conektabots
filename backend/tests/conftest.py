"""Pytest Configuration — Fixtures para testes.

Fornece fixtures compartilhadas:
- session (AsyncSession com limpeza)
- event_loop (para async tests)
- Fixtures de dados: user, tenant, bot, etc.
- Role-based fixtures: owner, admin, editor, viewer
"""

import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.user import User
from app.models.tenant import Tenant, TenantMember
from app.models.bot import Bot
from app.models.marketplace import MarketplaceIntegracao
from app.services.auth_service import AuthService


# SQLite in-memory database para testes
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
    """Create test database engine.
    
    Creates all tables and cleans up after test.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    """Create test database session with rollback on cleanup.
    
    Ensures database isolation between tests.
    """
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ═══════════════════════════════════════════════════════════════
# User Fixtures
# ═══════════════════════════════════════════════════════════════

@pytest_asyncio.fixture
async def user_owner(session: AsyncSession):
    """Create owner user for testing.
    
    Returns:
        User instance with owner role
    """
    user = User(
        email="owner@example.com",
        senha_hash=AuthService.hash_password("SecurePass123!"),
        nome="Owner User",
        ativo=True,
    )
    session.add(user)
    await session.commit()
    return user


@pytest_asyncio.fixture
async def user_admin(session: AsyncSession):
    """Create admin user for testing."""
    user = User(
        email="admin@example.com",
        senha_hash=AuthService.hash_password("SecurePass123!"),
        nome="Admin User",
        ativo=True,
    )
    session.add(user)
    await session.commit()
    return user


@pytest_asyncio.fixture
async def user_editor(session: AsyncSession):
    """Create editor user for testing."""
    user = User(
        email="editor@example.com",
        senha_hash=AuthService.hash_password("SecurePass123!"),
        nome="Editor User",
        ativo=True,
    )
    session.add(user)
    await session.commit()
    return user


@pytest_asyncio.fixture
async def user_viewer(session: AsyncSession):
    """Create viewer user for testing."""
    user = User(
        email="viewer@example.com",
        senha_hash=AuthService.hash_password("SecurePass123!"),
        nome="Viewer User",
        ativo=True,
    )
    session.add(user)
    await session.commit()
    return user


# ═══════════════════════════════════════════════════════════════
# Tenant Fixtures
# ═══════════════════════════════════════════════════════════════

@pytest_asyncio.fixture
async def tenant_a(session: AsyncSession):
    """Create first test tenant (Tenant A)."""
    tenant = Tenant(
        nome="Tenant A",
        slug="tenant-a",
        plano="free",
        ativo=True,
    )
    session.add(tenant)
    await session.commit()
    return tenant


@pytest_asyncio.fixture
async def tenant_b(session: AsyncSession):
    """Create second test tenant (Tenant B - for isolation testing)."""
    tenant = Tenant(
        nome="Tenant B",
        slug="tenant-b",
        plano="free",
        ativo=True,
    )
    session.add(tenant)
    await session.commit()
    return tenant


@pytest_asyncio.fixture
async def tenant_pro(session: AsyncSession):
    """Create Pro plan tenant for rate limit testing."""
    tenant = Tenant(
        nome="Pro Tenant",
        slug="tenant-pro",
        plano="pro",
        ativo=True,
    )
    session.add(tenant)
    await session.commit()
    return tenant


# ═══════════════════════════════════════════════════════════════
# Tenant Member Fixtures (User + Tenant + Role)
# ═══════════════════════════════════════════════════════════════

@pytest_asyncio.fixture
async def tenant_member_owner(session: AsyncSession, user_owner: User, tenant_a: Tenant):
    """Create owner member in Tenant A."""
    member = TenantMember(
        tenant_id=tenant_a.id,
        user_id=user_owner.id,
        role="owner",
    )
    session.add(member)
    await session.commit()
    return member


@pytest_asyncio.fixture
async def tenant_member_admin(session: AsyncSession, user_admin: User, tenant_a: Tenant):
    """Create admin member in Tenant A."""
    member = TenantMember(
        tenant_id=tenant_a.id,
        user_id=user_admin.id,
        role="admin",
    )
    session.add(member)
    await session.commit()
    return member


@pytest_asyncio.fixture
async def tenant_member_editor(session: AsyncSession, user_editor: User, tenant_a: Tenant):
    """Create editor member in Tenant A."""
    member = TenantMember(
        tenant_id=tenant_a.id,
        user_id=user_editor.id,
        role="editor",
    )
    session.add(member)
    await session.commit()
    return member


@pytest_asyncio.fixture
async def tenant_member_viewer(session: AsyncSession, user_viewer: User, tenant_a: Tenant):
    """Create viewer member in Tenant A."""
    member = TenantMember(
        tenant_id=tenant_a.id,
        user_id=user_viewer.id,
        role="viewer",
    )
    session.add(member)
    await session.commit()
    return member


# ═══════════════════════════════════════════════════════════════
# Bot Fixtures
# ═══════════════════════════════════════════════════════════════

@pytest_asyncio.fixture
async def bot_user_type(session: AsyncSession, tenant_a: Tenant):
    """Create USER type bot (MTProto with session_string)."""
    bot = Bot(
        tenant_id=tenant_a.id,
        nome="Bot MTProto User",
        tipo="user",
        api_id=123456,
        phone="+5531999999999",
        ativo=True,
    )
    session.add(bot)
    await session.commit()
    return bot


@pytest_asyncio.fixture
async def bot_bot_type(session: AsyncSession, tenant_a: Tenant):
    """Create BOT type bot (Bot API with token)."""
    bot = Bot(
        tenant_id=tenant_a.id,
        nome="Bot API",
        tipo="bot",
        ativo=True,
    )
    session.add(bot)
    await session.commit()
    return bot


@pytest_asyncio.fixture
async def bot_other_tenant(session: AsyncSession, tenant_b: Tenant):
    """Create bot in different tenant (Tenant B - for isolation testing)."""
    bot = Bot(
        tenant_id=tenant_b.id,
        nome="Bot in Tenant B",
        tipo="bot",
        ativo=True,
    )
    session.add(bot)
    await session.commit()
    return bot


# ═══════════════════════════════════════════════════════════════
# Marketplace Fixtures
# ═══════════════════════════════════════════════════════════════

@pytest_asyncio.fixture
async def marketplace_shopee(session: AsyncSession, tenant_a: Tenant):
    """Create Shopee marketplace integration."""
    marketplace = MarketplaceIntegracao(
        tenant_id=tenant_a.id,
        tipo="shopee",
        nome="Loja Shopee",
        api_key_enc=b"encrypted_key_here",
        ativo=True,
    )
    session.add(marketplace)
    await session.commit()
    return marketplace


@pytest_asyncio.fixture
async def marketplace_mercado_livre(session: AsyncSession, tenant_a: Tenant):
    """Create Mercado Livre marketplace integration."""
    marketplace = MarketplaceIntegracao(
        tenant_id=tenant_a.id,
        tipo="mercado_livre",
        nome="Loja ML",
        api_key_enc=b"encrypted_key_here",
        ativo=True,
    )
    session.add(marketplace)
    await session.commit()
    return marketplace


# ═══════════════════════════════════════════════════════════════
# Auth Tokens (for testing JWT)
# ═══════════════════════════════════════════════════════════════

@pytest_asyncio.fixture
async def auth_service(session: AsyncSession):
    """Create auth service instance."""
    return AuthService(session)


@pytest_asyncio.fixture
async def access_token_owner(auth_service: AuthService, user_owner: User, tenant_a: Tenant, tenant_member_owner: TenantMember):
    """Create valid access token for owner."""
    token = auth_service.create_token({
        "sub": str(user_owner.id),
        "email": user_owner.email,
        "tenant": str(tenant_a.id),
        "role": "owner",
    })
    return token


@pytest_asyncio.fixture
async def access_token_admin(auth_service: AuthService, user_admin: User, tenant_a: Tenant, tenant_member_admin: TenantMember):
    """Create valid access token for admin."""
    token = auth_service.create_token({
        "sub": str(user_admin.id),
        "email": user_admin.email,
        "tenant": str(tenant_a.id),
        "role": "admin",
    })
    return token


@pytest_asyncio.fixture
async def access_token_editor(auth_service: AuthService, user_editor: User, tenant_a: Tenant, tenant_member_editor: TenantMember):
    """Create valid access token for editor."""
    token = auth_service.create_token({
        "sub": str(user_editor.id),
        "email": user_editor.email,
        "tenant": str(tenant_a.id),
        "role": "editor",
    })
    return token


@pytest_asyncio.fixture
async def access_token_viewer(auth_service: AuthService, user_viewer: User, tenant_a: Tenant, tenant_member_viewer: TenantMember):
    """Create valid access token for viewer."""
    token = auth_service.create_token({
        "sub": str(user_viewer.id),
        "email": user_viewer.email,
        "tenant": str(tenant_a.id),
        "role": "viewer",
    })
    return token


@pytest_asyncio.fixture
async def refresh_token_valid(auth_service: AuthService, user_owner: User):
    """Create valid refresh token."""
    from datetime import timedelta
    token = auth_service.create_token(
        {"sub": str(user_owner.id), "type": "refresh"},
        expires_delta=timedelta(days=7),
    )
    return token
