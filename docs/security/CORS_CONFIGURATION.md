# ⚙️ CORS Configuration Guide

## Overview

CORS (Cross-Origin Resource Sharing) determines which frontend domains can access your ConektaBots API.

## Current Configuration

**Backend File**: [main.py#L31-L38](../../main.py#L31-L38)

`python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
`

**Settings File**: [app/core/config.py#L51-L52](../../app/core/config.py#L51-L52)

`python
CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
`

---

## Development Setup

### 1. Backend Configuration (.env.development)

`ash
# .env.development

# Development CORS origins
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000","http://127.0.0.1:3000"]

# Allow development tools
DEBUG=true
`

**Apply**:
`ash
# Create .env.development from template
cp .env.example .env.development

# Edit .env file
echo 'CORS_ORIGINS=["http://localhost:3000"]' >> .env
`

### 2. Frontend Configuration (.env.development.local)

**React/Vue/Next.js** — Create .env.development.local:

`ash
# .env.development.local

# API endpoint
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development

# Feature flags (optional)
REACT_APP_DEBUG=true
`

**Important**: Add to .gitignore:
`ash
echo ".env.development.local" >> .gitignore
echo ".env.production.local" >> .gitignore
`

### 3. Test CORS Setup

`ash
# Terminal 1: Start backend
cd /path/to/conektabots
python main.py

# Terminal 2: Start frontend
cd /path/to/conektabots-frontend
npm start  # Starts on http://localhost:3000
`

**Test in browser console** (http://localhost:3000):

`javascript
const testCORS = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/health', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    console.log('✅ CORS OK:', response.status);
  } catch (error) {
    console.error('❌ CORS Error:', error.message);
  }
};

testCORS();
`

**Expected output**:
`
✅ CORS OK: 200
`

---

## Production Setup

### 1. Hardened CORS Configuration

**Backend .env.production**:

`ash
# Production CORS whitelist (STRICT)
CORS_ORIGINS=["https://app.conektabots.com","https://conektabots.com","https://www.conektabots.com"]

# Security settings
DEBUG=false
SECURE_COOKIES=true
ALLOW_HTTP=false
`

**Why so strict?**
- Only whitelisted production domains
- No wildcards (* not allowed)
- No localhost or development URLs
- Reduces attack surface

### 2. Frontend Configuration (.env.production)

`ash
# .env.production

# Production API endpoint (HTTPS!)
REACT_APP_API_URL=https://api.conektabots.com
REACT_APP_ENVIRONMENT=production

# Disable debugging
REACT_APP_DEBUG=false
`

### 3. Backend FastAPI Code (Optional Override)

If you need to configure CORS from code instead of .env:

`python
# app/main.py

from fastapi.middleware.cors import CORSMiddleware
import os

# Get CORS origins from environment
cors_origins_str = os.getenv("CORS_ORIGINS", '["http://localhost:3000"]')
import json
cors_origins = json.loads(cors_origins_str)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # ✅ Whitelist only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],  # ✅ Explicit methods
    allow_headers=["Authorization", "Content-Type"],  # ✅ Only needed headers
    max_age=3600,  # ✅ Preflight cache (1 hour)
)
`

### 4. HTTP to HTTPS Redirect

Before deploying, ensure production backend redirects HTTP → HTTPS:

`python
# app/middleware/https.py (add this if needed)

from fastapi import Request

@app.middleware("http")
async def redirect_https(request: Request, call_next):
    """Redirect HTTP to HTTPS in production."""
    if os.getenv("ENVIRONMENT") == "production":
        if request.url.scheme == "http":
            url = request.url.replace(scheme="https")
            return RedirectResponse(url=url, status_code=301)
    
    return await call_next(request)
`

---

## Common CORS Issues & Solutions

### Issue 1: "CORS Policy: No Access-Control-Allow-Origin"

**Cause**: Frontend origin not whitelisted

**Debug**:
`javascript
// Browser console shows:
// Access to XMLHttpRequest at 'http://localhost:8000/api/v1/bots' 
// from origin 'http://localhost:3000' has been blocked by CORS policy

// Solution: Add http://localhost:3000 to CORS_ORIGINS
`

**Fix**:
`ash
# .env
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
`

**Restart backend**:
`ash
# Kill running process
Ctrl+C

# Start again
python main.py
`

### Issue 2: "CORS Policy: Method Not Allowed"

**Cause**: HTTP method (POST, PATCH, DELETE) not whitelisted

**Debug**:
`javascript
// Browser console shows:
// CORS policy: Request method POST not allowed by Access-Control-Allow-Methods

// Solution: Add POST to allow_methods
`

**Fix**:
`python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],  # ← Add POST
)
`

### Issue 3: "CORS Policy: Custom Header Not Allowed"

**Cause**: Custom header (e.g., Authorization) not whitelisted

**Debug**:
`javascript
// Browser console shows:
// CORS policy: Request header X-Custom-Header not allowed by Access-Control-Allow-Headers

// Solution: Add header to allow_headers
`

**Fix**:
`python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_headers=["Authorization", "Content-Type", "X-Custom-Header"],
)
`

### Issue 4: "Credentials Included But CORS Does Not Allow"

**Cause**: Credentials (cookies) included but allow_credentials=False

**Debug**:
`javascript
// Browser console shows:
// CORS policy: when responding to a credentials mode request,
// Access-Control-Allow-Credentials must be true

// Solution: Set allow_credentials=True
`

**Fix**:
`python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,  # ← Must be true if sending cookies
)
`

---

## Frontend Integration Patterns

### Pattern 1: Fetch API with CORS

`javascript
// ✅ CORRECT

const makeRequest = async (endpoint, options = {}) => {
  const url = \\\\;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': \Bearer \\,
      ...options.headers,
    },
  });

  // Handle CORS errors
  if (response.status === 0) {
    console.error('CORS Error - check backend CORS_ORIGINS');
    throw new Error('CORS policy violation');
  }

  return response;
};
`

### Pattern 2: Axios Interceptor

`javascript
// ✅ BEST: Axios auto-configures CORS requests

import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 10000,
  withCredentials: true,  // ← Send cookies if using HttpOnly
});

// Requests automatically include Authorization header
api.defaults.headers.common['Authorization'] = \Bearer \\;

export default api;
`

### Pattern 3: Error Handling

`javascript
// ✅ CORRECT: Handle CORS and auth errors

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired - refresh
      console.warn('Unauthorized - refreshing token');
      return refreshToken().then(() => api.request(error.config));
    }

    if (error.message === 'Network Error' && !error.response) {
      // Could be CORS issue
      console.error('Network Error - check CORS configuration');
    }

    return Promise.reject(error);
  }
);
`

---

## Deployment Checklist

### ✅ Before Deploying to Staging

- [ ] Backend .env.staging created with CORS_ORIGINS
- [ ] Frontend .env.production points to staging backend
- [ ] CORS_ORIGINS includes staging domain
- [ ] Test API request from staging frontend
- [ ] No console errors about CORS
- [ ] Token refresh works
- [ ] Multi-tenant isolation verified

### ✅ Before Deploying to Production

- [ ] Backend .env.production created
- [ ] Production domain in CORS_ORIGINS
- [ ] HTTPS enforced (no http://...)
- [ ] Frontend .env.production updated
- [ ] CORS test passed in production URL
- [ ] SSL certificate valid for domain
- [ ] HSTS headers configured
- [ ] Rate limiting active
- [ ] Logging doesn't expose tokens

---

## Troubleshooting Script

Save as scripts/test-cors.sh:

`ash
#!/bin/bash
# Test CORS configuration

BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

echo "🔍 Testing CORS Configuration..."
echo ""

# Test 1: Backend is running
echo "1. Is backend running?"
curl -s -o /dev/null -w "%{http_code}" /health
echo ""

# Test 2: CORS headers present
echo ""
echo "2. CORS Headers:"
curl -s -I -X OPTIONS /api/v1/health \
  -H "Origin: " \
  | grep "Access-Control"

# Test 3: API accessible
echo ""
echo "3. Can frontend access API?"
curl -s -X GET /api/v1/health | jq '.'

echo ""
echo "✅ CORS test complete"
`

**Run**:
`ash
chmod +x scripts/test-cors.sh
./scripts/test-cors.sh
`

---

## CORS Matrix

| Scenario | Development | Production |
|----------|-------------|-----------|
| Frontend URL | http://localhost:3000 | https://app.conektabots.com |
| Backend URL | http://localhost:8000 | https://api.conektabots.com |
| CORS Origins | ["http://localhost:3000"] | ["https://app.conektabots.com"] |
| allow_methods | ["*"] | ["GET","POST","PATCH","DELETE","OPTIONS"] |
| allow_headers | ["*"] | ["Authorization","Content-Type"] |
| allow_credentials | true | true |
| DEBUG | true | false |
| HTTPS | false | true |

---

## Summary

✅ **Your CORS setup is ready when**:
- Frontend domain is in CORS_ORIGINS
- HTTP methods are whitelisted
- Authorization header is allowed
- No CORS errors in browser console
- API requests succeeding from frontend
- csrf token handling (if using cookies)

❌ **Common mistakes to avoid**:
- Using allow_origins=["*"] in production
- Allowing all methods/headers without filtering
- Forgetting to add new frontend domain to CORS_ORIGINS
- Mixing HTTP and HTTPS URLs
- Not restarting backend after .env changes

---

**Last Updated**: April 15, 2026  
**Version**: 1.0.0 (Phase 3)  
**Template**: CORS Configuration Specification
