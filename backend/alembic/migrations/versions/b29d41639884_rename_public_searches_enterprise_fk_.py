"""rename_public_searches_enterprise_fk_constraint

Revision ID: b29d41639884
Revises: 326b31d42696
Create Date: 2025-03-22 19:32:45.852950

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = 'b29d41639884'
down_revision: Union[str, None] = '326b31d42696'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get the database connection
    connection = op.get_bind()
    inspector = Inspector.from_engine(connection)
    
    # Get foreign key constraints for public_searches table
    fks = inspector.get_foreign_keys('public_searches', schema='public')
    
    # Look for existing enterprise_id foreign key
    enterprise_fk = None
    for fk in fks:
        if len(fk['constrained_columns']) == 1 and fk['constrained_columns'][0] == 'enterprise_id':
            enterprise_fk = fk
            break
    
    # If we found an existing FK constraint
    if enterprise_fk:
        # Drop the existing constraint if it's not the one we want
        if enterprise_fk['name'] != 'fk_public_searches_enterprise_id_enterprises':
            op.drop_constraint(
                enterprise_fk['name'],
                'public_searches',
                type_='foreignkey',
                schema='public'
            )
            # Create the new constraint with our explicit name
            op.create_foreign_key(
                'fk_public_searches_enterprise_id_enterprises',
                'public_searches',
                'enterprises',
                ['enterprise_id'],
                ['id'],
                source_schema='public',
                referent_schema='public'
            )
    else:
        # No existing FK found, create a new one
        op.create_foreign_key(
            'fk_public_searches_enterprise_id_enterprises',
            'public_searches',
            'enterprises',
            ['enterprise_id'],
            ['id'],
            source_schema='public',
            referent_schema='public'
        )


def downgrade() -> None:
    # Get the database connection
    connection = op.get_bind()
    inspector = Inspector.from_engine(connection)
    
    # Check if our named constraint exists
    fks = inspector.get_foreign_keys('public_searches', schema='public')
    constraint_exists = any(fk['name'] == 'fk_public_searches_enterprise_id_enterprises' for fk in fks)
    
    if constraint_exists:
        # Drop our explicitly named constraint
        op.drop_constraint(
            'fk_public_searches_enterprise_id_enterprises',
            'public_searches',
            type_='foreignkey',
            schema='public'
        )
        
        # Create a new constraint with SQLAlchemy's auto-generated name pattern
        # This mimics the default behavior before our explicit naming
        op.create_foreign_key(
            None,  # Let SQLAlchemy auto-generate the name
            'public_searches',
            'enterprises',
            ['enterprise_id'],
            ['id'],
            source_schema='public',
            referent_schema='public'
        )
