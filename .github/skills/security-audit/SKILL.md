---
name: security-audit
description: 'Comprehensive security audit for SaaS multi-tenant applications. Use when: reviewing JWT implementation, validating RLS policies, auditing encryption, checking multi-tenant isolation, detecting vulnerabilities, analyzing RBAC logic, preparing security reports.'
argument-hint: 'Task: full audit, JWT review, RLS validation, encryption check, etc.'
user-invocable: true
---

# Security Audit Skill

Perform comprehensive security audits on ConektaBots backend. This skill guides systematic review of authentication, encryption, multi-tenant isolation, and access control.

## When to Use

- **Pre-deployment security review** — Before releasing to staging/production
- **Vulnerability assessment** — After major code changes
- **Security incident investigation** — When suspicious activity occurs
- **Compliance validation** — For SOC 2, GDPR, or customer audits
- **Third-party review** — Prepare audit documentation for external auditors
- **Architecture review** — Validate new features are secure by design

## Quick Start (5-Minute Checklist)

Use [Quick Security Checklist](./references/checklist.md#quick-5-minute-check) for fast validation:
- [ ] JWT tokens properly validated
- [ ] All queries filtered by tenant_id
- [ ] RLS policies block cross-tenant access
- [ ] Sensitive data encrypted
- [ ] Password hashing uses bcrypt
- [ ] No hardcoded secrets in code
- [ ] CORS configured (not "*" for sensitive endpoints)
- [ ] Rate limiting enforced
- [ ] Error messages don't leak sensitive info
- [ ] Soft deletes respected (deletado_em checked)

**Result**: ✅ Pass/❌ Fail for each item

---

## Full Security Audit Procedure

### Phase 1: Preparation (15 minutes)

1. **Understand scope**
   - Which systems to audit? (auth, databases, APIs, workers)
   - What's the threat model? (external attack, insider threat, data breach)
   - What compliance requirements? (GDPR, SOC 2, HIPAA)

2. **Gather documentation**
   - Read `app/core/security.py` — JWT, password handling
   - Read `app/core/deps.py` — Auth dependencies
   - List all sensitive data types (passwords, API secrets, user PII)
   - Read [Security Checklist](./references/checklist.md)

3. **Tools & access**
   - Have code editor open to `app/` directory
   - Have database access (dev/staging, NOT production initially)
   - Run audit script: `python ./scripts/audit.py`
   - Generate baseline report

**Output**: Scope document + baseline findings

---

### Phase 2: Authentication & JWT (30 minutes)

**Objective**: Verify JWT tokens are generated, validated, and revoked correctly

1. **Review JWT Generation**
   - [ ] Check `AuthService.create_tokens()` — are claims included?
   - [ ] Verify token TTL (access_token: 24h, refresh_token: 30d)
   - [ ] Confirm JWT_SECRET is never hardcoded (check .env)
   - [ ] Check JWT_ALGORITHM is HS256 (recommended) or RS256
   - [ ] Verify token includes `sub` (user_id) and `exp` (expiration)

2. **Validate JWT Middleware**
   - [ ] Read `app/middleware/auth.py` — does it validate signature?
   - [ ] Check expiration is verified (not accepting expired tokens)
   - [ ] Verify token is extracted from `Authorization: Bearer <token>`
   - [ ] Check what happens with invalid/missing token (401 Unauthorized)
   - [ ] Test: Can expired token still access endpoints? (Should be 401)

3. **Test Refresh Token Flow**
   - [ ] Verify refresh tokens stored in `refresh_tokens` table
   - [ ] Check old refresh tokens are revoked (one-time use or TTL)
   - [ ] Test: Can old refresh token be reused? (Should fail)
   - [ ] Verify refresh endpoint returns new access_token + refresh_token

4. **Test Token Revocation**
   - [ ] Does logout endpoint invalidate token?
   - [ ] Are refresh tokens deleted on logout?
   - [ ] Can revoked tokens still access endpoints? (Should be 401)

**Test Script**: Use `pytest tests/test_auth.py -v`

**Output**: JWT audit pass/fail + findings

---

### Phase 3: Multi-Tenant Isolation (45 minutes)

**Objective**: Verify tenant A cannot read/write tenant B data

1. **Review Data Model**
   - [ ] Check all tables have `tenant_id` FK constraint
   - [ ] Verify no data shared globally (everything tenant-scoped)
   - [ ] Check soft deletes respect tenant isolation (deletado_em)

2. **Validate RLS Policies**
   - [ ] Read `supabase/migrations/005_rls_policies.sql`
   - [ ] For each table, verify RLS SELECT policy filters by tenant_id
   - [ ] Check UPDATE policies only allow owner to modify
   - [ ] Verify DELETE policies use soft delete (update deletado_em)
   - [ ] Test: Can tenant B user SELECT rows from tenant A? (Should fail)

3. **Audit API Endpoints**
   - [ ] Check GET endpoints filter by `get_current_tenant()`
   - [ ] Verify POST endpoints assign `tenant_id` from dependency
   - [ ] Check PATCH/DELETE endpoints verify ownership (403 if not owner)
   - [ ] Run [audit script](./scripts/audit.py) to test endpoints

4. **Test Tenant Switching**
   - [ ] Can user with 2 tenants access both? (Yes, but only their data)
   - [ ] Can user access tenant they don't belong to? (403 Forbidden)
   - [ ] Run: `pytest tests/test_tenant_isolation.py -v`

5. **Check Member Roles**
   - [ ] Review `tenant_members` table roles (owner/admin/editor/viewer)
   - [ ] Verify editor cannot modify sensitive settings
   - [ ] Check viewer can only read, not write
   - [ ] Test: Viewer tries to update bot config — gets 403? (Yes)

**Output**: Multi-tenant audit pass/fail + isolation verified

---

### Phase 4: Encryption & Secrets (30 minutes)

**Objective**: Verify sensitive data is encrypted and managed securely

1. **Identify Sensitive Data**
   - [ ] Passwords (should be bcrypt hashed, never stored plaintext)
   - [ ] Bot credentials (api_id, api_hash, phone, session_string)
   - [ ] Marketplace API keys (Shopee, Mercado Livre, etc.)
   - [ ] Refresh tokens
   - [ ] User emails (PII)

2. **Verify Password Hashing**
   - [ ] Check `AuthService.hash_password()` uses bcrypt
   - [ ] Verify password is never logged or exposed in errors
   - [ ] Test: Can password be recovered from hash? (No)
   - [ ] Check password length requirement (>=8 chars recommended)

3. **Audit Field-Level Encryption**
   - [ ] Check `CryptoService` uses AES-256 for encryption
   - [ ] Verify encryption key comes from secrets (not hardcoded)
   - [ ] Check encrypted fields in models (bot.credentials, marketplace.api_secret)
   - [ ] Verify decrypt happens only on explicit read, not on load
   - [ ] Test: Can encrypted field be read without key? (No)

4. **Check Secret Management**
   - [ ] Verify all secrets in `.env` (not in code)
   - [ ] Check secrets are not logged or printed in debug output
   - [ ] Confirm encryption key rotation process exists
   - [ ] Run: `grep -r "JWT_SECRET\|API_KEY\|PASSWORD" app/ --include="*.py"` — should find none

5. **Verify HTTPS/TLS**
   - [ ] Confirm production uses HTTPS (not HTTP)
   - [ ] Check SSL certificate is valid and not self-signed
   - [ ] Verify TLS version >= 1.2

**Output**: Encryption audit pass/fail + secrets validation

---

### Phase 5: Role-Based Access Control (30 minutes)

**Objective**: Verify permissions are correctly enforced

1. **Map Roles & Permissions**
   - [ ] Document all roles (owner/admin/editor/viewer)
   - [ ] Define permissions per role (read/write/delete/admin)
   - [ ] Create permission matrix (role × action)

2. **Audit Endpoints**
   - [ ] Check each protected endpoint validates role
   - [ ] Verify 403 Forbidden returned for unauthorized roles
   - [ ] Check role is required from `Depends(require_role(...))`
   - [ ] Test: Editor tries admin-only action — gets 403? (Yes)

3. **Test RBAC Enforcement**
   - Run: `pytest tests/test_rbac.py -v` (if exists, or create)
   - Test: Viewer can GET /bots but not POST? (Yes)
   - Test: Admin can modify users but Editor cannot? (Yes)

4. **Check Cascading Permissions**
   - [ ] Owner has all permissions
   - [ ] Admin has all except user management
   - [ ] Editor can write but not delete
   - [ ] Viewer is read-only

**Output**: RBAC audit pass/fail + permission matrix validated

---

### Phase 6: API Security (30 minutes)

**Objective**: Verify API endpoints don't leak sensitive information

1. **Review Error Handling**
   - [ ] Error messages don't reveal internal paths or versions
   - [ ] Database errors not exposed (e.g., constraint violations)
   - [ ] Stack traces not returned to clients (only in logs)
   - [ ] Test: Invalid input doesn't reveal too much info

2. **Check Rate Limiting**
   - [ ] Rate limit is enforced per plan (Free/Starter/Pro/Enterprise)
   - [ ] Limit is per tenant, not global
   - [ ] Test: Exceed quota — get 429 Too Many Requests? (Yes)
   - [ ] Verify rate limit headers are present (X-RateLimit-Remaining)

3. **Validate Input/Output**
   - [ ] All inputs validated with Pydantic schemas
   - [ ] No SQL injection (all queries parameterized)
   - [ ] No XXS vulnerabilities (outputs properly escaped)
   - [ ] No CSRF protection needed (stateless JWT auth)

4. **Check CORS Configuration**
   - [ ] CORS is not `"*"` for sensitive endpoints
   - [ ] Allowed origins are whitelisted (not wildcards)
   - [ ] Credentials are only sent to same-origin

5. **Verify Logging**
   - [ ] Logs don't contain passwords or API keys
   - [ ] Sensitive operations are logged (who changed what)
   - [ ] Logs have timestamps and user context

**Output**: API security audit pass/fail + recommendations

---

### Phase 7: Audit Report (15 minutes)

1. **Generate Report**
   - Use [Report Template](./templates/report.md)
   - Run audit script: `python ./scripts/audit.py > audit_report.txt`
   - Summarize findings by severity (critical/high/medium/low)

2. **Create Action Items**
   - For each finding, define:
     - Root cause
     - Recommended fix
     - Priority (urgent/important/nice-to-have)
     - Owner (who fixes)
     - Timeline (when to fix)

3. **Review & Approve**
   - Security team reviews findings
   - Approve fixes and timeline
   - Track action items to completion

**Output**: Security audit report + action items

---

## Checklists

Refer to [Detailed Security Checklist](./references/checklist.md) for:
- Quick 5-minute check
- Full security audit checklist
- Compliance checklists (GDPR, SOC 2)
- Post-deployment verification

## Audit Script

Run [automated audit](./scripts/audit.py) to test endpoints:
```bash
python ./.github/skills/security-audit/scripts/audit.py \
  --base-url http://localhost:8000 \
  --admin-token <jwt-token> \
  --report-output audit_report.json
```

Generates:
- ✅/❌ for each endpoint
- Response time metrics
- Security header validation
- CORS policy validation

## Report Template

Use [Audit Report Template](./templates/report.md) to document findings:
- Executive summary
- Vulnerabilities (critical/high/medium/low)
- Recommendations
- Action items with owners & timelines
- Approval signatures

---

## Example Workflows

### Workflow 1: Quick Pre-Release Check (20 min)
```
1. Run quick checklist (5 min)
2. Run audit script (10 min)
3. Review critical findings (5 min)
→ Output: Pass/Fail + actions needed
```

### Workflow 2: Full Security Audit (4-5 hours)
```
1. Prep + Scope (15 min)
2. JWT review (30 min)
3. Multi-tenant validation (45 min)
4. Encryption & secrets (30 min)
5. RBAC enforcement (30 min)
6. API security (30 min)
7. Report & action items (15 min)
→ Output: Comprehensive audit report
```

### Workflow 3: Vulnerability Investigation (30-60 min)
```
1. Identify affected system (5 min)
2. Test for exploitation (10 min)
3. Determine impact (10 min)
4. Generate report (5 min)
5. Create fix + test (10 min)
→ Output: Incident report + patch
```

---

## Tools & Commands

| Task | Command |
|------|---------|
| Quick check | Use [Checklist](./references/checklist.md) |
| Full audit | `python ./scripts/audit.py` |
| JWT test | `pytest tests/test_auth.py -v` |
| Isolation test | `pytest tests/test_tenant_isolation.py -v` |
| Encryption test | `pytest tests/test_crypto.py -v` |
| RLS validation | `pytest tests/test_rls.py -v` |
| RBAC test | `pytest tests/test_rbac.py -v` |
| Rate limit test | `pytest tests/test_rate_limit.py -v` |

---

## Integration with Security Auditor Agent

Use this skill with [@Security Auditor](../../agents/security-auditor.agent.md) agent:
```
@Security Auditor: Run the full security audit skill to produce a comprehensive report.
Use the JWT review + multi-tenant validation + encryption audit phases.
```

---

## Related Skills & Resources

- [API Testing](./references/checklist.md) — Endpoint security testing
- [Compliance](./references/checklist.md#compliance-checklists) — GDPR, SOC 2 requirements
- [Incident Response](./templates/report.md) — Security incident documentation

---

**Last Updated**: April 15, 2026  
**Estimated Duration**: 4-5 hours for full audit | 20 minutes for quick check  
**Owner**: Security Audit Skill
