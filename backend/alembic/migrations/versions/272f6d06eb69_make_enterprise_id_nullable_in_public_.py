"""make_enterprise_id_nullable_in_public_searches

Revision ID: 272f6d06eb69
Revises: 02f1d5d2c1a9
Create Date: 2025-03-15 11:23:10.638588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '272f6d06eb69'
down_revision: Union[str, None] = '02f1d5d2c1a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('public_searches', 'enterprise_id', 
                    existing_type=sa.UUID(), 
                    nullable=True, 
                    schema='vault')


def downgrade() -> None:
    op.alter_column('public_searches', 'enterprise_id', 
                    existing_type=sa.UUID(), 
                    nullable=False, 
                    schema='vault')
