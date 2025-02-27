"""convert_workspace_models_to_public_schema

Revision ID: 9e84d2be44d1
Revises: b56ef52335fa
Create Date: 2025-01-29 08:31:34.219527

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9e84d2be44d1'
down_revision: Union[str, None] = 'b56ef52335fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Step 1: Move all tables to public schema
    # Order matters - move independent tables first, then dependent ones
    tables = [
        'clients',
        'contacts',
        'projects',
        'notebooks',
        'tasks',
        'reminders',
        'project_clients',
        'contact_clients',
        'contact_projects'
    ]

    for table in tables:
        op.execute(f'ALTER TABLE IF EXISTS vault.{table} SET SCHEMA public')

    # Step 2: Update foreign key constraints for all tables

    # Clients foreign keys
    op.execute("""
        ALTER TABLE public.clients 
        DROP CONSTRAINT IF EXISTS clients_created_by_fkey,
        ADD CONSTRAINT clients_created_by_fkey 
        FOREIGN KEY (created_by) REFERENCES vault.users(id);
    """)
    op.execute("""
        ALTER TABLE public.clients 
        DROP CONSTRAINT IF EXISTS clients_modified_by_fkey,
        ADD CONSTRAINT clients_modified_by_fkey 
        FOREIGN KEY (modified_by) REFERENCES vault.users(id);
    """)

    # Contacts foreign keys
    op.execute("""
        ALTER TABLE public.contacts 
        DROP CONSTRAINT IF EXISTS contacts_created_by_fkey,
        ADD CONSTRAINT contacts_created_by_fkey 
        FOREIGN KEY (created_by) REFERENCES vault.users(id);
    """)
    op.execute("""
        ALTER TABLE public.contacts 
        DROP CONSTRAINT IF EXISTS contacts_modified_by_fkey,
        ADD CONSTRAINT contacts_modified_by_fkey 
        FOREIGN KEY (modified_by) REFERENCES vault.users(id);
    """)

    # Projects foreign keys
    op.execute("""
        ALTER TABLE public.projects 
        DROP CONSTRAINT IF EXISTS projects_created_by_fkey,
        ADD CONSTRAINT projects_created_by_fkey 
        FOREIGN KEY (created_by) REFERENCES vault.users(id);
    """)
    op.execute("""
        ALTER TABLE public.projects 
        DROP CONSTRAINT IF EXISTS projects_modified_by_fkey,
        ADD CONSTRAINT projects_modified_by_fkey 
        FOREIGN KEY (modified_by) REFERENCES vault.users(id);
    """)

    # Tasks foreign keys
    op.execute("""
        ALTER TABLE public.tasks 
        DROP CONSTRAINT IF EXISTS tasks_project_id_fkey,
        ADD CONSTRAINT tasks_project_id_fkey 
        FOREIGN KEY (project_id) REFERENCES public.projects(project_id) ON DELETE CASCADE;
    """)
    op.execute("""
        ALTER TABLE public.tasks 
        DROP CONSTRAINT IF EXISTS tasks_assigned_to_fkey,
        ADD CONSTRAINT tasks_assigned_to_fkey 
        FOREIGN KEY (assigned_to) REFERENCES vault.users(id);
    """)
    op.execute("""
        ALTER TABLE public.tasks 
        DROP CONSTRAINT IF EXISTS tasks_created_by_fkey,
        ADD CONSTRAINT tasks_created_by_fkey 
        FOREIGN KEY (created_by) REFERENCES vault.users(id);
    """)
    op.execute("""
        ALTER TABLE public.tasks 
        DROP CONSTRAINT IF EXISTS tasks_modified_by_fkey,
        ADD CONSTRAINT tasks_modified_by_fkey 
        FOREIGN KEY (modified_by) REFERENCES vault.users(id);
    """)

    # Reminders foreign keys
    op.execute("""
        ALTER TABLE public.reminders 
        DROP CONSTRAINT IF EXISTS reminders_project_id_fkey,
        ADD CONSTRAINT reminders_project_id_fkey 
        FOREIGN KEY (project_id) REFERENCES public.projects(project_id) ON DELETE CASCADE;
    """)
    op.execute("""
        ALTER TABLE public.reminders 
        DROP CONSTRAINT IF EXISTS reminders_created_by_fkey,
        ADD CONSTRAINT reminders_created_by_fkey 
        FOREIGN KEY (created_by) REFERENCES vault.users(id);
    """)
    op.execute("""
        ALTER TABLE public.reminders 
        DROP CONSTRAINT IF EXISTS reminders_modified_by_fkey,
        ADD CONSTRAINT reminders_modified_by_fkey 
        FOREIGN KEY (modified_by) REFERENCES vault.users(id);
    """)

    # Notebooks foreign keys
    op.execute("""
        ALTER TABLE public.notebooks 
        DROP CONSTRAINT IF EXISTS notebooks_project_id_fkey,
        ADD CONSTRAINT notebooks_project_id_fkey 
        FOREIGN KEY (project_id) REFERENCES public.projects(project_id) ON DELETE CASCADE;
    """)
    op.execute("""
        ALTER TABLE public.notebooks 
        DROP CONSTRAINT IF EXISTS notebooks_created_by_fkey,
        ADD CONSTRAINT notebooks_created_by_fkey 
        FOREIGN KEY (created_by) REFERENCES vault.users(id);
    """)
    op.execute("""
        ALTER TABLE public.notebooks 
        DROP CONSTRAINT IF EXISTS notebooks_modified_by_fkey,
        ADD CONSTRAINT notebooks_modified_by_fkey 
        FOREIGN KEY (modified_by) REFERENCES vault.users(id);
    """)

    # Junction tables foreign keys
    op.execute("""
        ALTER TABLE public.project_clients 
        DROP CONSTRAINT IF EXISTS project_clients_project_id_fkey,
        ADD CONSTRAINT project_clients_project_id_fkey 
        FOREIGN KEY (project_id) REFERENCES public.projects(project_id) ON DELETE CASCADE;
    """)
    op.execute("""
        ALTER TABLE public.project_clients 
        DROP CONSTRAINT IF EXISTS project_clients_client_id_fkey,
        ADD CONSTRAINT project_clients_client_id_fkey 
        FOREIGN KEY (client_id) REFERENCES public.clients(client_id) ON DELETE CASCADE;
    """)
    op.execute("""
        ALTER TABLE public.project_clients 
        DROP CONSTRAINT IF EXISTS project_clients_created_by_fkey,
        ADD CONSTRAINT project_clients_created_by_fkey 
        FOREIGN KEY (created_by) REFERENCES vault.users(id) ON DELETE SET NULL;
    """)

    op.execute("""
        ALTER TABLE public.contact_clients 
        DROP CONSTRAINT IF EXISTS contact_clients_contact_id_fkey,
        ADD CONSTRAINT contact_clients_contact_id_fkey 
        FOREIGN KEY (contact_id) REFERENCES public.contacts(contact_id) ON DELETE CASCADE;
    """)
    op.execute("""
        ALTER TABLE public.contact_clients 
        DROP CONSTRAINT IF EXISTS contact_clients_client_id_fkey,
        ADD CONSTRAINT contact_clients_client_id_fkey 
        FOREIGN KEY (client_id) REFERENCES public.clients(client_id) ON DELETE CASCADE;
    """)
    op.execute("""
        ALTER TABLE public.contact_clients 
        DROP CONSTRAINT IF EXISTS contact_clients_created_by_fkey,
        ADD CONSTRAINT contact_clients_created_by_fkey 
        FOREIGN KEY (created_by) REFERENCES vault.users(id) ON DELETE SET NULL;
    """)

    op.execute("""
        ALTER TABLE public.contact_projects 
        DROP CONSTRAINT IF EXISTS contact_projects_contact_id_fkey,
        ADD CONSTRAINT contact_projects_contact_id_fkey 
        FOREIGN KEY (contact_id) REFERENCES public.contacts(contact_id) ON DELETE CASCADE;
    """)
    op.execute("""
        ALTER TABLE public.contact_projects 
        DROP CONSTRAINT IF EXISTS contact_projects_project_id_fkey,
        ADD CONSTRAINT contact_projects_project_id_fkey 
        FOREIGN KEY (project_id) REFERENCES public.projects(project_id) ON DELETE CASCADE;
    """)
    op.execute("""
        ALTER TABLE public.contact_projects 
        DROP CONSTRAINT IF EXISTS contact_projects_created_by_fkey,
        ADD CONSTRAINT contact_projects_created_by_fkey 
        FOREIGN KEY (created_by) REFERENCES vault.users(id) ON DELETE SET NULL;
    """)

    # Step 3: Create indexes for each table
    # Create index creation function to avoid repetition
    op.execute("""
        CREATE OR REPLACE FUNCTION create_index_if_not_exists(
            p_schema text,
            p_table text,
            p_index_name text,
            p_column_list text
        )
        RETURNS void AS
        $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_indexes
                WHERE schemaname = p_schema
                AND tablename = p_table
                AND indexname = p_index_name
            ) THEN
                EXECUTE format('CREATE INDEX %I ON %I.%I(%s)',
                    p_index_name,
                    p_schema,
                    p_table,
                    p_column_list
                );
            END IF;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Clients indexes
    op.execute("SELECT create_index_if_not_exists('public', 'clients', 'idx_client_name', 'name')")
    op.execute("SELECT create_index_if_not_exists('public', 'clients', 'idx_client_status', 'status')")
    op.execute("SELECT create_index_if_not_exists('public', 'clients', 'idx_client_entity_type', 'legal_entity_type')")
    op.execute("SELECT create_index_if_not_exists('public', 'clients', 'idx_client_join_date', 'client_join_date')")
    op.execute("SELECT create_index_if_not_exists('public', 'clients', 'idx_client_created', 'created_by')")
    op.execute("SELECT create_index_if_not_exists('public', 'clients', 'idx_client_modified', 'modified_by, updated_at')")

    # Contacts indexes
    op.execute("SELECT create_index_if_not_exists('public', 'contacts', 'idx_contact_name', 'first_name, last_name')")
    op.execute("SELECT create_index_if_not_exists('public', 'contacts', 'idx_contact_email', 'email')")
    op.execute("SELECT create_index_if_not_exists('public', 'contacts', 'idx_contact_type', 'contact_type')")
    op.execute("SELECT create_index_if_not_exists('public', 'contacts', 'idx_contact_status', 'status')")
    op.execute("SELECT create_index_if_not_exists('public', 'contacts', 'idx_contact_created', 'created_by')")
    op.execute("SELECT create_index_if_not_exists('public', 'contacts', 'idx_contact_modified', 'modified_by, updated_at')")

    # Projects indexes
    op.execute("SELECT create_index_if_not_exists('public', 'projects', 'idx_project_name', 'name')")
    op.execute("SELECT create_index_if_not_exists('public', 'projects', 'idx_project_status_practice', 'status, practice_area')")
    op.execute("SELECT create_index_if_not_exists('public', 'projects', 'idx_project_created_by', 'created_by')")
    op.execute("SELECT create_index_if_not_exists('public', 'projects', 'idx_project_modified', 'modified_by, updated_at')")

    # Tasks indexes
    op.execute("SELECT create_index_if_not_exists('public', 'tasks', 'idx_task_project', 'project_id')")
    op.execute("SELECT create_index_if_not_exists('public', 'tasks', 'idx_task_status', 'status')")
    op.execute("SELECT create_index_if_not_exists('public', 'tasks', 'idx_task_due_date', 'due_date')")
    op.execute("SELECT create_index_if_not_exists('public', 'tasks', 'idx_task_assigned', 'assigned_to')")
    op.execute("SELECT create_index_if_not_exists('public', 'tasks', 'idx_task_created_by', 'created_by')")
    op.execute("SELECT create_index_if_not_exists('public', 'tasks', 'idx_task_modified', 'modified_by, updated_at')")

    # Reminders indexes
    op.execute("SELECT create_index_if_not_exists('public', 'reminders', 'idx_reminder_project', 'project_id')")
    op.execute("SELECT create_index_if_not_exists('public', 'reminders', 'idx_reminder_status', 'status')")
    op.execute("SELECT create_index_if_not_exists('public', 'reminders', 'idx_reminder_due_date', 'due_date')")
    op.execute("SELECT create_index_if_not_exists('public', 'reminders', 'idx_reminder_created_by', 'created_by')")
    op.execute("SELECT create_index_if_not_exists('public', 'reminders', 'idx_reminder_modified', 'modified_by, updated_at')")

    # Notebooks indexes
    op.execute("SELECT create_index_if_not_exists('public', 'notebooks', 'idx_notebook_project', 'project_id')")
    op.execute("SELECT create_index_if_not_exists('public', 'notebooks', 'idx_notebook_modified', 'modified_by, updated_at')")
    op.execute("SELECT create_index_if_not_exists('public', 'notebooks', 'idx_notebook_created', 'created_by')")


def downgrade() -> None:
    # Step 1: Drop all foreign key constraints
    tables = [
        'contact_projects',
        'contact_clients',
        'project_clients',
        'reminders',
        'tasks',
        'notebooks',
        'projects',
        'contacts',
        'clients'
    ]

    for table in tables:
        op.execute(f"""
            DO $$
            BEGIN
                -- Get all foreign key constraint names for the table
                FOR constraint_name IN (
                    SELECT conname
                    FROM pg_constraint
                    WHERE conrelid = 'public.{table}'::regclass
                    AND contype = 'f'
                )
                LOOP
                    EXECUTE 'ALTER TABLE public.{table} DROP CONSTRAINT IF EXISTS ' || constraint_name;
                END LOOP;
            END;
            $$;
        """)

    # Step 2: Drop all indexes (except primary key indexes)
    op.execute("""
        DO $$
        DECLARE
            idx record;
        BEGIN
            FOR idx IN (
                SELECT schemaname, tablename, indexname 
                FROM pg_indexes 
                WHERE schemaname = 'public'
                AND indexname NOT LIKE '%_pkey'
                AND (
                    indexname LIKE 'idx_%'
                    OR indexname LIKE 'uq_%'
                )
            )
            LOOP
                EXECUTE format('DROP INDEX IF EXISTS %I.%I', idx.schemaname, idx.indexname);
            END LOOP;
        END;
        $$;
    """)

    # Step 3: Drop the index creation helper function
    op.execute('DROP FUNCTION IF EXISTS create_index_if_not_exists(text, text, text, text)')

    # Step 4: Move tables back to vault schema in reverse order
    tables_reverse = [
        'contact_projects',
        'contact_clients',
        'project_clients',
        'reminders',
        'tasks',
        'notebooks',
        'projects',
        'contacts',
        'clients'
    ]

    # Create vault schema if it doesn't exist
    op.execute('CREATE SCHEMA IF NOT EXISTS vault')

    for table in tables_reverse:
        op.execute(f'ALTER TABLE IF EXISTS public.{table} SET SCHEMA vault')

    # Step 5: Recreate original foreign key constraints in vault schema
    # Note: These would need to be customized based on the original constraints
    # This is a basic example - you may need to add specific constraint names and options
    op.execute("""
        ALTER TABLE vault.clients 
        ADD CONSTRAINT clients_created_by_fkey 
        FOREIGN KEY (created_by) REFERENCES vault.users(id);
    """)
    op.execute("""
        ALTER TABLE vault.clients 
        ADD CONSTRAINT clients_modified_by_fkey 
        FOREIGN KEY (modified_by) REFERENCES vault.users(id);
    """)

    # Add similar constraints for other tables as needed
    # The specific constraints would depend on your original schema setup

    # Step 6: Clean up any remaining artifacts
    # This ensures no remnants of the public schema implementation remain
    op.execute("""
        DO $$
        BEGIN
            -- Drop any remaining indexes
            FOR indname IN (
                SELECT indexname 
                FROM pg_indexes 
                WHERE schemaname = 'public'
                AND tablename = ANY(ARRAY['clients', 'contacts', 'projects', 
                                        'notebooks', 'tasks', 'reminders', 
                                        'project_clients', 'contact_clients', 
                                        'contact_projects'])
            )
            LOOP
                EXECUTE 'DROP INDEX IF EXISTS public.' || indname;
            END LOOP;
        END;
        $$;
    """)
