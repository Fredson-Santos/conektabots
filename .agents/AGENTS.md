# Regras de Segurança para Agentes

> **CRÍTICO:** Os agentes devem seguir RIGOROSAMENTE essas regras. Qualquer violação pode danificar a integridade do projeto.

## ❌ Pastas e Arquivos Protegidos (NÃO DELETAR)

Os agentes **NUNCA** devem deletar, renomear ou mover as seguintes pastas:

- `.agents/` — Configurações e skills dos agentes
- `.git/` — Histórico de versão do projeto
- `.project/` — Configurações do projeto
- `supabase/migrations/` — Migrações de banco de dados
- `alembic/versions/` — Migrações Alembic
- `tests/` — Suite de testes
- `worker/` — Workers de processamento
- `.vscode/` — Configurações do VS Code

## ⚠️ Arquivos Sensíveis (CUIDADO)

Os agentes devem ter **extrema cautela** ao modificar:

- `.env` — Variáveis de ambiente (NUNCA expor em repositório)
- `.env.example` — Exemplo de variáveis (manter sincronizado com `.env`)
- `.mcp.json` — Configuração de MCP servers
- `docker-compose.yml` — Orquestração de containers
- `Dockerfile` — Build de imagem Docker
- `requirements.txt` — Dependências Python
- `alembic.ini` — Configuração de migrações
- `main.py` — Arquivo principal da aplicação

**Regra:** Antes de modificar esses arquivos, sempre:
1. Fazer backup mental ou comentar a mudança
2. Avisar o usuário sobre a mudança
3. Validar sintaxe antes de salvar

## 🚫 Operações Proibidas

Os agentes **NÃO PODEM:**

- Deletar qualquer arquivo em `.agents/`, `.git/`, ou `.project/`
- Modificar credenciais ou API keys (use variáveis de ambiente)
- Alterar estrutura de migrations sem avisar
- Executar `git reset --hard` ou comando similar
- Deletar banco de dados ou fazer rollback sem confirmação
- Instalar/desinstalar dependências sem avisar

## ✅ Operações Permitidas

Os agentes **PODEM:**

- Criar/editar arquivos em `app/`, `worker/`, `tests/`, `docs/`
- Criar novas migrations com nomes descritivos
- Atualizar `requirements.txt` (apenas adicionar/remover)
- Editar configuração em `app/core/config.py`
- Criar novos serviços, routers, modelos
- Refatorar código existente
- Adicionar testes

## 📋 Checklist Antes de Qualquer Operação Destrutiva

Antes de deletar ou modificar estrutura, verificar:

- [ ] Está dentro de uma pasta permitida?
- [ ] A mudança foi solicitada explicitamente?
- [ ] Há confirmação do usuário?
- [ ] O arquivo não está em `.git/`, `.agents/`, ou `.project/`?
- [ ] As dependências não serão quebradas?

## 🔒 Segurança Multi-tenant

Logo que aplicável, os agentes devem respeitar:

- Isolamento de dados por `tenant_id`
- Políticas de Row-Level Security (RLS)
- Criptografia de dados sensíveis
- Validação de permissões em todas as operações

---

**Última atualização:** 2026-04-15
