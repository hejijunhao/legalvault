"""Remove virtual_paralegal_id from vp_profile_pictures

Revision ID: d7ed4190e15b
Revises: 1c94e5cda518
Create Date: 2025-04-28 10:26:34.442868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd7ed4190e15b'
down_revision: Union[str, None] = '1c94e5cda518'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop unique constraint first
    op.drop_constraint(
        'uq_vp_profile_pictures_virtual_paralegal_id',
        'vp_profile_pictures',
        type_='unique',
        schema='public'
    )
    
    # Drop foreign key constraint
    op.drop_constraint(
        'fk_vp_profile_pictures_virtual_paralegal_id_virtual_paralegals',
        'vp_profile_pictures',
        type_='foreignkey',
        schema='public'
    )
    
    # Drop the column
    op.drop_column(
        'vp_profile_pictures',
        'virtual_paralegal_id',
        schema='public'
    )


def downgrade() -> None:
    # Add the column back
    op.add_column(
        'vp_profile_pictures',
        sa.Column(
            'virtual_paralegal_id',
            postgresql.UUID(as_uuid=True),
            nullable=False
        ),
        schema='public'
    )
    
    # Add foreign key constraint back
    op.create_foreign_key(
        'fk_vp_profile_pictures_virtual_paralegal_id_virtual_paralegals',
        'vp_profile_pictures',
        'virtual_paralegals',
        ['virtual_paralegal_id'],
        ['id'],
        source_schema='public',
        referent_schema='public'
    )
    
    # Add unique constraint back
    op.create_unique_constraint(
        'uq_vp_profile_pictures_virtual_paralegal_id',
        'vp_profile_pictures',
        ['virtual_paralegal_id'],
        schema='public'
    )
