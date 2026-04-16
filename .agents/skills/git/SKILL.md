# Git Workflow Skill

> **OBJETIVO:** Estabelecer um workflow Git seguro, organizado e auditável para agentes trabalhando no projeto conektabots.

---

## 📋 Quando Usar Esta Skill

Use esta skill quando:
- Precisa fazer commit de mudanças
- Necessita criar ou mudar de branch
- Vai fazer merges ou rebases
- Precisa resolver conflitos
- Quer revisar histórico de commits
- Necessita fazer push/pull de changes

---

## 🚫 O que NÃO Fazer

```
❌ git reset --hard          ← Nunca, sem confirmação explícita
❌ git force-push            ← Extremamente perigoso
❌ git rebase -i             ← Apenas em branches pessoais
❌ git clean -fd             ← Pode deletar arquivos
❌ rm -rf .git               ← NUNCA deletar histórico
```

---

## ✅ Workflow Recomendado

### 1. Antes de Começar Qualquer Mudança

```bash
# Verificar status
git status

# Trazer últimas mudanças
git fetch origin

# Verificar branch atual
git branch -v
```

### 2. Criar Branch para Feature

```bash
# Padrão: feature/{ticket}/{descricao} ou fix/{ticket}/{descricao}
git checkout -b feature/TICKET-123/add-shopee-integration
git checkout -b fix/TICKET-456/discount-calculation-bug
```

**Nomes de branch:**
- `feature/{ticket}/{desc}` — Novas features
- `fix/{ticket}/{desc}` — Bug fixes
- `refactor/{ticket}/{desc}` — Refatoração
- `docs/{desc}` — Documentação
- `chore/{desc}` — Manutenção

### 3. Fazer Commits Atômicos

```bash
# Ver mudanças
git diff

# Adicionar arquivos específicos (não git add .)
git add app/models/bot.py
git add app/services/bot_service.py

# Commit com mensagem descritiva
git commit -m "feat(bot): add shopee marketplace integration

- Add Shopee OAuth configuration
- Implement marketplace sync service
- Add unit tests for Shopee API client

Closes: TICKET-123"
```

**Formato de commit (Conventional Commits):**
```
<type>(<scope>): <subject>

<body>

Closes: <ticket-id>
```

**Types:**
- `feat` — Nova feature
- `fix` — Bug fix
- `docs` — Documentação
- `style` — Formatação/whitespace
- `refactor` — Refatoração de código
- `perf` — Melhoria de performance
- `test` — Testes
- `chore` — Build, deps, etc

### 4. Push e Pull Request

```bash
# Push do branch local
git push origin feature/TICKET-123/add-shopee-integration

# Criar PR (via GitHub)
# - Descrição clara do que foi feito
# - Link para ticket
# - Screenshots se aplicável
# - Checklist de testes
```

### 5. After Merge

```bash
# Voltar para main
git checkout main

# Trazer mudanças remotas
git pull origin main

# Deletar branch local antigo
git branch -d feature/TICKET-123/add-shopee-integration

# Deletar branch remoto antigo
git push origin --delete feature/TICKET-123/add-shopee-integration
```

---

## 🔍 Operações Comuns

### Verificar Mudanças

```bash
# Mudanças não staged
git diff

# Mudanças staged
git diff --cached

# Resumo de mudanças
git status

# Ver commits do branch atual
git log --oneline -10

# Ver commits com detalhes
git log --pretty=format:"%h - %an, %ar : %s"
```

### Atualizar Branch com Main

```bash
# Opção 1: Rebase (linear history - preferido)
git fetch origin
git rebase origin/main

# Opção 2: Merge (preserva history - se houver conflitos)
git fetch origin
git merge origin/main
```

### Resolver Conflitos

```bash
# 1. Ver conflitos
git status

# 2. Editar arquivos em conflito (remover marcadores <<<, ===, >>>)

# 3. Após resolvidos:
git add <arquivo-resolvido>

# 4. Continuar rebase (se applicable)
git rebase --continue

# 5. Ou fazer commit (se foi merge)
git commit -m "Resolve merge conflicts"
```

### Desfazer Mudanças

```bash
# Desfazer mudanças em arquivo não staged
git checkout -- app/models/bot.py

# Desfazer último commit (mantém mudanças)
git reset HEAD~1

# Desfazer último commit (descarta mudanças)
git revert HEAD

# Remover arquivo do staging
git reset app/services/bot_service.py
```

---

## 🔒 Proteções e Regras

### Branches Protegidos

Estes branches têm proteção (não podem fazer force-push):

- `main` — Produção
- `develop` — Desenvolvimento
- `staging` — Pre-produção

**Regra:** Qualquer mudança nesses branches DEVE passar por Pull Request aprovado.

### Cobertura de Testes

Antes de fazer commit:

```bash
# Rodar testes
pytest tests/

# Verificar coverage
pytest --cov=app tests/

# Rodar linters
flake8 app/
black --check app/
pylint app/
```

### Commits Específicos Obrigatórios

Ao fazer commit em arquivos sensíveis, adicionar contexto:

**`.env` ou credenciais:**
```
❌ NUNCA fazer commit de .env
✅ Fazer commit de .env.example
```

**`requirements.txt`:**
```
git commit -m "chore(deps): add sqlalchemy 2.0 library

Added dependency for async ORM support.
Updated requirements.txt with pinned version 2.0.3"
```

**`supabase/migrations/` ou `alembic/versions/`:**
```
git commit -m "chore(db): add user_metadata column to tenants

Migration: {timestamp}_add_user_metadata_to_tenants.py

This is required for storing custom tenant data.
Tested with migration up/down.

Closes: TICKET-789"
```

---

## 📊 Exemplo Completo: Feature Branch

```bash
# 1. Start
git fetch origin
git checkout -b feature/TICKET-100/implement-telegram-bot

# 2. Work and commit atomically
git add app/models/telegram_bot.py
git commit -m "feat(models): add TelegramBot model"

git add app/services/telegram_service.py
git commit -m "feat(services): implement Telegram API client"

git add tests/test_telegram_service.py
git commit -m "test(telegram): add unit tests for Telegram service"

# 3. Keep up to date
git fetch origin
git rebase origin/main
# (resolve conflicts if any)

# 4. Push
git push origin feature/TICKET-100/implement-telegram-bot

# 5. Create PR on GitHub with:
#    - Description of changes
#    - Link to TICKET-100
#    - Testing instructions
#    - Checklist

# 6. After approval and merge on GitHub
git checkout main
git pull origin main
git branch -d feature/TICKET-100/implement-telegram-bot
git push origin --delete feature/TICKET-100/implement-telegram-bot
```

---

## ⚠️ Troubleshooting

### Commit foi pro branch errado

```bash
# 1. Criar novo branch no commit correto
git branch feature/correct-branch

# 2. Resetar branch antigo
git checkout branch-errado
git reset HEAD~1

# 3. Ir para novo branch
git checkout feature/correct-branch
```

### Preciso desfazer um commit já feito push

```bash
# Usar revert (seguro, cria novo commit)
git revert <commit-hash>
git push origin main

# NÃO usar reset --hard + force-push (destroi history)
```

### Conflito durante rebase/merge

```bash
# 1. Ver arquivo em conflito
git status

# 2. Editar e resolver conflitos manualmente

# 3. Marcar como resolvido
git add <arquivo>

# 4. Continuar
git rebase --continue  # ou git merge --continue
```

---

## 🎯 Best Practices para Agentes

1. **Commits atômicos:** Cada commit deve representar uma mudança lógica completa
2. **Mensagens descritivas:** Sempre explicar o "por quê", não apenas o "o quê"
3. **Testes antes de commit:** Nunca commitar código quebrado
4. **Sem force-push:** Em branches compartilhadas, sempre usar merge/rebase normal
5. **Review branches:** Sempre pull da origin antes de começar novo trabalho
6. **Limpar branches:** Deletar branches locais e remotas após merge
7. **Link com tickets:** Sempre referenciar ticket no commit (`Closes: TICKET-123`)
8. **Pequenos commits:** Melhor ter 10 commits pequenos que 1 commit gigante

---

## 🔗 Referências Úteis

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Rebase vs Merge](https://www.atlassian.com/git/tutorials/merging-vs-rebasing)
- [Git Flow Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)

---

**Versão:** 1.0  
**Última atualização:** 2026-04-15  
**Criado para:** conektabots project
