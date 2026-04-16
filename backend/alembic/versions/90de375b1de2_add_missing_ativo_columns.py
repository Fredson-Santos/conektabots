"""add_missing_ativo_columns

Revision ID: 90de375b1de2
Revises: 834164764f9a
Create Date: 2026-02-24 02:59:46.886477

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '90de375b1de2'
down_revision: Union[str, None] = '834164764f9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Todas as colunas já foram incluídas na migração inicial consolidada.
    # Esta migração existe apenas para manter a cadeia de revisões.
    pass


def downgrade() -> None:
    pass
