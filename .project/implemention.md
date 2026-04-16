# ConektaBots → SaaS MVP: Roadmap Completo

## Visão Geral

Transformação do ConektaBots de ferramenta single-user em **SaaS multi-tenant para afiliados**.

**Decisões confirmadas:**
- ✅ Frontend: **Next.js + React**
- ✅ Backend: **FastAPI** (mantido) + **Supabase** (DB + Auth)
- ✅ Pricing: Free / Starter / Pro / Enterprise (com rate limit de mensagens no Free)
- ✅ Prioridade: Fases 1-2 primeiro (estrutura + segurança), frontend depois
- ✅ Foco: **Segurança em primeiro lugar**

**Branch ativo:** `mvp-saas`

---

## Stack Final do MVP

| Camada | Atual | Novo |
|--------|-------|------|
| **Database** | PostgreSQL local | Supabase PostgreSQL (managed) |
| **Auth** | Nenhuma (aberto) | Supabase Auth (JWT + RLS) |
| **Backend API** | FastAPI + Jinja2 | FastAPI (API REST pura) |
| **ORM** | SQLModel sync | SQLModel + asyncpg (async) |
| **Frontend** | Jinja2 + HTMX | Next.js 15 + React |
| **Deploy API** | Docker local | Railway / Render |
| **Deploy Front** | Junto com API | Vercel |
| **Secrets** | Plaintext | pgcrypto + Vault |
| **CI/CD** | Nenhum | GitHub Actions |

---

# FASE 1 — Modelagem do Banco de Dados (Supabase)

> [!IMPORTANT]
> Esta fase é a fundação de tudo. Nenhum código backend deve ser modificado até que o schema esteja finalizado e testado.

## 1.1 — Setup do Projeto Supabase

### Tarefas
- [ ] Criar projeto no Supabase Dashboard (região: São Paulo)
- [ ] Salvar credenciais (URL, anon key, service role key, connection string)
- [ ] Habilitar extensões necessárias: `pgcrypto`, `uuid-ossp`, `pg_trgm`
- [ ] Configurar connection pooling (PgBouncer) no Supabase
- [ ] Atualizar `.env.example` e `.env` com variáveis Supabase

### Arquivo: `.env.example` (atualizado)
```env
# ─── Supabase ───
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
DATABASE_URL=postgresql://postgres:xxx@db.xxx.supabase.co:5432/postgres

# ─── App ───
SECRET_KEY=xxx
ENVIRONMENT=development
ENCRYPTION_KEY=xxx

# ─── Configurações ───
TZ=America/Sao_Paulo
```

---

## 1.2 — Schema: Tabelas Core (Multi-Tenancy)

> [!CAUTION]
> Todas as tabelas de negócio **devem** ter `tenant_id` como FK. Isso é a base do isolamento de dados via RLS.

### Diagrama ER Completo

```mermaid
erDiagram
    TENANT ||--o{ TENANT_MEMBER : "tem membros"
    TENANT ||--o{ BOT : "possui"
    TENANT ||--o{ MARKETPLACE_INTEGRACAO : "tem integrações"
    TENANT ||--o{ REGRA : "possui"
    TENANT ||--o{ AGENDAMENTO : "possui"
    TENANT ||--o{ LOG_EXECUCAO : "possui"

    BOT ||--o{ REGRA : "executa"
    BOT ||--o{ AGENDAMENTO : "executa"
    BOT ||--o{ LOG_EXECUCAO : "gera"

    MARKETPLACE_INTEGRACAO ||--o{ REGRA : "converte links"
    MARKETPLACE_INTEGRACAO ||--o{ AGENDAMENTO : "converte links"

    REGRA ||--o{ REGRA_ORIGEM : "monitora"
    REGRA ||--o{ REGRA_DESTINO : "envia para"
    REGRA ||--o{ REGRA_FILTRO : "aplica substituição"
    REGRA ||--o{ REGRA_CONDICAO : "filtra por"

    AGENDAMENTO ||--o{ AG_ORIGEM : "busca de"
    AGENDAMENTO ||--o{ AG_DESTINO : "envia para"
    AGENDAMENTO ||--o{ AG_HORARIO : "executa em"
    AGENDAMENTO ||--o{ AG_FILTRO : "aplica substituição"
    AGENDAMENTO ||--o{ AG_CONDICAO : "filtra por"

    TENANT {
        uuid id PK
        string nome
        uuid owner_id FK
        enum plano
        int limite_bots
        int limite_regras
        int limite_agendamentos
        int limite_msgs_hora
        int limite_marketplaces
        timestamp criado_em
        timestamp atualizado_em
        timestamp deletado_em
    }

    MARKETPLACE_INTEGRACAO {
        uuid id PK
        uuid tenant_id FK
        enum marketplace_tipo
        string nome_exibicao
        bytea credenciais_enc
        boolean ativo
        timestamp criado_em
        timestamp atualizado_em
        timestamp deletado_em
    }

    REGRA {
        uuid id PK
        uuid tenant_id FK
        uuid bot_id FK
        uuid marketplace_integracao_id FK
        string nome
        enum filtro_midia
        boolean ativo
        timestamp criado_em
        timestamp atualizado_em
        timestamp deletado_em
    }

    AGENDAMENTO {
        uuid id PK
        uuid tenant_id FK
        uuid bot_id FK
        uuid marketplace_integracao_id FK
        string nome
        int msg_id_atual
        enum tipo_envio
        enum filtro_midia
        boolean ativo
        timestamp criado_em
        timestamp atualizado_em
        timestamp deletado_em
    }

    LOG_EXECUCAO {
        uuid id PK
        uuid tenant_id FK
        uuid bot_id FK
        uuid regra_id FK
        uuid agendamento_id FK
        string origem
        string destino
        enum status
        string mensagem
        timestamp criado_em
    }
```

> [!NOTE]
> **Diagrama simplificado** — tabelas filhas normalizadas (origem, destino, filtro, condicao, horario) e tabelas auxiliares (tenant_member, bot, uso_mensal) omitidas para clareza. Estrutura completa no SQL abaixo.

### Enums do Banco

```sql
-- Tipos enumerados
CREATE TYPE plano_tipo AS ENUM ('free', 'starter', 'pro', 'enterprise');
CREATE TYPE bot_tipo AS ENUM ('user', 'bot');
CREATE TYPE envio_tipo AS ENUM ('sequencial', 'pontual');
CREATE TYPE midia_tipo AS ENUM ('todos', 'foto', 'video', 'foto_video', 'texto');
CREATE TYPE condicao_tipo AS ENUM ('whitelist', 'blacklist');
CREATE TYPE log_status AS ENUM ('sucesso', 'erro', 'bloqueado', 'erro_protocolo');
CREATE TYPE membro_role AS ENUM ('owner', 'admin', 'editor', 'viewer');
CREATE TYPE marketplace_tipo AS ENUM (
    'shopee', 'mercado_livre', 'amazon', 'magalu',
    'americanas', 'aliexpress', 'shein', 'outro'
);
```

### Tabelas — SQL Completo

#### Arquivo: `supabase/migrations/001_extensions_and_types.sql`
```sql
-- Extensões
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Enums (listados acima)
```

#### Arquivo: `supabase/migrations/002_core_tables.sql`

**Tabela `tenant`** — Workspace/organização do afiliado
```sql
CREATE TABLE public.tenant (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome        VARCHAR(100) NOT NULL,
    owner_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    plano       plano_tipo NOT NULL DEFAULT 'free',
    
    -- Limites por plano
    limite_bots             INT NOT NULL DEFAULT 1,
    limite_regras           INT NOT NULL DEFAULT 3,
    limite_agendamentos     INT NOT NULL DEFAULT 2,
    limite_msgs_hora        INT NOT NULL DEFAULT 50,
    limite_marketplaces     INT NOT NULL DEFAULT 1,  -- free = 1 marketplace
    
    -- Auditoria
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ,
    
    CONSTRAINT tenant_nome_length CHECK (char_length(nome) >= 2)
);

-- ⭐ NEW: Integrações com Marketplaces (Shopee, ML, Amazon, Magalu...)
-- Cada tenant pode ter N integrações, cada uma com credenciais criptografadas.
-- O campo `credenciais_enc` armazena um JSON criptografado com os dados específicos
-- de cada marketplace (app_id, app_secret, affiliate_id, token, etc.)
CREATE TABLE public.marketplace_integracao (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    tipo            marketplace_tipo NOT NULL,
    nome_exibicao   VARCHAR(64) NOT NULL,  -- ex: "Minha Shopee", "ML Principal"
    credenciais_enc BYTEA NOT NULL,        -- JSON criptografado: {app_id, secret, ...}
    endpoint_url    VARCHAR(256),          -- URL da API (customizável por marketplace)
    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ,
    
    -- Um tenant pode ter múltiplas integrações do mesmo tipo
    CONSTRAINT mkt_nome_length CHECK (char_length(nome_exibicao) >= 1)
);
```

**Tabela `tenant_member`** — Membros da organização
```sql
CREATE TABLE public.tenant_member (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id   UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role        membro_role NOT NULL DEFAULT 'viewer',
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT unique_tenant_user UNIQUE (tenant_id, user_id)
);
```

**Tabela `bot`** — Bots do Telegram (dados sensíveis criptografados)
```sql
CREATE TABLE public.bot (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    nome            VARCHAR(64) NOT NULL,
    api_id          INTEGER NOT NULL,
    api_hash_enc    BYTEA NOT NULL,        -- criptografado
    phone_enc       BYTEA,                 -- criptografado
    bot_token_enc   BYTEA,                 -- criptografado
    tipo            bot_tipo NOT NULL DEFAULT 'user',
    session_string_enc BYTEA,              -- criptografado
    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ,
    
    CONSTRAINT bot_nome_length CHECK (char_length(nome) >= 1)
);
```

**Tabela `regra`** — Regras de encaminhamento (header normalizado)
```sql
CREATE TABLE public.regra (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    bot_id          UUID NOT NULL REFERENCES public.bot(id) ON DELETE CASCADE,
    nome            VARCHAR(64) NOT NULL,
    -- ⭐ Link para marketplace (NULL = sem conversão de link)
    marketplace_integracao_id UUID REFERENCES public.marketplace_integracao(id) ON DELETE SET NULL,
    filtro_midia    midia_tipo NOT NULL DEFAULT 'todos',
    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ
);
```

#### Arquivo: `supabase/migrations/003_normalized_tables.sql`

**Tabelas normalizadas para `regra`:**
```sql
-- Origens de uma regra (1:N)
CREATE TABLE public.regra_origem (
    id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    regra_id  UUID NOT NULL REFERENCES public.regra(id) ON DELETE CASCADE,
    chat_id   VARCHAR(64) NOT NULL
);

-- Destinos de uma regra (1:N)
CREATE TABLE public.regra_destino (
    id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    regra_id  UUID NOT NULL REFERENCES public.regra(id) ON DELETE CASCADE,
    chat_id   VARCHAR(64) NOT NULL
);

-- Pares filtro/substituição (1:N, ordenadas)
CREATE TABLE public.regra_filtro (
    id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    regra_id  UUID NOT NULL REFERENCES public.regra(id) ON DELETE CASCADE,
    busca     VARCHAR(256) NOT NULL,
    substitui VARCHAR(256) NOT NULL DEFAULT '',
    ordem     INT NOT NULL DEFAULT 0
);

-- Condições whitelist/blacklist (1:N)
CREATE TABLE public.regra_condicao (
    id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    regra_id  UUID NOT NULL REFERENCES public.regra(id) ON DELETE CASCADE,
    tipo      condicao_tipo NOT NULL,  -- 'whitelist' ou 'blacklist'
    valor     VARCHAR(256) NOT NULL
);
```

**Tabelas normalizadas para `agendamento`:**
```sql
CREATE TABLE public.agendamento (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    bot_id          UUID NOT NULL REFERENCES public.bot(id) ON DELETE CASCADE,
    nome            VARCHAR(64) NOT NULL,
    msg_id_atual    INTEGER NOT NULL DEFAULT 1,
    tipo_envio      envio_tipo NOT NULL DEFAULT 'sequencial',
    -- ⭐ Link para marketplace (NULL = sem conversão de link)
    marketplace_integracao_id UUID REFERENCES public.marketplace_integracao(id) ON DELETE SET NULL,
    filtro_midia    midia_tipo NOT NULL DEFAULT 'todos',
    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ
);

CREATE TABLE public.agendamento_origem (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agendamento_id  UUID NOT NULL REFERENCES public.agendamento(id) ON DELETE CASCADE,
    chat_id         VARCHAR(64) NOT NULL
);

CREATE TABLE public.agendamento_destino (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agendamento_id  UUID NOT NULL REFERENCES public.agendamento(id) ON DELETE CASCADE,
    chat_id         VARCHAR(64) NOT NULL
);

CREATE TABLE public.agendamento_horario (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agendamento_id  UUID NOT NULL REFERENCES public.agendamento(id) ON DELETE CASCADE,
    horario         TIME NOT NULL
);

CREATE TABLE public.agendamento_filtro (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agendamento_id  UUID NOT NULL REFERENCES public.agendamento(id) ON DELETE CASCADE,
    busca           VARCHAR(256) NOT NULL,
    substitui       VARCHAR(256) NOT NULL DEFAULT '',
    ordem           INT NOT NULL DEFAULT 0
);

CREATE TABLE public.agendamento_condicao (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agendamento_id  UUID NOT NULL REFERENCES public.agendamento(id) ON DELETE CASCADE,
    tipo            condicao_tipo NOT NULL,
    valor           VARCHAR(256) NOT NULL
);
```

**Tabela `log_execucao`:**
```sql
CREATE TABLE public.log_execucao (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    bot_id          UUID NOT NULL REFERENCES public.bot(id) ON DELETE SET NULL,
    regra_id        UUID REFERENCES public.regra(id) ON DELETE SET NULL,
    agendamento_id  UUID REFERENCES public.agendamento(id) ON DELETE SET NULL,
    origem          VARCHAR(128) NOT NULL,
    destino         VARCHAR(128) NOT NULL,
    status          log_status NOT NULL,
    mensagem        VARCHAR(512) NOT NULL,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Tabela `uso_mensal`** — Tracking de uso para billing/rate limiting:
```sql
CREATE TABLE public.uso_mensal (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id   UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    mes_ref     DATE NOT NULL,  -- primeiro dia do mês
    msgs_enviadas   INT NOT NULL DEFAULT 0,
    msgs_bloqueadas INT NOT NULL DEFAULT 0,
    regras_ativas   INT NOT NULL DEFAULT 0,
    
    CONSTRAINT unique_tenant_mes UNIQUE (tenant_id, mes_ref)
);
```

---

## 1.3 — Índices de Performance

#### Arquivo: `supabase/migrations/004_indexes.sql`

```sql
-- === Tenant ===
CREATE INDEX idx_tenant_owner ON public.tenant(owner_id) WHERE deletado_em IS NULL;
CREATE INDEX idx_tenant_plano ON public.tenant(plano) WHERE deletado_em IS NULL;

-- === Tenant Member ===
CREATE INDEX idx_tmember_user ON public.tenant_member(user_id);
CREATE INDEX idx_tmember_tenant ON public.tenant_member(tenant_id);

-- === Bot ===
CREATE INDEX idx_bot_tenant ON public.bot(tenant_id) WHERE deletado_em IS NULL;
CREATE INDEX idx_bot_ativo ON public.bot(tenant_id, ativo) WHERE deletado_em IS NULL;

-- === Marketplace Integração ===
CREATE INDEX idx_mkt_tenant ON public.marketplace_integracao(tenant_id) WHERE deletado_em IS NULL;
CREATE INDEX idx_mkt_tipo ON public.marketplace_integracao(tenant_id, tipo) WHERE deletado_em IS NULL;

-- === Regra ===
CREATE INDEX idx_regra_tenant ON public.regra(tenant_id) WHERE deletado_em IS NULL;
CREATE INDEX idx_regra_bot ON public.regra(bot_id) WHERE deletado_em IS NULL;
CREATE INDEX idx_regra_ativo ON public.regra(bot_id, ativo) WHERE deletado_em IS NULL;
CREATE INDEX idx_regra_mkt ON public.regra(marketplace_integracao_id) WHERE marketplace_integracao_id IS NOT NULL;

-- === Regra Filhos ===
CREATE INDEX idx_regra_origem_regra ON public.regra_origem(regra_id);
CREATE INDEX idx_regra_origem_chat ON public.regra_origem(chat_id);
CREATE INDEX idx_regra_destino_regra ON public.regra_destino(regra_id);
CREATE INDEX idx_regra_condicao_regra ON public.regra_condicao(regra_id);
CREATE INDEX idx_regra_filtro_regra ON public.regra_filtro(regra_id);

-- === Agendamento ===
CREATE INDEX idx_ag_tenant ON public.agendamento(tenant_id) WHERE deletado_em IS NULL;
CREATE INDEX idx_ag_bot ON public.agendamento(bot_id) WHERE deletado_em IS NULL;
CREATE INDEX idx_ag_ativo ON public.agendamento(bot_id, ativo) WHERE deletado_em IS NULL;

-- === Agendamento Filhos ===
CREATE INDEX idx_ag_origem_ag ON public.agendamento_origem(agendamento_id);
CREATE INDEX idx_ag_destino_ag ON public.agendamento_destino(agendamento_id);
CREATE INDEX idx_ag_horario_ag ON public.agendamento_horario(agendamento_id);
CREATE INDEX idx_ag_horario_val ON public.agendamento_horario(horario);
CREATE INDEX idx_ag_filtro_ag ON public.agendamento_filtro(agendamento_id);
CREATE INDEX idx_ag_condicao_ag ON public.agendamento_condicao(agendamento_id);

-- === Log ===
CREATE INDEX idx_log_tenant ON public.log_execucao(tenant_id);
CREATE INDEX idx_log_bot ON public.log_execucao(bot_id);
CREATE INDEX idx_log_status ON public.log_execucao(status);
CREATE INDEX idx_log_criado ON public.log_execucao(criado_em DESC);
CREATE INDEX idx_log_tenant_data ON public.log_execucao(tenant_id, criado_em DESC);

-- === Uso Mensal ===
CREATE INDEX idx_uso_tenant ON public.uso_mensal(tenant_id);
CREATE INDEX idx_uso_mes ON public.uso_mensal(mes_ref);
```

---

## 1.4 — Row-Level Security (RLS)

> [!CAUTION]
> RLS é a camada de segurança mais importante. Sem isso, um tenant pode acessar dados de outro. **Cada policy deve ser testada.**

#### Arquivo: `supabase/migrations/005_rls_policies.sql`

```sql
-- === Habilitar RLS em todas as tabelas ===
ALTER TABLE public.tenant ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tenant_member ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marketplace_integracao ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bot ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.regra ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.regra_origem ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.regra_destino ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.regra_filtro ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.regra_condicao ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agendamento ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agendamento_origem ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agendamento_destino ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agendamento_horario ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agendamento_filtro ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agendamento_condicao ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.log_execucao ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.uso_mensal ENABLE ROW LEVEL SECURITY;

-- === Função helper: retorna tenant_ids do usuário logado ===
CREATE OR REPLACE FUNCTION public.get_user_tenant_ids()
RETURNS SETOF UUID
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT tenant_id FROM public.tenant_member
    WHERE user_id = auth.uid()
$$;

-- === Policies para TENANT ===
CREATE POLICY "Membros veem seus tenants"
    ON public.tenant FOR SELECT
    USING (id IN (SELECT public.get_user_tenant_ids()));

CREATE POLICY "Owner pode atualizar tenant"
    ON public.tenant FOR UPDATE
    USING (owner_id = auth.uid());

CREATE POLICY "Usuário autenticado cria tenant"
    ON public.tenant FOR INSERT
    WITH CHECK (owner_id = auth.uid());

-- === Policies para BOT (exemplo — mesmo padrão para regra, agendamento, etc.) ===
CREATE POLICY "Membros veem bots do tenant"
    ON public.bot FOR SELECT
    USING (tenant_id IN (SELECT public.get_user_tenant_ids()));

CREATE POLICY "Admin/Owner gerencia bots"
    ON public.bot FOR ALL
    USING (
        tenant_id IN (
            SELECT tenant_id FROM public.tenant_member
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin')
        )
    );

-- (Mesmo padrão se repete para regra, agendamento, log_execucao, uso_mensal)
-- Tabelas filhas (regra_origem, etc.) herdam acesso via JOIN com a tabela pai
```

---

## 1.5 — Funções de Criptografia

> [!WARNING]
> Session strings, API hashes, tokens de bot e telefones são dados **extremamente sensíveis**. Devem ser criptografados at-rest.

#### Arquivo: `supabase/migrations/006_crypto_functions.sql`

```sql
-- Funções de encrypt/decrypt usando pgcrypto + chave do app
-- A chave vem de uma variável de configuração do Supabase (vault)

CREATE OR REPLACE FUNCTION public.encrypt_sensitive(plaintext TEXT)
RETURNS BYTEA
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN pgp_sym_encrypt(
        plaintext,
        current_setting('app.encryption_key', true)
    );
END;
$$;

CREATE OR REPLACE FUNCTION public.decrypt_sensitive(ciphertext BYTEA)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN pgp_sym_decrypt(
        ciphertext,
        current_setting('app.encryption_key', true)
    );
END;
$$;
```

---

## 1.6 — Triggers de Auditoria

#### Arquivo: `supabase/migrations/007_triggers.sql`

```sql
-- Auto-atualiza "atualizado_em" em qualquer UPDATE
CREATE OR REPLACE FUNCTION public.set_atualizado_em()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplica em todas as tabelas com atualizado_em
CREATE TRIGGER tr_tenant_updated BEFORE UPDATE ON public.tenant
    FOR EACH ROW EXECUTE FUNCTION public.set_atualizado_em();
CREATE TRIGGER tr_mkt_updated BEFORE UPDATE ON public.marketplace_integracao
    FOR EACH ROW EXECUTE FUNCTION public.set_atualizado_em();
CREATE TRIGGER tr_bot_updated BEFORE UPDATE ON public.bot
    FOR EACH ROW EXECUTE FUNCTION public.set_atualizado_em();
CREATE TRIGGER tr_regra_updated BEFORE UPDATE ON public.regra
    FOR EACH ROW EXECUTE FUNCTION public.set_atualizado_em();
CREATE TRIGGER tr_agendamento_updated BEFORE UPDATE ON public.agendamento
    FOR EACH ROW EXECUTE FUNCTION public.set_atualizado_em();

-- Incrementar contador de mensagens (rate limiting)
CREATE OR REPLACE FUNCTION public.incrementar_uso_msgs()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.uso_mensal (tenant_id, mes_ref, msgs_enviadas)
    VALUES (
        NEW.tenant_id,
        date_trunc('month', NOW())::DATE,
        1
    )
    ON CONFLICT (tenant_id, mes_ref) DO UPDATE
    SET msgs_enviadas = uso_mensal.msgs_enviadas + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_log_incrementa_uso
    AFTER INSERT ON public.log_execucao
    FOR EACH ROW
    WHEN (NEW.status = 'sucesso')
    EXECUTE FUNCTION public.incrementar_uso_msgs();
```

---

## 1.7 — Migração de Dados Existentes

#### Arquivo: `supabase/migrations/008_seed_existing_data.sql`

```sql
-- Migra dados do schema antigo para o novo
-- Executar APÓS importar o dump antigo em schema temporário

-- 1. Criar tenant para o owner original
-- 2. Migrar bots (com encrypt)
-- 3. Migrar regras (normalizando campos comma-separated)
-- 4. Migrar agendamentos (normalizando)
-- 5. Migrar logs

-- (Script detalhado será gerado na execução)
```

---

# FASE 2 — Refatoração do Backend (API Multi-Tenant)

## 2.1 — Reestruturação do Projeto

### Nova Estrutura de Diretórios

```
conektabots/
├── .project/                  ← ⭐ Tracking multi-agente (detalhes abaixo)
│   ├── roadmap.md             ← Tarefas por fase com status [todo/doing/done]
│   ├── state.md               ← Snapshot do estado atual do projeto
│   ├── changelog.md           ← Log append-only de cada mudança
│   └── conventions.md         ← Regras para agentes IA
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          ← Settings via Pydantic
│   │   ├── database.py        ← Async engine + Supabase
│   │   ├── deps.py            ← Dependencies (session, current_user, tenant)
│   │   ├── security.py        ← NEW: JWT validation, encryption helpers
│   │   └── exceptions.py      ← NEW: Custom exceptions + handlers
│   ├── models/
│   │   ├── __init__.py
│   │   ├── tenant.py          ← NEW
│   │   ├── tenant_member.py   ← NEW
│   │   ├── marketplace.py     ← NEW: marketplace_integracao
│   │   ├── bot.py             ← REFACTORED
│   │   ├── regra.py           ← REFACTORED (+ tabelas filhas)
│   │   ├── agendamento.py     ← REFACTORED (+ tabelas filhas)
│   │   ├── log.py             ← REFACTORED
│   │   ├── uso.py             ← NEW: uso_mensal
│   │   └── enums.py           ← NEW: todos os enums
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py            ← NEW: SignUp, Login, Token
│   │   ├── tenant.py          ← NEW
│   │   ├── bot.py             ← NEW: Create/Update/Response DTOs
│   │   ├── regra.py           ← NEW
│   │   ├── agendamento.py     ← NEW
│   │   ├── log.py             ← NEW
│   │   └── common.py          ← NEW: PaginatedResponse, etc.
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py    ← NEW: Supabase Auth integration
│   │   ├── tenant_service.py  ← NEW: CRUD tenant + limites
│   │   ├── bot_service.py     ← NEW: CRUD bot + criptografia
│   │   ├── regra_service.py   ← NEW: CRUD regra normalizada
│   │   ├── agendamento_service.py ← NEW
│   │   ├── log_service.py     ← NEW
│   │   ├── marketplace_service.py ← NEW: CRUD integrações + link conversion
│   │   ├── crypto_service.py  ← NEW: encrypt/decrypt helpers
│   │   └── quota_service.py   ← NEW: rate limiting + plano checks
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py            ← NEW: /auth/signup, /auth/login, etc.
│   │   ├── tenants.py         ← NEW: /tenants CRUD
│   │   ├── bots.py            ← REFACTORED: API REST JSON
│   │   ├── regras.py          ← REFACTORED: API REST JSON
│   │   ├── agendamentos.py    ← REFACTORED: API REST JSON
│   │   ├── logs.py            ← NEW: GET com paginação
│   │   └── health.py          ← NEW: /health endpoint
│   └── middleware/
│       ├── __init__.py
│       ├── auth.py            ← NEW: JWT middleware
│       ├── tenant.py          ← NEW: tenant context injection
│       └── rate_limit.py      ← NEW: rate limiting
├── worker/                    ← REFACTORED from worker.py
│   ├── __init__.py
│   ├── bot_worker.py          ← BotWorker class (limpa)
│   ├── message_processor.py   ← Lógica de processamento
│   ├── queue_manager.py       ← Fila de envio
│   ├── marketplace_clients/   ← ⭐ Clientes de API por marketplace
│   │   ├── __init__.py
│   │   ├── base.py            ← ABC: MarketplaceClient interface
│   │   ├── shopee.py          ← ShopeeClient (extraído)
│   │   ├── mercado_livre.py   ← MercadoLivreClient
│   │   ├── amazon.py          ← AmazonClient
│   │   ├── magalu.py          ← MagaluClient
│   │   └── factory.py         ← get_client(marketplace_tipo) → Client
│   └── scheduler.py           ← Loop de agendamentos
├── manager.py                 ← REFACTORED: multi-tenant aware
├── main.py                    ← REFACTORED: com middleware
├── supabase/
│   └── migrations/            ← SQL files (Fase 1)
├── tests/
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_auth.py
│   ├── test_tenant_isolation.py
│   ├── test_bot_crud.py
│   ├── test_regra_crud.py
│   ├── test_worker.py
│   └── test_crypto.py
├── alembic/                   ← Mantido para migrações incrementais
├── .agents/
│   ├── skills/
│   │   ├── supabase/
│   │   │   └── SKILL.md       ← Como criar migrations, rodar SQL, testar RLS
│   │   ├── models/
│   │   │   └── SKILL.md       ← Convenções de models (UUID, timestamps, soft delete)
│   │   ├── api/
│   │   │   └── SKILL.md       ← Padrões REST (DTOs, paginação, error handling)
│   │   ├── security/
│   │   │   └── SKILL.md       ← Auth JWT, criptografia, RLS, rate limiting
│   │   ├── marketplace/
│   │   │   └── SKILL.md       ← Como adicionar novo marketplace client
│   │   └── testing/
│   │       └── SKILL.md       ← Como escrever testes (fixtures, isolamento tenant)
│   └── workflows/
│       ├── new-model.md       ← Passo a passo: criar model + schema + service + router
│       ├── new-migration.md   ← Passo a passo: criar migration Supabase
│       ├── new-marketplace.md ← Passo a passo: adicionar marketplace novo
│       ├── deploy.md          ← Passo a passo: deploy staging/prod
│       └── debug-worker.md   ← Passo a passo: debugar bot worker
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## 2.2 — Core: Config, Database, Security

### Tarefas Detalhadas

#### `app/core/config.py` — Settings centralizadas
- [ ] Usar `pydantic-settings` para validação de env vars
- [ ] Definir `Settings` class com todos os campos tipados
- [ ] Separar configs por environment (dev/staging/prod)
- [ ] Adicionar `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- [ ] Adicionar `ENCRYPTION_KEY` para pgcrypto

#### `app/core/database.py` — Async engine
- [ ] Trocar `create_engine` sync por `create_async_engine` (asyncpg)
- [ ] Configurar connection pooling (pool_size, max_overflow)
- [ ] Async session factory
- [ ] Manter suporte a Alembic (sync fallback para migrações)

#### `app/core/security.py` — Autenticação e Criptografia
- [ ] Validação de JWT do Supabase Auth
- [ ] Extração de `user_id` do token
- [ ] Funções `encrypt_field()` / `decrypt_field()` para dados sensíveis
- [ ] Rate limiting decorator baseado em `tenant.limite_msgs_hora`
- [ ] CORS configuration

#### `app/core/deps.py` — Dependency Injection
- [ ] `get_async_session()` — async DB session
- [ ] `get_current_user()` — extrai user do JWT
- [ ] `get_current_tenant()` — resolve tenant do user
- [ ] `require_role(roles)` — verifica permissões
- [ ] `check_quota(resource)` — verifica limites do plano

#### `app/core/exceptions.py` — Exception Handlers
- [ ] `TenantNotFoundError`, `QuotaExceededError`, `UnauthorizedError`
- [ ] Global exception handler com respostas padronizadas
- [ ] Logging estruturado de erros

---

## 2.3 — Models (SQLModel Refatorados)

### Tarefas por Modelo

#### `app/models/enums.py`
- [ ] Definir todos os enums Python mapeados para os PG enums

#### `app/models/tenant.py`
- [ ] Model `Tenant` com relationships para members, bots, regras, agendamentos
- [ ] Validações: nome mínimo 2 chars, plano válido

#### `app/models/bot.py`
- [ ] Adicionar `tenant_id` (UUID FK)
- [ ] `api_id` → `int` (era string incorretamente)
- [ ] Campos sensíveis como `bytes` (criptografados)
- [ ] Timestamps + soft delete
- [ ] Property helpers: `api_hash` (decrypt on access)

#### `app/models/marketplace.py`
- [ ] Model `MarketplaceIntegracao` com `tipo` (enum), `credenciais_enc` (BYTEA), `endpoint_url`
- [ ] Relationship com tenant
- [ ] Property helper: `credenciais` (decrypt JSON on access)
- [ ] Timestamps + soft delete

#### `app/models/regra.py`
- [ ] Remover campos comma-separated (`origem`, `destino`, `filtro`, etc.)
- [ ] Remover `converter_shopee` → substituir por `marketplace_integracao_id` FK (nullable)
- [ ] Adicionar relationships para `RegraOrigem`, `RegraDestino`, `RegraFiltro`, `RegraCondicao`
- [ ] `tenant_id` obrigatório
- [ ] Timestamps + soft delete

#### `app/models/agendamento.py`
- [ ] Mesma normalização que regra
- [ ] `horario` → tabela separada `AgendamentoHorario` com tipo `TIME`
- [ ] Timestamps + soft delete

#### `app/models/log.py`
- [ ] Remover `bot_nome` (redundante — vem via JOIN)
- [ ] Adicionar `tenant_id`, `regra_id`, `agendamento_id`
- [ ] `status` como enum
- [ ] Renomear `data_hora` → `criado_em`

---

## 2.4 — Schemas (DTOs Pydantic)

### Padrão para cada recurso

```
├── schemas/
│   ├── bot.py
│   │   ├── BotCreate          ← Input para criação
│   │   ├── BotUpdate          ← Input para atualização (partial)
│   │   ├── BotResponse        ← Output (sem dados sensíveis!)
│   │   └── BotListResponse    ← Lista paginada
```

- [ ] **Nunca expor** campos criptografados na response
- [ ] Paginação padrão: `PaginatedResponse[T]` com `items`, `total`, `page`, `per_page`
- [ ] Validação de input com `Field(min_length=..., max_length=...)`

---

## 2.5 — Services (Lógica de Negócio)

> [!IMPORTANT]
> **Regra de ouro:** Routers nunca acessam o banco diretamente. Sempre via Service.

#### `app/services/auth_service.py`
- [ ] `signup(email, password)` → cria user no Supabase Auth + tenant + member
- [ ] `login(email, password)` → retorna JWT
- [ ] `refresh_token(token)` → renova JWT
- [ ] `reset_password(email)` → envia email de reset

#### `app/services/tenant_service.py`
- [ ] `create_tenant(user_id, nome)` → cria tenant com limites do plano free
- [ ] `get_tenant(tenant_id)` → com validação de acesso
- [ ] `update_tenant(tenant_id, data)` → atualiza nome
- [ ] `invite_member(tenant_id, email, role)` → convite por email
- [ ] `upgrade_plan(tenant_id, plano)` → altera limites

#### `app/services/marketplace_service.py`
- [ ] `create_integracao(tenant_id, tipo, nome, credenciais)` → valida quota + criptografa
- [ ] `get_integracoes(tenant_id)` → lista por tenant
- [ ] `update_integracao(tenant_id, id, data)` → re-criptografa credenciais
- [ ] `delete_integracao(tenant_id, id)` → soft delete
- [ ] `converter_link(integracao_id, url)` → despacha para o client correto
- [ ] `get_client(integracao)` → factory: retorna ShopeeClient/MLClient/etc

#### `app/services/bot_service.py`
- [ ] `create_bot(tenant_id, data)` → valida quota + criptografa campos
- [ ] `get_bots(tenant_id)` → lista com soft delete filter
- [ ] `update_bot(tenant_id, bot_id, data)` → atualiza + re-criptografa
- [ ] `delete_bot(tenant_id, bot_id)` → soft delete
- [ ] `toggle_bot(tenant_id, bot_id)` → ativa/desativa
- [ ] `decrypt_bot_credentials(bot)` → retorna dados plain para worker

#### `app/services/regra_service.py`
- [ ] `create_regra(tenant_id, data)` → valida quota + cria filhos normalizados
- [ ] `update_regra(tenant_id, regra_id, data)` → replace filhos (delete + insert)
- [ ] `get_regras_com_detalhes(bot_id)` → JOIN com origens, destinos, filtros, condições
- [ ] `delete_regra(tenant_id, regra_id)` → soft delete

#### `app/services/quota_service.py`
- [ ] `check_can_create(tenant_id, resource_type)` → verifica limites do plano
- [ ] `check_rate_limit(tenant_id)` → verifica msgs/hora
- [ ] `get_usage(tenant_id, month)` → retorna uso do mês

#### `app/services/crypto_service.py`
- [ ] `encrypt(plaintext)` → usa `ENCRYPTION_KEY` via Fernet ou pgcrypto
- [ ] `decrypt(ciphertext)` → retorna plaintext
- [ ] Key rotation support preparado

---

## 2.6 — Routers (API REST)

### Padrão de Rotas

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/auth/signup` | Cadastro |
| `POST` | `/auth/login` | Login → JWT |
| `POST` | `/auth/refresh` | Refresh token |
| `POST` | `/auth/reset-password` | Reset senha |
| `GET` | `/tenants` | Lista tenants do user |
| `POST` | `/tenants` | Cria tenant |
| `PATCH` | `/tenants/{id}` | Atualiza tenant |
| `GET` | `/tenants/{id}/usage` | Uso mensal |
| `GET` | `/marketplaces` | ⭐ Lista integrações do tenant |
| `POST` | `/marketplaces` | ⭐ Cria integração (Shopee/ML/Amazon...) |
| `PATCH` | `/marketplaces/{id}` | ⭐ Atualiza credenciais |
| `DELETE` | `/marketplaces/{id}` | ⭐ Soft delete |
| `POST` | `/marketplaces/{id}/test` | ⭐ Testa conexão com API do marketplace |
| `GET` | `/bots` | Lista bots (filtrado por tenant) |
| `POST` | `/bots` | Cria bot (valida quota) |
| `GET` | `/bots/{id}` | Detalhe bot |
| `PATCH` | `/bots/{id}` | Atualiza bot |
| `DELETE` | `/bots/{id}` | Soft delete |
| `POST` | `/bots/{id}/toggle` | Ativa/desativa |
| `GET` | `/regras` | Lista regras |
| `POST` | `/regras` | Cria regra (com marketplace_id opcional) |
| `GET` | `/regras/{id}` | Detalhe com origens/destinos/filtros |
| `PUT` | `/regras/{id}` | Full update |
| `DELETE` | `/regras/{id}` | Soft delete |
| `POST` | `/regras/{id}/toggle` | Ativa/desativa |
| `GET` | `/agendamentos` | Lista agendamentos |
| `POST` | `/agendamentos` | Cria agendamento |
| `GET` | `/agendamentos/{id}` | Detalhe |
| `PUT` | `/agendamentos/{id}` | Full update |
| `DELETE` | `/agendamentos/{id}` | Soft delete |
| `POST` | `/agendamentos/{id}/toggle` | Ativa/desativa |
| `POST` | `/agendamentos/{id}/enviar` | Envio manual |
| `GET` | `/logs` | Lista logs (paginado, filtrado) |
| `GET` | `/health` | Health check |

Todas as rotas (exceto `/auth/*` e `/health`):
- Requerem header `Authorization: Bearer <JWT>`
- Filtram automaticamente por `tenant_id` do user
- Retornam JSON padronizado

---

## 2.7 — Worker Refatorado

### Tarefas

- [ ] Criar `worker/marketplace_clients/base.py` — interface `MarketplaceClient` (ABC)
- [ ] Implementar `ShopeeClient` (extraído do `ShopeeAPI` atual)
- [ ] Implementar `MercadoLivreClient`, `AmazonClient`, `MagaluClient` (stubs iniciais)
- [ ] Criar `worker/marketplace_clients/factory.py` — `get_client(tipo) → MarketplaceClient`
- [ ] Extrair `aplicar_processamento_mensagem` → `worker/message_processor.py`
- [ ] Extrair lógica de fila → `worker/queue_manager.py`
- [ ] Extrair lógica de agendamento → `worker/scheduler.py`
- [ ] `BotWorker` carrega `marketplace_integracao` da regra e usa o client correto
- [ ] `BotWorker` usa queries normalizadas (JOINs com tabelas filhas)
- [ ] `BotWorker` decripta credenciais via `crypto_service` antes de conectar
- [ ] Rate limiting: verificar `uso_mensal.msgs_enviadas` vs `tenant.limite_msgs_hora` antes de enviar
- [ ] Manager carrega workers agrupados por tenant

### Mudanças na Query de Regras (exemplo)

```python
# ANTES (string parsing)
regras_raw = session.exec(select(Regra).where(Regra.bot_id == self.bot_id))
for r in regras_raw:
    origens = r.origem.split(",")  # ← frágil!

# DEPOIS (JOIN normalizado)
stmt = (
    select(Regra)
    .where(Regra.bot_id == self.bot_id, Regra.ativo == True, Regra.deletado_em == None)
    .options(
        selectinload(Regra.origens),
        selectinload(Regra.destinos),
        selectinload(Regra.filtros),
        selectinload(Regra.condicoes),
    )
)
regras = await session.exec(stmt)
for r in regras:
    origens = [o.chat_id for o in r.origens]  # ← tipado!
```

---

## 2.8 — Middleware

#### `app/middleware/auth.py`
- [ ] Intercepta todas as requests (exceto whitelist)
- [ ] Valida JWT do Supabase
- [ ] Injeta `request.state.user_id`

#### `app/middleware/tenant.py`
- [ ] Resolve tenant do user
- [ ] Injeta `request.state.tenant_id`
- [ ] Header opcional `X-Tenant-ID` para users multi-tenant

#### `app/middleware/rate_limit.py`
- [ ] Verifica `tenant.limite_msgs_hora` vs uso atual
- [ ] Retorna `429 Too Many Requests` quando excedido

---

## 2.9 — Testes de Segurança

> [!CAUTION]
> Testes de isolamento multi-tenant são **obrigatórios** antes de deploy.

- [ ] `test_tenant_isolation.py` — Tenant A não acessa dados de Tenant B
- [ ] `test_auth.py` — JWT inválido/expirado retorna 401
- [ ] `test_crypto.py` — Dados criptografados não são legíveis sem chave
- [ ] `test_rls.py` — RLS policies bloqueiam acesso direto ao banco
- [ ] `test_quota.py` — Plano free é bloqueado ao exceder limites
- [ ] `test_rate_limit.py` — Rate limiting funciona corretamente

---

# FASE 3 — Frontend (Next.js + React)

> [!NOTE]
> Executar **após** Fases 1-2 estarem validadas e testadas.

## 3.1 — Setup do Projeto

- [ ] `npx -y create-next-app@latest ./frontend` (App Router, TypeScript, Tailwind)
- [ ] Integrar Supabase Auth client-side (`@supabase/supabase-js`)
- [ ] Configurar API client (axios/fetch) apontando para FastAPI

## 3.2 — Páginas

| Página | Rota | Descrição |
|--------|------|-----------|
| Landing | `/` | Marketing + pricing |
| Login | `/login` | Supabase Auth UI |
| Signup | `/signup` | Cadastro + criação de tenant |
| Dashboard | `/dashboard` | Overview: bots, regras, logs recentes |
| Bots | `/dashboard/bots` | CRUD de bots |
| Regras | `/dashboard/regras` | CRUD de regras (normalizado) |
| Agendamentos | `/dashboard/agendamentos` | CRUD de agendamentos |
| Logs | `/dashboard/logs` | Tabela paginada + filtros |
| Marketplaces | `/dashboard/marketplaces` | ⭐ CRUD integrações (Shopee, ML, Amazon...) |
| Configurações | `/dashboard/configuracoes` | Perfil, plano |
| Billing | `/dashboard/billing` | Plano atual, upgrade |

---

# FASE 4 — Deploy & DevOps

## 4.1 — Infraestrutura

| Serviço | Ferramenta | Custo Estimado |
|---------|-----------|---------------|
| Database | Supabase (free→pro) | R$0-125/mês |
| Backend API | Railway ou Render | R$5-50/mês |
| Frontend | Vercel | R$0/mês (free tier) |
| CI/CD | GitHub Actions | R$0 |
| Monitoring | Sentry (free tier) | R$0 |

## 4.2 — Tarefas
- [ ] Configurar GitHub Actions (lint, test, deploy)
- [ ] Docker-compose simplificado (sem PG local)
- [ ] Environment separation (dev/staging/prod)
- [ ] Sentry para error tracking
- [ ] Health check endpoints

---

# Cronograma Estimado

```mermaid
gantt
    title ConektaBots → SaaS MVP
    dateFormat YYYY-MM-DD
    
    section Fase 1 - Database
    Setup Supabase + Extensions       :f1a, 2026-04-15, 1d
    Schema Core (tenant, bot)          :f1b, after f1a, 2d
    Schema Normalizado (regra, ag)     :f1c, after f1b, 2d
    Índices + RLS Policies             :f1d, after f1c, 2d
    Crypto Functions + Triggers        :f1e, after f1d, 1d
    Migração dados existentes          :f1f, after f1e, 1d
    Testes de Schema                   :f1g, after f1f, 1d
    
    section Fase 2 - Backend
    Core (config, database, security)  :f2a, after f1g, 3d
    Models refatorados                 :f2b, after f2a, 3d
    Schemas (DTOs)                     :f2c, after f2b, 2d
    Services (auth, tenant, CRUD)      :f2d, after f2c, 4d
    Services (crypto, quota, shopee)   :f2e, after f2d, 2d
    Routers (API REST)                 :f2f, after f2e, 3d
    Middleware (auth, tenant, rate)     :f2g, after f2f, 2d
    Worker refatorado                  :f2h, after f2g, 3d
    Manager multi-tenant               :f2i, after f2h, 1d
    Testes de segurança                :f2j, after f2i, 3d
    
    section Fase 3 - Frontend
    Setup Next.js + Auth               :f3a, after f2j, 2d
    Landing + Login/Signup             :f3b, after f3a, 3d
    Dashboard + CRUD pages             :f3c, after f3b, 5d
    Logs + Config + Billing            :f3d, after f3c, 3d
    Polish + Responsividade            :f3e, after f3d, 2d
    
    section Fase 4 - Deploy
    CI/CD + Docker                     :f4a, after f3e, 2d
    Deploy staging                     :f4b, after f4a, 1d
    Testes E2E                         :f4c, after f4b, 2d
    Deploy produção                    :f4d, after f4c, 1d
```

**Estimativa total: ~8-10 semanas** (trabalhando consistentemente)

---

# Limites por Plano (Confirmado)

| Recurso | Free | Starter (R$29) | Pro (R$79) | Enterprise |
|---------|------|----------------|------------|------------|
| Bots | 1 | 3 | 10 | Custom |
| Regras | 3 | 10 | Ilimitado | Custom |
| Agendamentos | 2 | 10 | Ilimitado | Custom |
| **Msgs/hora** | **50** | 500 | Ilimitado | Custom |
| **Marketplaces** | **1** | 3 | Todos | Custom |
| Logs (retenção) | 7 dias | 30 dias | 90 dias | Ilimitado |
| Membros | 1 | 3 | 10 | Custom |
| Suporte | Comunidade | Email | Prioritário | Dedicado |

---

