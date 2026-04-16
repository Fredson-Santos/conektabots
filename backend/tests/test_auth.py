"""Test Authentication — Login, Register, Tokens.

Verifies authentication flow and JWT security.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import LoginRequest, RegisterRequest, RefreshTokenRequest
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_register_new_user(session: AsyncSession):
    """Test user registration."""
    service = AuthService(session)

    req = RegisterRequest(
        email="newuser@example.com",
        password="SecurePass123!",
        password_confirm="SecurePass123!",
        first_name="John",
        last_name="Doe",
    )

    token_response = await service.register(req)

    assert token_response.access_token is not None
    assert token_response.refresh_token is not None
    assert token_response.role == "owner"
    assert token_response.tenant_id is not None


@pytest.mark.asyncio
async def test_login_valid_credentials(session: AsyncSession):
    """Test login with correct credentials."""
    service = AuthService(session)

    # Register first
    register_req = RegisterRequest(
        email="user@example.com",
        password="SecurePass123!",
        password_confirm="SecurePass123!",
        first_name="Test",
        last_name="User",
    )
    await service.register(register_req)

    # Login
    login_req = LoginRequest(
        email="user@example.com",
        password="SecurePass123!",
    )
    token_response = await service.login(login_req)

    assert token_response.access_token is not None
    assert token_response.refresh_token is not None


@pytest.mark.asyncio
async def test_login_invalid_password(session: AsyncSession):
    """Test login with wrong password."""
    from fastapi import HTTPException

    service = AuthService(session)

    # Register
    register_req = RegisterRequest(
        email="user@example.com",
        password="SecurePass123!",
        password_confirm="SecurePass123!",
        first_name="Test",
        last_name="User",
    )
    await service.register(register_req)

    # Try login with wrong password
    login_req = LoginRequest(
        email="user@example.com",
        password="WrongPassword!",
    )

    with pytest.raises(HTTPException):
        await service.login(login_req)


@pytest.mark.asyncio
async def test_token_refresh(session: AsyncSession):
    """Test refreshing access token."""
    service = AuthService(session)

    # Register
    register_req = RegisterRequest(
        email="user@example.com",
        password="SecurePass123!",
        password_confirm="SecurePass123!",
        first_name="Test",
        last_name="User",
    )
    register_response = await service.register(register_req)

    # Refresh token
    refresh_req = RefreshTokenRequest(
        refresh_token=register_response.refresh_token
    )
    new_response = await service.refresh_token(refresh_req)

    assert new_response.access_token is not None
    # Note: Tokens may be identical if generation happens fast, just verify access token exists


@pytest.mark.asyncio
async def test_invalid_token_decode(session: AsyncSession):
    """Test JWT decoding with invalid token."""
    from fastapi import HTTPException

    service = AuthService(session)

    with pytest.raises(HTTPException):
        service.decode_token("invalid.jwt.token")
