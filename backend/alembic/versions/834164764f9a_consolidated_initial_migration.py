"""Consolidated initial migration

Revision ID: 834164764f9a
Revises: 
Create Date: 2026-02-24 02:45:29.320076

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '834164764f9a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Cria todas as tabelas com o schema final completo
    op.create_table(
        'bot',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('nome', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('api_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('api_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('phone', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('bot_token', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('tipo', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='user'),
        sa.Column('session_string', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    )

    op.create_table(
        'regra',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('nome', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('origem', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('destino', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('filtro', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('substituto', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('bloqueios', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('somente_se_tiver', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('filtro_midia', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=sa.text("'todos'")),
        sa.Column('converter_shopee', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('bot_id', sa.Integer(), sa.ForeignKey('bot.id'), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    )

    op.create_table(
        'agendamento',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('nome', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('origem', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('destino', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('msg_id_atual', sa.Integer(), nullable=False),
        sa.Column('tipo_envio', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('horario', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('filtro', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('substituto', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('bloqueios', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('somente_se_tiver', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('filtro_midia', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=sa.text("'todos'")),
        sa.Column('bot_id', sa.Integer(), sa.ForeignKey('bot.id'), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    )

    op.create_table(
        'logexecucao',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('bot_id', sa.Integer(), sa.ForeignKey('bot.id'), nullable=False),
        sa.Column('bot_nome', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('origem', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('destino', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('mensagem', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('data_hora', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'configuracao',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('shopee_app_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('shopee_app_secret', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('logexecucao')
    op.drop_table('agendamento')
    op.drop_table('regra')
    op.drop_table('bot')
    op.drop_table('configuracao')
