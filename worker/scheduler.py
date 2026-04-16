"""Scheduler — Scheduled Task Automation.

Runs scheduled automations based on configured times.
"""

import asyncio
import logging
from datetime import datetime, time
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agendamento import Agendamento, AgendamentoHorario


logger = logging.getLogger(__name__)


class Scheduler:
    """Execute scheduled automations."""

    def __init__(self, session: AsyncSession):
        """Initialize scheduler.

        Args:
            session: Database session
        """
        self.session = session
        self.running = False

    async def start_scheduler(self) -> None:
        """Start scheduler loop.

        Runs continuously, checking scheduled automations every minute.
        """
        self.running = True
        logger.info("Scheduler started")

        while self.running:
            try:
                await self._check_schedules()
            except Exception as e:
                logger.error(f"Scheduler error: {e}")

            # Check every minute
            await asyncio.sleep(60)

    async def stop_scheduler(self) -> None:
        """Stop scheduler loop."""
        self.running = False
        logger.info("Scheduler stopped")

    async def _check_schedules(self) -> None:
        """Check if any schedules should run now."""
        now = datetime.utcnow()
        current_hour = time(now.hour, now.minute)

        # Get all active schedules
        stmt = select(Agendamento).where(Agendamento.ativo == True)
        result = await self.session.execute(stmt)
        agendamentos = result.scalars().all()

        for agendamento in agendamentos:
            # Check if any horario matches current time
            for horario in agendamento.horarios:
                # Simple hour/minute match (ignores seconds)
                horario_time = horario.horario  # TIME type
                if (
                    horario_time.hour == current_hour.hour
                    and horario_time.minute == current_hour.minute
                ):
                    # Time to run this schedule!
                    logger.info(
                        f"Running scheduled automation {agendamento.id} at {current_hour}"
                    )
                    await self._execute_schedule(agendamento)

    async def _execute_schedule(self, agendamento: Agendamento) -> None:
        """Execute a scheduled automation.

        Args:
            agendamento: Schedule to run
        """
        try:
            # TODO: Implement actual message sending based on schedule config
            # - Get destinos
            # - Build message
            # - Send via bot/marketplace clients
            # - Log execution
            # - Update stats

            logger.info(f"Executed schedule {agendamento.id}")

        except Exception as e:
            logger.error(f"Error executing schedule {agendamento.id}: {e}")

    async def get_next_execution(
        self, agendamento_id: UUID
    ) -> Optional[datetime]:
        """Get next execution time for schedule.

        Args:
            agendamento_id: Schedule UUID

        Returns:
            Next execution datetime or None
        """
        stmt = select(Agendamento).where(Agendamento.id == agendamento_id)
        result = await self.session.execute(stmt)
        agendamento = result.scalar_one_or_none()

        if not agendamento or not agendamento.horarios:
            return None

        now = datetime.utcnow()
        next_execution = None

        # Find next scheduled horario
        for horario in agendamento.horarios:
            horario_time = horario.horario
            # Build datetime for today
            today_scheduled = datetime(
                now.year,
                now.month,
                now.day,
                horario_time.hour,
                horario_time.minute,
            )

            # If today's time has passed, use tomorrow
            if today_scheduled <= now:
                tomorrow = now.replace(day=now.day + 1)
                today_scheduled = datetime(
                    tomorrow.year,
                    tomorrow.month,
                    tomorrow.day,
                    horario_time.hour,
                    horario_time.minute,
                )

            if next_execution is None or today_scheduled < next_execution:
                next_execution = today_scheduled

        return next_execution
