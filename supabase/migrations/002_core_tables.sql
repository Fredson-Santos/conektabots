-- ============================================================
-- Migration 002: Tabelas Core (Multi-Tenant)
-- ConektaBots SaaS MVP
-- Data: 2026-04-14
-- ============================================================

BEGIN;

-- ────────────────────────────────────────────────────────────
-- tenant — Organização/empresa (raiz do multi-tenancy)
-- ────────────────────────────────────────────────────────────
CREATE TABLE public.tenant (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome            VARCHAR(100) NOT NULL,
    slug            VARCHAR(100) UNIQUE NOT NULL,
    plano           public.plano_tipo NOT NULL DEFAULT 'free',

    -- Limites por plano (desnormalizados para performance)
    limite_bots             INTEGER NOT NULL DEFAULT 2,
    limite_regras           INTEGER NOT NULL DEFAULT 5,
    limite_agendamentos     INTEGER NOT NULL DEFAULT 5,
    limite_msgs_hora        INTEGER NOT NULL DEFAULT 50,

    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ
);

COMMENT ON TABLE public.tenant IS 'Organização/empresa — raiz do isolamento multi-tenant';
COMMENT ON COLUMN public.tenant.slug IS 'Identificador URL-safe único (ex: minha-empresa)';
COMMENT ON COLUMN public.tenant.plano IS 'Plano ativo: free, starter, pro, enterprise';

-- ────────────────────────────────────────────────────────────
-- tenant_member — Liga auth.users a um tenant com papel
-- ────────────────────────────────────────────────────────────
CREATE TABLE public.tenant_member (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role            public.membro_role NOT NULL DEFAULT 'viewer',

    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ,

    UNIQUE(tenant_id, user_id)
);

COMMENT ON TABLE public.tenant_member IS 'Associação entre usuário Supabase Auth e tenant';

-- ────────────────────────────────────────────────────────────
-- marketplace_integracao — Credenciais de marketplace
-- ────────────────────────────────────────────────────────────
CREATE TABLE public.marketplace_integracao (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    tipo            public.marketplace_tipo NOT NULL,
    nome            VARCHAR(100) NOT NULL,

    -- Credenciais armazenadas como JSON criptografado
    -- Ex: {"app_id": 123, "app_secret": "xxx", "access_token": "yyy"}
    credenciais_enc BYTEA,

    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ
);

COMMENT ON TABLE public.marketplace_integracao IS 'Integrações com marketplaces (credenciais criptografadas)';
COMMENT ON COLUMN public.marketplace_integracao.credenciais_enc IS 'JSON criptografado via pgp_sym_encrypt — NUNCA retornar em API responses';

-- ────────────────────────────────────────────────────────────
-- bot — Contas Telegram (user ou bot)
-- ────────────────────────────────────────────────────────────
CREATE TABLE public.bot (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id           UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    nome                VARCHAR(64) NOT NULL,
    api_id              INTEGER,
    tipo                public.bot_tipo NOT NULL DEFAULT 'user',
    phone               VARCHAR(64),

    -- Campos sensíveis criptografados (BYTEA)
    api_hash_enc        BYTEA,
    bot_token_enc       BYTEA,
    session_string_enc  BYTEA,

    ativo               BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em         TIMESTAMPTZ
);

COMMENT ON TABLE public.bot IS 'Contas Telegram — credenciais sensíveis em campos _enc (criptografados)';
COMMENT ON COLUMN public.bot.api_hash_enc IS 'api_hash criptografado — NUNCA retornar em API responses';
COMMENT ON COLUMN public.bot.session_string_enc IS 'Session string criptografada — NUNCA retornar em API responses';

COMMIT;
