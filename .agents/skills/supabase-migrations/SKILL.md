# SKILL: Supabase Migrations & Database Design

**Purpose**: Guidelines for creating migrations, managing schema changes, implementing RLS policies, and working with Supabase.

**Used for**: Adding new tables, modifying schema, implementing security policies, managing cryptocurrency functions.

---

## Migration Structure

### File Naming Convention
```
supabase/migrations/00X_description.sql
└─ Sequential numbering (001, 002, 003...)
└─ Kebab-case description
└─ Single, focused responsibility per file
```

### Template: Basic Migration
```sql
-- Migration: 00X_add_new_feature
-- Created: YYYY-MM-DD
-- Description: [What this migration does]

BEGIN;

-- === Drop (if needed) ===
-- DROP TABLE IF EXISTS public.old_table CASCADE;

-- === Create New Tables ===
CREATE TABLE IF NOT EXISTS public.new_table (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES public.tenant(id) ON DELETE CASCADE,
    campo_texto     VARCHAR(255) NOT NULL,
    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletado_em     TIMESTAMPTZ,
    
    -- Constraints
    CONSTRAINT new_table_name_length CHECK (char_length(campo_texto) >= 1)
);

-- === Add Indexes ===
CREATE INDEX idx_new_table_tenant ON public.new_table(tenant_id) WHERE deletado_em IS NULL;
CREATE INDEX idx_new_table_ativo ON public.new_table(tenant_id, ativo) WHERE deletado_em IS NULL;

-- === Enable RLS ===
ALTER TABLE public.new_table ENABLE ROW LEVEL SECURITY;

-- === RLS Policies ===
CREATE POLICY "Membros veem dados do tenant"
    ON public.new_table FOR SELECT
    USING (tenant_id IN (SELECT public.get_user_tenant_ids()));

-- === Triggers (auto-update atualizado_em) ===
CREATE TRIGGER tr_new_table_updated BEFORE UPDATE ON public.new_table
    FOR EACH ROW EXECUTE FUNCTION public.set_atualizado_em();

COMMIT;
```

---

## Schema Design Checklist

✅ **Multi-Tenancy**
- [ ] `tenant_id` FK added to all business tables
- [ ] NOT NULL constraint on tenant_id
- [ ] ON DELETE CASCADE to cleanup on tenant deletion

✅ **Timestamps**
- [ ] `criado_em` TIMESTAMPTZ DEFAULT NOW()
- [ ] `atualizado_em` TIMESTAMPTZ DEFAULT NOW()
- [ ] `deletado_em` TIMESTAMPTZ NULL (for soft deletes)
- [ ] Trigger auto-updates `atualizado_em` on UPDATE

✅ **Indexes**
- [ ] Primary filter columns indexed (tenant_id, status, created_at)
- [ ] Soft delete filter: WHERE deletado_em IS NULL
- [ ] Complex queries: composite indexes (tenant_id, ativo, created_at)

✅ **Constraints**
- [ ] Foreign keys with appropriate ON DELETE action
- [ ] CHECK constraints for string length validation
- [ ] UNIQUE constraints where needed (no duplicates)

✅ **Security (RLS)**
- [ ] RLS enabled on table
- [ ] SELECT policy (read access)
- [ ] INSERT policy (who can create)
- [ ] UPDATE policy (who can modify)
- [ ] DELETE policy (soft or hard delete permission)

✅ **Encryption**
- [ ] Sensitive fields stored as BYTEA (encrypted)
- [ ] PL/pgSQL functions for encrypt/decrypt
- [ ] Never store plaintext: passwords, API keys, tokens

---

## RLS Policy Patterns

### Pattern 1: Tenant-Based Row Access
```sql
-- Users see only their tenant's data
CREATE POLICY "Tenant isolation"
    ON public.table_name FOR SELECT
    USING (tenant_id IN (SELECT public.get_user_tenant_ids()));
```

### Pattern 2: Role-Based Access (Admin/Editor/Viewer)
```sql
-- Only admin/editor can modify
CREATE POLICY "Admin/Editor modify"
    ON public.table_name FOR UPDATE
    USING (
        tenant_id IN (
            SELECT tenant_id FROM public.tenant_member
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin', 'editor')
        )
    );
```

### Pattern 3: Public Read, Authenticated Write
```sql
-- Everyone reads, only authenticated writes (rarely used)
CREATE POLICY "Public read, auth write"
    ON public.table_name FOR INSERT
    WITH CHECK (auth.uid() IS NOT NULL);
```

---

## Encryption Helpers

### Field Encryption Pattern
```sql
-- In migration, use PL/pgSQL function:
CREATE OR REPLACE FUNCTION public.encrypt_field(plaintext TEXT)
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

-- In application (Python):
from cryptography.fernet import Fernet

class CryptoService:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())
    
    def encrypt(self, text: str) -> bytes:
        return self.cipher.encrypt(text.encode())
    
    def decrypt(self, encrypted: bytes) -> str:
        return self.cipher.decrypt(encrypted).decode()
```

---

## Testing Migrations

### 1. Test Locally (SQLite)
```bash
# For development, use SQLite in-memory
from sqlalchemy import create_engine
engine = create_engine("sqlite:///:memory:")

# Run migration scripts (pseudo-code)
with engine.begin() as conn:
    conn.exec_text(open("migration.sql").read())
```

### 2. Test Against Supabase Staging
```bash
# Using psql:
psql "postgresql://user:pass@db.supabase.co:5432/postgres" \
    -f supabase/migrations/00X_new_feature.sql

# Verify:
SELECT * FROM public.table_name LIMIT 1;
```

### 3. Verify RLS Polices
```sql
-- Check active policies
SELECT * FROM pg_policies WHERE tablename = 'table_name';

-- Test as different user (simulate Supabase RLS)
SET LOCAL rls.user_id = 'different-uuid';
SELECT * FROM table_name;  -- Should return empty if policy works
```

---

## Common Mistakes ⚠️

❌ **Mistake 1**: Forgetting tenant_id on business tables
```sql
-- BAD
CREATE TABLE bot (id UUID, name VARCHAR);

-- GOOD
CREATE TABLE bot (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    name VARCHAR
);
```

❌ **Mistake 2**: Not enabling RLS
```sql
-- BAD
CREATE TABLE sensitive_data (...);  -- RLS not enabled

-- GOOD
ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY "isolate_tenants" ON sensitive_data
    USING (tenant_id IN (SELECT get_user_tenant_ids()));
```

❌ **Mistake 3**: Hardcoding encryption keys
```sql
-- BAD
RETURN pgp_sym_encrypt(text, 'hardcoded-key');

-- GOOD
RETURN pgp_sym_encrypt(text, current_setting('app.encryption_key', true));
```

❌ **Mistake 4**: No soft delete support
```sql
-- BAD
DELETE FROM table WHERE id = id;  -- Hard delete, no recovery

-- GOOD
UPDATE table SET deletado_em = NOW() WHERE id = id;
-- Query: SELECT * FROM table WHERE deletado_em IS NULL;
```

---

## Triggers & Auditing

### Auto-Update Timestamps
```sql
CREATE OR REPLACE FUNCTION public.set_atualizado_em()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables
CREATE TRIGGER tr_table_updated BEFORE UPDATE ON public.table_name
    FOR EACH ROW EXECUTE FUNCTION public.set_atualizado_em();
```

### Audit Trail Trigger (Optional)
```sql
CREATE TABLE public.audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR NOT NULL,  -- INSERT, UPDATE, DELETE
    changes JSONB,
    changed_by UUID,
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION public.audit_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, record_id, action, changes, changed_by)
        VALUES (TG_TABLE_NAME, OLD.id, TG_OP, row_to_json(OLD), auth.uid());
    ELSE
        INSERT INTO audit_log (table_name, record_id, action, changes, changed_by)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, row_to_json(NEW), auth.uid());
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
```

---

## Performance Tips

### 1. Index Strategy
```sql
-- Always index foreign keys
CREATE INDEX idx_tenant_id ON table_name(tenant_id);

-- Composite indexes for common filters
CREATE INDEX idx_tenant_status ON table_name(tenant_id, status) 
    WHERE deletado_em IS NULL;

-- Partial indexes (active records only)
CREATE INDEX idx_active ON table_name(id) 
    WHERE ativo = TRUE AND deletado_em IS NULL;
```

### 2. Query Optimization
```sql
-- Use EXPLAIN ANALYZE before/after changes
EXPLAIN ANALYZE
SELECT * FROM table_name
WHERE tenant_id = 'uuid'
AND deletado_em IS NULL
ORDER BY criado_em DESC
LIMIT 10;

-- Check query plan, look for Sequential Scans on large tables
```

### 3. Connection Pooling
```
Supabase PgBouncer settings:
- Pool size: 20-30 (standard)
- Max overflow: 10
- Connection timeout: 30s
```

---

## Rollback Strategy

### Reversible Migration Template
```sql
-- UP (Apply migration)
BEGIN;

CREATE TABLE new_feature (...);
-- ... changes ...

COMMIT;

-- DOWN (Rollback if needed)
BEGIN;

DROP TABLE IF EXISTS new_feature CASCADE;
-- ... revert changes ...

COMMIT;
```

### Test Rollback
```bash
# After migration, verify data integrity
SELECT COUNT(*) FROM table_name;

# If issue found, rollback:
psql "..." -f rollback.sql
```

---

## Troubleshooting

### Issue: RLS Policy Blocking Legitimate Access
**Solution**: Check policy logic, verify user's tenant_id, test with `SET LOCAL rls.user_id`.

### Issue: Migration Taking Too Long (Locks)
**Solution**: Use `CONCURRENTLY` for index creation, avoid `REINDEX`.

### Issue: Query Performance Degrading After Migration
**Solution**: Run `ANALYZE` on table, check new indexes, review query plan.

---

## Resources
- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL RLS Guide](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [pgcrypto Extension](https://www.postgresql.org/docs/current/pgcrypto.html)

---

**Last Updated**: April 15, 2026  
**Status**: Active
