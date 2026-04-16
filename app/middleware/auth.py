"""Auth Middleware — JWT Token Validation.

Extracts and validates JWT tokens from request headers.
Injects user and tenant information into request state.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.security import decode_token


async def auth_middleware(request: Request, call_next):
    """Validate JWT token and inject user context.

    Args:
        request: FastAPI request
        call_next: Next middleware/endpoint

    Returns:
        Response from next handler
    """
    # Skip auth for public endpoints and documentation
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

    # Extract token if present
    auth_header = request.headers.get("Authorization", "")
    
    # If no token, let request pass - endpoint dependencies will handle auth
    if not auth_header.startswith("Bearer "):
        return await call_next(request)

    token = auth_header.split(" ")[1]

    # Validate token
    try:
        payload = decode_token(token)
    except HTTPException:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid token"},
        )

    # Inject into request state
    request.state.token = token
    request.state.user_id = payload.get("sub")
    request.state.tenant_id = payload.get("tenant")
    request.state.role = payload.get("role")

    response = await call_next(request)
    return response
