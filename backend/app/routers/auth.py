"""Auth Router — Authentication Endpoints.

POST /api/v1/auth/login — Login with email/password
POST /api/v1/auth/register — Register new user
POST /api/v1/auth/refresh — Refresh access token
GET /api/v1/auth/me — Get current user profile
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.common import SuccessResponse
from app.services.auth_service import AuthService


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    req: RegisterRequest,
    session: AsyncSession = Depends(get_session),
):
    """Register new user and create tenant.

    Args:
        req: Registration request
        session: Database session

    Returns:
        Token response with access and refresh tokens
    """
    service = AuthService(session)
    return await service.register(req)


@router.post("/login", response_model=TokenResponse)
async def login(
    req: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    """Login with email and password.

    Args:
        req: Login request
        session: Database session

    Returns:
        Token response with access and refresh tokens
    """
    service = AuthService(session)
    return await service.login(req)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    req: RefreshTokenRequest,
    session: AsyncSession = Depends(get_session),
):
    """Refresh access token using refresh token.

    Args:
        req: Refresh request with refresh token
        session: Database session

    Returns:
        Token response with new access token
    """
    service = AuthService(session)
    return await service.refresh_token(req)


@router.get("/me", response_model=UserResponse)
async def get_current_profile(
    current_user: tuple = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get current authenticated user profile.

    Args:
        current_user: Injected current user from JWT
        session: Database session

    Returns:
        User profile response
    """
    member, tenant = current_user

    return UserResponse(
        id=member.id,
        email=member.email,
        nome=member.email.split("@")[0],  # TODO: Store full_name in DB
        role=member.role,
        tenant_id=tenant.id,
        tenant_name=tenant.nome,
        ativo=member.ativo,
        criado_em=member.criado_em,
        atualizado_em=member.atualizado_em,
    )
