"""initial

Revision ID: 3ec7edfe66e3
Revises: 
Create Date: 2024-03-19 12:34:56.789012

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3ec7edfe66e3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table first
    op.create_table('users',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Then create virtual_paralegals table
    op.create_table('virtual_paralegals',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('whatsapp', sa.String(), nullable=True),
        sa.Column('owner_id', postgresql.UUID(), nullable=False),
        sa.Column('abilities', postgresql.JSONB(), nullable=False),
        sa.Column('behaviors', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_virtual_paralegals_name', 'virtual_paralegals', ['name'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_virtual_paralegals_name', table_name='virtual_paralegals')
    op.drop_table('virtual_paralegals')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')