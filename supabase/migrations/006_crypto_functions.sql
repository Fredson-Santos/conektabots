-- ============================================================
-- Migration 006: Funções de Criptografia
-- ConektaBots SaaS MVP
-- Data: 2026-04-14
-- Usa pgp_sym_encrypt/decrypt do pgcrypto (AES-256).
-- ============================================================

BEGIN;

CREATE OR REPLACE FUNCTION public.encrypt_sensitive(p_plaintext TEXT, p_key TEXT)
RETURNS BYTEA LANGUAGE sql IMMUTABLE SECURITY DEFINER SET search_path = public
AS $$ SELECT pgp_sym_encrypt(p_plaintext, p_key, 'cipher-algo=aes256'); $$;

CREATE OR REPLACE FUNCTION public.decrypt_sensitive(p_ciphertext BYTEA, p_key TEXT)
RETURNS TEXT LANGUAGE sql IMMUTABLE SECURITY DEFINER SET search_path = public
AS $$ SELECT pgp_sym_decrypt(p_ciphertext, p_key); $$;

CREATE OR REPLACE FUNCTION public.encrypt_json(p_json JSONB, p_key TEXT)
RETURNS BYTEA LANGUAGE sql IMMUTABLE SECURITY DEFINER SET search_path = public
AS $$ SELECT pgp_sym_encrypt(p_json::TEXT, p_key, 'cipher-algo=aes256'); $$;

CREATE OR REPLACE FUNCTION public.decrypt_json(p_ciphertext BYTEA, p_key TEXT)
RETURNS JSONB LANGUAGE sql IMMUTABLE SECURITY DEFINER SET search_path = public
AS $$ SELECT pgp_sym_decrypt(p_ciphertext, p_key)::JSONB; $$;

COMMIT;
