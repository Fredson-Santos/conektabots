# ✅ JWT Implementation Checklist

## JWT Token Structure

### Access Token Claims

`json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // User UUID
  "email": "user@example.com",                    // Email
  "tenant": "660e8400-e29b-41d4-a716-446655440001",  // Tenant UUID
  "role": "owner|admin|editor|viewer",           // User role
  "exp": 1713301500,                             // Expiration (Unix timestamp = 30 min)
  "iat": 1713299700,                             // Issued at
  "type": "access"                               // Token type (optional)
}
`

### Refresh Token Claims

`json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // User UUID
  "exp": 1714508700,                             // Expiration (Unix timestamp = 7 days)
  "iat": 1713299700,                             // Issued at
  "type": "refresh"                              // Token type marker
}
`

---

## Token Lifecycle

### 1. Registration/Login

`
User submits credentials (email, password)
         ↓
Backend validates email + password
         ↓
Backend generates:
  - Access token (30 min)
  - Refresh token (7 days)
         ↓
Frontend receives both tokens
         ↓
Frontend stores:
  - accessToken in localStorage
  - refreshToken in localStorage
  - tenant_id in app state (Redux/Pinia)
`

**Endpoint**: POST /api/v1/auth/login

**Request**:
`json
{
  "email": "user@example.com",
  "password": "secure-password"
}
`

**Response**:
`json
{
  "access_token": "eyJhbGc...",           // JWT token
  "refresh_token": "eyJhbGc...",          // JWT token (longer TTL)
  "token_type": "bearer",
  "expires_in": 1800,                     // seconds (30 min)
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "660e8400-e29b-41d4-a716-446655440001",
  "role": "owner"
}
`

### 2. Using Access Token

`
Frontend includes token in Authorization header
         ↓
GET /api/v1/bots
Authorization: Bearer eyJhbGc...
         ↓
Backend middleware extracts token
         ↓
Backend validates:
  - Signature (matches JWT_SECRET)
  - Expiration (not expired)
  - Claims present (sub, tenant, role)
         ↓
If valid: Request continues
If invalid/expired: Return 401 Unauthorized
`

### 3. Token Refresh

`
Access token expires (TTL = 30 min)
         ↓
Frontend detects 401 response
         ↓
Frontend calls: POST /api/v1/auth/refresh
  Body: { refresh_token: "eyJhbGc..." }
         ↓
Backend validates refresh_token:
  - Signature valid
  - Not expired (TTL = 7 days)
  - Not revoked (optional: check DB)
         ↓
Backend generates new tokens
         ↓
Frontend updates localStorage
         ↓
Frontend retries original request
`

**Endpoint**: POST /api/v1/auth/refresh

**Request**:
`json
{
  "refresh_token": "eyJhbGc..."
}
`

**Response**:
`json
{
  "access_token": "eyJhbGc...",           // NEW token (30 min TTL)
  "refresh_token": "eyJhbGc...",          // NEW token (7 days TTL)
  "expires_in": 1800
}
`

### 4. Logout

`
User clicks "Logout"
         ↓
Frontend clears localStorage:
  - Remove accessToken
  - Remove refreshToken
         ↓
Frontend redirects to /login
         ↓
Backend (optional):
  - Mark refresh_token as revoked
  - Clear session (if any)
`

**Optional**: Send logout event to backend:

`
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
         ↓
Backend revokes refresh_token
`

---

## Storage Strategies

### Option 1: localStorage (Recommended for SPAs)

**Pros**:
- ✅ Persists across page reloads
- ✅ Easy to manage
- ✅ Works with multiple tabs

**Cons**:
- ⚠️ Vulnerable to XSS attacks
- ⚠️ Requires manual cleanup on logout

**Implementation**:

`javascript
// Store tokens
localStorage.setItem('access_token', response.access_token);
localStorage.setItem('refresh_token', response.refresh_token);

// Retrieve token
const token = localStorage.getItem('access_token');

// Clear on logout
localStorage.removeItem('access_token');
localStorage.removeItem('refresh_token');
`

### Option 2: sessionStorage

**Pros**:
- ✅ Safer than localStorage (cleared on tab close)
- ✅ Can't be stolen if page closed

**Cons**:
- ❌ Lost on page refresh
- ❌ Not shared across tabs

**Implementation**:

`javascript
sessionStorage.setItem('access_token', response.access_token);
`

### Option 3: HttpOnly Cookies (Most Secure)

**Pros**:
- ✅ Immune to XSS
- ✅ Auto-included in requests
- ✅ Server can invalidate immediately

**Cons**:
- ⚠️ More complex setup
- ⚠️ Requires CSRF protection
- ⚠️ Less flexible for mobile

**Implementation**:

`python
# Backend: Set HttpOnly cookie
response = JSONResponse({"success": True})
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,      # ✅ JavaScript can't access
    secure=True,        # ✅ HTTPS only
    samesite="Strict",  # ✅ Prevents CSRF
    max_age=1800,       # 30 minutes
)
return response
`

`javascript
// Frontend: Automatically included in fetch requests
const response = await fetch('/api/v1/bots', {
  credentials: 'include',  // ← Include cookies
});
`

---

## Token Storage Recommendation Matrix

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Web SPA (React/Vue) | localStorage | Persists, simple |
| Mobile (React Native) | In-memory + AsyncStorage | No cookies support |
| High-security app | HttpOnly cookies | Immune to XSS |
| Multi-tab scenarios | localStorage | Shared across tabs |
| Logout on tab close | sessionStorage | Auto-clears |

**Verdict for ConektaBots**: Use **localStorage** for now (good balance), upgrade to HttpOnly cookies later if needed.

---

## Frontend Implementation Patterns

### Pattern 1: Basic Token Management

`javascript
// ❌ WRONG: Token expires silently

const login = async (email, password) => {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  const { access_token } = await response.json();
  localStorage.setItem('access_token', access_token);
};

const callApi = async (endpoint) => {
  const token = localStorage.getItem('access_token');
  const response = await fetch(endpoint, {
    headers: { 'Authorization': \Bearer \\ }
  });
  
  // ❌ What if token expired 5 minutes ago?
  if (response.status === 401) {
    // ❌ User not notified, request just fails
  }
  return response;
};
`

**Problems**:
- Token expires silently
- No automatic refresh
- Bad UX (random 401 errors)

### Pattern 2: Token Expiration Check (Better)

`javascript
// ✅ BETTER: Check expiration before request

const isTokenExpired = () => {
  const token = localStorage.getItem('access_token');
  if (!token) return true;

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const expiresAt = payload.exp * 1000;  // ms
    const now = Date.now();
    return now >= expiresAt;
  } catch (e) {
    return true;
  }
};

const ensureValidToken = async () => {
  // If token expires in < 5 min, refresh now
  const token = localStorage.getItem('access_token');
  if (!token) return false;

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const expiresAt = payload.exp * 1000;
    const timeUntilExpiry = expiresAt - Date.now();
    
    if (timeUntilExpiry < 5 * 60 * 1000) {  // < 5 minutes
      await refreshAccessToken();
    }
  } catch (e) {
    return false;
  }
  return true;
};
`

### Pattern 3: Axios Interceptor (Best)

`javascript
// ✅ BEST: Automatic token refresh on 401

import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 10000,
});

// Request interceptor: Add token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = \Bearer \\;
  }
  return config;
}, (error) => Promise.reject(error));

// Response interceptor: Handle 401
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
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          \\/api/v1/auth/refresh\,
          { refresh_token: refreshToken }
        );

        const { access_token, refresh_token } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);

        api.defaults.headers.common.Authorization = \Bearer \\;
        originalRequest.headers.Authorization = \Bearer \\;

        processQueue(null, access_token);
        return api(originalRequest);
      } catch (err) {
        processQueue(err, null);
        localStorage.clear();  // Clear tokens
        window.location.href = '/login';  // Redirect to login
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

---

## Backend Token Generation & Validation

### Backend: Generate Token

**File**: [app/services/auth_service.py#L72-L91](../../app/services/auth_service.py#L72-L91)

`python
def create_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=self.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    return encoded_jwt
`

**Usage**:

`python
# Generate access token (30 min)
access_token = await auth_service.create_token(
    {
        "sub": str(user.id),
        "email": user.email,
        "tenant": str(tenant.id),
        "role": member.role,
    }
)

# Generate refresh token (7 days)
refresh_token = await auth_service.create_token(
    {"sub": str(user.id), "type": "refresh"},
    expires_delta=timedelta(days=7)
)
`

### Backend: Validate Token

**File**: [app/services/auth_service.py#L93-L105](../../app/services/auth_service.py#L93-L105)

`python
def decode_token(self, token: str) -> dict:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
`

**Used in middleware**:

`python
# app/middleware/auth.py
payload = decode_token(token)
if payload is None:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"error": "Invalid or expired token"},
    )
`

---

## Security Best Practices

### ✅ DO

- ✅ Include exp (expiration) in every token
- ✅ Include sub (user ID) for identification
- ✅ Include 	enant for multi-tenant isolation
- ✅ Include ole for permission checking
- ✅ Sign tokens with strong secret (MIN 32 chars)
- ✅ Use HS256 or RS256 algorithm
- ✅ Validate signature AND expiration
- ✅ Rotate refresh tokens (one-time use or TTL)
- ✅ Store refresh token in secure storage
- ✅ Clear tokens on logout
- ✅ Handle token expiration gracefully (refresh)

### ❌ DON'T

- ❌ Store tokens in URL (history leak)
- ❌ Log tokens (sensitive data leak)
- ❌ Use weak secrets (< 32 chars)
- ❌ Skip signature validation
- ❌ Skip expiration check
- ❌ Reuse refresh tokens (allow one-time use)
- ❌ Store sensitive data in token payload (it's readable!)
- ❌ Use tokens for CSRF protection (use separate tokens if needed)
- ❌ Hardcode token secret in code
- ❌ Accept tokens without Authorization header

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Token expires immediately | time_delta too small | Check ACCESS_TOKEN_EXPIRE_MINUTES = 30 |
| "Invalid signature" | Different SECRET_KEY used | Verify all servers use same .env SECRET_KEY |
| 401 errors randomly | Token refresh not implemented | Add interceptor to auto-refresh on 401 |
| Token in logs | Security audit fail | Never log(token), use log(token[:10]+"...") |
| CORS + 401 error | Both happen together | Debug separately: CORS first, then auth |
| Refresh token not working | Token revoked or expired | Check refresh_token TTL (7 days) |
| User logged out but still accessing API | Tokens not cleared | localStorage.clear() on logout |
| Multiple tabs sync issue | Token in one tab not synced | Use localStorage (shared across tabs) + storage events |

---

## Refresh Token Strategy: One-Time Use vs TTL

### Option 1: One-Time Use (More Secure)

`python
# Backend: Mark refresh token as used
class RefreshTokenBlacklist(Base):
    id: int
    token_jti: str  # JWT ID claim
    revoked_at: datetime
    used_at: datetime

async def refresh_token(self, req: RefreshTokenRequest):
    """Refresh access token (one-time use)."""
    
    # Check if refresh token was already used
    jti = decode_token(req.refresh_token).get("jti")
    used = await session.get(RefreshTokenBlacklist, jti)
    if used:
        # Token reuse detected → potential attack
        raise HTTPException(status_code=401, detail="Token reuse detected")
    
    # Generate new tokens
    new_access = create_token(...)
    new_refresh = create_token(..., type="refresh", jti=uuid())
    
    # Mark old token as used
    blacklist = RefreshTokenBlacklist(token_jti=jti, used_at=now())
    session.add(blacklist)
    await session.commit()
    
    return { access_token: new_access, refresh_token: new_refresh }
`

**Pros**:
- ✅ Detects token reuse (attack indicator)
- ✅ More secure (tokens not valid twice)

**Cons**:
- ❌ Need database lookup on every refresh
- ❌ Requires token revocation table

### Option 2: TTL Only (Simpler)

`python
# Backend: Simple JWT validation (no DB needed)
async def refresh_token(self, req: RefreshTokenRequest):
    """Refresh access token (TTL-based)."""
    
    payload = decode_token(req.refresh_token)
    # If decode succeeds and exp > now, token is valid
    # No DB lookup needed
    
    return {
        access_token: create_token(...),
        refresh_token: create_token(..., expires_delta=7days),
    }
`

**Pros**:
- ✅ Stateless (no DB needed)
- ✅ Fast (no DB lookup)

**Cons**:
- ⚠️ Can't detect token reuse
- ⚠️ Stolen token valid until TTL expires

**Recommendation**: Use TTL for now (simpler), upgrade to one-time-use after initial release.

---

## Checklist: JWT Implementation Status

### Backend ✅ Implemented

- [x] JWT token generation (AccessToken + RefreshToken)
- [x] Token signing with HS256
- [x] Expiration times set (30 min access, 7 days refresh)
- [x] Middleware validates token signature
- [x] Middleware validates expiration
- [x] 401 returned for invalid/expired token
- [x] Claims include: sub, email, tenant, role, exp, iat
- [x] Password hashing with bcrypt (rounds=12)
- [x] Refresh endpoint implemented

### Frontend ⚠️ To Implement

- [ ] Token fetched on login/register
- [ ] Access token stored in localStorage
- [ ] Refresh token stored in localStorage
- [ ] Authorization header included in API calls
- [ ] 401 response triggers token refresh
- [ ] Refresh endpoint called with refresh_token
- [ ] New tokens updated in localStorage
- [ ] Original request retried after refresh
- [ ] Axios interceptors configured
- [ ] Token expiration checked before requests (optional)
- [ ] Tokens cleared on logout
- [ ] Multi-tab sync (storage events)
- [ ] CSP headers prevent XSS token theft

---

## Test Plan

### Test 1: Token Generation

`python
# tests/test_jwt.py

def test_access_token_has_correct_claims():
    \"\"\"Test access token includes required claims.\"\"\"
    service = AuthService(session)
    token = service.create_token({
        "sub": "user-123",
        "email": "test@example.com",
        "tenant": "tenant-123",
        "role": "owner",
    })
    
    payload = service.decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["email"] == "test@example.com"
    assert "exp" in payload
    assert "iat" in payload

def test_token_expires_after_expiration_time():
    \"\"\"Test token validation fails after expiration.\"\"\"
    service = AuthService(session)
    token = service.create_token(
        {"sub": "user-123"},
        expires_delta=timedelta(seconds=-1),  # Already expired
    )
    
    # Should raise HTTPException
    with pytest.raises(HTTPException):
        service.decode_token(token)

def test_refresh_token_has_longer_ttl():
    \"\"\"Test refresh token has 7-day TTL.\"\"\"
    service = AuthService(session)
    access = service.create_token({"sub": "user-123"})
    refresh = service.create_token(
        {"sub": "user-123", "type": "refresh"},
        expires_delta=timedelta(days=7)
    )
    
    access_exp = service.decode_token(access)["exp"]
    refresh_exp = service.decode_token(refresh)["exp"]
    
    assert refresh_exp > access_exp + (6 * 24 * 3600)  # At least 6 days
`

### Test 2: Token Refresh

`python
def test_refresh_token_endpoint():
    \"\"\"Test refresh endpoint returns new tokens.\"\"\"
    client = TestClient(app)
    
    # Login first
    login_response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    refresh_token = login_response.json()["refresh_token"]
    
    # Refresh token
    refresh_response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()
    assert "refresh_token" in refresh_response.json()

def test_expired_refresh_token_fails():
    \"\"\"Test refresh fails with expired token.\"\"\"
    client = TestClient(app)
    
    # Manually create expired refresh token
    expired_token = create_expired_jwt()  #  Helper
    
    response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": expired_token
    })
    
    assert response.status_code == 401
`

---

## Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Access Token | ✅ Implemented | 30-min TTL, all claims present |
| Refresh Token | ✅ Implemented | 7-day TTL |
| Token Storage | ⚠️ Recommend localStorage | Implement in frontend |
| Token Refresh | ✅ Endpoint ready | Frontend interceptor needed |
| CORS | ✅ Configured | Dev: localhost:3000 |
| JWT Secret | ✅ From .env | Not hardcoded |
| Password Hash | ✅ bcrypt | rounds=12 |
| Token Validation | ✅ In middleware | Signature + expiration checked |

---

**Last Updated**: April 15, 2026  
**Version**: 1.0.0 (Phase 3 Kickoff)  
**Review**: After frontend token implementation
