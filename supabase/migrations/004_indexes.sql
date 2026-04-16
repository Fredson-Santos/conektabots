-- ============================================================
-- Migration 004: Índices de Performance
-- ConektaBots SaaS MVP
-- Data: 2026-04-14
--
-- Convenção: índices parciais com WHERE deletado_em IS NULL
-- para ignorar registros soft-deleted automaticamente.
-- ============================================================

BEGIN;

-- ╔══════════════════════════════════════════════════════════╗
-- ║  TENANT                                                  ║
-- ╚══════════════════════════════════════════════════════════╝

CREATE INDEX idx_tenant_slug
    ON public.tenant (slug)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_tenant_plano
    ON public.tenant (plano)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_tenant_ativo
    ON public.tenant (ativo)
    WHERE deletado_em IS NULL;

-- ╔══════════════════════════════════════════════════════════╗
-- ║  TENANT_MEMBER                                           ║
-- ╚══════════════════════════════════════════════════════════╝

CREATE INDEX idx_tenant_member_user_id
    ON public.tenant_member (user_id)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_tenant_member_tenant_id
    ON public.tenant_member (tenant_id)
    WHERE deletado_em IS NULL;

-- ╔══════════════════════════════════════════════════════════╗
-- ║  MARKETPLACE_INTEGRACAO                                  ║
-- ╚══════════════════════════════════════════════════════════╝

CREATE INDEX idx_marketplace_tenant_id
    ON public.marketplace_integracao (tenant_id)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_marketplace_tipo
    ON public.marketplace_integracao (tenant_id, tipo)
    WHERE deletado_em IS NULL;

-- ╔══════════════════════════════════════════════════════════╗
-- ║  BOT                                                     ║
-- ╚══════════════════════════════════════════════════════════╝

CREATE INDEX idx_bot_tenant_id
    ON public.bot (tenant_id)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_bot_tenant_ativo
    ON public.bot (tenant_id, ativo)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_bot_nome
    ON public.bot (tenant_id, nome)
    WHERE deletado_em IS NULL;

-- ╔══════════════════════════════════════════════════════════╗
-- ║  REGRA + FILHAS                                          ║
-- ╚══════════════════════════════════════════════════════════╝

CREATE INDEX idx_regra_tenant_id
    ON public.regra (tenant_id)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_regra_bot_id
    ON public.regra (bot_id)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_regra_tenant_ativo
    ON public.regra (tenant_id, ativo)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_regra_marketplace
    ON public.regra (marketplace_integracao_id)
    WHERE marketplace_integracao_id IS NOT NULL AND deletado_em IS NULL;

-- Filhas da regra
CREATE INDEX idx_regra_origem_regra_id
    ON public.regra_origem (regra_id)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_regra_origem_valor
    ON public.regra_origem (origem)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_regra_destino_regra_id
    ON public.regra_destino (regra_id)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_regra_filtro_regra_id
    ON public.regra_filtro (regra_id)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_regra_filtro_tipo
    ON public.regra_filtro (regra_id, tipo)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_regra_condicao_regra_id
    ON public.regra_condicao (regra_id)
    WHERE deletado_em IS NULL;

-- ╔══════════════════════════════════════════════════════════╗
-- ║  AGENDAMENTO + FILHAS                                    ║
-- ╚══════════════════════════════════════════════════════════╝

CREATE INDEX idx_agendamento_tenant_id
    ON public.agendamento (tenant_id)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_agendamento_bot_id
    ON public.agendamento (bot_id)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_agendamento_tenant_ativo
    ON public.agendamento (tenant_id, ativo)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_agendamento_marketplace
    ON public.agendamento (marketplace_integracao_id)
    WHERE marketplace_integracao_id IS NOT NULL AND deletado_em IS NULL;

-- Filhas do agendamento
CREATE INDEX idx_agendamento_origem_agendamento_id
    ON public.agendamento_origem (agendamento_id)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_agendamento_destino_agendamento_id
    ON public.agendamento_destino (agendamento_id)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_agendamento_horario_agendamento_id
    ON public.agendamento_horario (agendamento_id)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_agendamento_horario_hora
    ON public.agendamento_horario (horario)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_agendamento_filtro_agendamento_id
    ON public.agendamento_filtro (agendamento_id)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_agendamento_condicao_agendamento_id
    ON public.agendamento_condicao (agendamento_id)
    WHERE deletado_em IS NULL;

-- ╔══════════════════════════════════════════════════════════╗
-- ║  LOG_EXECUCAO                                            ║
-- ╚══════════════════════════════════════════════════════════╝

CREATE INDEX idx_log_tenant_id
    ON public.log_execucao (tenant_id)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_log_bot_id
    ON public.log_execucao (bot_id)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_log_data_hora
    ON public.log_execucao (data_hora DESC)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_log_status
    ON public.log_execucao (status)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_log_tenant_data
    ON public.log_execucao (tenant_id, data_hora DESC)
    WHERE deletado_em IS NULL;

CREATE INDEX idx_log_bot_data
    ON public.log_execucao (bot_id, data_hora DESC)
    WHERE deletado_em IS NULL;

-- ╔══════════════════════════════════════════════════════════╗
-- ║  USO_MENSAL                                              ║
-- ╚══════════════════════════════════════════════════════════╝

CREATE INDEX idx_uso_mensal_tenant
    ON public.uso_mensal (tenant_id, ano DESC, mes DESC)
    WHERE deletado_em IS NULL;

COMMIT;
