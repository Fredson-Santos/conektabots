-- ============================================================
-- Migration 007: Triggers
-- ConektaBots SaaS MVP
-- Data: 2026-04-14
-- ============================================================

BEGIN;

-- ────────────────────────────────────────────────────────────
-- Trigger: Atualizar atualizado_em automaticamente em UPDATEs
-- ────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.set_atualizado_em()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.atualizado_em = NOW();
    RETURN NEW;
END;
$$;

-- Aplicar a todas as tabelas
DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'tenant', 'tenant_member', 'marketplace_integracao', 'bot',
        'regra', 'regra_origem', 'regra_destino', 'regra_filtro', 'regra_condicao',
        'agendamento', 'agendamento_origem', 'agendamento_destino',
        'agendamento_horario', 'agendamento_filtro', 'agendamento_condicao',
        'log_execucao', 'uso_mensal'
    ] LOOP
        EXECUTE format(
            'CREATE TRIGGER trg_%s_atualizado_em
                BEFORE UPDATE ON public.%I
                FOR EACH ROW
                EXECUTE FUNCTION public.set_atualizado_em();',
            t, t
        );
    END LOOP;
END;
$$;

-- ────────────────────────────────────────────────────────────
-- Trigger: Incrementar uso_mensal.msgs_enviadas em cada log
-- ────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.incrementar_uso_msgs()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_limite INTEGER;
BEGIN
    -- Buscar limite do plano do tenant
    SELECT t.limite_msgs_hora INTO v_limite
    FROM public.tenant t
    WHERE t.id = NEW.tenant_id;

    -- Upsert no uso_mensal
    INSERT INTO public.uso_mensal (
        tenant_id, ano, mes, msgs_enviadas, msgs_limite
    ) VALUES (
        NEW.tenant_id,
        EXTRACT(YEAR FROM NOW())::INTEGER,
        EXTRACT(MONTH FROM NOW())::INTEGER,
        1,
        COALESCE(v_limite, 50) * 24 * 30  -- msgs/hora * 24h * 30 dias
    )
    ON CONFLICT (tenant_id, ano, mes)
    DO UPDATE SET
        msgs_enviadas = uso_mensal.msgs_enviadas + 1,
        atualizado_em = NOW();

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_log_incrementar_uso
    AFTER INSERT ON public.log_execucao
    FOR EACH ROW
    EXECUTE FUNCTION public.incrementar_uso_msgs();

COMMIT;
