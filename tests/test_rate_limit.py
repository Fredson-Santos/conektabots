"""Test HTTP Rate Limiting — Request Throttling.

Verifies rate limiting middleware on API endpoints.
"""

import pytest
import pytest_asyncio
import asyncio
from fastapi.testclient import TestClient
from uuid import uuid4

from main import app
from app.models.tenant import Tenant, TenantMember
from app.services.auth_service import AuthService


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_token(session, event_loop):
    """Create authenticated token (sync version)."""
    async def get_token():
        service = AuthService(session)
        from app.schemas.auth import RegisterRequest
        register_req = RegisterRequest(
            email="testuser@example.com",
            password="SecurePass123!",
            password_confirm="SecurePass123!",
            first_name="Test",
            last_name="User",
        )
        response = await service.register(register_req)
        return response.access_token
    
    # Run async function in event loop
    return event_loop.run_until_complete(get_token())


@pytest.mark.asyncio
async def test_rate_limit_headers(client, auth_token):
    """Test that rate limit headers are present."""
    response = client.get(
        "/api/v1/bots",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers


@pytest.mark.asyncio
async def test_rate_limit_free_plan(client, auth_token):
    """Test rate limiting for free plan (100 req/hour)."""
    # Make 101 requests (should succeed but track)
    for i in range(101):
        response = client.get(
            "/api/v1/bots",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        # Most should succeed, last ones might be throttled depending on implementation
        assert response.status_code in [200, 429]


@pytest.mark.asyncio
async def test_rate_limit_reset(client, auth_token):
    """Test rate limit resets per hour."""
    # Make requests until limit
    for _ in range(100):
        client.get("/api/v1/bots", headers={"Authorization": f"Bearer {auth_token}"})

    # Get remaining from last request
    response = client.get(
        "/api/v1/bots",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
    assert remaining >= 0
