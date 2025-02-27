"""rename_techtree_id_to_ability_id

Revision ID: 8ae2a0a068bf
Revises: # leave this empty if it's your first migration
Create Date: 2024-12-16 11:XX:XX.XXXXXX

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision: str = '8ae2a0a068bf'
down_revision: Union[str, None] = None  # or previous revision id if this isn't first
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.alter_column('task_management_abilities', 'techtree_id',
                    new_column_name='ability_id')

def downgrade() -> None:
    op.alter_column('task_management_abilities', 'ability_id',
                    new_column_name='techtree_id')