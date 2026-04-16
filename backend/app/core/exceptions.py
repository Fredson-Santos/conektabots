"""
Exceções customizadas — Exceções da aplicação
Definição de exceções específicas para tratamento de erros
"""

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Exceção base para todas as exceções da API"""
    
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "Erro interno do servidor",
        headers: dict = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class UnauthorizedException(BaseAPIException):
    """401 - Não autenticado"""
    def __init__(self, detail: str = "Não autenticado"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


class ForbiddenException(BaseAPIException):
    """403 - Não autorizado"""
    def __init__(self, detail: str = "Acesso negado"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundException(BaseAPIException):
    """404 - Recurso não encontrado"""
    def __init__(self, detail: str = "Recurso não encontrado"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ConflictException(BaseAPIException):
    """409 - Conflito (ex: recurso já existe)"""
    def __init__(self, detail: str = "Conflito no servidor"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class ValidationException(BaseAPIException):
    """422 - Erro de validação"""
    def __init__(self, detail: str = "Erro de validação"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class RateLimitException(BaseAPIException):
    """429 - Limite de taxa excedido"""
    def __init__(self, detail: str = "Você excedeu o limite de requisições"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
        )


class TenantLimitException(BaseAPIException):
    """Limite do tenant excedido (ex: máximo de bots)"""
    def __init__(self, detail: str = "Limite do tenant excedido"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class InvalidCredentialsException(UnauthorizedException):
    """Credenciais inválidas (ex: senha errada)"""
    def __init__(self):
        super().__init__(detail="Email ou senha inválidos")


class UserAlreadyExistsException(ConflictException):
    """Usuário já existe"""
    def __init__(self):
        super().__init__(detail="Este email já está registrado")


class BotNotFoundError(NotFoundException):
    """Bot não encontrado"""
    def __init__(self):
        super().__init__(detail="Bot não encontrado")


class RegracartNotFoundError(NotFoundException):
    """Regra não encontrada"""
    def __init__(self):
        super().__init__(detail="Regra não encontrada")


class AgendamentoNotFoundError(NotFoundException):
    """Agendamento não encontrado"""
    def __init__(self):
        super().__init__(detail="Agendamento não encontrado")


# Handler para exception da aplicação
exception_handlers = {
    # Será registrado em main.py
}
