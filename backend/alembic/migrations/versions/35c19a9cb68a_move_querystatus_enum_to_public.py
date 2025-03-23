"""move_querystatus_enum_to_public

Revision ID: 35c19a9cb68a
Revises: b29d41639884
Create Date: 2025-03-23 15:42:16.066524

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '35c19a9cb68a'
down_revision: Union[str, None] = 'b29d41639884'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create enum in public schema
    querystatus = postgresql.ENUM('PENDING', 'COMPLETED', 'FAILED', 'NEEDS_CLARIFICATION', 'IRRELEVANT', 
                                name='querystatus', create_type=True, schema='public')
    querystatus.create(op.get_bind(), checkfirst=False)
    
    # First drop the default
    op.execute('ALTER TABLE public.public_search_messages ALTER COLUMN status DROP DEFAULT')
    
    # Update column to use new enum
    op.execute('ALTER TABLE public.public_search_messages ALTER COLUMN status TYPE public.querystatus USING status::text::public.querystatus')
    
    # Restore the default
    op.execute("ALTER TABLE public.public_search_messages ALTER COLUMN status SET DEFAULT 'PENDING'::public.querystatus")
    
    # Drop old enum from vault schema
    op.execute('DROP TYPE IF EXISTS vault.querystatus')


def downgrade():
    # Recreate enum in vault schema
    querystatus = postgresql.ENUM('PENDING', 'COMPLETED', 'FAILED', 'NEEDS_CLARIFICATION', 'IRRELEVANT',
                                name='querystatus', create_type=True, schema='vault')
    querystatus.create(op.get_bind(), checkfirst=False)
    
    # First drop the default
    op.execute('ALTER TABLE public.public_search_messages ALTER COLUMN status DROP DEFAULT')
    
    # Update column to use vault schema enum
    op.execute('ALTER TABLE public.public_search_messages ALTER COLUMN status TYPE vault.querystatus USING status::text::vault.querystatus')
    
    # Restore the default
    op.execute("ALTER TABLE public.public_search_messages ALTER COLUMN status SET DEFAULT 'PENDING'::vault.querystatus")
    
    # Drop enum from public schema
    op.execute('DROP TYPE IF EXISTS public.querystatus')
