"""add_explicit_public_schema_to_longterm_memory_tables

Revision ID: bebb531075b6
Revises: 9e84d2be44d1
Create Date: 2025-01-30 10:36:58.585612

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bebb531075b6'
down_revision: Union[str, None] = '9e84d2be44d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Set search path to handle schemas explicitly
    op.execute('SET search_path TO public, vault')

    # --- 1. SelfIdentity table ---
    op.execute("""
        DO $$
        BEGIN
            -- Ensure table is in public schema
            IF EXISTS (
                SELECT 1
                FROM information_schema.tables 
                WHERE table_schema = CURRENT_SCHEMA()
                AND table_name = 'longterm_memory_self_identity'
            ) THEN
                ALTER TABLE IF EXISTS longterm_memory_self_identity SET SCHEMA public;
            END IF;

            -- Update foreign key to reference vault schema
            ALTER TABLE IF EXISTS public.longterm_memory_self_identity 
            DROP CONSTRAINT IF EXISTS longterm_memory_self_identity_vp_id_fkey,
            ADD CONSTRAINT longterm_memory_self_identity_vp_id_fkey 
            FOREIGN KEY (vp_id) REFERENCES vault.virtual_paralegals(id);
        END $$;
    """)

    # --- 2. GlobalKnowledge table ---
    op.execute("""
        DO $$
        BEGIN
            -- Ensure table is in public schema
            IF EXISTS (
                SELECT 1
                FROM information_schema.tables 
                WHERE table_schema = CURRENT_SCHEMA()
                AND table_name = 'longterm_memory_global_knowledge'
            ) THEN
                ALTER TABLE IF EXISTS longterm_memory_global_knowledge SET SCHEMA public;
            END IF;

            -- Update foreign key to reference vault schema
            ALTER TABLE IF EXISTS public.longterm_memory_global_knowledge 
            DROP CONSTRAINT IF EXISTS longterm_memory_global_knowledge_vp_id_fkey,
            ADD CONSTRAINT longterm_memory_global_knowledge_vp_id_fkey 
            FOREIGN KEY (vp_id) REFERENCES vault.virtual_paralegals(id);
        END $$;
    """)

    # --- 3. EducationalKnowledge table ---
    op.execute("""
        DO $$
        BEGIN
            -- Ensure table is in public schema
            IF EXISTS (
                SELECT 1
                FROM information_schema.tables 
                WHERE table_schema = CURRENT_SCHEMA()
                AND table_name = 'longterm_memory_educational_knowledge'
            ) THEN
                ALTER TABLE IF EXISTS longterm_memory_educational_knowledge SET SCHEMA public;
            END IF;

            -- Update foreign key to reference vault schema
            ALTER TABLE IF EXISTS public.longterm_memory_educational_knowledge 
            DROP CONSTRAINT IF EXISTS longterm_memory_educational_knowledge_vp_id_fkey,
            ADD CONSTRAINT longterm_memory_educational_knowledge_vp_id_fkey 
            FOREIGN KEY (vp_id) REFERENCES vault.virtual_paralegals(id);
        END $$;
    """)

    # --- 4. ActionsHistory table ---
    op.execute("""
        DO $$
        BEGIN
            -- Ensure table is in public schema
            IF EXISTS (
                SELECT 1
                FROM information_schema.tables 
                WHERE table_schema = CURRENT_SCHEMA()
                AND table_name = 'longterm_memory_actions_history'
            ) THEN
                ALTER TABLE IF EXISTS longterm_memory_actions_history SET SCHEMA public;
            END IF;

            -- Update foreign key to reference vault schema
            ALTER TABLE IF EXISTS public.longterm_memory_actions_history 
            DROP CONSTRAINT IF EXISTS longterm_memory_actions_history_vp_id_fkey,
            ADD CONSTRAINT longterm_memory_actions_history_vp_id_fkey 
            FOREIGN KEY (vp_id) REFERENCES vault.virtual_paralegals(id);
        END $$;
    """)

    # --- 5. ConversationalHistory table ---
    op.execute("""
        DO $$
        BEGIN
            -- Ensure table is in public schema
            IF EXISTS (
                SELECT 1
                FROM information_schema.tables 
                WHERE table_schema = CURRENT_SCHEMA()
                AND table_name = 'longterm_memory_conversational_history'
            ) THEN
                ALTER TABLE IF EXISTS longterm_memory_conversational_history SET SCHEMA public;
            END IF;

            -- Update foreign key to reference vault schema
            ALTER TABLE IF EXISTS public.longterm_memory_conversational_history 
            DROP CONSTRAINT IF EXISTS longterm_memory_conversational_history_vp_id_fkey,
            ADD CONSTRAINT longterm_memory_conversational_history_vp_id_fkey 
            FOREIGN KEY (vp_id) REFERENCES vault.virtual_paralegals(id);
        END $$;
    """)


def downgrade() -> None:
    """
    Downgrade operations if needed:
    - Revert FK constraints to non-schema-qualified references
    - Tables can remain in public schema as that's our new standard
    """
    op.execute('SET search_path TO public, vault')

    # Revert FK constraints to non-schema-qualified references for SelfIdentity
    op.execute("""
        ALTER TABLE IF EXISTS public.longterm_memory_self_identity
        DROP CONSTRAINT IF EXISTS longterm_memory_self_identity_vp_id_fkey,
        ADD CONSTRAINT longterm_memory_self_identity_vp_id_fkey 
        FOREIGN KEY (vp_id) REFERENCES virtual_paralegals(id);
    """)

    # Revert FK constraints to non-schema-qualified references for GlobalKnowledge
    op.execute("""
        ALTER TABLE IF EXISTS public.longterm_memory_global_knowledge
        DROP CONSTRAINT IF EXISTS longterm_memory_global_knowledge_vp_id_fkey,
        ADD CONSTRAINT longterm_memory_global_knowledge_vp_id_fkey 
        FOREIGN KEY (vp_id) REFERENCES virtual_paralegals(id);
    """)

    # Revert FK constraints to non-schema-qualified references for EducationalKnowledge
    op.execute("""
        ALTER TABLE IF EXISTS public.longterm_memory_educational_knowledge
        DROP CONSTRAINT IF EXISTS longterm_memory_educational_knowledge_vp_id_fkey,
        ADD CONSTRAINT longterm_memory_educational_knowledge_vp_id_fkey 
        FOREIGN KEY (vp_id) REFERENCES virtual_paralegals(id);
    """)

    # Revert FK constraints to non-schema-qualified references for ActionsHistory
    op.execute("""
        ALTER TABLE IF EXISTS public.longterm_memory_actions_history
        DROP CONSTRAINT IF EXISTS longterm_memory_actions_history_vp_id_fkey,
        ADD CONSTRAINT longterm_memory_actions_history_vp_id_fkey 
        FOREIGN KEY (vp_id) REFERENCES virtual_paralegals(id);
    """)

    # Revert FK constraints to non-schema-qualified references for ConversationalHistory
    op.execute("""
        ALTER TABLE IF EXISTS public.longterm_memory_conversational_history
        DROP CONSTRAINT IF EXISTS longterm_memory_conversational_history_vp_id_fkey,
        ADD CONSTRAINT longterm_memory_conversational_history_vp_id_fkey 
        FOREIGN KEY (vp_id) REFERENCES virtual_paralegals(id);
    """)