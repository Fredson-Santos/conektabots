# SKILL: Security Multi-Tenant & Encryption

**Purpose**: Guidelines for implementing secure multi-tenancy, encryption, authentication, rate limiting, and RLS.

**Used for**: Implementing JWT auth, encrypting sensitive data, setting up multi-tenant isolation, rate limiting by plan, CORS configuration.

---

## Multi-Tenancy Security Model

### Layers of Isolation

**Layer 1: RLS (Row-Level Security) - Database Level**
```sql
-- Each tenant can only see their own records
CREATE POLICY "tenant_isolation"
    ON public.resource
    FOR SELECT
    USING (tenant_id IN (SELECT public.get_user_tenant_ids()));
```

**Layer 2: Middleware - Application Level**
```python
# Every request includes X-Tenant-ID (resolved from JWT)
@app.middleware("http")
async def add_tenant_id(request: Request, call_next):
    user_id = request.state.user_id
    tenant_id = await get_user_tenant(user_id)
    request.state.tenant_id = tenant_id
    return await call_next(request)
```

**Layer 3: Service Layer - Business Logic**
```python
async def get_resource(tenant_id: UUID, resource_id: UUID):
    # Every query explicitly filters by tenant_id
    resource = await db.query(Resource).filter(
        Resource.tenant_id == tenant_id,
        Resource.id == resource_id
    ).first()
    
    if not resource:
        raise NotFoundError("Resource not in tenant")
    
    return resource
```

### Verification Checklist
- [x] Every service method receives `tenant_id` parameter
- [x] All queries filter by tenant_id (WHERE clause)
- [x] RLS policies enabled on all business tables
- [x] Middleware injects tenant_id from JWT
- [x] API responses filtered by tenant_id

---

## JWT Authentication

### Token Structure
```python
from datetime import timedelta
from jose import JWTError, jwt

class TokenService:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_access_token(
        self,
        user_id: str,
        tenant_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Generate JWT access token."""
        if expires_delta is None:
            expires_delta = timedelta(hours=24)
        
        to_encode = {
            "sub": user_id,  # Subject (user ID)
            "tenant_id": str(tenant_id),
            "iat": datetime.utcnow(),  # Issued at
            "exp": datetime.utcnow() + expires_delta,  # Expiration
            "type": "access"
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> dict:
        """Validate and extract claims from JWT."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError as e:
            raise UnauthorizedError(f"Invalid token: {e}")
```

### Token Payload Example
```json
{
  "sub": "uuid-of-user",
  "tenant_id": "uuid-of-tenant",
  "iat": 1713118261,
  "exp": 1713204661,
  "type": "access"
}
```

### Dependency Injection
```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Extract user from JWT token."""
    try:
        payload = token_service.verify_token(token)
        user_id = UUID(payload["sub"])
        tenant_id = UUID(payload["tenant_id"])
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    
    user = await db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
```

---

## Field-Level Encryption

### Pattern: Encrypt on Insert, Decrypt on Read

```python
from cryptography.fernet import Fernet

class CryptoService:
    def __init__(self, encryption_key: str):
        # Key must be 32 bytes, base64-encoded
        self.cipher = Fernet(encryption_key.encode())
    
    def encrypt(self, plaintext: str) -> bytes:
        """Encrypt string to bytes."""
        return self.cipher.encrypt(plaintext.encode())
    
    def decrypt(self, encrypted: bytes) -> str:
        """Decrypt bytes to string."""
        return self.cipher.decrypt(encrypted).decode()
```

### Usage in Service Layer
```python
class BotService:
    async def create_bot(self, tenant_id: UUID, data: BotCreate) -> Bot:
        # Encrypt sensitive fields
        api_hash_enc = self.crypto_service.encrypt(data.api_hash)
        session_string_enc = self.crypto_service.encrypt(data.session_string)
        
        # Create model with encrypted data
        bot = Bot(
            tenant_id=tenant_id,
            nome=data.nome,
            api_hash_enc=api_hash_enc,
            session_string_enc=session_string_enc
        )
        
        await db.add(bot)
        await db.commit()
        return bot
    
    async def get_bot(self, tenant_id: UUID, bot_id: UUID) -> Bot:
        bot = await db.query(Bot).filter(
            Bot.tenant_id == tenant_id,
            Bot.id == bot_id
        ).first()
        
        # Decrypt on read (if needed for worker)
        if bot and bot.session_string_enc:
            bot.session_string = self.crypto_service.decrypt(bot.session_string_enc)
        
        return bot
```

### ⚠️ Security Rules
1. **Never expose encrypted data in API response** — decrypt only in worker
2. **Key rotation** — older messages may need separate decryption with old key
3. **Key storage** — use environment variable or secret vault (never commit!)

---

## Rate Limiting by Plan

### Schema
```
Free tier: 50 msgs/hour
Starter: 500 msgs/hour
Pro: Unlimited
```

### Implementation
```python
class QuotaService:
    async def check_rate_limit(self, tenant_id: UUID) -> bool:
        """Check if tenant can send message this hour."""
        tenant = await get_tenant(tenant_id)
        limit = get_plan_limit(tenant.plano)  # 50, 500, unlimited
        
        # Get usage in current hour
        usage = await db.query(UsoMensal).filter(
            UsoMensal.tenant_id == tenant_id,
            UsoMensal.mes_ref == date.today()
        ).first()
        
        if usage and usage.msgs_enviadas >= limit:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        
        return True
```

### Sliding Window Alternative
```python
async def check_rate_limit_sliding(self, tenant_id: UUID) -> bool:
    """Sliding window: check messages sent in last 60 minutes."""
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    
    count = await db.query(LogExecucao).filter(
        LogExecucao.tenant_id == tenant_id,
        LogExecucao.criado_em >= one_hour_ago,
        LogExecucao.status == "sucesso"
    ).count()
    
    tenant = await get_tenant(tenant_id)
    limit = get_plan_limit(tenant.plano)
    
    return count < limit
```

---

## Password Security

### Best Practice: bcrypt via passlib
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with bcrypt."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify plaintext vs hashed."""
        return pwd_context.verify(password, hashed)

# Usage
hashed = PasswordService.hash_password("user_password")
is_valid = PasswordService.verify_password("user_password", hashed)
```

---

## CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://conektabots.com",
        "https://www.conektabots.com",
        "http://localhost:3000",  # Dev frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-Total-Count"],
)
```

---

## Security Headers

```python
from fastapi.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

---

## Common Security Mistakes ⚠️

❌ **Mistake 1**: No multi-tenant filtering
```python
# BAD
async def get_all_resources():
    return await db.query(Resource).all()  # Anyone can fetch all tenants' data!

# GOOD
async def get_resources(tenant_id: UUID = Depends(get_current_tenant)):
    return await db.query(Resource).filter(Resource.tenant_id == tenant_id)
```

❌ **Mistake 2**: Exposing encrypted data in API
```python
# BAD
class BotResponse(BaseModel):
    session_string_enc: bytes  # Exposes encrypted data

# GOOD
class BotResponse(BaseModel):
    # Omit encrypted fields in API response
    id: UUID
    nome: str
    ativo: bool
```

❌ **Mistake 3**: Hard-coded encryption key
```python
# BAD
ENCRYPTION_KEY = "my-hardcoded-key"

# GOOD
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
assert ENCRYPTION_KEY, "ENCRYPTION_KEY not set"
```

❌ **Mistake 4**: No rate limiting
```python
# BAD
@router.post("/send-message")
async def send_message(data: MessageCreate):
    # No limit — anyone can spam!

# GOOD
@router.post("/send-message")
async def send_message(
    data: MessageCreate,
    tenant_id: UUID = Depends(get_current_tenant)
):
    await quota_service.check_rate_limit(tenant_id)
    # ... send message
```

---

## Audit & Compliance

### Logging Sensitive Actions
```python
class AuditService:
    async def log_action(
        self,
        tenant_id: UUID,
        user_id: UUID,
        action: str,
        resource_type: str,
        resource_id: UUID,
        changes: dict
    ):
        """Log sensitive actions for audit trail."""
        audit_log = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,  # CREATE, UPDATE, DELETE
            resource_type=resource_type,
            resource_id=resource_id,
            changes=changes,  # What changed (sanitized)
            timestamp=datetime.utcnow()
        )
        
        await db.add(audit_log)
        await db.commit()
```

---

## Resources
- [OWASP Top 10](https://owasp.org/Top10/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Cryptography.io](https://cryptography.io/)

---

**Last Updated**: April 15, 2026  
**Status**: Active
