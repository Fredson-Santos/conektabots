"""UUID Support for SQLite Testing.

Provides a TypeDecorator that allows SQLite to work with UUID columns.
"""

import uuid
from sqlalchemy import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class GUID(TypeDecorator):
    """Platform-independent GUID type that uses CHAR(36) for SQLite.

    Uses PostgreSQL's native UUID type when available.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Load appropriate implementation for dialect."""
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        """Convert value to appropriate format for database."""
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            if dialect.name == 'postgresql':
                return value
            return str(value)
        if not isinstance(value, str):
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        """Convert value from database to UUID."""
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)
