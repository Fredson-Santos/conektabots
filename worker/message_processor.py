"""Message Processor — Rule & Schedule Execution.

Evaluates forwarding rules and decides where to send messages.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

from app.models.regra import Regra, RegraFiltro, RegraCondicao
from app.models.agendamento import Agendamento
from worker.marketplace_clients.base import MarketplaceMessage


logger = logging.getLogger(__name__)


@dataclass
class ProcessedMessage:
    """Result of message processing."""

    original_message: MarketplaceMessage
    regra_id: Optional[str]  # Which rule matched
    should_forward: bool
    destinos: List[Dict[str, Any]]  # Where to send it
    razao: str  # Why forwarded or blocked


class MessageProcessor:
    """Process and route messages through rules."""

    def __init__(self):
        """Initialize processor."""
        pass

    async def process_message(
        self,
        message: MarketplaceMessage,
        regras: List[Regra],
        agendamentos: List[Agendamento],
    ) -> List[ProcessedMessage]:
        """Process message through all active rules.

        Args:
            message: Marketplace message
            regras: Active forwarding rules
            agendamentos: Active schedules

        Returns:
            List of processing results (may have multiple destinations)
        """
        results = []

        for regra in regras:
            if not regra.ativo:
                continue

            # Check if rule applies to this message
            applies = await self._check_regra_applies(message, regra)

            if applies:
                result = ProcessedMessage(
                    original_message=message,
                    regra_id=str(regra.id),
                    should_forward=True,
                    destinos=[
                        {
                            "tipo": d.tipo,
                            "canal": d.canal,
                            "chat_id": d.chat_id,
                        }
                        for d in regra.destinos
                    ],
                    razao="Regra ativa aplicou",
                )
                results.append(result)

        return results

    async def _check_regra_applies(
        self, message: MarketplaceMessage, regra: Regra
    ) -> bool:
        """Check if regex applies to message.

        Args:
            message: Marketplace message
            regra: Forwarding rule

        Returns:
            True if rule applies
        """
        # Check origem matches
        origem_match = any(
            o.canal == message.origem_id for o in regra.origens
        )
        if not origem_match:
            return False

        # Check filtros
        for filtro in regra.filtros:
            if not await self._check_filtro(message, filtro):
                return False

        # Check condicoes
        for condicao in regra.condicoes:
            if not await self._check_condicao(message, condicao):
                return False

        return True

    async def _check_filtro(self, message: MarketplaceMessage, filtro) -> bool:
        """Check if message passes filter.

        Args:
            message: Message to check
            filtro: Filter rule

        Returns:
            True if passes
        """
        if filtro.tipo == "palavra_chave":
            return filtro.valor.lower() in message.conteudo.lower()
        elif filtro.tipo == "senders":
            return message.sender_id in filtro.valor.split(",")
        elif filtro.tipo == "todos":
            return True

        return True

    async def _check_condicao(self, message: MarketplaceMessage, condicao) -> bool:
        """Check if message passes condition.

        Args:
            message: Message to check
            condicao: Condition rule

        Returns:
            True if passes
        """
        if condicao.tipo == "contem":
            return condicao.valor in message.conteudo
        elif condicao.tipo == "inicia_com":
            return message.conteudo.startswith(condicao.valor)
        elif condicao.tipo == "termina_com":
            return message.conteudo.endswith(condicao.valor)

        return True
