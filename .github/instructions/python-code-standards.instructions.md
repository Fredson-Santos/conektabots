---
description: "Use when: writing or modifying Python files in this project. Enforce code quality, security patterns, and architectural consistency across FastAPI backend."
name: "Python Code Standards & Best Practices"
applyTo: "**/*.py"
---

# 🐍 Python Code Standards for ConektaBots

**Applies to**: All Python files in the project  
**Focus**: Code quality, security, architecture, testing

---

## Architecture Compliance

### ✅ MUST Follow Project Structure

```
app/
├── core/config.py        ← Configuration & settings
├── core/database.py      ← Database engine & session
├── core/deps.py          ← Dependency injection
├── core/security.py      ← JWT, encryption, hashing
├── models/bot.py         ← SQLAlchemy ORM models
├── schemas/bot.py        ← Pydantic DTOs
├── services/bot.py       ← Business logic
└── routers/bots.py       ← FastAPI endpoints
```

**Rules**:
- ✅ Business logic ONLY in `services/`
- ✅ Data validation ONLY in `schemas/`
- ✅ Database queries ONLY in models + services
- ✅ HTTP handling ONLY in `routers/`
- ❌ NO logic in routers (routers just call services)
- ❌ NO routers importing from other routers

### Example: Adding New Bot Feature

**WRONG** (all in router):
```python
# ❌ app/routers/bots.py — DO NOT DO THIS
@router.post("/bots")
async def create_bot(name: str, session: AsyncSession):
    # Business logic in router!
    if len(name) < 2:
        raise HTTPException(...)
    bot = Bot(name=name)
    await session.add(bot)
    await session.commit()
    return bot
```

**RIGHT**:
```python
# ✅ app/schemas/bot.py
class BotCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)

# ✅ app/services/bot.py
class BotService:
    async def create_bot(self, session: AsyncSession, tenant_id: UUID, dto: BotCreate) -> Bot:
        """Create new bot with validation."""
        bot = Bot(name=dto.name, tenant_id=tenant_id)
        await session.add(bot)
        await session.commit()
        return bot

# ✅ app/routers/bots.py
@router.post("/bots", response_model=BotResponse)
async def create_bot(
    dto: BotCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """Create a new bot."""
    service = BotService(session)
    bot = await service.create_bot(session, tenant_id, dto)
    return bot
```

---

## Async/Await Patterns

### ✅ MUST Use Async/Await for All IO

```python
# ❌ WRONG — Blocking
def get_users():
    return session.query(User).all()  # BLOCKS entire app!

# ✅ CORRECT — Async
async def get_users(session: AsyncSession) -> List[User]:
    result = await session.execute(select(User))
    return result.scalars().all()
```

### ✅ MUST Use `select()` for Queries

```python
# ❌ OLD style (SQLAlchemy 1.3) — don't use
users = session.query(User).filter(User.active == True).all()

# ✅ NEW style (SQLAlchemy 2.0) — use this
result = await session.execute(
    select(User).where(User.active == True)
)
users = result.scalars().all()
```

### ✅ MUST Await All Async Calls

```python
# ✅ CORRECT pattern
async def fetch_data():
    # Await database calls
    result = await session.execute(select(User))
    users = result.scalars().all()
    
    # Await HTTP requests (if using httpx)
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
    
    # Await service method calls
    service = BotService(session)
    bot = await service.create_bot(...)
    
    return users, bot
```

---

## Type Hints & Validation

### ✅ MUST Use Type Hints

```python
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# ❌ WRONG
def process_user(user, session):
    return user

# ✅ CORRECT
async def process_user(
    user: User,
    session: AsyncSession,
) -> UserResponse:
    """Process user with type hints."""
    ...
```

### ✅ MUST Use Pydantic for Input Validation

```python
from pydantic import BaseModel, Field, EmailStr

# ✅ CORRECT — All validation centralized
class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    name: str = Field(..., min_length=2, max_length=255)
    age: Optional[int] = Field(None, ge=0, le=150)

# In router:
@router.post("/users")
async def create_user(dto: UserCreate, ...):
    # dto is already validated by Pydantic
    user = User(**dto.dict())
    ...
```

### ✅ MUST Define Response Models

```python
# ✅ CORRECT — Define response schema
class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # Convert SQLAlchemy → Pydantic

# In router:
@router.get("/users/{id}", response_model=UserResponse)
async def get_user(id: UUID, ...):
    ...
```

---

## Security Patterns

### ✅ MUST Check Authorization & Multi-Tenancy

```python
# ✅ CORRECT — full security stack
@router.delete("/bots/{bot_id}")
async def delete_bot(
    bot_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),           # ← Auth check
    tenant_id: UUID = Depends(get_current_tenant),    # ← Tenant isolation
    role: str = Depends(require_role("owner", "admin")),  # ← Role check
):
    """Delete bot - only owner/admin can delete."""
    
    # Verify bot exists and belongs to tenant
    bot = await session.get(Bot, bot_id)
    if not bot or bot.tenant_id != tenant_id:
        raise HTTPException(status_code=404)
    
    # Delete (soft delete via trigger)
    bot.deletado_em = datetime.utcnow()
    await session.commit()
    return {"status": "deleted"}
```

### ✅ MUST Encrypt Sensitive Fields

```python
from app.services.crypto_service import CryptoService

# In service:
class BotService:
    async def create_bot(self, session: AsyncSession, dto: BotCreate) -> Bot:
        crypto = CryptoService(session)
        
        # Encrypt sensitive field
        encrypted_credentials = crypto.encrypt(dto.api_hash)
        
        bot = Bot(
            name=dto.name,
            credentials_encrypted=encrypted_credentials,  # Store encrypted
        )
        await session.add(bot)
        await session.commit()
        return bot

# ✅ Never expose encrypted field directly
class BotResponse(BaseModel):
    id: UUID
    name: str
    # ❌ DON'T include: credentials_encrypted
    
    class Config:
        from_attributes = True
```

### ✅ MUST Filter Queries by Tenant

```python
# ❌ WRONG — Exposes all tenants' data!
async def get_user(user_id: UUID, session: AsyncSession):
    user = await session.get(User, user_id)
    return user

# ✅ CORRECT — Filter by tenant
async def get_user(
    user_id: UUID,
    session: AsyncSession,
    tenant_id: UUID = Depends(get_current_tenant),
):
    user = await session.get(User, user_id)
    if not user or user.tenant_id != tenant_id:
        raise HTTPException(status_code=404)
    return user

# ✅ BEST — RLS handles it automatically
# If RLS policy is correct, this alone works:
result = await session.execute(select(User).where(User.id == user_id))
user = result.scalar_one_or_none()
```

### ✅ MUST NOT Log Secrets

```python
# ❌ WRONG
logger.info(f"User {user.email} logged in with password {password}")

# ✅ CORRECT
logger.info(f"User {user.email} logged in successfully")

# ✅ CORRECT for debugging (dev only)
if settings.DEBUG:
    logger.debug(f"Auth token created for user {user.id}")
    # token value itself not logged, only that it was created
```

---

## Error Handling

### ✅ MUST Handle Exceptions Explicitly

```python
# ❌ WRONG — Bare except, hides errors
try:
    result = await session.execute(select(User))
except:
    pass  # Silent failure!

# ✅ CORRECT — Specific exceptions
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

try:
    user = User(email=dto.email, name=dto.name)
    await session.add(user)
    await session.commit()
except IntegrityError:
    # Email unique constraint violation
    raise HTTPException(
        status_code=409,
        detail="Email already registered"
    )
except SQLAlchemyError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(
        status_code=500,
        detail="Database error occurred"
    )
except Exception as e:
    # Unexpected error
    logger.exception(f"Unexpected error: {e}")
    raise HTTPException(
        status_code=500,
        detail="Internal server error"
    )
```

### ✅ MUST Return HTTP Status Codes

```python
# ✅ CORRECT status codes
@router.get("/users/{id}")
async def get_user(id: UUID, ...):
    user = await session.get(User, id)
    
    if not user:
        raise HTTPException(
            status_code=404,  # Not found
            detail="User not found"
        )
    
    return user

@router.post("/users")
async def create_user(dto: UserCreate, ...):
    try:
        user = User(**dto.dict())
        ...
    except IntegrityError:
        raise HTTPException(
            status_code=409,  # Conflict
            detail="Email already exists"
        )
    return user

# Status codes:
# 200 → Success
# 201 → Created
# 400 → Bad request (client error)
# 401 → Unauthorized (no auth)
# 403 → Forbidden (auth ok, permission denied)
# 404 → Not found
# 409 → Conflict
# 422 → Unprocessable entity (validation error - auto by Pydantic)
# 500 → Internal server error
```

---

## Naming Conventions

### ✅ Variables & Functions: `snake_case`

```python
# ✅ CORRECT
active_users = []
def get_active_users():
    pass

# ❌ WRONG
activeUsers = []
def GetActiveUsers():
    pass
```

### ✅ Classes: `PascalCase`

```python
# ✅ CORRECT
class UserService:
    pass

class AuthMiddleware:
    pass

# ❌ WRONG
class user_service:
    pass

class auth_middleware:
    pass
```

### ✅ Constants: `UPPER_CASE`

```python
# ✅ CORRECT
MAX_USERS_PER_TENANT = 1000
API_TIMEOUT_SECONDS = 30
DEFAULT_PAGE_SIZE = 20

# ❌ WRONG
max_users = 1000
api_timeout = 30
```

### ✅ Private/Internal: `_prefixed` or `__dunder`

```python
# ✅ CORRECT
class UserService:
    async def _validate_email(self, email: str) -> bool:
        """Internal validation - not part of public API."""
        ...
    
    def __init__(self):
        self.__private_key = "secret"

# ❌ WRONG — No leading underscore
class UserService:
    async def validate_email(self, email: str) -> bool:
        """Should be private!"""
        ...
```

---

## Testing Requirements

### ✅ MUST Write Tests for New Features

```python
# tests/test_bots.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.bot import Bot
from app.schemas.bot import BotCreate
from app.services.bot_service import BotService

@pytest.mark.asyncio
async def test_create_bot(session: AsyncSession):
    """Test bot creation."""
    service = BotService(session)
    dto = BotCreate(name="TestBot", description="Test")
    
    bot = await service.create_bot(session, dto)
    
    assert bot.id is not None
    assert bot.name == "TestBot"

@pytest.mark.asyncio
async def test_create_bot_invalid_name(session: AsyncSession):
    """Test validation rejects short names."""
    service = BotService(session)
    dto = BotCreate(name="A")  # Too short
    
    with pytest.raises(ValueError):
        await service.create_bot(session, dto)
```

### ✅ MUST Run Tests Before Committing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_bots.py::test_create_bot -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing
```

---

## Docstrings

### ✅ MUST Document Public Functions

```python
# ✅ CORRECT — Full docstring
async def create_bot(
    session: AsyncSession,
    tenant_id: UUID,
    dto: BotCreate
) -> Bot:
    """Create a new bot in the tenant.
    
    This function creates a new bot instance and associates it
    with the specified tenant. The bot credentials are encrypted
    before storage.
    
    Args:
        session: Database session for ORM operations
        tenant_id: UUID of the tenant that owns the bot
        dto: BotCreate schema with bot configuration
    
    Returns:
        Created Bot instance with generated ID
    
    Raises:
        HTTPException: If bot name already exists in tenant
        ValueError: If provided data is invalid
    
    Example:
        >>> dto = BotCreate(name="MyBot")
        >>> bot = await create_bot(session, tenant_id, dto)
        >>> print(bot.id)
    """
    ...
```

### ✅ Short Functions: Simple Docstrings OK

```python
# ✅ ACCEPTABLE for simple internal functions
async def _validate_email(email: str) -> bool:
    """Check if email format is valid."""
    return "@" in email and "." in email
```

---

## Import Organization

### ✅ MUST Follow Import Order

```python
# 1. Standard library
import os
import json
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# 2. Third-party
import sqlalchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI, Depends
from pydantic import BaseModel

# 3. Local imports
from app.core.config import settings
from app.core.deps import get_session, get_current_user
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.user_service import UserService
```

### ✅ MUST NOT Have Circular Imports

```
# ❌ WRONG — Circular dependency
app/models/bot.py imports from app/routers/bots.py
app/routers/bots.py imports from app/models/bot.py

# ✅ CORRECT — Unidirectional flow
routers → services → models ✓
models → routers ✗ (NEVER)
```

---

## Logging

### ✅ Use Structured Logging

```python
import logging

logger = logging.getLogger(__name__)

# ✅ CORRECT
logger.info(f"User {user_id} authenticated successfully")
logger.warning(f"Failed login attempt for email {email}")
logger.error(f"Database connection failed: {str(e)}")

# ❌ WRONG
print(f"User logged in")  # Use logger, not print
```

### ✅ Log Levels

```python
logger.debug("Entering function X")          # Development only
logger.info("User registration complete")     # Important events
logger.warning("Deprecated API used")         # Actions to address
logger.error("Database connection failed")    # Serious problems
logger.critical("API key compromised!")       # Immediate action needed
```

---

## Common Pitfalls to Avoid

| ❌ WRONG | ✅ CORRECT |
|---------|-----------|
| `session.query(...)` | `await session.execute(select(...))` |
| `def function():` (no types) | `async def function() -> Type:` (with types) |
| `except:` | `except SpecificError as e:` |
| `print()` | `logger.info()` |
| `if x == True:` | `if x:` |
| `for i in range(len(list)):` | `for item in list:` |
| `x = None; if x is not None:` | `if x:` (if safe) |
| Hardcoded config | `os.getenv("CONFIG")` |
| No validation | Pydantic schema |
| No error handling | Try/except with specific exceptions |

---

## Pre-Commit Checklist

Before pushing code:

- [ ] Type hints on all functions
- [ ] No bare `except:` statements
- [ ] Async/await used correctly
- [ ] No hardcoded secrets/config
- [ ] Tenant ID checked in queries
- [ ] Sensitive data encrypted/hashed
- [ ] Tests written & passing
- [ ] Docstrings added
- [ ] No circular imports
- [ ] Logging instead of print
- [ ] Proper HTTP status codes

---

## Resources

- [FastAPI Best Practices](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Validation](https://docs.pydantic.dev/)
- [Python Type Hints](https://peps.python.org/pep-0484/)

---

**Last Updated**: April 15, 2026  
**Applies To**: All Python files (`**/*.py`)  
**Severity**: 🟡 HIGH — Enforce during code review
