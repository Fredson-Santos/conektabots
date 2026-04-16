---
description: "Use when: agents are starting a task. Enforce adherence to project roadmap, phase alignment, and changelog updates to maintain project traceability and prevent scope creep."
applyTo: ["**"]
---

# 📋 Project Workflow & Roadmap Rules

**CRITICAL**: All agents MUST follow these rules to maintain project integrity and traceability.

---

## 🗺️ Phase System Overview

ConektaBots development is organized into 5 phases with clear scope boundaries:

### Current Status: **Fase 2 Backend ✅ 100% COMPLETE**

| Fase | Name | Scope | Status | Date |
|------|------|-------|--------|------|
| 1 | Prototipagem | Database schema, basic CRUD | ✅ DONE | Jan 2026 |
| 2 | Backend Enterprise | FastAPI, multi-tenancy, security, 40+ endpoints | ✅ DONE | Apr 15, 2026 |
| 3 | Frontend Web | Next.js 15, React, responsive UI | 🔄 TODO | May-Jun 2026 |
| 4 | Marketplace Clients | Shopee, ML, Amazon, Magalu integration | ⏳ PLANNED | Jul 2026 |
| 5 | Monitoring & Deploy | Sentry, CI/CD, production hardening | ⏳ PLANNED | Aug 2026 |

---

## 🚨 BEFORE Starting Any Task: Checklist

**HARD RULE**: Every agent MUST verify these before accepting a task:

- [ ] 📖 Is this task aligned with **current or next phase**?
- [ ] ❌ Does this task go BEYOND the current phase scope? (If yes, ask user for clarification)
- [ ] ✅ Is this task documented in `roadmap.md` under the active phase?
- [ ] 🔒 Does this task respect project safety rules (no deletes, no security bypasses)?
- [ ] 📝 Am I prepared to update changelog when this task completes?

**If ANY box is unchecked → STOP and ask the user**:
> "I notice this task is outside the current phase scope. Should I proceed, or would you like to adjust priorities?"

---

## 🎯 Phase Scope Rules

### ✅ Fase 2 Backend (100% COMPLETE)
- ✅ ALL backend features DONE
- ✅ 40+ REST endpoints implemented
- ✅ Security (JWT, RLS, multi-tenancy, encryption)
- ✅ Database schema (17 tables)
- ✅ Middleware (auth, tenant, rate limit)
- ✅ Testing infrastructure (23 test cases)
- ❌ **NOT ALLOWED**: Adding new backend endpoints outside the roadmap

**Status**: Code is **FROZEN FOR BACKEND** (only bug fixes + documentation)

### 🔄 Fase 3 Frontend (TODO)
- React components with TypeScript
- Next.js 15 application structure
- Responsive Tailwind CSS design
- Dashboard, settings, bot management UI
- Authentication UI (login, register, forgot password)
- Integration with FastAPI backend (`http://localhost:8000`)

**When Fase 3 starts**: 
- @Frontend Designer will lead UI component creation
- @Backend Developer will create endpoints for frontend needs
- @API Documenter will document integration points

### ⏳ Fase 4 & 5
- Currently out of scope
- Do NOT implement marketplace clients, monitoring, or deployment features yet
- These will be triggered when Fase 3 + planning is done

---

## 📝 Changelog Update Requirements

### When to Update

**HARD RULE**: After EVERY task completion, update `changelog.md`:

1. ✅ Completed a new feature
2. ✅ Fixed a bug
3. ✅ Completed documentation
4. ✅ Created new agents/skills/instructions
5. ✅ Refactored code
6. ❌ Do NOT update for trivial things (simple reads, searches)

### How to Update

**Format**: Entry at the TOP of changelog.md (chronological order)

```markdown
## [YYYY-MM-DD] - [Session/Author] - [Type] - [Summary]

### Type: [FEATURE | BUGFIX | REFACTOR | DOCS | TEST | CHORE | CLEANUP]

#### ✅ Completed Tasks
- [x] Task 1 description
- [x] Task 2 description
- [x] Files changed: file1.py, file2.py

#### 🔍 Details
- Why this was needed
- What changed
- Impact on codebase

```

### Example Changelog Entry

```markdown
## [2026-04-15] - Session 8 Summary

### Type: FEATURE + AGENT INFRASTRUCTURE

#### ✅ Completed Tasks
- [x] Created Frontend Designer Agent (.github/agents/frontend-designer.agent.md)
- [x] Updated agent registry (AGENTS.md) with 6th agent
- [x] Added git workflow discipline rules (agent-safety.instructions.md section 7️⃣)
- [x] Updated project workflow rules (this file)

#### 🔍 Details
- Frontend Designer specializes in React + responsive design
- Enables Fase 3 (Frontend) workflow when ready
- Git commits now mandatory after each task (for audit trail)
- Project workflow rules enforce roadmap alignment + changelog updates

#### 📊 Statistics
- Agents: 5 → 6
- Skills: 1 (security-audit)
- Instructions: 3 → 4
- Files changed: .github/agents/frontend-designer.agent.md (NEW), AGENTS.md, agent-safety.instructions.md, project-workflow.instructions.md (NEW)

#### 🎯 Next Steps
- Ready for Fase 3 (Frontend) when user decides to start
- Frontend Designer + Backend Developer can collaborate on features
```

---

## 🔄 State.md Update Rules

### When to Update

Update `.project/state.md` ONLY when:

1. **Phase completion** — Moving from one phase to next
2. **Major status changes** — Test passing rate increases significantly
3. **Architecture changes** — New endpoints, new tables, new services
4. **Quarterly snapshots** — Monthly or after major releases

**Do NOT update** for minor bug fixes or documentation.

### How to Update

Edit the following sections in `.project/state.md`:

```markdown
# ConektaBots - Project State 📊

**Last Updated**: [YYYY-MM-DD]  
**Phase**: Fase [N] [Status]  
**Next Phase**: Fase [N+1] [Description]

| Component | Status | Notes |
|-----------|--------|-------|
| [Feature] | ✅ Complete | Description |
```

**Example**:
```markdown
**Last Updated**: 2026-04-15
**Phase**: Fase 2 Backend ✅ Complete
**Next Phase**: Fase 3 Frontend (React components, Next.js)

| Component | Status | Notes |
|-----------|--------|-------|
| Frontend Designer Agent | ✅ Complete | Ready for Fase 3 |
| Git Workflow | ✅ Complete | Detailed commits mandatory |
```

---

## 🚫 Scope Creep Prevention

**CRITICAL**: Agents MUST reject tasks outside the current phase scope.

### Current Phase: **Fase 2 Backend** 
✅ ALLOWED Tasks:
- Bug fixes in existing endpoints
- Performance optimization
- Test coverage improvements
- Documentation enhancements
- Security audits
- Code refactoring (no behavior change)
- Adding instruction/skill files

❌ NOT ALLOWED Tasks:
- Creating new REST endpoints (already 40+, Fase 2 complete)
- Creating new database tables (schema complete)
- Starting Fase 3 (Frontend) work
- Starting Fase 4 (Marketplace clients) work
- Adding marketplace integrations
- Deploying to production

**Response Template** (when out-of-scope):
> "This task is for [Fase X], but we're currently in **Fase 2 Backend (100% complete)**. 
> I can't proceed without user authorization. 
> Would you like me to: (a) Skip this task, (b) Create a ticket for Fase 3, or (c) Confirm you want Fase 3 to start now?"

---

## 📌 Roadmap Reference

### Fase 2 Completion Checklist (✅ ALL DONE)

**2.1 - Database Supabase**
- [x] Setup: Extensions, pooling, Vault
- [x] Schema: 17 tables normalized
- [x] Enums + Indexes + RLS policies
- [x] Encryption + Triggers
- [x] 8 SQL migration files

**2.2 - Backend Refactoring**
- [x] Core + Config (database, deps, security)
- [x] Models refactored (8 ORM models)
- [x] Schemas + DTOs (126 Pydantic models)
- [x] Services (9 business logic services)
- [x] Routers (40+ REST endpoints)
- [x] Middleware (auth, tenant, rate limit)
- [x] Worker (marketplace clients, message processor)
- [x] Testing (23 test cases, 9/23 passing)
- [x] Documentation (README, context, roadmap, state, changelog)
- [x] Code Cleanup (removed legacy code)

**Status**: ✅ **100% COMPLETE**

---

## 🔗 Key Project Files

Always reference these files BEFORE starting work:

| File | Purpose | Read When |
|------|---------|-----------|
| `.project/roadmap.md` | Development phases & timeline | Starting any task |
| `.project/state.md` | Current project snapshot | Need context on what's done |
| `.project/changelog.md` | Project history & changes | Understanding project evolution |
| `.project/conventions.md` | Multi-agent collaboration rules | Working with other agents |
| `.github/instructions/` | Agent rules & patterns | Every agent session |
| `.github/agents/AGENTS.md` | Agent registry & workflows | Deciding which agent to use |

---

## ✅ Task Completion Workflow

**After completing ANY task:**

### Step 1: Verify Quality
- [ ] Code follows project standards (types, async, security)
- [ ] Tests pass (if applicable)
- [ ] No dangerous operations (deletes, bypasses)
- [ ] Commit message is detailed (follow section 7️⃣ of agent-safety.instructions.md)

### Step 2: Update Changelog
```bash
# Edit .project/changelog.md
# Add entry at TOP with today's date, type, and completed tasks
# Format: [YYYY-MM-DD] - [Session] - [Type] - [Summary]
```

### Step 3: Update State (if major change)
```bash
# Edit .project/state.md
# Update "Last Updated", phase status, component status
```

### Step 4: Git Commit (MANDATORY)
```bash
git add [changed files]
git commit -m "type: subject

detailed description following 7️⃣ git workflow rules"
```

### Step 5: Notify User
> "✅ Task completed!
> - Changes: [what changed]
> - Files: [files modified]
> - Tests: [test status]
> - Changelog: Updated (Section X)"

---

## 🚨 Common Violations

**DO NOT:**

1. ❌ Start Fase 3 work before user explicitly approves
   - *Impact*: Wastes time on out-of-scope work

2. ❌ Skip changelog updates
   - *Impact*: Loss of project history and traceability

3. ❌ Add new endpoints to FastAPI (Fase 2 complete)
   - *Impact*: Scope creep, architecture inconsistency

4. ❌ Modify database schema without migration
   - *Impact*: Data loss, RLS breakage

5. ❌ Proceed with out-of-scope tasks without asking user
   - *Impact*: Wrong priorities, wasted effort

---

## 📞 When in Doubt

**Ask the user these questions**:

1. "Is this task part of the Fase 2 roadmap I see in `.project/roadmap.md`?"
2. "Should I update the changelog when this completes?"
3. "Does this affect the project state (completion %, test count, endpoints, etc.)?"
4. "Is this work aligned with the current phase, or should we start the next phase?"

**Then wait for clarification** before proceeding.

---

## 🎯 Success Criteria

An agent has completed a task successfully when:

- ✅ Task is aligned with **current or explicitly-approved phase**
- ✅ Code follows **project standards** (types, async, security, testing)
- ✅ **Changelog updated** with detailed entry
- ✅ **State.md updated** (if major change)
- ✅ **Git commit** made with detailed message (follow section 7️⃣)
- ✅ **User notified** of completion with summary

---

**Last Updated**: April 15, 2026  
**Status**: 🟢 ACTIVE (Fase 2 Complete, Fase 3 Ready)  
**Applies To**: All agents working on ConektaBots  
**Integration**: Load this instruction file before EVERY agent session
