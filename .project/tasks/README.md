# 📋 Project Tasks

Central registry of all active and completed tasks.

---

## 🔴 CRÍTICA / Bloqueadores

| ID | Título | Status | Estimado | Fase |
|---|--------|--------|----------|------|
| [FASE2_BLOCKERS](./FASE2_BLOCKERS.md) | Resolver 3 bloqueadores pré-Fase 3 | ⚪ TODO | 20 min | Backend |

**Descrição**: 
1. Fix bug na middleware de auth
2. Commit detalhado de mudanças
3. Confirmar 23 testes passando

---

## 🟡 ALTA / Must-Have (Fase 3)

*(Será preenchido quando Fase 3 iniciar)*

---

## 🟢 MÉDIA / Nice-to-Have

| ID | Título | Status | Estimado |
|---|--------|--------|----------|
| PYDANTIC_WARNINGS | Fix deprecation warnings (min_items → min_length) | ⚪ TODO | 30 min |
| API_DOCS | Gerar documentação Swagger completa | ⚪ TODO | 1 hora |
| WORKER_TESTS | Adicionar testes para marketplace clients | ⚪ TODO | 2 horas |

---

## ✅ COMPLETADAS (Fase 2)

- ✅ Backend refactoring (FastAPI multi-tenant)
- ✅ Database schema (17 tabelas normalizadas)
- ✅ Security implementation (JWT, RLS, encryption)
- ✅ 40+ REST endpoints
- ✅ Test infrastructure (23 cases)
- ✅ Agent infrastructure (5 agents + governance)
- ✅ Documentation (roadmap, state, conventions)

---

## 📊 Kanban Status

```
TODO              BLOCKED        DONE
├─ FASE2_BLOCKERS  (depends on fix middleware)     ├─ Backend complete
├─ API_DOCS                                       ├─ Database complete
├─ WORKER_TESTS                                   ├─ Security complete
└─ PYDANTIC_WARNINGS                              └─ Tests setup
```

---

## 🚀 How to Use

1. **Revisar task**: Abra o arquivo `.md` correspondente
2. **Executar**: Siga o checklist passo a passo
3. **Reportar**: Atualize status em tempo real
4. **Fechar**: Marque como ✅ quando done

**Exemplo**:
```bash
# Ver tarefa
cat .project/tasks/FASE2_BLOCKERS.md

# Executar steps
# ... (make changes)

# Verificar progress
git status
pytest tests/ -v
```

---

**Last Updated**: 2026-04-15  
**Owner**: Backend Team  
**Next Review**: After blocker resolution
