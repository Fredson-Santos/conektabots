# SKILL: Testing Strategy & Fixtures

**Purpose**: Guidelines for writing unit tests, integration tests, fixtures, mocking, and test organization for multi-tenant FastAPI application.

**Used for**: Creating test files, writing test cases, setting up fixtures, mocking services, testing security policies.

---

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── __init__.py
├── unit/
│   ├── test_models.py       # Model validation
│   ├── test_schemas.py      # Pydantic schemas
│   └── test_services.py     # Business logic
├── integration/
│   ├── test_auth.py         # Auth flow
│   ├── test_routers.py      # API endpoints
│   └── test_multi_tenant.py # Tenant isolation
├── e2e/
│   ├── test_user_journey.py # Full workflows
│   └── test_marketplace.py  # Marketplace integration
└── fixtures/
    ├── users.json
    ├── tenants.json
    └── bots.json
```

---

## conftest.py - Shared Fixtures

```python
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from uuid import uuid4

# In-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest_asyncio.fixture
async def session(engine):
    """Create test database session."""
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session

@pytest.fixture
def anyio_backend():
    """Configure pytest-anyio backend."""
    return "asyncio"

# === Test Data Fixtures ===

@pytest_asyncio.fixture
async def tenant(session: AsyncSession):
    """Create test tenant."""
    tenant = Tenant(
        id=uuid4(),
        nome="Test Tenant",
        owner_id=uuid4(),
        plano="free"
    )
    
    session.add(tenant)
    await session.commit()
    
    return tenant

@pytest_asyncio.fixture
async def user(session: AsyncSession, tenant: Tenant):
    """Create test user."""
    user = User(
        id=uuid4(),
        email="test@example.com",
        password_hash="hashed_password",
        tenant_id=tenant.id
    )
    
    session.add(user)
    await session.commit()
    
    return user

@pytest_asyncio.fixture
async def bot(session: AsyncSession, tenant: Tenant):
    """Create test bot."""
    bot = Bot(
        id=uuid4(),
        tenant_id=tenant.id,
        nome="Test Bot",
        api_id=123456,
        api_hash_enc=b"encrypted_hash",
        ativo=True
    )
    
    session.add(bot)
    await session.commit()
    
    return bot

# === Mock Services ===

@pytest.fixture
def crypto_service_mock(mocker):
    """Mock CryptoService."""
    mock = mocker.MagicMock()
    mock.encrypt.return_value = b"encrypted_data"
    mock.decrypt.return_value = "decrypted_data"
    return mock

@pytest.fixture
def token_service_mock(mocker):
    """Mock TokenService."""
    mock = mocker.MagicMock()
    mock.create_access_token.return_value = "test_jwt_token"
    mock.verify_token.return_value = {
        "sub": str(uuid4()),
        "tenant_id": str(uuid4()),
        "exp": 9999999999
    }
    return mock
```

---

## Unit Test Examples

### Test Models
```python
from app.models import Bot
from uuid import uuid4

@pytest.mark.asyncio
async def test_bot_creation(session):
    """Test creating a bot."""
    tenant_id = uuid4()
    bot = Bot(
        tenant_id=tenant_id,
        nome="Test Bot",
        api_id=123456,
        api_hash_enc=b"hash",
    )
    
    assert bot.nome == "Test Bot"
    assert bot.api_id == 123456
    assert bot.ativo == True  # Default

@pytest.mark.asyncio
async def test_soft_delete(session, bot):
    """Test soft delete functionality."""
    bot.soft_delete()
    
    assert bot.is_deleted == True
    assert bot.deletado_em is not None

def test_bot_repr():
    """Test string representation."""
    bot = Bot(nome="Test", ativo=True)
    assert "Test" in repr(bot)
```

### Test Schemas
```python
from pydantic import ValidationError
from app.schemas.bot import BotCreate

def test_bot_create_schema_valid():
    """Test valid BotCreate schema."""
    data = {
        "nome": "My Bot",
        "api_id": 123456,
        "api_hash": "hash_value"
    }
    
    schema = BotCreate(**data)
    assert schema.nome == "My Bot"

def test_bot_create_schema_invalid():
    """Test invalid BotCreate schema."""
    data = {
        "nome": "",  # Empty name invalid
        "api_id": 123456
    }
    
    with pytest.raises(ValidationError):
        BotCreate(**data)
```

### Test Services
```python
@pytest.mark.asyncio
async def test_service_create_bot(session, tenant_id, mocker):
    """Test BotService.create()."""
    # Mock dependencies
    service = BotService(session, crypto_service_mock)
    
    data = BotCreate(nama="Test", api_id=123)
    bot = await service.create(tenant_id, data)
    
    assert bot.tenant_id == tenant_id
    assert bot.nome == "Test"

@pytest.mark.asyncio
async def test_service_enforces_quota(sesssion, mocker):
    """Test quota enforcement."""
    service = BotService(session, ...)
    
    # Mock QuotaService to raise exception
    mocker.patch.object(
        service,
        "check_quota",
        side_effect=QuotaExceededError()
    )
    
    with pytest.raises(QuotaExceededError):
        await service.create(tenant_id, data)
```

---

## Integration Test Examples

### Test Authentication
```python
@pytest.mark.asyncio
async def test_login(client: AsyncClient, user):
    """Test user login."""
    response = await client.post(
        "/auth/login",
        json={
            "email": user.email,
            "password": "correct_password"
        }
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, user):
    """Test login with wrong password."""
    response = await client.post(
        "/auth/login",
        json={
            "email": user.email,
            "password": "wrong_password"
        }
    )
    
    assert response.status_code == 401
```

### Test Multi-Tenant Isolation
```python
@pytest.mark.asyncio
async def test_tenant_isolation(client: AsyncClient, session, mocker):
    """Test Tenant A cannot see Tenant B's bots."""
    # Create two tenants with users
    tenant_a = create_tenant()
    tenant_b = create_tenant()
    
    user_a = create_user(tenant_a)
    user_b = create_user(tenant_b)
    
    # Create bot in tenant_a
    bot_a = create_bot(tenant_a)
    
    # Login as user_b and try to access bot_a
    token_b = generate_token(user_b)
    
    response = await client.get(
        f"/bots/{bot_a.id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    
    # Should get 404 (not 200 with data)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_rls_policy(session):
    """Test RLS policy enforcement at database level."""
    # Simulate RLS check
    # Usually requires PostgreSQL, so skip for SQLite tests
    pytest.skip("Requires PostgreSQL for RLS")
```

### Test API Endpoints
```python
@pytest.mark.asyncio
async def test_create_bot_endpoint(
    client: AsyncClient,
    user,
    token_generator,
    mocker
):
    """Test POST /bots endpoint."""
    token = token_generator(user)
    
    response = await client.post(
        "/bots",
        json={
            "nome": "New Bot",
            "api_id": 123456,
            "api_hash": "hash"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "New Bot"

@pytest.mark.asyncio
async def test_list_bots_pagination(
    client: AsyncClient,
    user,
    token_generator,
    session
):
    """Test GET /bots with pagination."""
    token = token_generator(user)
    
    # Create 5 bots
    for i in range(5):
        create_bot(session, tenant_id=user.tenant_id)
    
    response = await client.get(
        "/bots?page=1&per_page=2",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
```

---

## Test Utilities

### Helper Functions
```python
# tests/helpers.py

def create_token(user_id: UUID, tenant_id: UUID, expires_in: int = 3600):
    """Create JWT token for testing."""
    from jose import jwt
    
    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "exp": datetime.utcnow() + timedelta(seconds=expires_in)
    }
    
    token = jwt.encode(payload, "test-secret", algorithm="HS256")
    return token

async def assert_count(session, model, expected: int, **filters):
    """Assert record count in db."""
    stmt = select(model)
    for key, value in filters.items():
        stmt = stmt.where(getattr(model, key) == value)
    
    result = await session.execute(stmt)
    assert len(result.scalars().all()) == expected

async def assert_forbidden(client, method, endpoint, **kwargs):
    """Assert 403 Forbidden response."""
    response = await getattr(client, method)(endpoint, **kwargs)
    assert response.status_code == 403
```

---

## Mocking & Patching

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_with_mock_external_api(mocker):
    """Mock external API call."""
    mock_api = mocker.AsyncMock()
    mock_api.test_connection.return_value = True
    
    with patch(
        "app.services.marketplace_service.MarketplaceClient",
        return_value=mock_api
    ):
        result = await service.test_marketplace()
        assert result == True

@pytest.mark.asyncio
async def test_with_mock_db_error(mocker):
    """Mock database error."""
    mocker.patch.object(
        AsyncSession,
        "execute",
        side_effect=SQLAlchemyError("DB Error")
    )
    
    with pytest.raises(InternalServerError):
        await service.list()
```

---

## Test Organization Best Practices

✅ **Good Structure**
```python
class TestBotService:
    """Group related tests in class."""
    
    @pytest.mark.asyncio
    async def test_create_valid_bot(self):
        pass
    
    @pytest.mark.asyncio
    async def test_create_exceeds_quota(self):
        pass
    
    @pytest.mark.asyncio
    async def test_bot_soft_delete(self):
        pass
```

✅ **Descriptive Names**
```python
# GOOD
async def test_user_cannot_access_other_tenants_bots():
    pass

# BAD
async def test_isolation():
    pass
```

✅ **One Assertion per Test** (or related assertions)
```python
# GOOD
async def test_create_returns_201():
    response = await create()
    assert response.status_code == 201

async def test_create_returns_valid_bot():
    response = await create()
    data = response.json()
    assert data["id"] is not None

# BAD
async def test_create():
    response = await create()
    assert response.status_code == 201
    assert response.json()["id"] is not None
    assert response.json()["ativo"] == True
    # Too many assertions in one test
```

---

## Running Tests

```bash
# Run all tests
pytest -v

# Run specific file
pytest tests/unit/test_models.py -v

# Run specific test
pytest tests/unit/test_models.py::test_bot_creation -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run only fast tests (markers)
pytest -m "not slow" -v

# Run in parallel
pytest -n auto
```

---

## Common Testing Mistakes ⚠️

❌ **Mistake 1**: Testing implementation, not behavior
```python
# BAD
def test_get_user():
    user = User(name="John")
    assert user.__dict__["_name"] == "John"

# GOOD
def test_get_user():
    user = User(name="John")
    assert user.name == "John"
```

❌ **Mistake 2**: Brittle tests (too specific)
```python
# BAD
async def test_list_bots():
    response = await client.get("/bots")
    assert response.json()[0]["updated_at"] == "2024-04-15T10:30:45.123456"

# GOOD
async def test_list_bots():
    response = await client.get("/bots")
    assert len(response.json()["items"]) > 0
    assert "id" in response.json()["items"][0]
```

❌ **Mistake 3**: No isolation between tests
```python
# BAD (tests depend on execution order)
async def test_create_user():
    user = await create_user("john@example.com")
    # Tests assume john@example.com exists

async def test_get_user():
    user = await get_user("john@example.com")  # Fails if previous test didn't run

# GOOD (each test is independent)
async def test_create_user(session):
    user = await create_user(session, "test1@example.com")
    assert user.email == "test1@example.com"

async def test_get_user(session):
    await create_user(session, "test2@example.com")
    user = await get_user(session, "test2@example.com")
    assert user is not None
```

---

## Resources
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [httpx Testing Guide](https://www.python-httpx.org/api/#testing)
- [Testing Best Practices](https://pragprog.com/titles/bsaapp/the-pragmatic-programmer-your-journey-to-mastery/)

---

**Last Updated**: April 15, 2026  
**Status**: Active
