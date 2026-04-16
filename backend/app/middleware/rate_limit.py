"""Rate Limit Middleware — Rate Limiting by Plan.

Implements rate limiting based on tenant plan.
Tracks requests per hour and denies if over limit.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio



# In-memory rate limit tracker (for single-server; use Redis for distributed)
request_counts = defaultdict(list)  # tenant_id -> [timestamp, timestamp, ...]
request_lock = asyncio.Lock()


class RateLimitConfig:
    """Rate limit configuration by plan."""

    LIMITS = {
        "free": 100,  # requests per hour
        "starter": 1000,
        "pro": 10000,
        "enterprise": None,  # Unlimited
    }


async def rate_limit_middleware(request: Request, call_next):
    """Rate limit requests based on tenant plan.

    Args:
        request: FastAPI request
        call_next: Next middleware/endpoint

    Returns:
        Response or 429 if over limit
    """
    # Skip for public and documentation endpoints
    public_paths = [
        "/",
        "/healthz",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
    ]
    
    if request.url.path in public_paths:
        return await call_next(request)

    # Only rate limit API calls
    if not request.url.path.startswith("/api/"):
        return await call_next(request)

    # Allow public auth endpoints (register, login)
    if request.url.path in ["/api/v1/auth/register", "/api/v1/auth/login"]:
        if request.method in ["POST"]:
            return await call_next(request)

    # Get tenant from request state (injected by tenant middleware)
    if not hasattr(request.state, "tenant_id"):
        return await call_next(request)

    tenant_id = str(request.state.tenant_id)

    # Get plan from request state (would come from DB in production)
    plan = getattr(request.state, "plan", "free")
    limit = RateLimitConfig.LIMITS.get(plan, 0)

    # Unlimited for enterprise
    if limit is None:
        return await call_next(request)

    # Check and update request count
    async with request_lock:
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)

        # Clean up old requests
        if tenant_id in request_counts:
            request_counts[tenant_id] = [
                ts for ts in request_counts[tenant_id] if ts > hour_ago
            ]

        # Check limit
        if len(request_counts[tenant_id]) >= limit:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"error": f"Rate limit exceeded: {limit} requests per hour"},
            )

        # Record this request
        request_counts[tenant_id].append(now)

    # Add rate limit headers to response
    response = await call_next(request)
    remaining = limit - len(request_counts[tenant_id])
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
    response.headers["X-RateLimit-Reset"] = str(
        int((hour_ago + timedelta(hours=1)).timestamp())
    )

    return response
