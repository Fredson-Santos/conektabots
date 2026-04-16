# SKILL: Models & ORM (SQLAlchemy 2.0 + SQLModel)

**Purpose**: Guidelines for creating SQLAlchemy models with proper relationships, validations, and multi-tenancy patterns.

**Used for**: Defining database models, setting up ORM relationships, implementing business logic constraints, soft deletes.

---

## Model Structure Template

```python
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, TIMESTAMP, BYTEA
from sqlalchemy.orm import relationship
from sqlmodel import SQLModel, Field

class ResourceModel(SQLModel, table=True):
    """Resource description (what this entity represents)."""
    
    __tablename__ = "resource"
    
    # ✅ Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier"
    )
    
    # ✅ Multi-Tenancy (REQUIRED)
    tenant_id: UUID = Field(
        foreign_key="tenant.id",
        index=True,
        nullable=False,
        description="Tenant this resource belongs to"
    )
    
    # ✅ Business Fields
    nome: str = Field(
        min_length=1,
        max_length=255,
        nullable=False,
        description="Resource name"
    )
    descricao: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional description"
    )
    
    # ✅ Sensitive/Encrypted Fields (stored as BYTEA)
    chave_secreta_enc: Optional[bytes] = Field(
        default=None,
        sa_column=Column(BYTEA),
        description="Encrypted secret key (decrypt on access)"
    )
    
    # ✅ Status & Soft Delete
    ativo: bool = Field(
        default=True,
        nullable=False,
        index=True,
        description="Active/inactive status"
    )
    criado_em: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp"
    )
    atualizado_em: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp"
    )
    deletado_em: Optional[datetime] = Field(
        default=None,
        nullable=True,
        index=True,
        description="Soft delete timestamp"
    )
    
    # ✅ Relationships (lazy loading by default)
    tenant: Optional["Tenant"] = relationship(back_populates="resources")
    
    # ✅ Properties (virtual fields, no DB column)
    @property
    def is_deleted(self) -> bool:
        """Check if soft-deleted."""
        return self.deletado_em is not None
    
    @property
    def chave_secreta(self) -> Optional[str]:
        """Decrypt secret key on access (if needed)."""
        if self.chave_secreta_enc:
            from app.services.crypto_service import CryptoService
            crypto = CryptoService()
            return crypto.decrypt(self.chave_secreta_enc)
        return None
    
    # ✅ Methods
    def soft_delete(self) -> None:
        """Mark as deleted (soft delete)."""
        self.deletado_em = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore soft-deleted resource."""
        self.deletado_em = None
    
    def __repr__(self) -> str:
        return f"<Resource(id={self.id}, nome={self.nome}, ativo={self.ativo})>"
```

---

## Model Checklist

✅ **Structure**
- [ ] Inherits from `SQLModel` (not just `SQLAlchemy`)
- [ ] `__tablename__` set explicitly
- [ ] Docstring explaining the resource
- [ ] All fields typed (`field: Type`)

✅ **Multi-Tenancy**
- [ ] `tenant_id: UUID` as FK to tenant table
- [ ] NOT NULL constraint (every record belongs to tenant)
- [ ] Index on tenant_id for performance
- [ ] ON DELETE CASCADE (optional, depends on data model)

✅ **Timestamps**
- [ ] `criado_em: datetime` (creation, defaults to NOW)
- [ ] `atualizado_em: datetime` (update, defaults to NOW)
- [ ] `deletado_em: Optional[datetime]` (soft delete, nullable)

✅ **Encryption**
- [ ] Sensitive fields stored as `bytes` (BYTEA in DB)
- [ ] Property helper for transparent decryption (if small field)
- [ ] OR: Decrypt in service layer (if frequent access)
- [ ] Never expose encrypted bytes in API responses

✅ **Relationships**
- [ ] Use `relationship(back_populates=...)` for bidirectional
- [ ] Specify lazy loading strategy if high-volume queries
- [ ] Document which side is "parent" vs "child"

✅ **Validation**
- [ ] Use `Field(min_length, max_length)` for string constraints
- [ ] Use `Field(gt=0)` for numeric constraints
- [ ] Custom validators in service layer for business logic

✅ **Soft Delete Support**
- [ ] Has `deletado_em` field
- [ ] `is_deleted` property
- [ ] `soft_delete()` and `restore()` methods
- [ ] Queries filter with `WHERE deletado_em IS NULL`

---

## Relationship Patterns

### 1:N (One-to-Many)
```python
class Tenant(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    bots: List["Bot"] = relationship(back_populates="tenant", cascade="all, delete-orphan")

class Bot(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    tenant_id: UUID = Field(foreign_key="tenant.id")
    tenant: Tenant = relationship(back_populates="bots")
```

### N:N (Many-to-Many) - Through Table
```python
class TenantMarketplace(SQLModel, table=True):
    """Through table for tenant-marketplace many-to-many."""
    __tablename__ = "tenant_marketplace_association"
    
    id: UUID = Field(primary_key=True)
    tenant_id: UUID = Field(foreign_key="tenant.id", primary_key=True)
    marketplace_id: UUID = Field(foreign_key="marketplace.id", primary_key=True)

class Tenant(SQLModel, table=True):
    marketplaces: List["Marketplace"] = relationship(
        back_populates="tenants",
        secondary="tenant_marketplace_association"
    )
```

### Self-Referential (Hierarchical)
```python
class Category(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    parent_id: Optional[UUID] = Field(foreign_key="category.id")
    parent: Optional["Category"] = relationship(back_populates="children")
    children: List["Category"] = relationship(back_populates="parent")
```

---

## Normalization: Comma-Separated to 1:N Tables

### ❌ BAD (Denormalized)
```python
class Regra(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    origem: str = Field()  # "123,456,789" ← comma-separated!
    destino: str = Field()  # "111,222" ← problematic
```

### ✅ GOOD (Normalized)
```python
class Regra(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    origens: List["RegraOrigem"] = relationship(back_populates="regra", cascade="all, delete-orphan")
    destinos: List["RegraDestino"] = relationship(back_populates="regra", cascade="all, delete-orphan")

class RegraOrigem(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    regra_id: UUID = Field(foreign_key="regra.id")
    chat_id: str = Field()
    regra: Regra = relationship(back_populates="origens")

class RegraDestino(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    regra_id: UUID = Field(foreign_key="regra.id")
    chat_id: str = Field()
    regra: Regra = relationship(back_populates="destinos")
```

---

## Encryption in Models

### Pattern: Encrypted Field with Property
```python
from app.services.crypto_service import CryptoService

class Bot(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    
    # Store encrypted
    session_string_enc: Optional[bytes] = Field(
        default=None,
        sa_column=Column(BYTEA)
    )
    phone_enc: Optional[bytes] = Field(
        default=None,
        sa_column=Column(BYTEA)
    )
    
    # Property for transparent access (if small field)
    @property
    def session_string(self) -> Optional[str]:
        if self.session_string_enc:
            crypto = CryptoService()
            return crypto.decrypt(self.session_string_enc)
        return None
    
    # OR: Decrypt in service layer (recommended for frequent access)
```

---

## Query Helpers in Model Layer

### Static Method for Common Queries
```python
class Bot(SQLModel, table=True):
    
    @staticmethod
    def active_only_stmt(tenant_id: UUID):
        """Returns SELECT statement for active bots."""
        return (
            select(Bot)
            .where(Bot.tenant_id == tenant_id)
            .where(Bot.ativo == True)
            .where(Bot.deletado_em.is_(None))
        )
    
    @staticmethod
    def with_relationships_stmt(tenant_id: UUID):
        """Returns SELECT with eager-loaded relationships."""
        return (
            select(Bot)
            .where(Bot.tenant_id == tenant_id)
            .options(selectinload(Bot.regras), selectinload(Bot.agendamentos))
        )
```

---

## Validation & Business Logic

### ❌ DON'T: Validate in Model
```python
# BAD
class User(SQLModel, table=True):
    email: str = Field()
    
    def __init__(self, **data):
        if "@" not in data.get("email", ""):
            raise ValueError("Invalid email")
        super().__init__(**data)
```

### ✅ DO: Validate in Service or Schema
```python
# app/schemas/user.py
from pydantic import EmailStr

class UserCreate(BaseModel):
    email: EmailStr  # Pydantic validates email format
    password: str = Field(min_length=8, max_length=255)

# app/services/user_service.py
async def create_user(data: UserCreate) -> User:
    """Service validates business logic."""
    if await user_exists(data.email):
        raise ConflictError("User already exists")
    
    # Create model
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        tenant_id=...
    )
    await session.add(user)
    await session.commit()
    return user
```

---

## Index Strategy in Models

```python
class ImportantEntity(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    
    # Index frequently filtered columns
    tenant_id: UUID = Field(
        foreign_key="tenant.id",
        index=True  # ← Always index FK
    )
    
    # Index common query patterns
    status: str = Field(index=True)
    created_at: datetime = Field(index=True)
    
    # Composite index (if possible in SQLModel, else use migration)
    # In migration: CREATE INDEX idx_tenant_status ON table(tenant_id, status)
```

---

## Common Mistakes ⚠️

❌ **Mistake 1**: Missing tenant_id isolation
```python
# BAD
class Resource(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: str = Field()
    # No tenant_id → anyone can access all resources!

# GOOD
class Resource(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    tenant_id: UUID = Field(foreign_key="tenant.id", index=True)
    name: str = Field()
```

❌ **Mistake 2**: Storing plaintext secrets
```python
# BAD
class ApiKey(SQLModel, table=True):
    key: str = Field()  # Plaintext in database ⚠️

# GOOD
class ApiKey(SQLModel, table=True):
    key_enc: bytes = Field(sa_column=Column(BYTEA))  # Encrypted
    
    @property
    def key(self) -> str:
        return decrypt(self.key_enc)
```

❌ **Mistake 3**: Denormalized comma-separated values
```python
# BAD
chats: str = Field()  # "123,456,789" — fragile, hard to query

# GOOD
chats: List["Chat"] = relationship()  # Normalized, queryable
```

❌ **Mistake 4**: Hard delete instead of soft delete
```python
# BAD
session.delete(record)  # Hard delete — no recovery

# GOOD
record.soft_delete()  # Soft delete with timestamp
```

---

## Testing Models

```python
# tests/test_models.py
import pytest
from uuid import uuid4

def test_bot_model_structure():
    """Validate Bot model required fields."""
    bot = Bot(
        id=uuid4(),
        tenant_id=uuid4(),
        nome="Test Bot",
        ativo=True,
    )
    
    assert bot.nome == "Test Bot"
    assert bot.ativo == True
    assert bot.is_deleted == False

def test_soft_delete():
    """Test soft delete functionality."""
    bot = Bot(id=uuid4(), tenant_id=uuid4(), nome="Bot")
    bot.soft_delete()
    
    assert bot.is_deleted == True
    assert bot.deletado_em is not None

def test_encrypted_field():
    """Test encryption/decryption of sensitive fields."""
    # Requires service mocking
    pass
```

---

## Resources
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [SQLAlchemy ORM Guide](https://docs.sqlalchemy.org/en/20/orm/)
- [Relationship Patterns](https://docs.sqlalchemy.org/en/20/orm/relationship_api.html)

---

**Last Updated**: April 15, 2026  
**Status**: Active
