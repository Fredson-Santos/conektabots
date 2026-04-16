"""Auth Service — Authentication & Authorization.

Handles user registration, login, token refresh, and JWT operations.
Uses bcrypt for password hashing and JWT token generation.
"""

from datetime import datetime, timedelta
from uuid import UUID
from typing import Optional
import os
import bcrypt
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from fastapi import HTTPException, status

from app.models.user import User
from app.models.tenant import Tenant, TenantMember
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RegisterRequest,
    RefreshTokenRequest,
)


class AuthService:
    """Authentication and authorization service."""

    def __init__(self, session: AsyncSession):
        """Initialize auth service.

        Args:
            session: Database session
        """
        self.session = session
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        # Bcrypt has a 72-byte limit - truncate if needed
        password_truncated = password[:72]
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_truncated.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """Verify password against hash.

        Args:
            plain: Plain text password
            hashed: Hashed password

        Returns:
            True if password matches
        """
        # Bcrypt has a 72-byte limit - truncate if needed
        plain_truncated = plain[:72]
        try:
            return bcrypt.checkpw(plain_truncated.encode('utf-8'), hashed.encode('utf-8'))
        except (ValueError, TypeError):
            return False

    def create_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT token.

        Args:
            data: Token claims
            expires_delta: Expiration time delta

        Returns:
            JWT token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=self.access_token_expire_minutes)
        )
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> dict:
        """Decode and verify JWT token.

        Args:
            token: JWT token string

        Returns:
            Token claims

        Raises:
            HTTPException if token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )

    async def register(self, req: RegisterRequest) -> TokenResponse:
        """Register new user and create tenant.

        Args:
            req: Registration request

        Returns:
            Token response

        Raises:
            HTTPException if user already exists
        """
        # Validate passwords match
        if req.password != req.password_confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senhas não conferem",
            )
        
        # Check if user exists
        stmt = select(User).where(User.email == req.email)
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email já registrado",
            )

        # Create user
        user = User(
            email=req.email,
            senha_hash=self.hash_password(req.password),
            nome=f"{req.first_name} {req.last_name}",
            ativo=True,
        )
        self.session.add(user)
        await self.session.flush()

        # Create tenant (using email domain as name)
        tenant = Tenant(
            nome=req.first_name.title() or "Tenant",
            slug=req.email.split("@")[0].lower(),
            plano="free",
            ativo=True,
        )
        self.session.add(tenant)
        await self.session.flush()

        # Create tenant member (owner)
        member = TenantMember(
            tenant_id=tenant.id,
            user_id=user.id,
            role="owner",
        )
        self.session.add(member)
        await self.session.commit()

        # Create tokens
        access_token = self.create_token(
            {
                "sub": str(user.id),
                "email": user.email,
                "tenant": str(tenant.id),
                "role": member.role,
            }
        )
        refresh_token = self.create_token(
            {"sub": str(user.id), "type": "refresh"},
            expires_delta=timedelta(days=self.refresh_token_expire_days),
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            tenant_id=tenant.id,
            role=member.role,
        )

    async def login(self, req: LoginRequest) -> TokenResponse:
        """Login user with email and password.

        Args:
            req: Login request

        Returns:
            Token response

        Raises:
            HTTPException if credentials invalid
        """
        # Find user
        stmt = select(User).where(User.email == req.email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not self.verify_password(req.password, user.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
            )

        if not user.is_active():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário desativado",
            )

        # Get first tenant member (user pode estar em múltiplos tenants)
        stmt = select(TenantMember).where(
            and_(
                TenantMember.user_id == user.id,
                TenantMember.deletado_em == None,
            )
        )
        result = await self.session.execute(stmt)
        member = result.scalar_one_or_none()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário não tem acesso a nenhum tenant",
            )

        # Create tokens
        access_token = self.create_token(
            {
                "sub": str(user.id),
                "email": user.email,
                "tenant": str(member.tenant_id),
                "role": member.role,
            }
        )
        refresh_token = self.create_token(
            {"sub": str(user.id), "type": "refresh"},
            expires_delta=timedelta(days=self.refresh_token_expire_days),
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            tenant_id=member.tenant_id,
            role=member.role,
        )

    async def refresh_token(self, req: RefreshTokenRequest) -> TokenResponse:
        """Refresh access token using refresh token.

        Args:
            req: Refresh token request

        Returns:
            New token response

        Raises:
            HTTPException if refresh token invalid
        """
        payload = self.decode_token(req.refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )

        user_id = UUID(payload.get("sub"))

        # Find user
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.is_active():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
            )

        # Get first tenant member
        stmt = select(TenantMember).where(
            and_(
                TenantMember.user_id == user_id,
                TenantMember.deletado_em == None,
            )
        )
        result = await self.session.execute(stmt)
        member = result.scalar_one_or_none()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não tem acesso a nenhum tenant",
            )

        # Create new access token
        access_token = self.create_token(
            {
                "sub": str(user.id),
                "email": user.email,
                "tenant": str(member.tenant_id),
                "role": member.role,
            }
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=req.refresh_token,
            user_id=user.id,
            tenant_id=member.tenant_id,
            role=member.role,
        )

    async def get_current_user(
        self, token: str
    ) -> tuple[User, TenantMember, Tenant]:
        """Get current user from token.

        Args:
            token: JWT token

        Returns:
            Tuple of (user, member, tenant)

        Raises:
            HTTPException if token invalid or user not found
        """
        payload = self.decode_token(token)

        user_id = UUID(payload.get("sub"))
        tenant_id = UUID(payload.get("tenant"))

        # Fetch user
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        # Fetch tenant member
        stmt = select(TenantMember).where(
            and_(
                TenantMember.user_id == user_id,
                TenantMember.tenant_id == tenant_id,
                TenantMember.deletado_em == None,
            )
        )
        result = await self.session.execute(stmt)
        member = result.scalar_one_or_none()

        # Fetch tenant
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await self.session.execute(stmt)
        tenant = result.scalar_one_or_none()

        if not user or not member or not tenant:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário ou tenant não encontrado",
            )

        return user, member, tenant
