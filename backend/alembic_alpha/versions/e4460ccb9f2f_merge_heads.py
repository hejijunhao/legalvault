"""merge_heads

Revision ID: e4460ccb9f2f
Revises: f6d8d93b2b8e, 8ae2a0a068bf
Create Date: 2024-12-16 11:05:54.243388

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4460ccb9f2f'
down_revision: Union[str, None] = ('f6d8d93b2b8e', '8ae2a0a068bf')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
