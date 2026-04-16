"""
Dependency Injection — DI para FastAPI
Fornece dependências: session, current_user, current_tenant, require_role
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.security import decode_token
from typing import Optional
from uuid import UUID

security = HTTPBearer()


async def get_current_user(credentials=Depends(security)):
    """
    Obter usuário atual a partir do token JWT
    Valida o token e retorna o user_id
    """
    token = credentials.credentials
    
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sem user_id",
        )
    
    return user_id


async def get_current_tenant(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> UUID:
    """
    Obter tenant_id do usuário atual
    Retorna o primeiro tenant do usuário (ou implementar lógica de seleção)
    """
    from sqlalchemy import select
    from app.models.tenant import TenantMember
    
    # Converter user_id (string) para UUID
    user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
    
    # Buscar member do usuário
    stmt = select(TenantMember).where(
        TenantMember.user_id == user_uuid,
        TenantMember.deletado_em == None
    ).limit(1)
    result = await session.execute(stmt)
    member = result.scalars().first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não tem acesso a nenhum tenant",
        )
    
    return member.tenant_id


async def require_role(
    required_role: str,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    tenant_id: UUID = Depends(get_current_tenant)
) -> dict:
    """
    Validar se o usuário tem um papel específico no tenant
    Papéis: admin, moderator, viewer
    """
    from sqlalchemy import select, and_
    from app.models.tenant import TenantMember
    
    # Converter user_id (string) para UUID
    user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
    
    stmt = select(TenantMember).where(
        and_(
            TenantMember.user_id == user_uuid,
            TenantMember.tenant_id == tenant_id,
            TenantMember.deletado_em == None,
        )
    )
    result = await session.execute(stmt)
    member = result.scalars().first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não pertence a este tenant",
        )
    
    # Validar role (owner >= admin >= moderator >= viewer)
    role_hierarchy = {"owner": 4, "admin": 3, "moderator": 2, "viewer": 1}
    user_level = role_hierarchy.get(member.role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    if user_level < required_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requer papel {required_role}, mas você tem {member.role}",
        )
    
    return {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "role": member.role
    }
