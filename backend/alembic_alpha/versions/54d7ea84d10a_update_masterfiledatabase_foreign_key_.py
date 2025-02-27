"""update_masterfiledatabase_and_collections_foreign_key_schemas

Revision ID: 54d7ea84d10a
Revises: bebb531075b6
Create Date: 2025-01-30 11:13:13.699886
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '54d7ea84d10a'
down_revision: Union[str, None] = 'bebb531075b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Set search path to handle schemas explicitly
    op.execute('SET search_path TO public, vault')

    # Update MasterFileDatabase foreign key constraints
    op.execute("""
        DO $$
        BEGIN
            -- Update client_id foreign key
            ALTER TABLE IF EXISTS public.master_file_database 
            DROP CONSTRAINT IF EXISTS master_file_database_client_id_fkey,
            ADD CONSTRAINT master_file_database_client_id_fkey 
            FOREIGN KEY (client_id) REFERENCES public.clients(client_id) ON DELETE SET NULL;

            -- Update project_id foreign key
            ALTER TABLE IF EXISTS public.master_file_database 
            DROP CONSTRAINT IF EXISTS master_file_database_project_id_fkey,
            ADD CONSTRAINT master_file_database_project_id_fkey 
            FOREIGN KEY (project_id) REFERENCES public.projects(project_id) ON DELETE SET NULL;

            -- Update owner_id foreign key
            ALTER TABLE IF EXISTS public.master_file_database 
            DROP CONSTRAINT IF EXISTS master_file_database_owner_id_fkey,
            ADD CONSTRAINT master_file_database_owner_id_fkey 
            FOREIGN KEY (owner_id) REFERENCES vault.users(id) ON DELETE CASCADE;
        END $$;
    """)

    # Update Collections foreign key constraints
    op.execute("""
        DO $$
        BEGIN
            -- Update owner_id foreign key
            ALTER TABLE IF EXISTS public.collections 
            DROP CONSTRAINT IF EXISTS collections_owner_id_fkey,
            ADD CONSTRAINT collections_owner_id_fkey 
            FOREIGN KEY (owner_id) REFERENCES vault.users(id);
        END $$;
    """)


def downgrade() -> None:
    op.execute('SET search_path TO public, vault')

    # Revert MasterFileDatabase foreign key constraints
    op.execute("""
        DO $$
        BEGIN
            -- Revert client_id foreign key
            ALTER TABLE IF EXISTS public.master_file_database 
            DROP CONSTRAINT IF EXISTS master_file_database_client_id_fkey,
            ADD CONSTRAINT master_file_database_client_id_fkey 
            FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE SET NULL;

            -- Revert project_id foreign key
            ALTER TABLE IF EXISTS public.master_file_database 
            DROP CONSTRAINT IF EXISTS master_file_database_project_id_fkey,
            ADD CONSTRAINT master_file_database_project_id_fkey 
            FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE SET NULL;

            -- Revert owner_id foreign key
            ALTER TABLE IF EXISTS public.master_file_database 
            DROP CONSTRAINT IF EXISTS master_file_database_owner_id_fkey,
            ADD CONSTRAINT master_file_database_owner_id_fkey 
            FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE;
        END $$;
    """)

    # Revert Collections foreign key constraints
    op.execute("""
        DO $$
        BEGIN
            -- Revert owner_id foreign key
            ALTER TABLE IF EXISTS public.collections 
            DROP CONSTRAINT IF EXISTS collections_owner_id_fkey,
            ADD CONSTRAINT collections_owner_id_fkey 
            FOREIGN KEY (owner_id) REFERENCES users(id);
        END $$;
    """)