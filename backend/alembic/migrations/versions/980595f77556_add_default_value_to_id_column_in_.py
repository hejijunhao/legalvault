"""Add default value to id column in public.users

Revision ID: 980595f77556
Revises: 4996a3ce54e3
Create Date: 2025-04-18 13:45:18.501474

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '980595f77556'
down_revision: Union[str, None] = '4996a3ce54e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("ALTER TABLE public.users ALTER COLUMN id SET DEFAULT gen_random_uuid();")


def downgrade():
    op.execute("ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT;")

