"""add_profile_picture_id_to_virtual_paralegals

Revision ID: 8a76486a9852
Revises: d7ed4190e15b
Create Date: 2025-04-28 10:33:52.319809

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8a76486a9852'
down_revision: Union[str, None] = 'd7ed4190e15b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add profile_picture_id column
    op.add_column(
        'virtual_paralegals',
        sa.Column(
            'profile_picture_id',
            postgresql.UUID(as_uuid=True),
            nullable=True
        ),
        schema='public'
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_virtual_paralegals_profile_picture_id_vp_profile_pictures',
        'virtual_paralegals',
        'vp_profile_pictures',
        ['profile_picture_id'],
        ['id'],
        source_schema='public',
        referent_schema='public'
    )


def downgrade() -> None:
    # Drop foreign key constraint first
    op.drop_constraint(
        'fk_virtual_paralegals_profile_picture_id_vp_profile_pictures',
        'virtual_paralegals',
        type_='foreignkey',
        schema='public'
    )
    
    # Drop the column
    op.drop_column(
        'virtual_paralegals',
        'profile_picture_id',
        schema='public'
    )
