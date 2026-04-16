-- ============================================================
-- Migration 005: Row-Level Security (RLS) Policies
-- ConektaBots SaaS MVP
-- Data: 2026-04-14
--
-- Regra de ouro: Tenant A NUNCA vê dados de Tenant B.
-- Função helper get_user_tenant_ids() retorna os tenant_ids
-- do usuário autenticado via Supabase Auth.
-- ============================================================

BEGIN;

-- ────────────────────────────────────────────────────────────
-- Função Helper: retorna tenant_ids do usuário autenticado
-- ────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.get_user_tenant_ids()
RETURNS UUID[]
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT COALESCE(
        ARRAY_AGG(tm.tenant_id),
        ARRAY[]::UUID[]
    )
    FROM public.tenant_member tm
    WHERE tm.user_id = auth.uid()
      AND tm.deletado_em IS NULL;
$$;

COMMENT ON FUNCTION public.get_user_tenant_ids IS 'Retorna array de tenant_ids do usuário JWT autenticado';

-- ────────────────────────────────────────────────────────────
-- Função Helper: verifica se usuário tem role específica
-- ────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.user_has_role(p_tenant_id UUID, p_roles membro_role[])
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM public.tenant_member tm
        WHERE tm.user_id = auth.uid()
          AND tm.tenant_id = p_tenant_id
          AND tm.role = ANY(p_roles)
          AND tm.deletado_em IS NULL
    );
$$;

COMMENT ON FUNCTION public.user_has_role IS 'Verifica se usuário autenticado tem um dos roles no tenant';


-- ╔══════════════════════════════════════════════════════════╗
-- ║  HABILITAR RLS EM TODAS AS TABELAS                      ║
-- ╚══════════════════════════════════════════════════════════╝

ALTER TABLE public.tenant                ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tenant_member         ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marketplace_integracao ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bot                   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.regra                 ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.regra_origem          ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.regra_destino         ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.regra_filtro          ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.regra_condicao        ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agendamento           ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agendamento_origem    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agendamento_destino   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agendamento_horario   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agendamento_filtro    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agendamento_condicao  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.log_execucao          ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.uso_mensal            ENABLE ROW LEVEL SECURITY;


-- ╔══════════════════════════════════════════════════════════╗
-- ║  POLICIES: TENANT                                        ║
-- ╚══════════════════════════════════════════════════════════╝

-- Membros podem ver seus tenants
CREATE POLICY "tenant_select"
    ON public.tenant FOR SELECT
    USING (id = ANY(get_user_tenant_ids()));

-- Apenas owner/admin pode atualizar o tenant
CREATE POLICY "tenant_update"
    ON public.tenant FOR UPDATE
    USING (user_has_role(id, ARRAY['owner', 'admin']::membro_role[]))
    WITH CHECK (user_has_role(id, ARRAY['owner', 'admin']::membro_role[]));

-- Qualquer usuário autenticado pode criar um tenant (signup)
CREATE POLICY "tenant_insert"
    ON public.tenant FOR INSERT
    WITH CHECK (auth.uid() IS NOT NULL);

-- Apenas owner pode deletar
CREATE POLICY "tenant_delete"
    ON public.tenant FOR DELETE
    USING (user_has_role(id, ARRAY['owner']::membro_role[]));


-- ╔══════════════════════════════════════════════════════════╗
-- ║  POLICIES: TENANT_MEMBER                                 ║
-- ╚══════════════════════════════════════════════════════════╝

CREATE POLICY "tenant_member_select"
    ON public.tenant_member FOR SELECT
    USING (tenant_id = ANY(get_user_tenant_ids()));

CREATE POLICY "tenant_member_insert"
    ON public.tenant_member FOR INSERT
    WITH CHECK (
        user_has_role(tenant_id, ARRAY['owner', 'admin']::membro_role[])
        OR (
            -- Permitir auto-insert na criação do tenant (owner inicial)
            user_id = auth.uid()
            AND role = 'owner'
        )
    );

CREATE POLICY "tenant_member_update"
    ON public.tenant_member FOR UPDATE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin']::membro_role[]))
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin']::membro_role[]));

CREATE POLICY "tenant_member_delete"
    ON public.tenant_member FOR DELETE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin']::membro_role[]));


-- ╔══════════════════════════════════════════════════════════╗
-- ║  POLICIES: MARKETPLACE_INTEGRACAO                        ║
-- ╚══════════════════════════════════════════════════════════╝

CREATE POLICY "marketplace_select"
    ON public.marketplace_integracao FOR SELECT
    USING (tenant_id = ANY(get_user_tenant_ids()));

CREATE POLICY "marketplace_insert"
    ON public.marketplace_integracao FOR INSERT
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));

CREATE POLICY "marketplace_update"
    ON public.marketplace_integracao FOR UPDATE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]))
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));

CREATE POLICY "marketplace_delete"
    ON public.marketplace_integracao FOR DELETE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin']::membro_role[]));


-- ╔══════════════════════════════════════════════════════════╗
-- ║  POLICIES: BOT                                           ║
-- ╚══════════════════════════════════════════════════════════╝

CREATE POLICY "bot_select"
    ON public.bot FOR SELECT
    USING (tenant_id = ANY(get_user_tenant_ids()));

CREATE POLICY "bot_insert"
    ON public.bot FOR INSERT
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));

CREATE POLICY "bot_update"
    ON public.bot FOR UPDATE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]))
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));

CREATE POLICY "bot_delete"
    ON public.bot FOR DELETE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin']::membro_role[]));


-- ╔══════════════════════════════════════════════════════════╗
-- ║  POLICIES: REGRA + FILHAS                                ║
-- ╚══════════════════════════════════════════════════════════╝

-- Macro para criar policies padronizadas em tabelas com tenant_id
-- Regra (tabela mãe)
CREATE POLICY "regra_select" ON public.regra FOR SELECT
    USING (tenant_id = ANY(get_user_tenant_ids()));
CREATE POLICY "regra_insert" ON public.regra FOR INSERT
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "regra_update" ON public.regra FOR UPDATE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]))
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "regra_delete" ON public.regra FOR DELETE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin']::membro_role[]));

-- Regra Origem
CREATE POLICY "regra_origem_select" ON public.regra_origem FOR SELECT
    USING (tenant_id = ANY(get_user_tenant_ids()));
CREATE POLICY "regra_origem_insert" ON public.regra_origem FOR INSERT
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "regra_origem_update" ON public.regra_origem FOR UPDATE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]))
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "regra_origem_delete" ON public.regra_origem FOR DELETE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin']::membro_role[]));

-- Regra Destino
CREATE POLICY "regra_destino_select" ON public.regra_destino FOR SELECT
    USING (tenant_id = ANY(get_user_tenant_ids()));
CREATE POLICY "regra_destino_insert" ON public.regra_destino FOR INSERT
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "regra_destino_update" ON public.regra_destino FOR UPDATE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]))
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "regra_destino_delete" ON public.regra_destino FOR DELETE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin']::membro_role[]));

-- Regra Filtro
CREATE POLICY "regra_filtro_select" ON public.regra_filtro FOR SELECT
    USING (tenant_id = ANY(get_user_tenant_ids()));
CREATE POLICY "regra_filtro_insert" ON public.regra_filtro FOR INSERT
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "regra_filtro_update" ON public.regra_filtro FOR UPDATE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]))
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "regra_filtro_delete" ON public.regra_filtro FOR DELETE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin']::membro_role[]));

-- Regra Condição
CREATE POLICY "regra_condicao_select" ON public.regra_condicao FOR SELECT
    USING (tenant_id = ANY(get_user_tenant_ids()));
CREATE POLICY "regra_condicao_insert" ON public.regra_condicao FOR INSERT
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "regra_condicao_update" ON public.regra_condicao FOR UPDATE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]))
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "regra_condicao_delete" ON public.regra_condicao FOR DELETE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin']::membro_role[]));


-- ╔══════════════════════════════════════════════════════════╗
-- ║  POLICIES: AGENDAMENTO + FILHAS                          ║
-- ╚══════════════════════════════════════════════════════════╝

-- Agendamento (tabela mãe)
CREATE POLICY "agendamento_select" ON public.agendamento FOR SELECT
    USING (tenant_id = ANY(get_user_tenant_ids()));
CREATE POLICY "agendamento_insert" ON public.agendamento FOR INSERT
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "agendamento_update" ON public.agendamento FOR UPDATE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]))
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "agendamento_delete" ON public.agendamento FOR DELETE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin']::membro_role[]));

-- Agendamento Origem
CREATE POLICY "agendamento_origem_select" ON public.agendamento_origem FOR SELECT
    USING (tenant_id = ANY(get_user_tenant_ids()));
CREATE POLICY "agendamento_origem_insert" ON public.agendamento_origem FOR INSERT
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "agendamento_origem_update" ON public.agendamento_origem FOR UPDATE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]))
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "agendamento_origem_delete" ON public.agendamento_origem FOR DELETE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin']::membro_role[]));

-- Agendamento Destino
CREATE POLICY "agendamento_destino_select" ON public.agendamento_destino FOR SELECT
    USING (tenant_id = ANY(get_user_tenant_ids()));
CREATE POLICY "agendamento_destino_insert" ON public.agendamento_destino FOR INSERT
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "agendamento_destino_update" ON public.agendamento_destino FOR UPDATE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]))
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "agendamento_destino_delete" ON public.agendamento_destino FOR DELETE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin']::membro_role[]));

-- Agendamento Horário
CREATE POLICY "agendamento_horario_select" ON public.agendamento_horario FOR SELECT
    USING (tenant_id = ANY(get_user_tenant_ids()));
CREATE POLICY "agendamento_horario_insert" ON public.agendamento_horario FOR INSERT
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "agendamento_horario_update" ON public.agendamento_horario FOR UPDATE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]))
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "agendamento_horario_delete" ON public.agendamento_horario FOR DELETE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin']::membro_role[]));

-- Agendamento Filtro
CREATE POLICY "agendamento_filtro_select" ON public.agendamento_filtro FOR SELECT
    USING (tenant_id = ANY(get_user_tenant_ids()));
CREATE POLICY "agendamento_filtro_insert" ON public.agendamento_filtro FOR INSERT
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "agendamento_filtro_update" ON public.agendamento_filtro FOR UPDATE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]))
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "agendamento_filtro_delete" ON public.agendamento_filtro FOR DELETE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin']::membro_role[]));

-- Agendamento Condição
CREATE POLICY "agendamento_condicao_select" ON public.agendamento_condicao FOR SELECT
    USING (tenant_id = ANY(get_user_tenant_ids()));
CREATE POLICY "agendamento_condicao_insert" ON public.agendamento_condicao FOR INSERT
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "agendamento_condicao_update" ON public.agendamento_condicao FOR UPDATE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]))
    WITH CHECK (user_has_role(tenant_id, ARRAY['owner', 'admin', 'editor']::membro_role[]));
CREATE POLICY "agendamento_condicao_delete" ON public.agendamento_condicao FOR DELETE
    USING (user_has_role(tenant_id, ARRAY['owner', 'admin']::membro_role[]));


-- ╔══════════════════════════════════════════════════════════╗
-- ║  POLICIES: LOG_EXECUCAO                                  ║
-- ╚══════════════════════════════════════════════════════════╝

CREATE POLICY "log_select" ON public.log_execucao FOR SELECT
    USING (tenant_id = ANY(get_user_tenant_ids()));

-- Logs são criados pelo backend (service_role), não por usuários.
-- INSERT via service_role bypassa RLS. Mas adicionamos policy para segurança.
CREATE POLICY "log_insert" ON public.log_execucao FOR INSERT
    WITH CHECK (tenant_id = ANY(get_user_tenant_ids()));

-- Logs são imutáveis — sem UPDATE ou DELETE policies


-- ╔══════════════════════════════════════════════════════════╗
-- ║  POLICIES: USO_MENSAL                                    ║
-- ╚══════════════════════════════════════════════════════════╝

CREATE POLICY "uso_mensal_select" ON public.uso_mensal FOR SELECT
    USING (tenant_id = ANY(get_user_tenant_ids()));

-- Uso é gerenciado por triggers — INSERT/UPDATE apenas via service_role
CREATE POLICY "uso_mensal_insert" ON public.uso_mensal FOR INSERT
    WITH CHECK (tenant_id = ANY(get_user_tenant_ids()));

COMMIT;
