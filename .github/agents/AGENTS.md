# ConektaBots - Agents Registry 🤖

Inventory of specialized agents configured for the ConektaBots project. Each agent has a specific domain and can be invoked manually or as subagents.

---

## 📋 Available Agents

### 1. **QA Tester** ✅
**File**: `.github/agents/qa-tester.agent.md`  
**Role**: Quality Assurance specialist  
**Expertise**: Running tests, diagnosing failures, writing new test cases

**Use when**:
- Running pytest suite and need to debug failures
- Writing new test cases for features
- Analyzing test coverage and gaps
- Validating application behavior
- Fixing Pydantic schema validation issues

**Tools**: read, search, execute, edit, semantic-search  
**Example**: `@QA Tester: Fix the 11 failing tests in the suite`

---

### 2. **Backend Developer** ✅
**File**: `.github/agents/backend-developer.agent.md`  
**Role**: Backend engineer  
**Expertise**: FastAPI, async/await, business logic, services

**Use when**:
- Building new REST endpoints
- Refactoring existing services
- Fixing bugs in API logic
- Optimizing async patterns
- Improving code quality

**Tools**: read, search, execute, edit, semantic-search  
**Example**: `@Backend Developer: Implement marketplace integration endpoint`

---

### 3. **Database Architect** ✅
**File**: `.github/agents/database-architect.agent.md`  
**Role**: Database specialist  
**Expertise**: PostgreSQL, Alembic migrations, schema design, RLS

**Use when**:
- Creating database migrations
- Optimizing queries with indexes
- Designing schema changes
- Fixing RLS policies
- Analyzing database performance

**Tools**: read, search, execute, edit, semantic-search  
**Example**: `@Database Architect: Create migration to normalize the rules table`

---

### 4. **Security Auditor** ✅
**File**: `.github/agents/security-auditor.agent.md`  
**Role**: Security specialist  
**Expertise**: JWT, encryption, RLS, RBAC, multi-tenant isolation

**Use when**:
- Auditing JWT implementation
- Validating RLS policies
- Reviewing encryption usage
- Checking multi-tenant isolation
- Identifying vulnerabilities

**Tools**: read, search, semantic-search (read-only for safety)  
**Example**: `@Security Auditor: Verify tenant A cannot read tenant B data`

---

### 5. **API Documenter** ✅
**File**: `.github/agents/api-documenter.agent.md`  
**Role**: Technical writer  
**Expertise**: OpenAPI/Swagger, endpoint documentation, code examples

**Use when**:
- Generating API documentation
- Creating endpoint reference guides
- Writing integration guides
- Documenting error responses
- Creating client code examples

**Tools**: read, search, semantic-search (read-only for documentation)  
**Example**: `@API Documenter: Create API reference for all endpoints`

---

### 6. **Frontend Designer** 🎨
**File**: `.github/agents/frontend-designer.agent.md`  
**Role**: Frontend specialist  
**Expertise**: React, responsive design, design systems, UI/UX, modern aesthetics

**Use when**:
- Building reusable React components
- Creating responsive dashboards and layouts
- Designing UI component libraries
- Implementing design systems with tokens
- Crafting engaging user experiences
- Designing mobile-first interfaces
- Building accessibility-first components

**Tools**: read, edit, search, web, semantic-search  
**Example**: `@Frontend Designer: Create a bot metrics dashboard with modern minimalist aesthetic`

---

## 🎯 Workflow Examples

### Scenario 1: Fix Failing Tests
```
@QA Tester: 
Run pytest -v and identify why 11 tests are failing.
Categorize by issue type (schema, fixture, logic).
Provide top 3 issues to fix first.
```

### Scenario 2: Add New Bot Integration
```
@Backend Developer:
Create new endpoint POST /bots/{id}/integrations to link a marketplace.

1. Define BotIntegrationCreate schema
2. Implement service method
3. Create the router endpoint
4. Ensure tenant isolation in queries

@QA Tester:
Write test cases for the new endpoint.

@API Documenter:
Document the new endpoint in API reference.
```

### Scenario 3: Performance Optimization
```
@Database Architect:
Analyze current indexes on the logs table.
Suggest missing indexes for common queries.
Create migration to add recommended indexes.

@QA Tester:
Run performance tests before/after migration.
```

### Scenario 4: Security Review
```
@Security Auditor:
Audit JWT implementation and token lifecycle.
Verify all RLS policies block cross-tenant access.
Check encryption usage is consistent.

→ Report: List vulnerabilities and recommendations

@Backend Developer:
Implement recommended fixes.

@QA Tester:
Write security test cases to prevent regression.
```

### Scenario 5: Frontend & Backend Integration (Fase 3)
```
@Backend Developer:
Create new endpoint POST /dashboard/metrics for bot analytics.
Ensure multi-tenant filtering and RBAC.

@Frontend Designer:
Build a responsive dashboard component that displays metrics.
Create design system tokens for consistent theming.
Implement mobile-first with accessibility.

@API Documenter:
Document the new /dashboard/metrics endpoint with React integration examples.

→ Result: Complete, documented feature ready for production
```

---

## 🛠️ How to Use Agents

### Invoke Manually
In VS Code Chat (Copilot), type:
```
@QA Tester [describe your task]
@Backend Developer [describe your task]
@Database Architect [describe your task]
@Security Auditor [describe your task]
@API Documenter [describe your task]
```

### Invoke as Subagent
When working with the default Copilot agent, it can automatically delegate tasks:
```
"Help me fix the failing tests and then document the new endpoints"
→ Can delegate to @QA Tester first, then @API Documenter
```

### Best Practices
- ✅ Be specific in task descriptions
- ✅ Include context (which file, which endpoint, etc.)
- ✅ Use one agent per focused task (avoid mixing concerns)
- ✅ Review each agent's output before proceeding
- ✅ Reference agent names in chat for clarity

---

## 📊 Agent Capabilities Matrix

| Capability | QA | Backend | Database | Security | Docs | Frontend |
|-----------|----|---------|-----------| ---------|------|----------|
| Read code | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Search codebase | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Semantic search | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Web search | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Execute commands | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Edit files | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Focus Area** | Testing | APIs | Schema | Security | Docs | UI/React |

---

## 🔗 Integration Points

**For Frontend Development (Fase 3)**:
- @API Documenter → Generate client SDK specs
- @Backend Developer → Create endpoint for new features

**For Deployment**:
- @Database Architect → Verify migrations
- @Security Auditor → Pre-deployment security checklist
- @QA Tester → Run full test suite

**For Code Review**:
- @Backend Developer → Review endpoint implementations
- @Security Auditor → Security review
- @Database Architect → Database schema review
- @QA Tester → Test coverage review

---

## 📝 Agent Rules

All agents follow these principles:
- **Specificity**: Each agent has a focused domain (no "do everything" agents)
- **Safety**: All agents respect project constraints (no delete critical files, etc.)
- **Transparency**: Agents explain their reasoning and provide detailed output
- **Quality**: Only use agents with confidence they'll produce high-quality work

---

## 🚀 Future Agents (Candidates)

These agents could be created for future needs:
- **DevOps Engineer** — Docker, Kubernetes, CI/CD, infrastructure
- **Product Manager** — Feature planning, roadmap coordination
- **Data Analyst** — Usage analytics, performance metrics
- **Mobile Developer** — React Native, iOS/Android, mobile optimization

---

**Last Updated**: April 15, 2026  
**Status**: ✅ All 6 agents configured and ready  
**Location**: `.github/agents/`
