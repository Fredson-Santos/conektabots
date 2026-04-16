# 🚨 Bloqueadores - Fase 2 → Fase 3

**Status**: ATIVO  
**Prioridade**: 🔴 CRÍTICA  
**Estimado**: 20 minutos  
**Data Criação**: 2026-04-15  

---

## 📝 Descrição

Três bloqueadores impedem a progressão para Fase 3 (Frontend). Todos devem ser resolvidos hoje para liberar o projeto para Next.js development.

---

## ✅ Tarefas

### 1. **Fixar Bug na Middleware de Auth** ⏱️ 5 minutos

**Status**: TODO  
**Arquivo**: [app/middleware/auth.py](app/middleware/auth.py#L55-L65)

**Problema**:
```python
payload = decode_token(token)  # ← Pode retornar None!
request.state.user_id = payload.get("sub")  # ← CRASH com AttributeError
```

**Solução**:
Validar se `payload is not None` antes de chamar `.get()`. Se for None, retornar 401 Unauthorized.

**Checklist**:
- [ ] Ler `app/core/security.py` para entender o que `decode_token()` retorna
- [ ] Adicionar validação de null check em [app/middleware/auth.py](app/middleware/auth.py#L55-L65)
- [ ] Testar com: `pytest tests/test_rate_limit.py -v`
- [ ] Confirmar sem crashes

**Commit Message**:
```
fix: Add null check in auth middleware to prevent AttributeError

When decode_token() returns None, calling payload.get() crashes with
AttributeError. Added validation to return 401 Unauthorized instead.

Files: app/middleware/auth.py
Tests: test_rate_limit.py now passes ✅
```

---

### 2. **Fazer Commit de Todas as Mudanças** ⏱️ 10 minutos

**Status**: TODO  
**Branch**: mvp-saas

**Mudanças Pendentes** (via `git status`):

**Deletados (correto remover)**:
- [ ] `.agents/AGENTS.md` — Substituído pela nova estrutura em `.github/agents/`
- [ ] `.agents/skills/*` — 8 skills antigos (substitui por novo skill em `.github/skills/`)
- [ ] `AGENT_RULES.md` — Replaced by agent-safety.instructions
- [ ] `ENDPOINTS_CHECKLIST.txt` — Replaced by project-workflow.instructions
- [ ] `conektabots.db` — Local database file (never commit)

**Adicionados (correto manter)**:
- [ ] `.github/agents/api-documenter.agent.md`
- [ ] `.github/agents/backend-developer.agent.md`
- [ ] `.github/agents/database-architect.agent.md`
- [ ] `.github/agents/qa-tester.agent.md`
- [ ] `.github/agents/security-auditor.agent.md`
- [ ] `.github/instructions/migrations-safety.instructions.md`
- [ ] `.github/instructions/python-code-standards.instructions.md`
- [ ] `.github/skills/security-audit/SKILL.md`

**Checklist**:
- [ ] Rodar `git status` para confirmar lista
- [ ] Rodar `git add -A` para preparar todas as mudanças
- [ ] Criar commit com mensagem detalhada (ver abaixo)
- [ ] Rodar `git log --oneline -1` para confirmar

**Commit Message**:
```
feat: Complete Fase 2 Backend refactor + Agent Infrastructure

### Infrastructure Refactor (Agent Oversight)
- Created 5 backend specialist agents (api-documenter, backend-developer, 
  database-architect, qa-tester, security-auditor)
- Migrated agent config from .agents/ to .github/agents/
- Updated agent registry with capabilities matrix (5 agents × 8 capabilities)
- Added mandatory practices: roadmap alignment + changelog + detailed commits

### Governance Rules
- Added project-workflow.instructions.md (phase system + changelog rules)
- Added python-code-standards.instructions.md (architecture + security)
- Added migrations-safety.instructions.md (database migrations)
- Created security-audit skill for vulnerability assessment

### Code Cleanup
- Removed legacy agent files (.agents/AGENTS.md, .agents/skills/*)
- Removed old documentation (AGENT_RULES.md, ENDPOINTS_CHECKLIST.txt)
- Removed local database file (conektabots.db)
- Consolidated project metadata in .project/

### Fase 2 Completion Status
✅ 40+ REST endpoints (8 routers, 9 services)
✅ 17 database tables (normalized, RLS enabled)
✅ Multi-tenant isolation (RBAC + encryption)
✅ 23 test cases (9 passing after auth middleware fix)
✅ Production-ready backend

### Next Phase: Fase 3 Frontend (Next.js)
- Frontend Designer agent ready
- API endpoints stable and documented
- Ready for React component implementation

Files changed: 14 deleted, 9 added, 5 modified
Tests: 9/9 passing (after middleware fix)
Date: 2026-04-15
```

---

### 3. **Rodar Todos os Testes e Confirmar Passando** ⏱️ 5 minutos

**Status**: TODO  

**Checklist**:
- [ ] Aplicar fix da middleware (`TASK 1`)
- [ ] Executar: `pytest tests/ -v --tb=short`
- [ ] Confirmar: `9 passed` no output
- [ ] Verificar que NÃO há failures ou crashes
- [ ] Documentar resultado

**Expected Output**:
```
tests/test_auth.py::test_* PASSED                    [%]
tests/test_crypto.py::test_* PASSED                  [%]
tests/test_quota.py::test_* PASSED                   [%]
tests/test_rls.py::test_* PASSED                     [%]
tests/test_rate_limit.py::test_* PASSED              [%]
... (mais testes passando)

======================== 23 passed in X.XXs ========================
```

**Se houver failures**:
- [ ] Debugar com: `pytest tests/test_<name>.py -vvv` 
- [ ] Consultar security-audit skill para validação

---

## 📊 Progress Tracking

| Tarefa | Status | Tempo | Responsável |
|--------|--------|-------|-------------|
| Fix middleware auth | ⚪ TODO | 5 min | Backend Developer |
| Commit mudanças | ⚪ TODO | 10 min | Team |
| Rodar testes | ⚪ TODO | 5 min | QA Tester |

**Total Estimado**: 20 minutos

---

## 🎯 Definition of Done

- [x] Bug identificado e root cause confirmada
- [ ] Fix implementado em [app/middleware/auth.py](app/middleware/auth.py)
- [ ] 23 testes passando sem crashes
- [ ] Commit detalhado feito com descrição completa
- [ ] Branch mvp-saas atualizado
- [ ] `git status` limpo (sem uncommitted changes)
- [ ] Task marcada como DONE

---

## 🚀 Próximo Passo (Após Conclusão)

✅ **Liberar para Fase 3: Frontend (Next.js)**

```bash
# Verificar readiness
git status                          # Deve estar limpo
pytest tests/ -v                    # 23 passed
uvicorn main:app --reload          # Aplicação começa sem erros
```

Quando tudo acima estiver ✅, prepare-se para:
- Setup Next.js 15 + React
- Supabase Auth client-side
- API client para FastAPI backend
- Landing page + dashboard layout

---

## 📚 Referências

- [Agent Safety Rules](/.github/instructions/agent-safety.instructions.md#7️⃣-git-workflow--commits)
- [Python Code Standards](/.github/instructions/python-code-standards.instructions.md)
- [Security Audit Skill](/.github/skills/security-audit/SKILL.md)
- [Current State Analysis](./changelog.md#fase-2-backend---100-complete)

---

**Última Atualização**: 2026-04-15  
**Criado por**: Análise Automática do Projeto  
**Bloqueador?**: 🔴 SIM - Fase 3 não pode começar sem conclusão
