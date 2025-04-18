"""make_user_name_fields_nullable

Revision ID: 4996a3ce54e3
Revises: 35c19a9cb68a
Create Date: 2025-04-18 13:00:19.899200

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4996a3ce54e3'
down_revision: Union[str, None] = '35c19a9cb68a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('users', 'first_name', nullable=True, schema='public')
    op.alter_column('users', 'last_name', nullable=True, schema='public')
    op.alter_column('users', 'name', nullable=True, schema='public')

def downgrade():
    op.alter_column('users', 'first_name', nullable=False, schema='public')
    op.alter_column('users', 'last_name', nullable=False, schema='public')
    op.alter_column('users', 'name', nullable=False, schema='public')
