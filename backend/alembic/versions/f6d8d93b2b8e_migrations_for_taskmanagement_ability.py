# backend/alembic/versions/f6d8d93b2b8e_migrations_for_taskmanagement_ability.py
"""Migrations for TaskManagement ability

Revision ID: f6d8d93b2b8e
Revises: fd41aaf4be35
Create Date: 2024-12-16 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import AutoString  # Add this import

# revision identifiers, used by Alembic.
revision: str = 'f6d8d93b2b8e'
down_revision: Union[str, None] = 'fd41aaf4be35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create task_management_abilities table
    op.create_table(
        'task_management_abilities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ability_id', sa.Integer(), nullable=False),
        sa.Column('operation_name', AutoString(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('input_schema', JSONB(), nullable=False),
        sa.Column('output_schema', JSONB(), nullable=False),
        sa.Column('workflow_steps', JSONB(), nullable=False),
        sa.Column('constraints', JSONB(), nullable=False),
        sa.Column('permissions', JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['ability_id'], ['abilities.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_task_management_abilities_ability_id'),
        'task_management_abilities',
        ['ability_id'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix_task_management_abilities_ability_id'),
        table_name='task_management_abilities'
    )
    op.drop_table('task_management_abilities')