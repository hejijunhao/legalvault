"""add_tech_tree_progress_to_virtual_paralegals

Revision ID: 9dd2bf26ffd0
Revises: 3ec7edfe66e3
Create Date: 2024-12-11 13:41:25.737050

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = '9dd2bf26ffd0'
down_revision = '3ec7edfe66e3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add tech_tree_progress column to virtual_paralegals
    op.add_column('virtual_paralegals',
        sa.Column('tech_tree_progress', JSONB(), nullable=False, server_default='{"unlocked_nodes": {}, "progress": {}, "metadata": {}}')
    )


def downgrade() -> None:
    # Remove tech_tree_progress column
    op.drop_column('virtual_paralegals', 'tech_tree_progress')