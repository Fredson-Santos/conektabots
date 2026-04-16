"""
Enums — Tipos enumerados mapeados do PostgreSQL

Correspondência com migrations/001_extensions_and_types.sql
- Cada Python Enum corresponde a um PostgreSQL Type
- Herdam de (str, Enum) para serialização JSON
- Valores são strings para compatibilidade com JSONB/API

Uso:
    from app.models.enums import PlanoTipo, BotTipo, MarketplaceTipo
    
    tenant_plan = PlanoTipo.PRO
    # ✅ tenant_plan == "pro"
    # ✅ tenant_plan.value == "pro"
    # ✅ json.dumps({"plano": tenant_plan}) → {"plano": "pro"}
"""

from enum import Enum


# ═══════════════════════════════════════════════════════════════
# Planos de Assinatura
# ═══════════════════════════════════════════════════════════════

class PlanoTipo(str, Enum):
    """Planos de subscription disponíveis.
    
    Mapping:
        FREE → 2 bots, 5 regras, 5 agendamentos, 50 msgs/hora
        STARTER → 5 bots, 15 regras, 10 agendamentos, 200 msgs/hora
        PRO → 20 bots, 50 regras, 30 agendamentos, 1000 msgs/hora
        ENTERPRISE → ilimitado
    """
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# ═══════════════════════════════════════════════════════════════
# Tipo de Conta Telegram
# ═══════════════════════════════════════════════════════════════

class BotTipo(str, Enum):
    """Tipo de conta Telegram.
    
    USER: Conta pessoal (MTProto API + session_string)
    BOT: Bot oficial (Bot API + bot_token)
    """
    USER = "user"
    BOT = "bot"


# ═══════════════════════════════════════════════════════════════
# Modo de Envio de Mensagens
# ═══════════════════════════════════════════════════════════════

class TipoEnvio(str, Enum):
    """Modo de envio para agendamentos.
    
    SEQUENCIAL: Envia msgs em ordem (1, 2, 3, ...)
    ALEATORIO: Envia msgs em ordem aleatória
    """
    SEQUENCIAL = "sequencial"
    ALEATORIO = "aleatorio"


# ═══════════════════════════════════════════════════════════════
# Status de Execução (Logs)
# ═══════════════════════════════════════════════════════════════

class LogStatus(str, Enum):
    """Status de execução registrado em logs.
    
    SUCESSO: Mensagem enviada com êxito
    ERRO: Falha na execução
    AVISO: Execução com aviso (ex: timeout, retry)
    """
    SUCESSO = "sucesso"
    ERRO = "erro"
    AVISO = "aviso"


# ═══════════════════════════════════════════════════════════════
# Marketplaces Suportados
# ═══════════════════════════════════════════════════════════════

class MarketplaceTipo(str, Enum):
    """Marketplaces com suporte de integração.
    
    Cada tipo corresponde a um client em marketplace_clients/
    Credenciais armazenadas criptografadas em marketplace_integracao.credenciais_enc
    """
    SHOPEE = "shopee"
    MERCADO_LIVRE = "mercado_livre"
    AMAZON = "amazon"
    MAGALU = "magalu"
    AMERICANAS = "americanas"
    ALIEXPRESS = "aliexpress"
    SHEIN = "shein"


# ═══════════════════════════════════════════════════════════════
# Papéis (RBAC) dentro de um Tenant
# ═══════════════════════════════════════════════════════════════

class MembroRole(str, Enum):
    """Papéis/permissões dentro de um tenant.
    
    Hierarquia:
        OWNER (4) — Proprietário, acesso total + gerencia membros
        ADMIN (3) — Administrador, acesso total operacional
        EDITOR (2) — Editor, pode criar/editar regras e agendamentos
        VIEWER (1) — Visualizador, apenas leitura
    
    RLS Policy:
        - OWNER vê tudo do tenant
        - ADMIN vê tudo do tenant
        - EDITOR vê regras/agendamentos criados por si
        - VIEWER vê tudo mas sem permissão de edição
    """
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

    @property
    def level(self) -> int:
        """Retorna nível hierárquico (maior = mais permissões)."""
        levels = {
            MembroRole.OWNER: 4,
            MembroRole.ADMIN: 3,
            MembroRole.EDITOR: 2,
            MembroRole.VIEWER: 1,
        }
        return levels.get(self, 0)

    def has_permission(self, required_role: "MembroRole") -> bool:
        """Verifica se este role tem permissão >= required_role.
        
        Args:
            required_role: Role requerida
            
        Returns:
            True se self.level >= required_role.level
            
        Example:
            >>> admin_role = MembroRole.ADMIN
            >>> admin_role.has_permission(MembroRole.EDITOR)
            True
            >>> viewer_role = MembroRole.VIEWER
            >>> viewer_role.has_permission(MembroRole.ADMIN)
            False
        """
        return self.level >= required_role.level


# ═══════════════════════════════════════════════════════════════
# Filtro de Mídia
# ═══════════════════════════════════════════════════════════════

class FiltroMidiaTipo(str, Enum):
    """Tipos de mídia para filtro em regras/agendamentos.
    
    TODOS: Sem filtro, processa todas as mensagens
    FOTO: Apenas mensagens com fotos
    VIDEO: Apenas mensagens com vídeos
    FOTO_VIDEO: Fotos OU vídeos
    DOCUMENTO: Apenas documentos
    AUDIO: Apenas áudios
    """
    TODOS = "todos"
    FOTO = "foto"
    VIDEO = "video"
    FOTO_VIDEO = "foto_video"
    DOCUMENTO = "documento"
    AUDIO = "audio"


# ═══════════════════════════════════════════════════════════════
# Tipo de Filtro (Incluir vs Bloquear)
# ═══════════════════════════════════════════════════════════════

class FiltroRegraType(str, Enum):
    """Tipo de filtro de palavras-chave em regras/agendamentos.
    
    INCLUIR: Whitelist — só processa se contiver a palavra
    BLOQUEAR: Blacklist — pula se contiver a palavra
    
    Uso:
        - Uma regra pode ter múltiplos filtros
        - Se tipo=INCLUIR, mensagem só passa se contiver TODAS palavras
        - Se tipo=BLOQUEAR, mensagem é pulada se contiver QUALQUER palavra
    """
    INCLUIR = "incluir"
    BLOQUEAR = "bloquear"


# ═══════════════════════════════════════════════════════════════
# Mapping para Validação & Limits
# ═══════════════════════════════════════════════════════════════

# Limites por plano (referência para validação em service layer)
PLAN_LIMITS = {
    PlanoTipo.FREE: {
        "max_bots": 2,
        "max_regras": 5,
        "max_agendamentos": 5,
        "max_msgs_hora": 50,
    },
    PlanoTipo.STARTER: {
        "max_bots": 5,
        "max_regras": 15,
        "max_agendamentos": 10,
        "max_msgs_hora": 200,
    },
    PlanoTipo.PRO: {
        "max_bots": 20,
        "max_regras": 50,
        "max_agendamentos": 30,
        "max_msgs_hora": 1000,
    },
    PlanoTipo.ENTERPRISE: {
        "max_bots": float("inf"),
        "max_regras": float("inf"),
        "max_agendamentos": float("inf"),
        "max_msgs_hora": float("inf"),
    },
}


# ═══════════════════════════════════════════════════════════════
# Exports
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "PlanoTipo",
    "BotTipo",
    "TipoEnvio",
    "LogStatus",
    "MarketplaceTipo",
    "MembroRole",
    "FiltroMidiaTipo",
    "FiltroRegraType",
    "PLAN_LIMITS",
]
