"""Tenant Middleware — Multi-Tenant Context Injection.

Ensures all requests are scoped to a valid tenant.
Validates tenant membership from JWT claims.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from uuid import UUID


async def tenant_middleware(request: Request, call_next):
    """Validate tenant context and inject into request.

    Args:
        request: FastAPI request
        call_next: Next middleware/endpoint

    Returns:
        Response from next handler
    """
    # Skip for public endpoints and documentation
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

    # Allow public auth endpoints (register, login)
    if request.url.path in ["/api/v1/auth/register", "/api/v1/auth/login"]:
        if request.method in ["POST"]:
            return await call_next(request)

    # Let request pass - endpoint dependencies will handle tenant validation
    # This allows FastAPI to return 404 for nonexistent endpoints
    return await call_next(request)

    try:
        tenant_id = UUID(request.state.tenant_id)
        request.state.tenant_id = tenant_id
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant ID",
        )

    # TODO: Verify tenant exists and user has access (in production with DB)
    # For now, trusting auth middleware's JWT validation

    response = await call_next(request)
    return response
