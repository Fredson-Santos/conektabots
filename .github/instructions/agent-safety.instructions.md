---
description: "Use when: working with any file operations, code modifications, or any task in this project. Agent safety rules to prevent accidental deletions, security vulnerabilities, and code degradation."
name: "Agent Safety & Integrity Rules"
applyTo: "**"
---

# 🚫 Agent Safety & Integrity Rules

**CRITICAL:** These are non-negotiable rules. Violations can break the project or compromise security.

---

## 1️⃣ DELETE PROTECTION (HARD RULES)

### ❌ NEVER Delete These Folders

These are **COMPLETELY OFF-LIMITS**. Deleting them will destroy the project:

```
.git/                    # VERSION CONTROL — contains entire project history
.agents/                 # AGENT CONFIGURATION — custom agents and skills
.github/                 # WORKFLOW & CUSTOMIZATION — CI/CD, instructions, hooks
.project/                # PROJECT METADATA — roadmap, state, changelog
.vscode/                 # IDE CONFIGURATION — VS Code settings
```

### ❌ NEVER Delete These Critical Files

- `alembic.ini` — Database migration config
- `requirements.txt` — Python dependencies
- `Dockerfile` — Container build
- `docker-compose.yml` — Service orchestration
- `main.py` — FastAPI entry point
- `.env.example` — Environment template
- `README.md` — Project documentation

### ❌ NEVER Hard-Delete These Folder Trees

Even if they seem "old" or "unused", these contain active data:

- `supabase/migrations/` — Database schema history
- `alembic/versions/` — Alembic migration history
- `tests/` — Test suite (even if some fail)
- `worker/` — Background job workers
- `app/core/` — Core application logic
- `app/models/` — ORM models

**Action Rule**: 
- ✅ Can modify files inside these folders
- ✅ Can add/refactor code
- ❌ Cannot DELETE the folder itself

### ❌ NEVER Delete Without Explicit Permission

Before ANY delete operation:
1. **STOP and ask the user**: "I'm about to delete [PATH]. Is this intentional?"
2. **Wait for confirmation** — do not proceed without explicit "yes"
3. **Backup first** — mention what will be deleted
4. **Never delete during refactoring** — separate concerns

**Example (CORRECT)**:
```
❌ User: "Clean up old files"
Me: I found 5 files to remove. Before I delete:
    - scripts/old_telethon_bot.py (180 lines, unused)
    - templates/index.html (9 files in folder)
    Should I proceed? [Y/N]
```

**Example (WRONG)**:
```
❌ User: "Clean up old files"
Me: [Silently deletes entire scripts/ folder]
User: "WAIT that had important stuff!"
```

---

## 2️⃣ SECURITY PROTECTION (HARD RULES)

### 🔒 Multi-Tenant Isolation — NEVER Bypass

Every database operation MUST enforce tenant isolation:

```python
# ❌ WRONG — Exposes all data
async def get_bots(session: AsyncSession):
    result = await session.execute(select(Bot))
    return result.scalars().all()

# ✅ CORRECT — Filters by tenant
async def get_bots(session: AsyncSession, tenant_id: UUID):
    result = await session.execute(
        select(Bot).where(Bot.tenant_id == tenant_id)
    )
    return result.scalars().all()
```

**Rules**:
- ✅ Always include `WHERE tenant_id = ?` in queries
- ✅ Always call `get_current_tenant()` in endpoints
- ❌ Never return data without tenant filter
- ❌ Never bypass RLS policies

### 🔐 Encryption — NEVER Store Plaintext Secrets

Sensitive fields MUST be encrypted:

```python
# ❌ WRONG — Plaintext storage
class Marketplace(Base):
    api_key: str  # EXPOSED!

# ✅ CORRECT — Encrypted field
class Marketplace(Base):
    api_key_encrypted: bytes  # Stored as encrypted
    
    @property
    def api_key(self):
        """Decrypt on read"""
        return decrypt_field(self.api_key_encrypted)
```

**Sensitive Fields**:
- User passwords (must be bcrypt hashed)
- Bot credentials (api_id, api_hash, phone, session_string)
- Marketplace API keys
- Refresh tokens
- 3rd-party service credentials

**Rules**:
- ✅ Hash passwords with bcrypt
- ✅ Encrypt API keys with AES-256
- ✅ Use `CryptoService` for encryption/decryption
- ❌ Never store plaintext secrets in code or DB
- ❌ Never log passwords or tokens

### 🔑 Secrets Management — NEVER Hardcode

```python
# ❌ WRONG — Hardcoded!
JWT_SECRET = "my-secret-key-123"

# ✅ CORRECT — From environment
JWT_SECRET = os.getenv("JWT_SECRET", "dev-key-change-in-prod")
```

**Rules**:
- ✅ All secrets from `.env` (via `os.getenv()`)
- ✅ `.env` in `.gitignore` (never committed)
- ❌ No hardcoded API keys, passwords, or tokens
- ❌ No secrets in code comments
- ❌ No secrets in error messages or logs

### 🔐 RBAC & Authorization — NEVER Skip Permission Checks

```python
# ❌ WRONG — No permission check
@router.delete("/bots/{bot_id}")
async def delete_bot(bot_id: UUID, session: AsyncSession):
    await session.delete(...)  # Anyone can delete!

# ✅ CORRECT — Permission enforced
@router.delete("/bots/{bot_id}")
async def delete_bot(
    bot_id: UUID,
    session: AsyncSession,
    user: User = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
    role: str = Depends(require_role(["owner", "admin"])),
):
    # Only owner/admin can delete
    bot = await session.get(Bot, bot_id)
    assert bot.tenant_id == tenant_id  # Verify ownership
    await session.delete(bot)
```

**Rules**:
- ✅ All endpoints require authentication (JWT)
- ✅ Protected endpoints require role check
- ✅ Verify tenant ownership before data access
- ❌ No public endpoints with data access
- ❌ No skipped permission checks "for now"

### 🚫 Input Validation — NEVER Trust User Input

```python
# ❌ WRONG — No validation
def create_bot(name: str):
    bot = Bot(name=name)  # What if name is 10MB?

# ✅ CORRECT — Validated with Pydantic
class BotCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

@router.post("/bots")
async def create_bot(dto: BotCreate, ...):
    # Pydantic validates before function runs
    bot = Bot(**dto.dict())
```

**Rules**:
- ✅ Use Pydantic schemas for all input validation
- ✅ Define field constraints (min/max, pattern, enum)
- ✅ Validate email, UUID, dates
- ❌ No trusting raw request data
- ❌ No `eval()` or dynamic code execution

---

## 3️⃣ CODE QUALITY (SOFT RULES with HARD CORE)

### 📝 Type Hints — ALWAYS Use

```python
# ❌ WRONG — No types
def create_bot(data):
    return data

# ✅ CORRECT — Full type hints
from typing import Optional
from uuid import UUID
from app.schemas.bot import BotCreate, BotResponse
from sqlalchemy.ext.asyncio import AsyncSession

async def create_bot(
    session: AsyncSession,
    user_id: UUID,
    tenant_id: UUID,
    dto: BotCreate,
) -> BotResponse:
    """Create a new bot in the tenant."""
    ...
```

**Rules**:
- ✅ Type hint all function parameters
- ✅ Type hint return values
- ✅ Use `Optional[T]` for nullable fields
- ✅ Import types from `typing` module
- ❌ No bare `def function(x):` without types
- ⚠️ `Any` only when absolutely necessary

### 🔄 Async/Await Consistency — ALL IO Operations Must Be Async

```python
# ❌ WRONG — Blocking call
def get_bots():
    return session.query(Bot).all()  # BLOCKS!

# ✅ CORRECT — Async throughout
async def get_bots(session: AsyncSession) -> List[Bot]:
    result = await session.execute(select(Bot))
    return result.scalars().all()
```

**Rules**:
- ✅ Async for all database operations (`.execute()`, `.flush()`, etc.)
- ✅ Async for all HTTP calls
- ✅ Async for file I/O if heavy
- ❌ No synchronous database queries
- ❌ No blocking operations in async functions
- ❌ No `.query()` (use `.execute(select(...))` instead)

### ❌ Error Handling — ALWAYS Handle Exceptions

```python
# ❌ WRONG — Silently fails
try:
    result = await session.execute(...)
except:
    pass  # What happened?!

# ✅ CORRECT — Proper handling
try:
    result = await session.execute(...)
except IntegrityError:
    raise HTTPException(status_code=409, detail="Resource already exists")
except SQLAlchemyError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Database error")
```

**Rules**:
- ✅ Catch specific exceptions, not bare `except:`
- ✅ Log errors with context
- ✅ Return proper HTTP status codes (400, 403, 404, 500)
- ✅ Don't expose stack traces to client
- ❌ Never `except: pass`
- ❌ Never expose internal error messages

### 📚 Code Structure — FOLLOW Project Architecture

**HARD**: Do NOT deviate from established patterns:

```
app/
├── core/        → Configuration, database, dependencies
├── models/      → SQLAlchemy ORM models (1 file per entity)
├── schemas/     → Pydantic DTOs (1 file per entity)
├── services/    → Business logic (1 file per entity)
└── routers/     → REST endpoints (1 file per resource)
```

**Rules**:
- ✅ Business logic goes in `services/`, not routers
- ✅ Data models in `models/`, schemas in `schemas/`
- ✅ One file per entity (e.g., `bot.py` contains Bot model, schema, service)
- ✅ Dependency injection for services
- ❌ No circular imports
- ❌ No "God" files with everything

### 🎯 Variable Naming — Use Clear, Descriptive Names

```python
# ❌ WRONG
x = get_data()
d = x.filter(lambda i: i > 5)

# ✅ CORRECT
active_users = get_users()
filtered_users = [u for u in active_users if u.is_active]
```

**Rules**:
- ✅ Use English variable names
- ✅ Use snake_case for variables/functions
- ✅ Use PascalCase for classes
- ✅ Use UPPER_CASE for constants
- ❌ No single-letter variables (except `i` in loops)
- ❌ No abbreviations unless obvious (e.g., `id`, `msg`)

---

## 4️⃣ TESTING (SOFT RULES with HARD Review)

### ✅ New Features — MUST Have Tests

```python
# When adding a new router endpoint:
# 1. Add test file: tests/test_new_feature.py
# 2. Test happy path
# 3. Test error cases (400, 403, 404)
# 4. Test validation (invalid input)
# 5. Run: pytest tests/test_new_feature.py -v

# Before merge: ALL tests pass (pytest tests/ -v)
```

**Rules**:
- ✅ Add tests for new endpoints
- ✅ Test both success and error paths
- ✅ Test validation cases
- ✅ Run suite before merging: `pytest tests/ -v`
- ⚠️ If test fails: Fix code, not test
- ❌ Never skip tests with `@pytest.mark.skip`
- ❌ Never modify existing tests to make them pass (unless test is wrong)

### 🧪 Fixture Isolation — ALWAYS Use Fresh Data

```python
# ✅ CORRECT — Each test gets fresh fixture
@pytest.mark.asyncio
async def test_create_bot(session: AsyncSession):
    # session is fresh for this test
    bot = await create_bot(session, ...)
    assert bot.id is not None

@pytest.mark.asyncio
async def test_delete_bot(session: AsyncSession):
    # Different session, no interference
    ...
```

**Rules**:
- ✅ Use pytest fixtures for test data
- ✅ Fixtures auto-cleanup (rollback on test end)
- ✅ No test interdependencies
- ❌ No shared state between tests
- ❌ No hardcoded test data

---

## 5️⃣ DOCUMENTATION (SOFT RULES with HARD Essentials)

### 📖 Docstrings — ADD For Public Functions

```python
# ❌ MINIMAL
def create_bot(session, user_id, tenant_id, dto):
    ...

# ✅ BETTER
async def create_bot(
    session: AsyncSession,
    user_id: UUID,
    tenant_id: UUID,
    dto: BotCreate,
) -> BotResponse:
    """Create a new bot in the tenant.
    
    Args:
        session: Database session
        user_id: Owner user ID
        tenant_id: Tenant to create bot in
        dto: Bot creation data (name, description, etc.)
    
    Returns:
        Created BotResponse with generated ID
    
    Raises:
        HTTPException: If bot name already exists in tenant
    """
    ...
```

**Rules**:
- ✅ Add docstrings to public functions/classes
- ✅ Include: description, Args, Returns, Raises
- ✅ Use standard format (Google style or similar)
- ⚠️ Internal functions can skip if obvious
- ❌ Don't document `self` or `cls`
- ❌ Don't document private methods extensively

### 🔍 Code Comments — When Logic is NOT Obvious

```python
# ❌ UNNECESSARY
x = 5  # Set x to 5

# ✅ NECESSARY
# Using cost_factor=12 for bcrypt: slower (100ms/hash) but secure
# against GPU attacks. Balance between security and UX.
salt = bcrypt.gensalt(rounds=12)
```

**Rules**:
- ✅ Comment WHY, not WHAT
- ✅ Explain non-obvious business logic
- ✅ Explain performance trade-offs
- ❌ Don't comment obvious code
- ❌ Don't leave TODO/FIXME without context

---

## 6️⃣ CONFIG FILES (HARD RULES)

### ⚙️ `.env` Files

```python
# ❌ NEVER commit .env
# ✅ DO commit .env.example with placeholders

# .env.example:
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
JWT_SECRET=<generate-random-32-chars>
DB_ENCRYPTION_KEY=<generate-random-32-chars>
REDIS_URL=redis://localhost:6379
```

**Rules**:
- ✅ `.env` in `.gitignore`
- ✅ `.env.example` in repository (no actual secrets)
- ✅ Document all required variables
- ❌ Never commit actual `.env`
- ❌ Never put secrets in code

### 📋 `requirements.txt`

**Before modifying**:
1. Ask user: "I'm updating requirements.txt to add/remove [PACKAGE]. OK?"
2. Wait for approval
3. Run: `pip install -r requirements.txt` to verify
4. Test that app still starts

**Rules**:
- ✅ Pin versions to avoid surprises
- ✅ Keep updated with `pip freeze`
- ✅ Test after changes
- ❌ Don't add unused dependencies
- ❌ Don't remove deps without checking usage

### 🐳 `docker-compose.yml`, `Dockerfile`

**Before modifying**:
1. Ask user first
2. Validate syntax: `docker-compose config`
3. Note: Changes affect deployment

**Rules**:
- ✅ Always ask before changes
- ✅ Validate syntax
- ⚠️ Changes affect CI/CD pipelines
- ❌ Don't remove services
- ❌ Don't change ports without coordination

---

## 7️⃣ GIT WORKFLOW & COMMITS (HARD RULES)

### 📝 EVERY Task Completed = Detailed Git Commit

**Rule**: After completing ANY task or feature, commit with detailed message.

```bash
# ❌ WRONG — Vague, unhelpful commits
git commit -m "fixes"
git commit -m "update"
git commit -m "changes"

# ✅ CORRECT — Detailed, descriptive commits
git commit -m "feat: Add marketplace integration endpoint

- Implement POST /marketplaces for linking Shopee/ML/Amazon APIs
- Add MarketplaceCreate schema with validation
- Store encrypted API credentials in database
- Add RLS policies for tenant isolation
- Tests: 5 passing (create, validate, security)
- Security: Multi-tenant check + role-based access

Files changed:
- app/routers/marketplaces.py (new route)
- app/services/marketplace_service.py (logic)
- app/schemas/marketplace.py (validation)
- supabase/migrations/008_add_marketplaces.sql (schema)
- tests/test_marketplaces.py (5 new tests)"
```

### MUST Include Commit Format

**Structure**: `<type>: <subject>`

Then detailed body:

```
<type>: <subject line — max 50 chars>

<blank line>

<detailed description — explain WHAT and WHY>

- Bullet points for clarity
- What changed
- Why it changed
- Any breaking changes
- Security implications

Files:
- file1.py
- file2.py

Tests:
- X tests added
- Y tests passing
```

### Commit Types

```
feat:     → New feature
fix:      → Bug fix
refactor: → Code restructure (no behavior change)
test:     → Test additions/changes
docs:     → Documentation only
security: → Security fixes
perf:     → Performance optimization
ci:       → CI/CD changes
chore:    → Dependencies, config (no logic change)
```

### Example Commits by Task Type

**Example 1: Backend Feature**
```bash
git commit -m "feat: Implement bot credential encryption

- Add CryptoService for AES-256 encryption
- Encrypt bot.api_hash, bot.session_string on save
- Decrypt on read via property accessor
- Add tests: encryption/decryption round-trip
- Security: Keys from environment, never hardcoded

Files: app/services/crypto_service.py, app/models/bot.py, tests/test_crypto.py

Tests: 6 new tests, all passing ✅"
```

**Example 2: Bug Fix**
```bash
git commit -m "fix: Prevent cross-tenant bot access in list endpoint

Root cause: Query missing tenant_id filter in BotService.get_bots()
Impact: Tenant A could see Tenant B's bots via GET /bots
Fix: Add WHERE tenant_id = current_tenant_id

Affected: app/services/bot_service.py (1 line)
Tests: test_tenant_isolation.py now passes ✅

Security: HIGH — multi-tenant isolation
Backport candidate: Yes (affects v2.0 stable)"
```

**Example 3: Database Migration**
```bash
git commit -m "feat: Normalize bot rules to separate table

Migration: Add bot_origins table (1:N relationship)
Reason: Support multiple origin chats per rule (previously comma-separated)
Backward compat: Yes — old rules still work until migration runs
Data: 127 existing rules migrated, 0 data loss

Files:
- alembic/versions/003_normalize_bot_rules.py
- app/models/bot.py (add relationship)
- app/services/bot_service.py (update queries)
- tests/test_migration_normalization.py (new)

Migration tested: upgrade ✅ + downgrade ✅
Tests: 8 passing ✅"
```

**Example 4: Security Fix**
```bash
git commit -m "security: Add RBAC enforcement to settings endpoint

Vulnerability: Editor role could modify tenant billing settings (owner-only)
Impact: Data leak risk, unauthorized privilege escalation
Fix: Add role check to PATCH /tenants/{id}/settings

Before:
@router.patch('/tenants/{id}/settings')
async def update_settings(dto, user, tenant_id):  # ❌ No role check

After:
@router.patch('/tenants/{id}/settings')
async def update_settings(dto, user, tenant_id, role=Depends(require_role('owner'))):  # ✅

Files: app/routers/tenants.py (1 endpoint)
Tests: test_rbac.py — editor now gets 403 ✅

Severity: HIGH
Affects: All tenants with editor members
CVE: N/A (internal discovery)
Backport: Yes (immediate patch)"
```

### RULES for Commits

**HARD Rules**:
- ✅ MUST commit after every meaningful task
- ✅ Commit message MUST explain WHY, not just WHAT
- ✅ Commit message MUST include files changed
- ✅ Commit message MUST include test status (passing/failing)
- ✅ Security-related commits MUST mention impact
- ✅ Large refactors MUST explain reasoning
- ❌ Never commit with message like "fix" or "update"
- ❌ Never commit broken tests
- ❌ Never commit without tests for new features
- ❌ No commits that break backward compatibility without mentioning

### Before Committing: Checklist

- [ ] All tests pass (`pytest tests/ -v`)
- [ ] No uncommitted changes (git status clean)
- [ ] Code follows project standards
- [ ] Commit message is descriptive
- [ ] No secrets committed (verify with `git diff --staged`)
- [ ] Files match the change description
- [ ] Breaking changes documented (if any)

**Example Check**:
```bash
# Verify everything before committing
pytest tests/ -v                    # All pass? ✅
git status                          # Clean? ✅
git diff --staged                   # Review changes? ✅
git log --oneline -5                # Last commits make sense? ✅

# Then commit
git commit -m "feat: Your detailed message here"
```

---

## ✅ Checklist: Before Every Operation

Use this before executing ANY code modification:

- [ ] I'm NOT deleting a protected folder (check list above)
- [ ] I'm NOT hardcoding secrets
- [ ] Multi-tenant queries filter by `tenant_id`
- [ ] All async operations use `await`
- [ ] Functions have type hints
- [ ] Error handling is appropriate
- [ ] Sensitive data is encrypted/hashed
- [ ] Tests are added for new features
- [ ] No `except:` or bare exceptions
- [ ] I asked user before destructive operations
- [ ] Commit message is detailed and descriptive (after task)

**After Task Completion**:
- [ ] Run tests: `pytest tests/ -v`
- [ ] Commit with detailed message: `git commit -m "type: subject\n\nbody"`
- [ ] Push changes: `git push origin feature-branch`

**If ANY box is unchecked → STOP and ask for clarification**

---

## 🚨 Emergency: If You're About to Break Something

**STOP. DO THIS:**

1. **State your intent clearly**: "I'm about to modify [FILE] to [ACTION]"
2. **Explain the impact**: "This will affect [COMPONENTS]"
3. **Ask for permission**: "Should I proceed? [Y/N]"
4. **Wait for user confirmation** before proceeding
5. **Create backup reference**: Show what was there before

---

## 🔗 Related Documentation

- [Project Workflow Rules](./project-workflow.instructions.md) — Roadmap alignment + changelog updates
- [Agents Configuration](./../agents/AGENTS.md) — Agent setup rules
- [Security Audit Skill](./../skills/security-audit/SKILL.md) — Security procedures
- [Project Roadmap](./../../../.project/roadmap.md) — Development phases
- [API Design Agent](./../agents/api-documenter.agent.md) — Endpoint patterns

---

**Last Updated**: April 15, 2026  
**Severity**: 🔴 CRITICAL — All agents must follow  
**Violations**: Report to security team immediately  
**Git Discipline**: Mandatory detailed commits after each task (Section 7️⃣)
