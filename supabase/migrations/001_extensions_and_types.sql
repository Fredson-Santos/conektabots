-- ============================================================
-- Migration 001: Extensões e Tipos Enumerados
-- ConektaBots SaaS MVP
-- Data: 2026-04-14
-- ============================================================

BEGIN;

-- ────────────────────────────────────────────────────────────
-- Extensões
-- ────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";       -- criptografia AES/PGP
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- uuid_generate_v4()
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- busca fuzzy (trigram)

-- ────────────────────────────────────────────────────────────
-- Enums
-- ────────────────────────────────────────────────────────────

-- Planos de assinatura
CREATE TYPE public.plano_tipo AS ENUM (
    'free',
    'starter',
    'pro',
    'enterprise'
);

-- Tipo de conta Telegram
CREATE TYPE public.bot_tipo AS ENUM (
    'user',       -- conta de usuário (MTProto/session_string)
    'bot'         -- bot oficial (bot_token)
);

-- Modo de envio de mensagens
CREATE TYPE public.tipo_envio AS ENUM (
    'sequencial',
    'aleatorio'
);

-- Status de execução nos logs
CREATE TYPE public.log_status AS ENUM (
    'sucesso',
    'erro',
    'aviso'
);

-- Marketplaces suportados
CREATE TYPE public.marketplace_tipo AS ENUM (
    'shopee',
    'mercado_livre',
    'amazon',
    'magalu',
    'americanas',
    'aliexpress',
    'shein'
);

-- Papéis dentro de um tenant
CREATE TYPE public.membro_role AS ENUM (
    'owner',
    'admin',
    'editor',
    'viewer'
);

-- Tipos de mídia para filtro
CREATE TYPE public.filtro_midia_tipo AS ENUM (
    'todos',
    'foto',
    'video',
    'foto_video',
    'documento',
    'audio'
);

-- Tipo de filtro (incluir palavras vs bloquear palavras)
CREATE TYPE public.filtro_regra_tipo AS ENUM (
    'incluir',     -- antiga coluna "filtro" / "somente_se_tiver"
    'bloquear'     -- antiga coluna "bloqueios"
);

COMMIT;
