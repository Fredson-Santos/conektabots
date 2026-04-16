# Security Audit Checklist

Comprehensive checklists for security validation of ConektaBots.

---

## ⚡ Quick 5-Minute Check

Use this for rapid validation before deployments.

- [ ] **JWT Valid** — Run `pytest tests/test_auth.py -v` — all pass?
- [ ] **Tenant Isolation** — Read DB query: includes `WHERE tenant_id = ?`?
- [ ] **RLS Enabled** — Supabase dashboard shows RLS policies active?
- [ ] **Encryption Working** — Run `pytest tests/test_crypto.py -v` — all pass?
- [ ] **No Hardcoded Secrets** — Grep code: `JWT_SECRET`, `API_KEY` not in `.py` files?
- [ ] **Passwords Hashed** — Confirm bcrypt in `AuthService`?
- [ ] **Rate Limiting** — Run `pytest tests/test_rate_limit.py -v` — limits enforced?
- [ ] **Error Messages Safe** — Test invalid endpoint: no stack traces?
- [ ] **HTTPS Production** — Prod uses HTTPS, not HTTP?
- [ ] **Logs Sanitized** — Check logs don't contain passwords/tokens?

**Result**: ✅ All pass → Proceed | ❌ Any fail → Investigate

---

## 🔐 Full Security Audit Checklist

### A. Authentication & JWT (10 items)

**Generation & Encoding**
- [ ] JWT created with `create_tokens(user_id)` method
- [ ] Access token TTL = 24 hours (configurable)
- [ ] Refresh token TTL = 30 days (configurable)
- [ ] Token payload includes: `sub` (user_id), `exp`, `iat`
- [ ] JWT_SECRET is 32+ characters (strong enough)

**Validation & Middleware**
- [ ] JWT middleware extracts token from `Authorization: Bearer <token>`
- [ ] Invalid/missing token returns 401 Unauthorized
- [ ] Expired token returns 401 (not 403 or 200)
- [ ] Token signature verified (tampering detected)
- [ ] Token payload validated (not just base64 decoded)

**Refresh Token Management**
- [ ] Old refresh tokens are invalidated after use (one-time use)
- [ ] Refresh endpoint requires valid refresh_token
- [ ] Refresh returns new access_token + refresh_token pair
- [ ] Refresh token stored encrypted in DB
- [ ] Device fingerprint OR IP validation optional (but recommended)

**Logout & Revocation**
- [ ] Logout endpoint deletes refresh_token from DB
- [ ] Access token cannot be revoked (expires naturally)
- [ ] Revoked user's token rejected at middleware
- [ ] Token still works if cache not updated (acceptable, will expire)

**Test Commands**:
```bash
pytest tests/test_auth.py -v
```

---

### B. Password Security (5 items)

- [ ] Passwords hashed with bcrypt (not MD5, SHA1, or plain text)
- [ ] Hashing cost factor >= 10 (default is 12, good)
- [ ] Passwords never logged or printed (check code + logs)
- [ ] Password validation prevents weak passwords (min 8 chars)
- [ ] Password reset email is time-limited (1 hour expiration)

**Test**: 
```bash
# Check hashing in code
grep -n "bcrypt\|hash_password" app/services/auth_service.py
```

---

### C. Encryption & Secure Storage (8 items)

**Field-Level Encryption**
- [ ] Sensitive fields encrypted with AES-256
- [ ] Encryption key stored in secrets (not hardcoded)
- [ ] Encrypted fields: `bot.credentials`, `marketplace.api_secret`
- [ ] Decryption only happens on explicit read (not on model load)
- [ ] Encryption key has rotation process defined

**Secret Management**
- [ ] All secrets in `.env` (not in code)
- [ ] .env is in `.gitignore` (never committed)
- [ ] Secrets never printed in debug output
- [ ] Secrets never appear in logs
- [ ] Production secrets stored in secure vault (not .env)

**Database Encryption**
- [ ] pgcrypto extension enabled (columns marked ENCRYPTED)
- [ ] Encrypted fields cannot be searched plaintext (by design)

**Test**:
```bash
pytest tests/test_crypto.py -v
grep -r "API_KEY\|SECRET\|PASSWORD" app/ --include="*.py"  # Should be 0
```

---

### D. Multi-Tenant Isolation (12 items)

**Data Model**
- [ ] Every table has `tenant_id` FK to `tenants` table
- [ ] `tenant_id` is NOT NULL (enforced at DB level)
- [ ] No global data (not tenant-specific) — everything scoped
- [ ] Audit trail includes tenant context (soft deletes)

**Query Isolation**
- [ ] All SELECT queries include `WHERE tenant_id = values.get('tenant_id')`
- [ ] No JOIN across tenants (except to tenants table itself)
- [ ] No aggregate queries without GROUP BY tenant_id
- [ ] Pagination respects tenant isolation

**RLS Policies**
- [ ] SELECT policy: `(select auth.uid() as user_id) = usuarios.user_id AND usuarios.tenant_id = tenants.id`
- [ ] INSERT policy: `tenant_id = ANY(get_user_tenant_ids())`
- [ ] UPDATE policy: User is owner OR admin of tenant
- [ ] DELETE policy: Uses soft delete (update `deletado_em`)
- [ ] RLS enabled globally (disable bypassed by service role)

**API Enforcement**
- [ ] GET endpoints call `get_current_tenant()` dependency
- [ ] POST endpoints assign tenant_id from middleware
- [ ] PATCH/DELETE endpoints verify ownership (403 if not)
- [ ] No path traversal (e.g., `/api/tenants/{id}/bots/{bot_id}`)

**User Membership**
- [ ] User can only view/act on tenants they belong to
- [ ] Can user access tenant they're not member of? → 403
- [ ] Can user escalate role? → No (only owner can add members)
- [ ] can user see other users in different tenants? → No

**Test**:
```bash
pytest tests/test_tenant_isolation.py -v
```

---

### E. Role-Based Access Control (RBAC) (10 items)

**Role Definitions**
- [ ] Owner: Full access (all permissions)
- [ ] Admin: All except user management
- [ ] Editor: Can read & write data, not delete
- [ ] Viewer: Read-only access

**Permission Enforcement**
- [ ] Every protected endpoint checks role (missing role = 401/403)
- [ ] Role extracted from JWT `sub` + `tenant_members` lookup
- [ ] Invalid role returns 403 Forbidden
- [ ] Missing role returns 401 Unauthorized
- [ ] Role is re-validated per request (not cached unsafely)

**Specific Permission Checks**
- [ ] Viewer cannot POST/PATCH/DELETE (only GET)
- [ ] Editor cannot modify tenant settings (owner/admin only)
- [ ] Editor cannot delete users (owner/admin only)
- [ ] Viewer cannot see audit logs (admin only)
- [ ] Viewer cannot manage integrations (editor/admin only)

**Super-Admin Access**
- [ ] Super-admin role (if exists) documented & restricted
- [ ] Super-admin access logged at WARN level minimum
- [ ] Super-admin actions require approval/audit

**Test**:
```bash
pytest tests/test_rbac.py -v -k "editor" 
# Test: editor tries POST /bots → 403? Yes
```

---

### F. Rate Limiting & Quota (6 items)

**Per-Plan Limits**
- [ ] Free tier: 100 msgs/hour
- [ ] Starter: 1,000 msgs/hour
- [ ] Pro: 10,000 msgs/hour
- [ ] Enterprise: Unlimited (or SLA-based)

**Enforcement**
- [ ] Middleware checks quota before allowing request
- [ ] Over-limit returns 429 Too Many Requests
- [ ] Rate limit headers included: `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- [ ] Quota per tenant, not global

**Bypass Prevention**
- [ ] Cannot bypass by creating new tokens
- [ ] Cannot bypass by using different IP
- [ ] Token refresh doesn't reset rate limit

**Test**:
```bash
pytest tests/test_rate_limit.py -v
pytest tests/test_quota.py -v
```

---

### G. API Security & Input Validation (8 items)

**Input Validation**
- [ ] All inputs validated with Pydantic schemas
- [ ] Invalid input returns 422 Unprocessable Entity (with field errors)
- [ ] Email addresses validated (format check)
- [ ] UUIDs validated (format check)
- [ ] Enum values restricted (no arbitrary strings)

**Output Safety**
- [ ] Error messages don't reveal internal structure
- [ ] Database errors not exposed (e.g., UNIQUE constraint)
- [ ] Stack traces never returned to client
- [ ] SQL errors not shown (logged only)

**SQL Injection Prevention**
- [ ] All queries use parameterized statements (not string concat)
- [ ] No raw SQL with user input
- [ ] Grep: `format()`, `%` operator on SQL — should be 0

**CORS Security**
- [ ] CORS allowed origins are whitelist (not `"*"`)
- [ ] Sensitive endpoints limit CORS (or same-origin only)
- [ ] Credentials only sent to trusted origins

**Test**:
```bash
# Test invalid email
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "not-an-email", "password": "test123"}' 
# Should return 422, not 500

# Check for SQL injection vulnerability
grep -r "f\"" app/services/ --include="*.py" | grep -i "select\|insert"
```

---

### H. Secure Deletion & Audit Trail (6 items)

**Soft Deletes**
- [ ] All deletions use soft delete (update `deletado_em` timestamp)
- [ ] No hard deletes (DROP rows) except in migrations
- [ ] Queries always filter `WHERE deletado_em IS NULL`
- [ ] Deleted data still in DB (audit trail preserved)

**Audit Logging**
- [ ] All sensitive actions logged (create/update/delete)
- [ ] Logs include: timestamp, user_id, tenant_id, action, old/new values
- [ ] Logs stored in `audit_logs` table (in DB)
- [ ] Admin can query audit logs
- [ ] Logs cannot be deleted (append-only)

**Data Retention**
- [ ] Soft-deleted data retained per compliance requirements (GDPR: 30 days)
- [ ] Hard delete job runs after retention period
- [ ] Hard delete job is logged

**Test**:
```bash
# Delete a bot
curl -X DELETE http://localhost:8000/bots/{id} \
  -H "Authorization: Bearer $TOKEN"

# Try to fetch deleted bot
curl http://localhost:8000/bots/{id} \
  -H "Authorization: Bearer $TOKEN"
# Should return 404 (not found)

# Check audit trail
SELECT * FROM audit_logs WHERE resource_id = '$BOTID' ORDER BY criado_em DESC;
```

---

### I. Logging & Monitoring (6 items)

**Sensitive Data in Logs**
- [ ] Passwords NEVER logged
- [ ] API keys NEVER logged
- [ ] JWT tokens NEVER logged full (only first 10 chars + "..." if needed)
- [ ] User emails logged only when necessary (with approval)
- [ ] No PII in error messages

**Access Logging**
- [ ] All API requests logged (method, path, status, duration)
- [ ] Failed auth attempts logged (with fail reason)
- [ ] Permission denied (403) logged with user context
- [ ] Unusual activity flagged (e.g., 10 failed logins in 1 min)

**Error Logging**
- [ ] Errors logged with full stack trace (server-side only)
- [ ] Error ID provided to client (for support reference)
- [ ] Log level appropriate (INFO for normal, WARN for issues, ERROR for bugs)

**Test**:
```bash
# Make failed auth request
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "wrong123"}'

# Check logs (should NOT contain password)
tail -f logs/app.log | grep "wrong123"  # Should be 0
tail -f logs/app.log | grep "login.*failed"  # Should exist
```

---

### J. Infrastructure & Deployment (5 items)

**HTTPS/TLS**
- [ ] Production uses HTTPS (not HTTP)
- [ ] TLS version >= 1.2 (TLS 1.3 preferred)
- [ ] Certificate is valid (not expired, not self-signed)
- [ ] Certificate chains to known CA (not self-signed)
- [ ] Mixed content blocked (no HTTP resources from HTTPS page)

**Headers & Security Config**
- [ ] Security headers sent: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`
- [ ] HSTS enabled (browsers remember to use HTTPS)
- [ ] CSP header set (prevents XSS via style/script injection)
- [ ] Referrer-Policy set (controls what referrer is sent)

**Deployment Isolation**
- [ ] Dev, staging, production are isolated systems
- [ ] Dev/staging do NOT use production secrets
- [ ] Production secrets different from staging
- [ ] Database backups encrypted & stored securely
- [ ] Access logs retained for audit (30+ days)

**Test**:
```bash
curl -I https://api.conektabots.com/health
# Should see Security headers
```

---

## 📋 Compliance Checklists

### GDPR Compliance

- [ ] User can request data export (right to data portability)
- [ ] User can request deletion (right to be forgotten)
- [ ] Deleted data removed within 30 days (soft delete + purge job)
- [ ] Data processing consent documented
- [ ] Password reset available (user can change their password)
- [ ] No data shared without consent

### SOC 2 Compliance (Type I)

- [ ] Security policy documented (this checklist)
- [ ] Access controls enforced (RBAC, RLS)
- [ ] Encryption for data at-rest (AES-256)
- [ ] Encryption for data in-transit (HTTPS/TLS)
- [ ] Audit trail maintained (soft deletes, logs)
- [ ] Security training documented
- [ ] Incident response plan documented

### SOC 2 Compliance (Type II)

- [ ] Security controls effective over 6-12 months (monitoring logs)
- [ ] Access reviews documented
- [ ] Permission changes logged
- [ ] Unauthorized access attempts detected
- [ ] Incident response tested

---

## 🎯 Scoring

For each phase, calculate:
- **Pass**: All items checked AND tested
- **Warning**: Most items pass but some gaps
- **Fail**: Multiple items failed OR critical items unchecked

**Overall Score**:
```
Total Items: 73
Score = (Items Passed / 73) × 100

90-100% = ✅ Excellent (production-ready)
75-89%  = 🟡 Good (minor fixes needed)
50-74%  = 🔴 Poor (major fixes needed)
<50%    = 🚨 Critical (do not deploy)
```

---

**Last Updated**: April 15, 2026  
**Total Checklist Items**: 73  
**Estimated Review Time**: 4-5 hours  
