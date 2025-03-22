"""migrate_user_enterprise_paralegal_to_public_schema

Revision ID: 326b31d42696
Revises: db79c2138e02
Create Date: 2025-03-22 13:00:49.547457

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '326b31d42696'
down_revision: Union[str, None] = 'db79c2138e02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create new tables in public schema in dependency order
    op.create_table('enterprises',
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('domain', sa.String(), nullable=False),
        sa.Column('subscription_tier', sa.String(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_enterprises')),
        sa.UniqueConstraint('domain', name=op.f('uq_enterprises_domain')),
        schema='public'
    )
    op.create_index(op.f('ix_public_enterprises_name'), 'enterprises', ['name'], unique=False, schema='public')

    op.create_table('virtual_paralegals',
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('whatsapp', sa.String(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_virtual_paralegals')),
        sa.UniqueConstraint('email', name=op.f('uq_virtual_paralegals_email')),
        schema='public'
    )
    op.create_index(op.f('ix_public_virtual_paralegals_first_name'), 'virtual_paralegals', ['first_name'], unique=False, schema='public')
    op.create_index(op.f('ix_public_virtual_paralegals_last_name'), 'virtual_paralegals', ['last_name'], unique=False, schema='public')

    op.create_table('users',
        sa.Column('auth_user_id', sa.UUID(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('virtual_paralegal_id', sa.UUID(), nullable=True),
        sa.Column('enterprise_id', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['auth_user_id'], ['auth.users.id'], name=op.f('fk_users_auth_user_id_users')),
        sa.ForeignKeyConstraint(['enterprise_id'], ['public.enterprises.id'], name=op.f('fk_users_enterprise_id_enterprises')),
        sa.ForeignKeyConstraint(['virtual_paralegal_id'], ['public.virtual_paralegals.id'], name=op.f('fk_users_virtual_paralegal_id_virtual_paralegals')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
        schema='public'
    )
    op.create_index(op.f('ix_public_users_auth_user_id'), 'users', ['auth_user_id'], unique=True, schema='public')
    op.create_index(op.f('ix_public_users_email'), 'users', ['email'], unique=True, schema='public')
    op.create_index(op.f('ix_public_users_enterprise_id'), 'users', ['enterprise_id'], unique=False, schema='public')
    op.create_index(op.f('ix_public_users_virtual_paralegal_id'), 'users', ['virtual_paralegal_id'], unique=False, schema='public')

    op.create_table('public_searches',
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('tags', postgresql.JSONB(), nullable=True),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('enterprise_id', sa.UUID(), nullable=True),
        sa.Column('search_params', postgresql.JSONB(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['user_id'], ['public.users.id'], name=op.f('fk_public_searches_user_id_users')),
        sa.ForeignKeyConstraint(['enterprise_id'], ['public.enterprises.id'], name=op.f('fk_public_searches_enterprise_id_enterprises')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_public_searches')),
        schema='public'
    )
    op.create_index(op.f('ix_public_public_searches_user_id'), 'public_searches', ['user_id'], unique=False, schema='public')
    op.create_index(op.f('ix_public_public_searches_title'), 'public_searches', ['title'], unique=False, schema='public')
    op.create_index(op.f('ix_public_public_searches_is_featured'), 'public_searches', ['is_featured'], unique=False, schema='public')
    op.create_index('ix_public_searches_enterprise_user', 'public_searches', ['enterprise_id', 'user_id'], unique=False, schema='public')

    # Create enum type for query status if it doesn't exist
    op.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'query_status' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) THEN
            CREATE TYPE public.query_status AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED');
        END IF;
    END
    $$;
    """)

    # Create public_search_messages table using the existing enum type
    op.create_table('public_search_messages',
        sa.Column('search_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', postgresql.JSONB(), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False, server_default='0'),
        # Use postgresql.ENUM with create_type=False to reference existing enum
        sa.Column('status', postgresql.ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='query_status', create_type=False), nullable=False, server_default='PENDING'),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['search_id'], ['public.public_searches.id'], name=op.f('fk_public_search_messages_search_id_public_searches')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_public_search_messages')),
        schema='public'
    )
    op.create_index(op.f('ix_public_public_search_messages_search_id'), 'public_search_messages', ['search_id'], unique=False, schema='public')
    op.create_index(op.f('ix_public_public_search_messages_role'), 'public_search_messages', ['role'], unique=False, schema='public')
    op.create_index('ix_public_search_messages_search_sequence', 'public_search_messages', ['search_id', 'sequence'], unique=False, schema='public')

    # Migrate data from vault schema to public schema in dependency order
    op.execute("""
        INSERT INTO public.enterprises (id, name, domain, subscription_tier, created_at, updated_at)
        SELECT id, name, domain, subscription_tier, created_at, updated_at
        FROM vault.enterprises;
    """)
    op.execute("""
        INSERT INTO public.virtual_paralegals (id, first_name, last_name, email, phone, whatsapp, created_at, updated_at)
        SELECT id, first_name, last_name, email, phone, whatsapp, created_at, updated_at
        FROM vault.virtual_paralegals;
    """)
    op.execute("""
        INSERT INTO public.users (id, auth_user_id, first_name, last_name, name, email, role, virtual_paralegal_id, enterprise_id, created_at, updated_at)
        SELECT id, auth_user_id, first_name, last_name, name, email, role, virtual_paralegal_id, enterprise_id, created_at, updated_at
        FROM vault.users;
    """)
    op.execute("""
        INSERT INTO public.public_searches (
            id, title, description, is_featured, tags, user_id, enterprise_id, 
            search_params, created_at, updated_at
        )
        SELECT 
            id, title, NULL as description, FALSE as is_featured, 
            NULL as tags, user_id, NULL as enterprise_id, NULL as search_params, 
            created_at, updated_at
        FROM vault.public_searches;
    """)
    op.execute("""
        INSERT INTO public.public_search_messages (
            id, search_id, role, content, sequence, status, created_at, updated_at
        )
        SELECT 
            id, search_id, role, 
            jsonb_build_object('text', content) as content,
            0 as sequence, 'COMPLETED' as status,  -- No cast needed since it's now a string in migration
            created_at, updated_at
        FROM vault.public_search_messages;
    """)

    # Drop old tables from vault schema in reverse dependency order
    op.drop_table('public_search_messages', schema='vault')
    op.drop_table('public_searches', schema='vault')
    op.drop_table('users', schema='vault')
    op.drop_table('virtual_paralegals', schema='vault')
    op.drop_table('enterprises', schema='vault')


def downgrade() -> None:
    # Create tables in vault schema in dependency order
    op.create_table('enterprises',
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('domain', sa.String(), nullable=False),
        sa.Column('subscription_tier', sa.String(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_enterprises')),
        sa.UniqueConstraint('domain', name=op.f('uq_enterprises_domain')),
        schema='vault'
    )
    op.create_index(op.f('ix_vault_enterprises_name'), 'enterprises', ['name'], unique=False, schema='vault')

    op.create_table('virtual_paralegals',
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('whatsapp', sa.String(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_virtual_paralegals')),
        sa.UniqueConstraint('email', name=op.f('uq_virtual_paralegals_email')),
        schema='vault'
    )
    op.create_index(op.f('ix_vault_virtual_paralegals_first_name'), 'virtual_paralegals', ['first_name'], unique=False, schema='vault')
    op.create_index(op.f('ix_vault_virtual_paralegals_last_name'), 'virtual_paralegals', ['last_name'], unique=False, schema='vault')

    op.create_table('users',
        sa.Column('auth_user_id', sa.UUID(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('virtual_paralegal_id', sa.UUID(), nullable=True),
        sa.Column('enterprise_id', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['auth_user_id'], ['auth.users.id'], name=op.f('fk_users_auth_user_id_users')),
        sa.ForeignKeyConstraint(['enterprise_id'], ['vault.enterprises.id'], name=op.f('fk_users_enterprise_id_enterprises')),
        sa.ForeignKeyConstraint(['virtual_paralegal_id'], ['vault.virtual_paralegals.id'], name=op.f('fk_users_virtual_paralegal_id_virtual_paralegals')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
        schema='vault'
    )
    op.create_index(op.f('ix_vault_users_auth_user_id'), 'users', ['auth_user_id'], unique=True, schema='vault')
    op.create_index(op.f('ix_vault_users_email'), 'users', ['email'], unique=True, schema='vault')
    op.create_index(op.f('ix_vault_users_enterprise_id'), 'users', ['enterprise_id'], unique=False, schema='vault')
    op.create_index(op.f('ix_vault_users_virtual_paralegal_id'), 'users', ['virtual_paralegal_id'], unique=False, schema='vault')

    op.create_table('public_searches',
        sa.Column('query', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['vault.users.id'], name=op.f('fk_public_searches_user_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_public_searches')),
        schema='vault'
    )
    op.create_index(op.f('ix_vault_public_searches_user_id'), 'public_searches', ['user_id'], unique=False, schema='vault')

    op.create_table('public_search_messages',
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('search_id', sa.UUID(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['search_id'], ['vault.public_searches.id'], name=op.f('fk_public_search_messages_search_id_public_searches')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_public_search_messages')),
        schema='vault'
    )
    op.create_index(op.f('ix_vault_public_search_messages_search_id'), 'public_search_messages', ['search_id'], unique=False, schema='vault')

    # Migrate data back from public to vault schema
    op.execute("""
        INSERT INTO vault.enterprises (id, name, domain, subscription_tier, created_at, updated_at)
        SELECT id, name, domain, subscription_tier, created_at, updated_at
        FROM public.enterprises;
    """)
    op.execute("""
        INSERT INTO vault.virtual_paralegals (id, first_name, last_name, email, phone, whatsapp, created_at, updated_at)
        SELECT id, first_name, last_name, email, phone, whatsapp, created_at, updated_at
        FROM public.virtual_paralegals;
    """)
    op.execute("""
        INSERT INTO vault.users (id, auth_user_id, first_name, last_name, name, email, role, virtual_paralegal_id, enterprise_id, created_at, updated_at)
        SELECT id, auth_user_id, first_name, last_name, name, email, role, virtual_paralegal_id, enterprise_id, created_at, updated_at
        FROM public.users;
    """)
    op.execute("""
        INSERT INTO vault.public_searches (id, query, status, user_id, created_at, updated_at)
        SELECT id, title as query, 'COMPLETED' as status, user_id, created_at, updated_at
        FROM public.public_searches;
    """)
    op.execute("""
        INSERT INTO vault.public_search_messages (id, content, role, search_id, created_at, updated_at)
        SELECT id, content->>'text' as content, role, search_id, created_at, updated_at
        FROM public.public_search_messages;
    """)

    # Drop tables from public schema in reverse dependency order
    op.drop_table('public_search_messages', schema='public')
    op.drop_table('public_searches', schema='public')
    op.drop_table('users', schema='public')
    op.drop_table('virtual_paralegals', schema='public')
    op.drop_table('enterprises', schema='public')

    # Drop the enum type after dependent tables are gone
    op.execute("DROP TYPE IF EXISTS public.query_status")
