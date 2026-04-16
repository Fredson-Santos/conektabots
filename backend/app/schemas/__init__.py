"""
Schemas — Pydantic Request/Response Models

Organização:
    common.py — DTOs reutilizáveis (pagination, responses, etc)
    auth.py — Login, tokens, usuários
    tenant.py — Tenants e membros (RBAC)
    bot.py — Contas Telegram
    marketplace.py — Integrações
    regra.py — Regras de encaminhamento
    agendamento.py — Agendamentos
    log.py — Logs de execução e auditoria
    uso.py — Uso mensal e rate limiting

Padrão:
    - Todos herdam de BaseModel (Pydantic v2)
    - Responses usam from_attributes=True (ORM=True)
    - Nunca retornam campos sensíveis (_enc)
    - Type hints explícitos em todos os campos
"""

# ═══════════════════════════════════════════════════════════════
# COMMON
# ═══════════════════════════════════════════════════════════════
from .common import (
    SuccessResponse,
    ErrorResponse,
    PaginationParams,
    PaginatedResponse,
    BaseResponse,
    BaseAudit,
    TenantInfo,
    StatusUpdate,
    SoftDeleteResponse,
    BulkDeleteRequest,
    BulkDeleteResponse,
    BulkUpdateRequest,
    BulkUpdateResponse,
    FilterParams,
    ListQueryParams,
)

# ═══════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════
from .auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    UserResponse,
    UserUpdateRequest,
    ChangePasswordRequest,
    PermissionCheck,
    RoleInfo,
    APIKeyCreate,
    APIKeyResponse,
    APIKeyListResponse,
)

# ═══════════════════════════════════════════════════════════════
# TENANT
# ═══════════════════════════════════════════════════════════════
from .tenant import (
    TenantCreate,
    TenantUpdate,
    TenantUpgradePlan,
    TenantResponse,
    TenantLimitsResponse,
    TenantMemberAdd,
    TenantMemberUpdate,
    TenantMemberResponse,
    TenantMemberListResponse,
    TenantSettingsResponse,
    TenantNotificationSettings,
    TenantBillingInfo,
)

# ═══════════════════════════════════════════════════════════════
# BOT
# ═══════════════════════════════════════════════════════════════
from .bot import (
    BotCreate,
    BotUpdate,
    BotResponse,
    BotCredentialUpdateUser,
    BotCredentialUpdateBot,
    BotCredentialClear,
    BotHealthCheck,
    BotTestConnection,
    BotStats,
    BotListItem,
)

# ═══════════════════════════════════════════════════════════════
# MARKETPLACE
# ═══════════════════════════════════════════════════════════════
from .marketplace import (
    MarketplaceIntegracaoCreate,
    MarketplaceIntegracaoUpdate,
    MarketplaceIntegracaoResponse,
    ShopeeCredentials,
    MercadoLivreCredentials,
    AmazonCredentials,
    AliExpressCredentials,
    MarketplaceCredentialUpdate,
    MarketplaceCredentialClear,
    MarketplaceTestConnection,
    MarketplaceHealthCheck,
    MarketplaceStats,
    MarketplaceProduct,
    MarketplaceCategorySync,
    MarketplaceCategorySyncResponse,
)

# ═══════════════════════════════════════════════════════════════
# REGRA
# ═══════════════════════════════════════════════════════════════
from .regra import (
    RegraCreate,
    RegraUpdate,
    RegraResponse,
    RegraOrigemCreate,
    RegraOrigemResponse,
    RegraDestinoCreate,
    RegraDestinoResponse,
    RegraFiltroCreate,
    RegraFiltroResponse,
    RegraCondicaoCreate,
    RegraCondicaoResponse,
    RegraFullResponse,
    RegraStats,
    RegraTestExecution,
    RegraTestExecutionResponse,
    RegraBulkActivate,
    RegraBulkDeactivate,
    RegraBulkOperationResponse,
)

# ═══════════════════════════════════════════════════════════════
# AGENDAMENTO
# ═══════════════════════════════════════════════════════════════
from .agendamento import (
    AgendamentoCreate,
    AgendamentoUpdate,
    AgendamentoResponse,
    AgendamentoOrigemCreate,
    AgendamentoOrigemResponse,
    AgendamentoDestinoCreate,
    AgendamentoDestinoResponse,
    AgendamentoHorarioCreate,
    AgendamentoHorarioResponse,
    AgendamentoFiltroCreate,
    AgendamentoFiltroResponse,
    AgendamentoCondicaoCreate,
    AgendamentoCondicaoResponse,
    AgendamentoFullResponse,
    AgendamentoStats,
    AgendamentoTestExecution,
    AgendamentoTestExecutionResponse,
    AgendamentoNextExecution,
    AgendamentoResetSequence,
    AgendamentoResetSequenceResponse,
)

# ═══════════════════════════════════════════════════════════════
# LOG
# ═══════════════════════════════════════════════════════════════
from .log import (
    LogExecucaoResponse,
    LogFilter,
    LogStats,
    LogStatsByBot,
    LogStatsByChannel,
    LogStatsByStatus,
    LogStatsSummary,
    LogExportRequest,
    LogExportResponse,
    ErrorAnalysis,
    ErrorTrend,
    AuditLog,
)

# ═══════════════════════════════════════════════════════════════
# USO
# ═══════════════════════════════════════════════════════════════
from .uso import (
    UsoMensalResponse,
    UsoStats,
    UsoQuota,
    UsoHistorico,
    UsoHistoricoResponse,
    UsoByBot,
    UsoByChannel,
    UsoBreakdown,
    RateLimitStatus,
    RateLimitWarning,
    PlanUpgrade,
    PlanUpgradePreview,
    OverageCharge,
    OverageHistory,
)

# ═══════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Common
    "SuccessResponse",
    "ErrorResponse",
    "PaginationParams",
    "PaginatedResponse",
    "BaseResponse",
    "BaseAudit",
    "TenantInfo",
    "StatusUpdate",
    "SoftDeleteResponse",
    "BulkDeleteRequest",
    "BulkDeleteResponse",
    "BulkUpdateRequest",
    "BulkUpdateResponse",
    "FilterParams",
    "ListQueryParams",
    # Auth
    "LoginRequest",
    "LoginResponse",
    "RegisterRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "RefreshTokenResponse",
    "UserResponse",
    "UserUpdateRequest",
    "ChangePasswordRequest",
    "PermissionCheck",
    "RoleInfo",
    "APIKeyCreate",
    "APIKeyResponse",
    "APIKeyListResponse",
    # Tenant
    "TenantCreate",
    "TenantUpdate",
    "TenantUpgradePlan",
    "TenantResponse",
    "TenantLimitsResponse",
    "TenantMemberAdd",
    "TenantMemberUpdate",
    "TenantMemberResponse",
    "TenantMemberListResponse",
    "TenantSettingsResponse",
    "TenantNotificationSettings",
    "TenantBillingInfo",
    # Bot
    "BotCreate",
    "BotUpdate",
    "BotResponse",
    "BotCredentialUpdateUser",
    "BotCredentialUpdateBot",
    "BotCredentialClear",
    "BotHealthCheck",
    "BotTestConnection",
    "BotStats",
    "BotListItem",
    # Marketplace
    "MarketplaceIntegracaoCreate",
    "MarketplaceIntegracaoUpdate",
    "MarketplaceIntegracaoResponse",
    "ShopeeCredentials",
    "MercadoLivreCredentials",
    "AmazonCredentials",
    "AliExpressCredentials",
    "MarketplaceCredentialUpdate",
    "MarketplaceCredentialClear",
    "MarketplaceTestConnection",
    "MarketplaceHealthCheck",
    "MarketplaceStats",
    "MarketplaceProduct",
    "MarketplaceCategorySync",
    "MarketplaceCategorySyncResponse",
    # Regra
    "RegraCreate",
    "RegraUpdate",
    "RegraResponse",
    "RegraOrigemCreate",
    "RegraOrigemResponse",
    "RegraDestinoCreate",
    "RegraDestinoResponse",
    "RegraFiltroCreate",
    "RegraFiltroResponse",
    "RegraCondicaoCreate",
    "RegraCondicaoResponse",
    "RegraFullResponse",
    "RegraStats",
    "RegraTestExecution",
    "RegraTestExecutionResponse",
    "RegraBulkActivate",
    "RegraBulkDeactivate",
    "RegraBulkOperationResponse",
    # Agendamento
    "AgendamentoCreate",
    "AgendamentoUpdate",
    "AgendamentoResponse",
    "AgendamentoOrigemCreate",
    "AgendamentoOrigemResponse",
    "AgendamentoDestinoCreate",
    "AgendamentoDestinoResponse",
    "AgendamentoHorarioCreate",
    "AgendamentoHorarioResponse",
    "AgendamentoFiltroCreate",
    "AgendamentoFiltroResponse",
    "AgendamentoCondicaoCreate",
    "AgendamentoCondicaoResponse",
    "AgendamentoFullResponse",
    "AgendamentoStats",
    "AgendamentoTestExecution",
    "AgendamentoTestExecutionResponse",
    "AgendamentoNextExecution",
    "AgendamentoResetSequence",
    "AgendamentoResetSequenceResponse",
    # Log
    "LogExecucaoResponse",
    "LogFilter",
    "LogStats",
    "LogStatsByBot",
    "LogStatsByChannel",
    "LogStatsByStatus",
    "LogStatsSummary",
    "LogExportRequest",
    "LogExportResponse",
    "ErrorAnalysis",
    "ErrorTrend",
    "AuditLog",
    # Uso
    "UsoMensalResponse",
    "UsoStats",
    "UsoQuota",
    "UsoHistorico",
    "UsoHistoricoResponse",
    "UsoByBot",
    "UsoByChannel",
    "UsoBreakdown",
    "RateLimitStatus",
    "RateLimitWarning",
    "PlanUpgrade",
    "PlanUpgradePreview",
    "OverageCharge",
    "OverageHistory",
]
