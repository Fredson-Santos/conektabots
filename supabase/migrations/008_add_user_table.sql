-- ============================================================
-- Migration 008: Tabela User para Autenticação Local
-- ConektaBots SaaS MVP
-- Data: 2026-04-15
-- ============================================================

BEGIN;

-- ────────────────────────────────────────────────────────────
-- user — Usuários com autenticação local
-- ────────────────────────────────────────────────────────────
CREATE TABLE public."user" (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    senha_hash      VARCHAR(255) NOT NULL,
    nome            VARCHAR(255) NOT NULL,
    
    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ
);

-- Índices para performance
CREATE INDEX ix_user_email ON public."user"(email);
CREATE INDEX ix_user_ativo ON public."user"(ativo);
CREATE INDEX ix_user_criado_em ON public."user"(criado_em);
CREATE INDEX ix_user_deletado_em ON public."user"(deletado_em);

COMMENT ON TABLE public."user" IS 'Usuários do sistema com autenticação local (email + senha hash)';
COMMENT ON COLUMN public."user".email IS 'Email único para login e identificação';
COMMENT ON COLUMN public."user".senha_hash IS 'Senha hasheada com bcrypt (nunca plain text)';
COMMENT ON COLUMN public."user".ativo IS 'Soft flag: true = pode fazer login, false = desativado';


-- ────────────────────────────────────────────────────────────
-- Migrar tenant_member para referenciar user ao invés de auth.users
-- ────────────────────────────────────────────────────────────

-- 1. Adicionar coluna user_id_new (temporária)
ALTER TABLE public.tenant_member
ADD COLUMN user_id_new UUID;

-- 2. Criar índice para user_id_new
CREATE INDEX ix_tenant_member_user_id_new ON public.tenant_member(user_id_new);

-- 3. Adicionar constraint de FK para user_id_new (ainda não ativa)
--    Será ativada após migração de dados
ALTER TABLE public.tenant_member
ADD CONSTRAINT fk_tenant_member_user_id_new
    FOREIGN KEY (user_id_new) REFERENCES public."user"(id) ON DELETE CASCADE;


-- ────────────────────────────────────────────────────────────
-- Criar função para migração (se necessário)
-- Esta função pode ser executada manualmente depois
-- ────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION migrate_auth_users_to_local_user()
RETURNS TABLE(migrados INT, erros INT) AS $$
DECLARE
    v_migrados INT := 0;
    v_erros INT := 0;
BEGIN
    -- Esta é uma função placeholder
    -- A migração real será feita via Python/script
    RETURN QUERY SELECT v_migrados::INT, v_erros::INT;
END;
$$ LANGUAGE plpgsql;


-- ────────────────────────────────────────────────────────────
-- RLS para tabela user
-- ────────────────────────────────────────────────────────────
ALTER TABLE public."user" ENABLE ROW LEVEL SECURITY;

-- Política 1: Usuários só podem ler sua própria informação
CREATE POLICY "Users can read own data"
ON public."user"
FOR SELECT
TO authenticated
USING (id = auth.uid());

-- Política 2: Usuários podem atualizar sua própria informação (exceto email)
CREATE POLICY "Users can update own data"
ON public."user"
FOR UPDATE
TO authenticated
USING (id = auth.uid())
WITH CHECK (
    id = auth.uid() AND 
    email = (SELECT email FROM public."user" WHERE id = auth.uid()) -- email não pode mudar
);


COMMIT;
