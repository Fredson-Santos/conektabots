"""SQLAlchemy Type definitions for multi-database support.

Provides database-agnostic column types.
"""

from sqlalchemy import UUID as PG_UUID
from app.core.guid import GUID
import os

# Determine which ID type to use based on environment
USE_POSTGRESQL = "postgresql" in os.getenv("DATABASE_URL", "").lower()

# Use GUID for flexibility (works with both PostgreSQL and SQLite)
# UUID = GUID if not USE_POSTGRESQL else PG_UUID()
# Actually, always use GUID since it auto-detects the dialect
ID_TYPE = GUID()
