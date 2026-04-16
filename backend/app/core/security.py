"""
Segurança — JWT, Criptografia e Autenticação
Funções para validar tokens JWT e criptografar dados sensíveis
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

# Contexto de hash (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Chaves
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    """Hash uma senha com bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar se a senha corresponde ao hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Criar um JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Criar um JWT refresh token (válido por mais tempo)"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decodificar e validar um JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def encrypt_sensitive(data: str, key: Optional[str] = None) -> str:
    """
    Criptografar dados sensíveis (será usado para campos _enc no banco)
    Nota: Implementação simplificada — usar pgcrypto do PostgreSQL para armazenar
    """
    # Aqui seria implementada a criptografia real (ex: Fernet)
    # Por enquanto, retorna o dado como está
    # O banco fará a criptografia real via pgp_sym_encrypt do PostgreSQL
    return data


def decrypt_sensitive(data: str, key: Optional[str] = None) -> str:
    """
    Descriptografar dados sensíveis
    Nota: O PostgreSQL fará a descriptografia via pgp_sym_decrypt
    """
    return data
