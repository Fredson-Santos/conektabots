-- ============================================================
-- Migration 003: Tabelas Normalizadas
-- ConektaBots SaaS MVP
-- Data: 2026-04-14
-- ============================================================

BEGIN;

-- ╔══════════════════════════════════════════════════════════╗
-- ║  REGRA + TABELAS FILHAS                                 ║
-- ╚══════════════════════════════════════════════════════════╝

-- ────────────────────────────────────────────────────────────
-- regra — Tabela mãe de regras de encaminhamento
-- ────────────────────────────────────────────────────────────
CREATE TABLE public.regra (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id               UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    nome                    VARCHAR(64) NOT NULL,
    bot_id                  UUID NOT NULL REFERENCES public.bot(id) ON DELETE CASCADE,
    marketplace_integracao_id UUID REFERENCES public.marketplace_integracao(id) ON DELETE SET NULL,

    -- Configurações
    substituto              VARCHAR(255),
    filtro_midia            public.filtro_midia_tipo NOT NULL DEFAULT 'todos',
    converter_link          BOOLEAN NOT NULL DEFAULT FALSE,

    ativo                   BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em             TIMESTAMPTZ
);

COMMENT ON TABLE public.regra IS 'Regras de encaminhamento automático de mensagens';
COMMENT ON COLUMN public.regra.converter_link IS 'Converter links de afiliado (ex: shopee) — substitui antigo converter_shopee';

-- ────────────────────────────────────────────────────────────
-- regra_origem — Canais de origem (N por regra)
-- ────────────────────────────────────────────────────────────
CREATE TABLE public.regra_origem (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id   UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    regra_id    UUID NOT NULL REFERENCES public.regra(id) ON DELETE CASCADE,
    origem      VARCHAR(255) NOT NULL,

    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ,

    UNIQUE(regra_id, origem)
);

-- ────────────────────────────────────────────────────────────
-- regra_destino — Canais de destino (N por regra)
-- ────────────────────────────────────────────────────────────
CREATE TABLE public.regra_destino (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id   UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    regra_id    UUID NOT NULL REFERENCES public.regra(id) ON DELETE CASCADE,
    destino     VARCHAR(255) NOT NULL,

    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ,

    UNIQUE(regra_id, destino)
);

-- ────────────────────────────────────────────────────────────
-- regra_filtro — Palavras-chave (incluir OU bloquear, N por regra)
-- ────────────────────────────────────────────────────────────
CREATE TABLE public.regra_filtro (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id   UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    regra_id    UUID NOT NULL REFERENCES public.regra(id) ON DELETE CASCADE,
    tipo        public.filtro_regra_tipo NOT NULL DEFAULT 'incluir',
    valor       VARCHAR(255) NOT NULL,

    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ,

    UNIQUE(regra_id, tipo, valor)
);

COMMENT ON TABLE public.regra_filtro IS 'Filtros de palavras-chave: tipo=incluir (whitelist) ou tipo=bloquear (blacklist)';

-- ────────────────────────────────────────────────────────────
-- regra_condicao — Condições obrigatórias (somente_se_tiver)
-- ────────────────────────────────────────────────────────────
CREATE TABLE public.regra_condicao (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id   UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    regra_id    UUID NOT NULL REFERENCES public.regra(id) ON DELETE CASCADE,
    condicao    VARCHAR(255) NOT NULL,

    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ,

    UNIQUE(regra_id, condicao)
);

COMMENT ON TABLE public.regra_condicao IS 'Condições obrigatórias — mensagem só encaminha se contiver TODAS';


-- ╔══════════════════════════════════════════════════════════╗
-- ║  AGENDAMENTO + TABELAS FILHAS                           ║
-- ╚══════════════════════════════════════════════════════════╝

-- ────────────────────────────────────────────────────────────
-- agendamento — Tabela mãe de agendamentos
-- ────────────────────────────────────────────────────────────
CREATE TABLE public.agendamento (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id               UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    nome                    VARCHAR(64) NOT NULL,
    bot_id                  UUID NOT NULL REFERENCES public.bot(id) ON DELETE CASCADE,
    marketplace_integracao_id UUID REFERENCES public.marketplace_integracao(id) ON DELETE SET NULL,

    -- Controle de sequência
    msg_id_atual            INTEGER NOT NULL DEFAULT 0,
    tipo_envio              public.tipo_envio NOT NULL DEFAULT 'sequencial',

    -- Configurações
    substituto              VARCHAR(255),
    filtro_midia            public.filtro_midia_tipo NOT NULL DEFAULT 'todos',

    ativo                   BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em             TIMESTAMPTZ
);

COMMENT ON TABLE public.agendamento IS 'Agendamentos de envio automático de mensagens em horários definidos';

-- ────────────────────────────────────────────────────────────
-- agendamento_origem — Canais de origem (N por agendamento)
-- ────────────────────────────────────────────────────────────
CREATE TABLE public.agendamento_origem (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    agendamento_id  UUID NOT NULL REFERENCES public.agendamento(id) ON DELETE CASCADE,
    origem          VARCHAR(255) NOT NULL,

    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ,

    UNIQUE(agendamento_id, origem)
);

-- ────────────────────────────────────────────────────────────
-- agendamento_destino — Canais de destino (N por agendamento)
-- ────────────────────────────────────────────────────────────
CREATE TABLE public.agendamento_destino (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    agendamento_id  UUID NOT NULL REFERENCES public.agendamento(id) ON DELETE CASCADE,
    destino         VARCHAR(255) NOT NULL,

    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ,

    UNIQUE(agendamento_id, destino)
);

-- ────────────────────────────────────────────────────────────
-- agendamento_horario — Horários de disparo (N por agendamento)
-- ────────────────────────────────────────────────────────────
CREATE TABLE public.agendamento_horario (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    agendamento_id  UUID NOT NULL REFERENCES public.agendamento(id) ON DELETE CASCADE,
    horario         TIME NOT NULL,

    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ,

    UNIQUE(agendamento_id, horario)
);

COMMENT ON TABLE public.agendamento_horario IS 'Horários individuais — substitui o antigo campo comma-separated "12:26,19:39"';

-- ────────────────────────────────────────────────────────────
-- agendamento_filtro — Palavras-chave (incluir ou bloquear)
-- ────────────────────────────────────────────────────────────
CREATE TABLE public.agendamento_filtro (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    agendamento_id  UUID NOT NULL REFERENCES public.agendamento(id) ON DELETE CASCADE,
    tipo            public.filtro_regra_tipo NOT NULL DEFAULT 'incluir',
    valor           VARCHAR(255) NOT NULL,

    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ,

    UNIQUE(agendamento_id, tipo, valor)
);

-- ────────────────────────────────────────────────────────────
-- agendamento_condicao — Condições obrigatórias
-- ────────────────────────────────────────────────────────────
CREATE TABLE public.agendamento_condicao (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    agendamento_id  UUID NOT NULL REFERENCES public.agendamento(id) ON DELETE CASCADE,
    condicao        VARCHAR(255) NOT NULL,

    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ,

    UNIQUE(agendamento_id, condicao)
);


-- ╔══════════════════════════════════════════════════════════╗
-- ║  LOG + USO                                              ║
-- ╚══════════════════════════════════════════════════════════╝

-- ────────────────────────────────────────────────────────────
-- log_execucao — Histórico de execuções
-- ────────────────────────────────────────────────────────────
CREATE TABLE public.log_execucao (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id   UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    bot_id      UUID NOT NULL REFERENCES public.bot(id) ON DELETE CASCADE,
    origem      VARCHAR(255) NOT NULL,
    destino     VARCHAR(255) NOT NULL,
    status      public.log_status NOT NULL,
    mensagem    VARCHAR(500),
    data_hora   TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ
);

COMMENT ON TABLE public.log_execucao IS 'Log de execuções — sem bot_nome redundante (derivar via JOIN)';

-- ────────────────────────────────────────────────────────────
-- uso_mensal — Controle de uso e rate limiting
-- ────────────────────────────────────────────────────────────
CREATE TABLE public.uso_mensal (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    ano             INTEGER NOT NULL,
    mes             INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
    msgs_enviadas   INTEGER NOT NULL DEFAULT 0,
    msgs_limite     INTEGER NOT NULL DEFAULT 0,

    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ,

    UNIQUE(tenant_id, ano, mes)
);

COMMENT ON TABLE public.uso_mensal IS 'Contadores de uso mensal para rate limiting e billing';

COMMIT;
