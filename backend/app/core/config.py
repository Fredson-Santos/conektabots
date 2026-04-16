"""
Configurações da aplicação — Pydantic Settings
Carrega variáveis de ambiente e fornece configuração centralizada
"""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Configurações globais da aplicação"""
    
    # Sistema
    APP_NAME: str = "ConektaBots SaaS"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    TZ: Optional[str] = "America/Sao_Paulo"
    
    # Servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WEB_PORT: int = 8005
    RELOAD: bool = True
    
    # Banco de dados
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost/conektabots",
        description="URL de conexão ao PostgreSQL (Supabase)"
    )
    
    # Supabase (alternativa para usar bibliotecas Supabase)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # JWT
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Chave secreta para JWT"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Criptografia
    ENCRYPTION_KEY: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD_SECONDS: int = 60
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


# Instância global de settings
settings = Settings()
