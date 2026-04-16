"""Add User table for local authentication

Revision ID: 001_add_user_table
Revises: 90de375b1de2_add_missing_ativo_columns
Create Date: 2026-04-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '001_add_user_table'
down_revision = '90de375b1de2_add_missing_ativo_columns'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create User table
    op.create_table(
        'user',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('senha_hash', sa.String(255), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('criado_em', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('atualizado_em', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('deletado_em', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_user_email'),
    )
    op.create_index('ix_user_email', 'user', ['email'])
    op.create_index('ix_user_ativo', 'user', ['ativo'])
    op.create_index('ix_user_criado_em', 'user', ['criado_em'])
    op.create_index('ix_user_deletado_em', 'user', ['deletado_em'])
    
    # Modify TenantMember to add FK to user and remove old fields
    # First, add the new user_id FK column (nullable during transition)
    if not check_column_exists('tenant_member', 'user_id_new'):
        op.add_column('tenant_member', 
            sa.Column('user_id_new', postgresql.UUID(as_uuid=True), nullable=True)
        )
    
    # Create index on new user_id
    op.create_index('ix_tenant_member_user_id_new', 'tenant_member', ['user_id_new'])


def downgrade() -> None:
    # Drop the new user_id column
    op.drop_column('tenant_member', 'user_id_new')
    
    # Drop User table
    op.drop_table('user')


def check_column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    inspector = sa.inspect(op.get_context().bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns
