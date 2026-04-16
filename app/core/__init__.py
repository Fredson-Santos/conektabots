"""Core package — configurações, banco de dados, segurança"""

from app.core.config import settings
from app.core.database import engine, async_session_maker, get_session, init_db, close_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.deps import get_current_user, get_current_tenant, require_role
from app.core.exceptions import (
    BaseAPIException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
    ValidationException,
)

__all__ = [
    "settings",
    "engine",
    "async_session_maker",
    "get_session",
    "init_db",
    "close_db",
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "get_current_user",
    "get_current_tenant",
    "require_role",
    "BaseAPIException",
    "UnauthorizedException",
    "ForbiddenException",
    "NotFoundException",
    "ConflictException",
    "ValidationException",
]

