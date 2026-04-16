---
description: "Use when: creating or modifying migrations in Alembic or Supabase. Ensure database changes are safe, reversible, and maintain data integrity."
name: "Database Migration Safety Rules"
applyTo: ["alembic/versions/**", "supabase/migrations/**"]
---

# 🗄️ Migration Safety Rules

**Applies to**:
- `alembic/versions/` — Python migrations
- `supabase/migrations/` — SQL migrations

---

## 🚫 NEVER Do These Things in Migrations

### ❌ NEVER Drop Columns in Same Release

```sql
-- ❌ WRONG — Breaks backward compatibility
-- Migration 001_remove_old_field.py
def upgrade():
    op.drop_column('users', 'old_field')  # App still expects this!

-- ✅ CORRECT — Two-step process (safer)
-- Migration 001_deprecate_old_field.py — hide in app
def upgrade():
    op.execute("ALTER TABLE users RENAME COLUMN old_field TO _old_field_deprecated")

-- Migration 002_drop_old_field.py (next release) — delete from DB
def upgrade():
    op.drop_column('users', '_old_field_deprecated')
```

### ❌ NEVER Modify Data Without Backup

```python
# ❌ WRONG — Destructive without context
def upgrade():
    op.execute("UPDATE users SET age = 0")  # WHO? WHY?

# ✅ CORRECT — Explicit, reversible
def upgrade():
    """Backfill users.age with default values where missing."""
    op.execute("""
        UPDATE users 
        SET age = 18 
        WHERE age IS NULL AND deleted_at IS NULL
    """)

def downgrade():
    """Reverse: clear backfilled ages."""
    op.execute("""
        UPDATE users 
        SET age = NULL 
        WHERE age = 18 AND created_at > '2026-04-15'
    """)
```

### ❌ NEVER Add NOT NULL Without Default

```sql
-- ❌ WRONG — Breaks existing rows
ALTER TABLE bots ADD COLUMN status VARCHAR NOT NULL;

-- ✅ CORRECT — Provide default
ALTER TABLE bots ADD COLUMN status VARCHAR DEFAULT 'inactive';

-- Or two-step:
-- Step 1: Add nullable
ALTER TABLE bots ADD COLUMN status VARCHAR DEFAULT 'inactive';
-- Step 2: Update existing rows
UPDATE bots SET status = 'inactive' WHERE status IS NULL;
-- Step 3: Make NOT NULL
ALTER TABLE bots ALTER COLUMN status SET NOT NULL;
```

### ❌ NEVER Change Column Type Carelessly

```python
# ❌ WRONG — Data loss risk
def upgrade():
    op.alter_column('logs', 'duration', type_=sa.Float)  # Was String!

# ✅ CORRECT — Safe conversion
def upgrade():
    """Convert duration from string to float."""
    # Step 1: Create new column with new type
    op.add_column('logs', sa.Column('duration_float', sa.Float))
    
    # Step 2: Populate new column with converted data
    op.execute("""
        UPDATE logs
        SET duration_float = CAST(duration AS FLOAT)
        WHERE duration IS NOT NULL
    """)
    
    # Step 3: Drop old column
    op.drop_column('logs', 'duration')
    
    # Step 4: Rename new column
    op.rename_table('logs', 'logs_temp')
    op.rename_table('logs_temp', 'logs')

def downgrade():
    """Reverse: restore string column."""
    ...
```

### ❌ NEVER Assume Row Count Won't Break Migration

```python
# ❌ WRONG — Fragile, breaks with large tables
def upgrade():
    # This simple UPDATE will LOCK table and timeout on 10M+ rows
    op.execute("UPDATE users SET updated_at = NOW()")

# ✅ CORRECT — Batch processing
def upgrade():
    """Update timestamp in batches (no full lock)."""
    op.execute("""
        UPDATE users
        SET updated_at = NOW()
        WHERE updated_at IS NULL
        LIMIT 10000
    """)
    # Run multiple times or use background job for large tables
```

---

## ✅ ALWAYS Do These Things

### ✅ ALWAYS Create Downgrade

```python
def upgrade():
    """Add tenant_id column to bots table."""
    op.add_column('bots', sa.Column('tenant_id', sa.UUID, nullable=False, 
                                     server_default=uuid.uuid4))
    # Create foreign key
    op.create_foreign_key('fk_bots_tenant', 'bots', 'tenants', 
                         ['tenant_id'], ['id'], ondelete='CASCADE')

def downgrade():
    """Reverse: remove tenant_id column."""
    op.drop_constraint('fk_bots_tenant', 'bots', type_='foreignkey')
    op.drop_column('bots', 'tenant_id')
```

### ✅ ALWAYS Test Migration Locally First

```bash
# Test upgrade
alembic upgrade +1

# Test downgrade
alembic downgrade -1

# Verify schema match
alembic current
alembic heads
```

### ✅ ALWAYS Write Descriptive Migration Names

```python
# ❌ WRONG
# 001_changes.py
# 002_fixes.py
# 003_update.py

# ✅ CORRECT
# 001_add_user_table.py
# 002_add_tenant_foreign_key.py
# 003_create_index_on_email.py
```

### ✅ ALWAYS Include Comments Explaining Why

```python
def upgrade():
    """
    Add bot_status column to track bot lifecycle.
    
    Values: 'pending', 'active', 'paused', 'error'
    
    Requires: Backend must set initial values in app startup
    Backward compat: Old code ignores missing column
    """
    op.add_column('bots', sa.Column('status', sa.String(50)))
    op.create_index('ix_bots_status', 'bots', ['status'])

def downgrade():
    """Remove bot_status column and index."""
    op.drop_index('ix_bots_status', 'bots')
    op.drop_column('bots', 'status')
```

### ✅ ALWAYS Validate Foreign Keys

```python
# ✅ CORRECT — Explicit FK setup
op.create_table('bot_credentials',
    sa.Column('id', sa.UUID, primary_key=True),
    sa.Column('bot_id', sa.UUID, nullable=False),  # FK
    sa.ForeignKeyConstraint(['bot_id'], ['bots.id'], ondelete='CASCADE'),
)

# ✅ Test: Verify FK works
# DELETE bots.id → bot_credentials should cascade delete
```

### ✅ ALWAYS Add Indexes for Queries

```python
# After adding column, think: "Will this be queried?"
def upgrade():
    """Add email column to users with index."""
    op.add_column('users', sa.Column('email', sa.String(255), unique=True))
    # Index for WHERE email = ? and ORDER BY email queries
    op.create_index('ix_users_email', 'users', ['email'])

def downgrade():
    """Remove email column and index."""
    op.drop_index('ix_users_email', 'users')
    op.drop_column('users', 'email')
```

---

## Migration Checklist

Before creating a migration:

- [ ] Do I have a downgrade path?
- [ ] Will this break existing code?
- [ ] Does the data conversion preserve existing data?
- [ ] Are foreign keys correct?
- [ ] Do I need indexes?
- [ ] Have I tested locally (upgrade + downgrade)?
- [ ] Is the name descriptive?
- [ ] Does it include comments explaining WHY?
- [ ] Will it work on large tables (10M+ rows)?
- [ ] Have I verified in staging before production?

---

## Example: Safe Migration

```python
"""
Migration: Add marketplace integrations support

Motivation: Phase 2 feature for linking Shopee, Mercado Livre, Amazon, Magalu
Purpose: Store API credentials for marketplace APIs
Safety: Uses soft delete (completado_em) for compliance
Backward compat: Optional columns, old code can ignore
"""

def upgrade():
    """Create marketplace_integrations table."""
    
    # Step 1: Create new table
    op.create_table('marketplace_integrations',
        sa.Column('id', sa.UUID, primary_key=True, default=uuid.uuid4),
        sa.Column('tenant_id', sa.UUID, nullable=False),
        sa.Column('tipo', sa.String(50), nullable=False),  # enum
        sa.Column('api_key_encrypted', sa.LargeBinary, nullable=True),
        sa.Column('api_secret_encrypted', sa.LargeBinary, nullable=True),
        sa.Column('ativo', sa.Boolean, default=True),
        sa.Column('criado_em', sa.DateTime, default=datetime.utcnow),
        sa.Column('atualizado_em', sa.DateTime, default=datetime.utcnow),
        sa.Column('deletado_em', sa.DateTime, nullable=True),  # soft delete
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], 
                               ondelete='CASCADE'),
    )
    
    # Step 2: Create indexes
    op.create_index('ix_marketplace_tenant', 'marketplace_integrations', 
                   ['tenant_id'])
    op.create_index('ix_marketplace_tipo', 'marketplace_integrations', 
                   ['tipo'])
    
    # Step 3: Create RLS policy (if using Supabase)
    op.execute("""
        CREATE POLICY "marketplace_integrations_rls"
        ON marketplace_integrations
        FOR SELECT USING (
            tenant_id IN (SELECT tenant_id FROM tenant_members WHERE user_id = auth.uid())
        )
    """)

def downgrade():
    """Remove marketplace_integrations table."""
    op.drop_table('marketplace_integrations')
```

---

## Pre-Migration Checklist

**Before running in production:**

- [ ] Migration tested locally (upgrade + downgrade)
- [ ] Data backup taken
- [ ] Downtime window identified (if needed)
- [ ] Team notified
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured
- [ ] Post-migration validation script prepared

**Running migration in production:**

```bash
# 1. Backup database
# 2. Test in staging first
# 3. Run migration
alembic upgrade head

# 4. Validate
# 5. Monitor logs for errors
# 6. Be ready to rollback
alembic downgrade -1
```

---

## Common Migration Patterns

### Pattern: Add Soft Delete Support

```python
def upgrade():
    """Add soft delete column."""
    op.add_column('bots', sa.Column('deletado_em', sa.DateTime, nullable=True))
    # Index for WHERE deletado_em IS NULL queries
    op.create_index('ix_bots_not_deleted', 'bots', ['deletado_em'])

def downgrade():
    """Remove soft delete column."""
    op.drop_index('ix_bots_not_deleted')
    op.drop_column('bots', 'deletado_em')
```

### Pattern: Add Audit Timestamp

```python
def upgrade():
    """Add audit timestamps."""
    op.add_column('bots', sa.Column('criado_em', sa.DateTime, 
                                    default=datetime.utcnow))
    op.add_column('bots', sa.Column('atualizado_em', sa.DateTime, 
                                    default=datetime.utcnow))

def downgrade():
    """Remove audit timestamps."""
    op.drop_column('bots', 'criado_em')
    op.drop_column('bots', 'atualizado_em')
```

### Pattern: Normalize Comma-Separated Fields

```
OLD: Bot.chats_origem = "123,456,789"  (comma-separated string)
NEW: BotOrigem table with 1:N relationship
```

```python
def upgrade():
    """Normalize chats_origem to separate table."""
    
    # Create new table
    op.create_table('bot_origens',
        sa.Column('id', sa.UUID, primary_key=True),
        sa.Column('bot_id', sa.UUID, nullable=False),
        sa.Column('chat_id', sa.String(255), nullable=False),
        sa.ForeignKeyConstraint(['bot_id'], ['bots.id'], ondelete='CASCADE'),
    )
    
    # Migrate data: split comma-separated values
    op.execute("""
        INSERT INTO bot_origens (bot_id, chat_id)
        SELECT b.id, unnest(string_to_array(b.chats_origem, ','))
        FROM bots b
        WHERE b.chats_origem IS NOT NULL
    """)
    
    # Drop old column
    op.drop_column('bots', 'chats_origem')

def downgrade():
    """Restore comma-separated format."""
    # Reverse the process...
```

---

**Last Updated**: April 15, 2026  
**Applies To**: Migrations only  
**Severity**: 🔴 CRITICAL — Data loss risk if violated
