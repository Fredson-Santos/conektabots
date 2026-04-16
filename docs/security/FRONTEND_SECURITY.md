# 🔐 Frontend Security Guide — ConektaBots Integration

## Table of Contents
1. [JWT Token Management](#jwt-token-management)
2. [CORS Configuration](#cors-configuration)
3. [XSS Prevention](#xss-prevention)
4. [CSRF Protection](#csrf-protection)
5. [Tenant Context Management](#tenant-context-management)
6. [Secrets Management](#secrets-management)
7. [HTTPS & Transport Security](#https--transport-security)
8. [Authentication Flow](#authentication-flow)
9. [Common Vulnerabilities & Mitigations](#common-vulnerabilities--mitigations)
10. [Checklists](#checklists)

---

## JWT Token Management

### Overview

ConektaBots uses **JWT (JSON Web Tokens)** for stateless authentication. The frontend receives tokens after login/registration, stores them locally, and includes them in API requests.

### Token Structure

**Access Token** (used for API requests):
`json
{
  "sub": "user-id-uuid",          // Subject (user ID)
  "email": "user@example.com",    // User email
  "tenant": "tenant-id-uuid",     // Current tenant
  "role": "owner|admin|editor|viewer",  // User role in tenant
  "exp": 1713298800,              // Expiration (Unix timestamp)
  "iat": 1713295200               // Issued at (Unix timestamp)
}
`

**Token Lifecycle**:
- **Access Token TTL**: 30 minutes (1800 seconds)
- **Refresh Token TTL**: 7 days (604800 seconds)
- **Generated at**: Login & Registration endpoints

### Browser Storage Strategy

#### ⚠️ Trade-offs Analysis

| Storage | Security | Convenience | XSS Risk | CSRF Risk |
|---------|----------|-------------|----------|-----------|
| **localStorage** | ❌ Low | ⭐⭐⭐ Highest | ⚠️ High | ✅ None |
| **sessionStorage** | ✅ Medium | ⭐⭐ Medium | ⚠️ High | ✅ None |
| **HttpOnly Cookie** | ✅⭐ Highest | ⭐ Lowest | ✅ None | ⚠️ Need CSRF Token |
| **In-Memory (Vuex/Pinia)** | ✅⭐ Highest | ⭐ Lowest | ✅ None | ✅ None |

#### Recommended Strategy: **Hybrid Approach**

For ConektaBots, use **localStorage + In-Memory Cache**:

`javascript
// ✅ SECURE IMPLEMENTATION

// 1. On Login, store tokens in localStorage
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});

const tokens = await response.json();

// Store refresh token (longer-lived, used only for refresh)
localStorage.setItem('refresh_token', tokens.refresh_token);

// Store access token
localStorage.setItem('access_token', tokens.access_token);

// 2. Cache tenant_id and role in in-memory state (Vuex/Pinia)
store.commit('setCurrentTenant', tokens.tenant_id);
store.commit('setCurrentRole', tokens.role);
`

**Why this approach?**
- **localStorage**: Persists across page reloads (better UX)
- **In-Memory**: Clears on logout/page refresh (reduces XSS attack surface)
- **Split tokens**: Access token in localStorage, but validated quickly; refresh token is higher security

#### Alternative: Pure HttpOnly Cookies (Most Secure)

`javascript
// Backend returns tokens in HttpOnly cookies
// Frontend automatically includes cookies in requests

// ✅ SECURE but less flexible
// - Can't access token in JavaScript (good for XSS)
// - Requires CSRF protection (POST/PATCH/DELETE)
// - Cookies included automatically in fetch (if credentials: 'include')
`

**Pros**:
- Immune to XSS (JavaScript cannot access token)
- Automatic cookie inclusion in requests

**Cons**:
- Requires CSRF token for state-changing operations
- Less flexible for mobile apps (no cookie storage in React Native)
- More complex CORS setup

**Recommendation**: Use HttpOnly cookies if building **web-only app**. Use localStorage if also building **mobile or multi-origin app**.

### Token Refresh Flow

**Access token expires in 30 minutes. Here's how to refresh:**

`javascript
// ❌ WRONG: Store expired access token
const accessToken = localStorage.getItem('access_token');
// ... 30 minutes later, token is expired ...
// Request fails with 401 → User must login again!

// ✅ CORRECT: Refresh token before expiration or on 401

// 1. Calculate expiration (from JWT payload)
const decodeToken = (token) => {
  return JSON.parse(atob(token.split('.')[1]));  // Decode payload
};

const token = localStorage.getItem('access_token');
const payload = decodeToken(token);
const expiresIn = (payload.exp * 1000) - Date.now();  // ms until expiration

if (expiresIn < 5 * 60 * 1000) {  // Less than 5 minutes left
  // Refresh immediately
  await refreshToken();
}

// 2. Or use axios interceptor (cleaner approach)
// See next section...
`

### API Request Integration (Fetch/Axios)

#### Using Fetch API

`javascript
// ✅ CORRECT: Include token in Authorization header

const apiCall = async (endpoint, options = {}) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(endpoint, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': \Bearer \\,
      'Content-Type': 'application/json',
    },
  });

  // Handle 401 Unauthorized → Token expired
  if (response.status === 401) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      // Retry request with new token
      return apiCall(endpoint, options);
    } else {
      // Refresh failed → Logout user
      logout();
      return null;
    }
  }

  return response;
};

const refreshAccessToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) return false;

  try {
    const response = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (response.ok) {
      const { access_token, refresh_token } = await response.json();
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      return true;
    }
  } catch (error) {
    console.error('Token refresh failed:', error);
  }

  return false;
};
`

#### Using Axios Interceptors (Recommended for SPAs)

`javascript
// ✅ BEST APPROACH: Automatic token refresh on 401

import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 10000,
});

// Request interceptor: Add token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = \Bearer \\;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Handle 401 and refresh
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = \Bearer \\;
          return api(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const { access_token } = await refreshAccessToken();
        api.defaults.headers.common.Authorization = \Bearer \\;
        originalRequest.headers.Authorization = \Bearer \\;
        processQueue(null, access_token);
        return api(originalRequest);
      } catch (err) {
        processQueue(err, null);
        // Redirect to login
        window.location.href = '/login';
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
`

### Token Expiration Handling

**Scenario**: User is on page A, token expires, user navigates to page B

**Solution**: Check token expiration before every request:

`javascript
const isTokenExpired = () => {
  const token = localStorage.getItem('access_token');
  if (!token) return true;

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const expiresAt = payload.exp * 1000;  // Convert to ms
    return Date.now() >= expiresAt;
  } catch {
    return true;
  }
};

// Usage in app initialization
if (isTokenExpired()) {
  await refreshAccessToken();  // Try to refresh
  if (isTokenExpired()) {
    // Refresh failed, logout
    logout();
  }
}
`

---

## CORS Configuration

### Overview

CORS (Cross-Origin Resource Sharing) controls which domains can access your API.

### Current Backend Configuration

**File**: [main.py](../../main.py#L31-L38)

`python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],  # ⚠️ Check this!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
`

**From [config.py](../../app/core/config.py#L51-L52)**:
`python
CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
`

### Development Setup

Create .env.local in your frontend project:

`ash
# .env.local (development)
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
`

### Production Setup

**Backend** ([.env.production](../../.env.example)):
`ash
# Production CORS whitelist
CORS_ORIGINS=["https://app.conektabots.com","https://conektabots.com"]
`

**Frontend** [.env.production](#):
`ash
REACT_APP_API_URL=https://api.conektabots.com
REACT_APP_ENV=production
`

### Making CORS-Safe Requests

`javascript
// ✅ CORRECT: Credentials included for auth

const response = await fetch('http://localhost:8000/api/v1/bots', {
  method: 'GET',
  credentials: 'include',  // ✅ Send cookies/auth headers
  headers: {
    'Authorization': \Bearer \\,
    'Content-Type': 'application/json',
  },
});
`

### Debugging CORS Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| CORS policy: no 'Access-Control-Allow-Origin' | Origin not whitelisted | Add origin to CORS_ORIGINS |
| CORS policy: request method not allowed | Method not in allow_methods | Check CORS config allows POST/PATCH/DELETE |
| CORS policy: Request header not allowed | Custom header not allowed | Add header to allow_headers |

**Debug command** (test from browser console):
`javascript
fetch('http://localhost:8000/api/v1/tenants', {
  method: 'GET',
  headers: { 'Authorization': \Bearer \\ }
})
.then(r => r.json())
.then(console.log)
.catch(e => console.error('CORS Error:', e.message));
`

---

## XSS Prevention

### Content Security Policy (CSP)

Add CSP headers to frontend (if using a backend, via middleware):

**In public/index.html** (or via middleware):
`html
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' http://localhost:8000 https://api.conektabots.com;
  font-src 'self';
  object-src 'none';
  base-uri 'self';
  form-action 'self';
  upgrade-insecure-requests;
">
`

**Meaning**:
- default-src 'self' — Only load resources from same origin
- script-src 'self' — Only load scripts from same origin
- connect-src 'self' https://api.conektabots.com — Only API calls to whitelisted domains
- object-src 'none' — Never embed Flash/objects
- upgrade-insecure-requests — Force HTTPS

### Input Sanitization

**❌ WRONG: Render user input directly**
`javascript
// Dangerous!
const bot_name = userInput;  // "Click me" or "<img src=X onerror=alert(1)>"
document.getElementById('name').innerHTML = bot_name;  // XSS!
`

**✅ CORRECT: Sanitize with DOMPurify**
`javascript
import DOMPurify from 'dompurify';

const bot_name = userInput;
const safe_name = DOMPurify.sanitize(bot_name);
document.getElementById('name').textContent = safe_name;  // Safe!
`

Or use React's built-in escaping:
`jsx
const BotName = ({ name }) => (
  <div>{name}</div>  // React automatically escapes by default
);
`

### Output Encoding

**Always encode user-generated content**:

`javascript
// ❌ Dangerous
<div dangerouslySetInnerHTML={{ __html: botDescription }} />

// ✅ Safe
<div>{botDescription}</div>  // React escapes HTML automatically
`

---

## CSRF Protection

### Is CSRF Protection Needed?

**No, because** ConektaBots uses **stateless JWT authentication**:

- CSRF attacks work on **cookie-based sessions** (automatic inclusion)
- JWT tokens are **explicitly included** in Authorization header
- Attacker cannot trick browser into sending token (not in cookies)

**However, if using HttpOnly Cookies**, CSRF protection is needed:

`javascript
// ✅ If using HttpOnly cookies, add CSRF tokenemand backend validation

// 1. Get CSRF token from response header
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

// 2. Include in request headers
const response = await fetch('/api/v1/bots', {
  method: 'POST',
  headers: {
    'X-CSRF-Token': csrfToken,  // ← Backend validates this
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(botData),
});
`

---

## Tenant Context Management

### How to Get Tenant ID

**On Login Response**:
`javascript
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  body: JSON.stringify({ email, password }),
});

const { access_token, tenant_id, role } = await response.json();

// Store in app state (Redux/Vuex/Pinia)
store.dispatch('setTenant', {
  tenant_id,
  role,
});
`

### Passing Tenant ID in Requests

**Option 1: Via JWT Token (Recommended)**

The tenant_id is already in the JWT token → Backend extracts it

`javascript
// No need to pass tenant_id explicitly!
// Backend gets it from Depends(get_current_tenant)

const response = await api.get('/api/v1/bots');  // ✅ Backend knows tenant
`

**Option 2: Via Query Parameter (Less Secure)**

`javascript
// ❌ Not recommended (raises security concerns)
const response = await api.get(\/api/v1/bots?tenant_id=\\);

// ✅ Problem: User could pass a different tenant_id
// ✅ Backend MUST validate tenant_id matches JWT claim
`

### Multi-Tenant Selection

If user has multiple tenants:

`javascript
const response = await fetch('/api/v1/me', {
  headers: { 'Authorization': \Bearer \\ }
});

const { tenants } = await response.json();
// [{ id: 'tenant-1', name: 'Company A' }, ...]

// User selects tenant → Update app state
store.commit('setCurrentTenant', 'tenant-2');

// Next API calls use tenant-2
`

---

## Secrets Management

### Environment Variables

**Frontend** (.env files):

`ash
# ❌ NEVER store secrets in frontend
REACT_APP_API_URL=https://api.conektabots.com  # ✅ OK
REACT_APP_API_KEY=sk-abc123  # ❌ NEVER! (visible in browser)

# ✅ CORRECT: Only public configuration
REACT_APP_FEATURE_FLAGS=advanced_analytics
REACT_APP_VERSION=1.0.0
`

**Private Data** (Backend only):

- API keys (Telegram, Stripe, Shopee, etc.)
- Database credentials
- JWT secrets
- Encryption keys

These should **never** be sent to frontend.

### API Key Rotation

If frontend needs an API key (e.g., to call a third-party service):

1. **Backend generates short-lived token** specifically for frontend
2. Frontend uses token (valid 5-10 minutes)
3. Token expires → Frontend must get new token
4. Even if leaked, damage is limited

`javascript
// Example: Get temporary API token
const getTempApiToken = async () => {
  const response = await fetch('/api/v1/tokens/temp', {
    headers: { 'Authorization': \Bearer \\ }
  });
  return await response.json();  // { temp_token, expires_in }
};
`

---

## HTTPS & Transport Security

### Production Requirements

✅ **MUST** use HTTPS for all production traffic:

`javascript
// ❌ WRONG: HTTP in production
const API_URL = 'http://api.conektabots.com';

// ✅ CORRECT: HTTPS
const API_URL = 'https://api.conektabots.com';
`

### SSL/TLS Certificate

- Use valid certificate (not self-signed)
- Minimum TLS 1.2 (recommend 1.3)
- Certificate must match domain name
- Auto-renewal (Let's Encrypt is free)

### HSTS Headers

Backend should return HSTS headers (forces HTTPS):

`python
# In FastAPI middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
`

### Secure Cookies (if using cookies)

`javascript
// Backend must set cookies with Secure + SameSite flags
// This is automatic if using HttpOnly cookies in production
`

---

## Authentication Flow

### Visual Flow Diagram

`
┌─────────────────────────────────────────────────────────────┐
│                    CONEKTABOTS AUTH FLOW                     │
└─────────────────────────────────────────────────────────────┘

1. USER REGISTRATION / LOGIN
   ├─ Frontend: POST /api/v1/auth/register or /login
   ├─ Backend: Validate credentials, hash password (bcrypt)
   ├─ Backend: Generate JWT tokens (access + refresh)
   └─ Frontend: Receive tokens → Store in localStorage

2. AUTHENTICATED API REQUEST
   ├─ Frontend: GET /api/v1/bots with Authorization header
   ├─ Backend: Validate JWT token signature + expiration
   ├─ Backend: Extract user_id, tenant_id from JWT
   ├─ Backend: Verify user belongs to tenant (RLS)
   └─ Backend: Return data filtered by tenant_id

3. TOKEN REFRESH (Access token expires)
   ├─ Frontend: 401 response → Trigger refresh
   ├─ Frontend: POST /api/v1/auth/refresh with refresh_token
   ├─ Backend: Validate refresh_token (not revoked, not expired)
   ├─ Backend: Generate new access_token + refresh_token
   └─ Frontend: Update tokens, retry original request

4. LOGOUT
   ├─ Frontend: Clear localStorage (remove tokens)
   ├─ Backend: (Optional) Blacklist refresh_token in DB
   └─ Frontend: Redirect to login page

5. TENANT SWITCHING (if user has multiple tenants)
   ├─ Frontend: User selects new tenant
   ├─ Frontend: POST /api/v1/tenants/{tenant_id}/switch
   ├─ Backend: Generate new token with new tenant_id
   └─ Frontend: Update localStorage with new access_token
`

---

## Common Vulnerabilities & Mitigations

| Vulnerability | Risk | Mitigation |
|---------------|------|-----------|
| **JWT Token Theft (XSS)** | Attacker steals token, impersonates user | Use HttpOnly cookies, CSP, input sanitization |
| **JWT Token Expired** | User stuck on stale page | Implement token refresh on 401 |
| **CORS Misconfiguration** | Attacker origin is whitelisted | Maintain strict CORS_ORIGINS whitelist |
| **Token in URL** | Token logged in browser history | Always use Authorization header, never URL param |
| **Token in Logs** | Sensitive info exposed | Never log tokens, use {token_prefix}... |
| **Plaintext Password Storage** | Passwords exposed if DB breached | Backend uses bcrypt (not reversible) |
| **XSS Attack** | JavaScript runs user code | Use DOMPurify, CSP, React escaping |
| **CSRF (if cookies)** | Attacker tricks user into state-changing request | CSRF tokens (if using cookies) |
| **Missing Tenant Check** | User A sees User B's data | Always filter by tenant_id |
| **Privilege Escalation** | Viewer becomes Admin | Check role in every permission-required endpoint |

---

## Checklists

### ✅ Development Environment Checklist

- [ ] JWT tokens stored in localStorage
- [ ] Axios interceptors configured (token refresh on 401)
- [ ] CORS_ORIGINS includes localhost:3000
- [ ] CSP headers defined (even in dev)
- [ ] Environment variables are public-only (no secrets)
- [ ] DOMPurify installed and used for user input
- [ ] No JWT tokens logged to console
- [ ] Token refresh flow tested (let token expire, verify refresh works)
- [ ] Multi-tenant context passed in requests
- [ ] API calls include Authorization header

### ✅ Pre-Production Checklist

- [ ] All localhost:3000 origins removed from CORS_ORIGINS
- [ ] SSL certificate installed (HTTPS working)
- [ ] HSTS headers configured in production
- [ ] CSP headers hardened (no 'unsafe-inline' if possible)
- [ ] DOMPurify sanitization active
- [ ] Token refresh flow tested in production URL
- [ ] HttpOnly cookies considered (vs localStorage)
- [ ] CSRF tokens setup (if using cookies)
- [ ] Tenant isolation verified (cross-tenant access denied)
- [ ] Rate limiting tested (quota enforcement)
- [ ] Error messages don't leak sensitive info
- [ ] No secrets in frontend code
- [ ] Password requirements documented (>=8 chars, complexity rules)

### ✅ Post-Deployment Checklist

- [ ] Monitor for JWT token theft (unusual IP addresses, rapid requests)
- [ ] Token refresh working for all users
- [ ] No false 401 errors from token expiration
- [ ] CORS errors monitored (might indicate attack)
- [ ] Logs don't contain tokens or passwords
- [ ] Rate limiting protecting against brute force
- [ ] Tenant data isolation working (no cross-tenant leaks)
- [ ] User can switch tenants without re-login

---

## Summary

| Component | Recommendation | Status |
|-----------|----------------|--------|
| Token Storage | localStorage + In-Memory | ✅ Implemented |
| Token Refresh | Axios interceptor on 401 | ⚠️ To implement |
| CORS | Whitelisted origins (dev: localhost:3000) | ✅ Configured |
| CSP Headers | Content-Security-Policy meta tag | ⚠️ To add |
| XSS Prevention | DOMPurify + React escaping | ✅ Use framework default |
| CSRF | Not needed (stateless JWT) | ✅ N/A |
| Secrets | Never in frontend environment | ✅ Follow policy |
| HTTPS | Enforced in production | ✅ Setup in deployment |
| Multi-tenant | Filter by tenant_id (backend) | ✅ Backend enforces |

---

**Last Updated**: April 15, 2026  
**Version**: 1.0.0 (Phase 3 Kickoff)  
**Next Review**: After frontend integration testing
