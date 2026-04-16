# ConektaBots - Agent Collaboration Conventions 🤖

**Purpose**: Define rules, patterns, and best practices for multi-agent development and handoffs across sessions.

**Audience**: GitHub Copilot (multi-session), future developers, and AI collaborators on this project.

---

## 📋 Session Management

### Session Goals
Each session should have explicit goals:
1. **Define** - What problem are we solving?
2. **Research** - What context do we need?
3. **Implement** - What code changes?
4. **Verify** - Did it work?
5. **Document** - What changed?

### Session Handoff Protocol

#### Before End of Session
- [ ] Update `.project/state.md` with current snapshot
- [ ] Append major changes to `.project/changelog.md`
- [ ] Update `.project/roadmap.md` if phase changed
- [ ] Commit to git with clear message: `[Fase X] Description`
- [ ] Leave next session notes in `.project/state.md` under "Next Priorities"

#### At Start of New Session
- [ ] Read `.project/state.md` for current status
- [ ] Check `.project/roadmap.md` for phase alignment
- [ ] Review `.project/changelog.md` for recent changes
- [ ] Verify git status (clean working directory)
- [ ] Ask user: "What would you like to work on?"

---

## 🏗 Architecture Principles

### 1. Maintain Clean Separation
- **Controllers (routers/)** - HTTP request handling only
- **Services** - Business logic, no HTTP concerns
- **Models** - Data schema definition, no business logic
- **Schemas** - Pydantic validation, serialization helpers

**Anti-Pattern**: Business logic in routers or database queries in schemas

### 2. Async-First Design
- All I/O operations (DB, API calls, file ops) must be `async`
- Use `await` for database queries
- Never `time.sleep()` - use async alternatives
- Configure pytest with `pytest-asyncio` for tests

**Example**:
```python
@router.get("/items")
async def list_items(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Item))
    return result.scalars().all()
```

### 3. Security-By-Default
- All endpoints require authentication token
- Use `get_current_user()` dependency
- Check tenant_id for multi-tenancy
- Encrypt sensitive fields (credentials, API keys)
- Use RLS policies on database

**Required Checks**:
```python
async def get_endpoint(
    user: User = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    # User + tenant verified at dependency level
```

### 4. Error Handling Standards

**Always return proper HTTP status codes**:
- 200 OK - Success
- 201 Created - Resource created
- 204 No Content - Success, no body
- 400 Bad Request - Invalid input
- 401 Unauthorized - Missing/invalid auth
- 403 Forbidden - Auth valid, but access denied
- 404 Not Found - Resource not found
- 422 Unprocessable Entity - Validation error
- 429 Too Many Requests - Rate limit exceeded
- 500 Internal Server Error - Server fault

**Use FastAPI's HTTPException**:
```python
from fastapi import HTTPException

if not resource:
    raise HTTPException(status_code=404, detail="Not found")
```

### 5. Database Transactions
- Use SQLAlchemy async sessions
- Explicit commit/rollback
- Use context managers for cleanup

```python
async with async_session() as session:
    # Transaction auto-rolls back on error
    await session.execute(update_stmt)
    await session.commit()
```

---

## 📝 Code Style Conventions

### Python Style (PEP 8)
- Line length: 100 characters (soft limit)
- Indentation: 4 spaces
- Naming:
  - `snake_case` for functions/variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants
  - Prefix private methods with `_`

### File Organization
```
module/
├── __init__.py        # Exports key symbols
├── models.py          # SQLAlchemy models (if small)
├── schemas.py         # Pydantic schemas
├── services.py        # Business logic
├── routers.py         # FastAPI routes
└── utils.py           # Helper functions
```

### Docstring Convention (Google style)
```python
def process_message(msg: Message, target_id: UUID) -> bool:
    """Process messages according to filtering rules.
    
    Applies forwarding rules to determine if message should be sent
    to target marketplace. Handles encryption/decryption transparently.
    
    Args:
        msg: Message object with content, sender, timestamp
        target_id: Target bot/marketplace UUID
        
    Returns:
        True if message matches rules and sent, False otherwise
        
    Raises:
        QuotaExceeded: If tenant exceeded message quota
        InvalidCredentials: If marketplace credentials invalid
    """
```

### Type Hints (Required)
```python
from typing import Optional, List
from uuid import UUID

async def get_user(user_id: UUID) -> Optional[User]:
    """Fetch user by ID."""
    ...

async def list_items(limit: int = 10) -> List[ItemSchema]:
    """Fetch paginated items."""
    ...
```

---

## 🧪 Testing Standards

### Test File Structure
```
tests/
├── conftest.py              # Shared fixtures
├── test_auth.py             # Authentication tests
├── test_services.py         # Service unit tests
├── test_routers.py          # Router integration tests
└── test_security.py         # Security/RLS tests
```

### Fixture Reuse
- Use `conftest.py` for shared fixtures
- Fixtures for: engine, session, user, tenant, bot
- Prefix fixtures with module name: `auth_token_fixture`, `bot_fixture`

### Test Naming
```python
# Pattern: test_<function>_<scenario>_<expected_result>

def test_authenticate_valid_credentials_returns_token():
    """Test successful login with valid credentials."""
    ...

def test_authenticate_invalid_password_raises_401():
    """Test login with wrong password."""
    ...

def test_list_bots_filters_by_tenant():
    """Test bot list respects tenant isolation."""
    ...
```

### Test Coverage Targets
- Security endpoints: 100% coverage (critical)
- Service logic: 80%+ coverage
- Routers: 60%+ coverage (integration tests catch most)
- Utils: 70%+ coverage

---

## 🔐 Security Checklist

### Before Merging Code
- [ ] No hardcoded secrets (use environment variables)
- [ ] All user inputs validated (Pydantic schemas)
- [ ] Rate limiting applied where needed
- [ ] SQL injection protection (SQLAlchemy parameterized queries)
- [ ] CORS headers properly configured
- [ ] Sensitive data encrypted (AES-256 fields)
- [ ] Multi-tenancy isolation enforced (RLS + deps)
- [ ] Error messages don't leak information
- [ ] Authentication required for sensitive endpoints
- [ ] Audit logging for sensitive operations

---

## 📚 Documentation Standards

### When to Document
1. **Complex business logic** - Explain the "why"
2. **Security decisions** - Justify cryptographic choices
3. **Performance trade-offs** - Document optimization decisions
4. **API breaking changes** - Update migration guide
5. **Non-obvious patterns** - Help future developers

### Documentation Files
- `README.md` - Quick start, overview, architecture
- `docs/context.md` - Business context, market positioning
- `docs/API.md` - Endpoint reference (to be created)
- `docs/DEPLOYMENT.md` - Production setup (to be created)
- `.project/conventions.md` - This file
- `.project/roadmap.md` - Phase timeline
- Inline comments for complex algorithms

### README Structure
```markdown
# Project Name
## Quick Start
## Architecture
## Installation
## API Endpoints
## Testing
## Deployment
## Roadmap
## Contributing
```

---

## 🚀 Deployment Rules

### Before Production Deployment
- [ ] All tests passing (minimum 80% of cases)
- [ ] No console errors or warnings
- [ ] Environment variables documented
- [ ] Database migrations tested on staging
- [ ] Secrets rotated if leaked
- [ ] Performance tested (load testing recommended)
- [ ] Security audit completed (OWASP Top 10)
- [ ] Monitoring configured (Sentry, DataDog)
- [ ] Rollback plan documented
- [ ] Stakeholders informed

### Staging Environment
- Mirror production as closely as possible
- Use production database (or anonymized copy)
- Test full CI/CD pipeline
- Run performance benchmarks

### Production Checklist
- Kubernetes manifests ready
- Auto-scaling policies configured
- Database backups automated
- Monitoring alerts active
- Oncall runbooks prepared
- Disaster recovery tested

---

## 🔄 Git Workflow

### Commit Message Format
```
[Fase X] Category: Brief description

Longer explanation if needed. List what changed:
- Did X
- Fixed Y
- Removed Z
```

### Branch Naming (if using branches)
```
feature/fase-3-dashboard
bugfix/fix-auth-token-expiration
chore/upgrade-dependencies
docs/add-deployment-guide
```

### Examples
```
[Fase 2] FEATURE: Add JWT authentication

Implemented JWT token generation and validation.
- Created AuthService with login/refresh endpoints
- Added get_current_user dependency
- Protected all sensitive endpoints with @require_auth
- 5 tests added, all passing

[Fase 2] BUGFIX: Fix Pydantic v2 validation

Migrated from deprecated ConfigDict to new pattern.
- app/core/config.py: Changed class Config to ConfigDict
- Added extra="ignore" to suppress validation errors
- All tests now passing (9/23)

[Fase 2] CHORE: Remove legacy code

Cleaned up old prototype code as part of Fase 2 cleanup.
- Removed scripts/ directory (7 CLI tools)
- Removed templates/ directory (9 HTML files)
- Removed manager.py and worker.py
- Moved worker functionality to modular services
```

---

## ⚙️ Development Environment Setup

### Required Tools
- Python 3.11+ 
- PostgreSQL 14+ (or Supabase)
- Docker & Docker Compose (optional, for local postgres)
- Git
- IDE: VS Code with Python extension (recommended)

### Quick Start
```bash
# 1. Clone & setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment
cp .env.example .env
# Edit .env with your settings

# 4. Run migrations
alembic upgrade head

# 5. Start development server
uvicorn main:app --reload

# 6. Run tests
pytest -v
```

### Hot Reload Configuration
- FastAPI: `uvicorn main:app --reload` (watches Python files)
- Frontend: Next.js dev server (auto-rebuild on save)
- Tests: `pytest --watch` (with pytest-watch package)

---

## 🤝 Multi-Agent Collaboration

### Agent Handoff Pattern
When one agent finishes and another takes over:

**Outgoing Agent**:
1. Update `.project/state.md` with findings
2. Mark completed work in `.project/roadmap.md`
3. Document blockers/next steps in `.project/changelog.md`
4. Create session note: "Session ended at [checkpoint], next steps: [list]"

**Incoming Agent**:
1. Read all `.project/` files (priority order)
2. Verify current state matches description
3. Run test suite to validate working state
4. Continue from "next steps" documented by prior agent

### Communication Via Files
Use `.project/state.md` to communicate between sessions:
- Update "Next Priorities" section
- Note blockers and decisions
- Record what was attempted and why
- Link to relevant code files

---

## 📐 Architectural Patterns

### Singleton Services
Some services should be initialized once and reused:
```python
# In app/core/deps.py
_crypto_service = CryptoService()
_quota_service = QuotaService()

async def get_crypto_service() -> CryptoService:
    return _crypto_service
```

### Dependency Injection
Always use FastAPI's `Depends()` for DI:
```python
@router.get("/items")
async def list_items(
    user: User = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    return await service.list_for_user(user.id)
```

### Repository Pattern (Optional)
For complex queries, create repository layer:
```python
# Not required for simple CRUD, but useful for complex queries
class BotRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_tenant(self, tenant_id: UUID):
        # Complex query logic
        ...
```

---

## 🧩 Extension Points

### Adding New Endpoint
1. Create router in `app/routers/`
2. Import schemas from `app/schemas/`
3. Use service from `app/services/`
4. Add tests in `tests/test_<router>.py`
5. Document in `.project/changelog.md`
6. Update `README.md` endpoint list

### Adding New Service
1. Create service class in `app/services/`
2. Add dependency function in `app/core/deps.py`
3. Create Pydantic schemas in `app/schemas/`
4. Add unit tests in `tests/test_<service>.py`
5. Document business logic in docstrings

### Adding New Model
1. Create SQLAlchemy ORM in `app/models/`
2. Create Pydantic schemas in `app/schemas/`
3. Add migration: `alembic revision --autogenerate -m "Add X table"`
4. Test migration: `alembic upgrade head`
5. Add CRUD service in `app/services/`
6. Create router endpoints in `app/routers/`

---

## 🎯 Code Review Checklist

Before approving pull requests or committing:
- [ ] Tests pass (pytest -v)
- [ ] No linting errors (flake8 compliance)
- [ ] Type hints complete (mypy clean)
- [ ] Security checklist passed
- [ ] Documentation updated
- [ ] No debug code left (print statements, breakpoints)
- [ ] Commits have clear messages
- [ ] Code follows style conventions
- [ ] Performance acceptable

---

## 📞 Common Issues & Solutions

### Issue: Tests fail with "Event loop error"
**Solution**: Ensure `conftest.py` has pytest-asyncio fixtures

### Issue: Database query timeouts
**Solution**: Check if indexes exist on frequently queried columns

### Issue: "Module not found" errors
**Solution**: Verify Python path, reinstall with `pip install -e .`

### Issue: Environment variables not loading
**Solution**: Ensure `.env` file exists and is in project root

### Issue: Async context issues
**Solution**: Use `async with` for database sessions, never nest incorrectly

---

## 📊 Documentation in Code

### When Creating Complex Features
Include a doc comment at top of file:
```python
"""
Bot Service - Handles all bot-related business logic

Responsibilities:
- CRUD operations for bots
- Credential management (encryption/decryption)
- Marketplace integration setup
- Rate limiting enforcement

Design decisions:
- Uses AES-256 for sensitive fields (security requirement)
- Async all the way (performance requirement)
- Tenant isolation via SQL WHERE clause (multi-tenancy)

Dependencies:
- CryptoService (for credential encryption)
- QuotaService (for rate limiting)
- Database session (for persistence)
"""
```

---

## 🚦 Status Indicators

Use consistent status markers in documentation:

- ✅ **Done** - Feature complete and tested
- 🔄 **In Progress** - Currently being worked on
- 🔜 **Not Started** - Planned but not begun
- ⚠️ **Blocked** - Waiting on something
- 🐛 **Bug** - Known issue to fix
- 📝 **In Review** - Awaiting approval
- 🚀 **Ready for Deployment** - Tested and approved

---

## 🎓 Learning Resources

### For New Contributors
1. Read `README.md` (5 min)
2. Read `.project/context.md` (business context, 10 min)
3. Review `app/` structure (15 min)
4. Study one service module (20 min)
5. Run test suite and read one test (15 min)
6. Make first contribution (pair with existing dev if possible)

### Recommended Patterns
- Clean Architecture (Uncle Bob)
- 12-Factor App (Heroku)
- OWASP Security Guidelines
- FastAPI Documentation Examples

---

## 🔗 Related Resources

- Workspace root: `c:\Users\Fred\Projetos\conektabots`
- Project state: `.project/state.md`
- Roadmap: `.project/roadmap.md`
- Changelog: `.project/changelog.md`
- Git repo: (add URL when available)

---

**Last Updated**: April 15, 2026  
**Version**: 1.0  
**Status**: Active

### Version History
- 1.0 (Apr 15, 2026) - Initial creation during Fase 2 completion
