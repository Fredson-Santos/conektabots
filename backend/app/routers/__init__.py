"""Routers — API Endpoint Definitions.

All REST API routers for ConektaBots SaaS v2.0
"""

from app.routers import auth, tenants, bots, marketplaces, regras, agendamentos, logs, health

__all__ = [
    "auth",
    "tenants",
    "bots",
    "marketplaces",
    "regras",
    "agendamentos",
    "logs",
    "health",
]
