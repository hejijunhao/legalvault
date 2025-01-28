"""move_models_to_vault_schema

Revision ID: b56ef52335fa
Revises: 97e65b9746e3
Create Date: 2025-01-28 19:38:22.701034
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b56ef52335fa'
down_revision: Union[str, None] = '97e65b9746e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Move tables to vault schema (order matters for FK constraints)

    # 1. Independent tables first
    op.execute('ALTER TABLE public.vp_profile_pictures SET SCHEMA vault')
    op.execute('ALTER TABLE public.abilities SET SCHEMA vault')
    op.execute('ALTER TABLE public.behaviours SET SCHEMA vault')
    op.execute('ALTER TABLE public.integrations SET SCHEMA vault')

    # 2. Tables with dependencies
    op.execute('ALTER TABLE public.virtual_paralegals SET SCHEMA vault')
    op.execute('ALTER TABLE public.users SET SCHEMA vault')
    op.execute('ALTER TABLE public.task_management_abilities SET SCHEMA vault')
    op.execute('ALTER TABLE public.ability_receive_email SET SCHEMA vault')
    op.execute('ALTER TABLE public.credentials SET SCHEMA vault')
    op.execute('ALTER TABLE public.integration_abilities SET SCHEMA vault')
    op.execute('ALTER TABLE public.ability_behaviours SET SCHEMA vault')
    op.execute('ALTER TABLE public.behaviour_vps SET SCHEMA vault')

    # Update foreign key constraints

    # Users -> VirtualParalegals
    op.execute('''
        ALTER TABLE vault.users
        DROP CONSTRAINT IF EXISTS users_paralegal_id_fkey,
        ADD CONSTRAINT users_paralegal_id_fkey 
        FOREIGN KEY (paralegal_id) REFERENCES vault.virtual_paralegals(id)
    ''')

    # VirtualParalegals -> Users (owner_id)
    op.execute('''
        ALTER TABLE vault.virtual_paralegals
        DROP CONSTRAINT IF EXISTS virtual_paralegals_owner_id_fkey,
        ADD CONSTRAINT virtual_paralegals_owner_id_fkey 
        FOREIGN KEY (owner_id) REFERENCES vault.users(id)
    ''')

    # VirtualParalegals -> ProfilePictures
    op.execute('''
        ALTER TABLE vault.virtual_paralegals
        DROP CONSTRAINT IF EXISTS virtual_paralegals_profile_picture_id_fkey,
        ADD CONSTRAINT virtual_paralegals_profile_picture_id_fkey 
        FOREIGN KEY (profile_picture_id) REFERENCES vault.vp_profile_pictures(id)
    ''')

    # TaskManagementAbility -> Abilities
    op.execute('''
        ALTER TABLE vault.task_management_abilities
        DROP CONSTRAINT IF EXISTS task_management_abilities_ability_id_fkey,
        ADD CONSTRAINT task_management_abilities_ability_id_fkey 
        FOREIGN KEY (ability_id) REFERENCES vault.abilities(id)
    ''')

    # ReceiveEmailAbility -> Abilities
    op.execute('''
        ALTER TABLE vault.ability_receive_email
        DROP CONSTRAINT IF EXISTS ability_receive_email_ability_id_fkey,
        ADD CONSTRAINT ability_receive_email_ability_id_fkey 
        FOREIGN KEY (ability_id) REFERENCES vault.abilities(id)
    ''')

    # Credentials -> Users and Integrations
    op.execute('''
        ALTER TABLE vault.credentials
        DROP CONSTRAINT IF EXISTS credentials_user_id_fkey,
        ADD CONSTRAINT credentials_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES vault.users(id)
    ''')

    op.execute('''
        ALTER TABLE vault.credentials
        DROP CONSTRAINT IF EXISTS credentials_integration_id_fkey,
        ADD CONSTRAINT credentials_integration_id_fkey 
        FOREIGN KEY (integration_id) REFERENCES vault.integrations(integration_id)
    ''')

    # IntegrationAbilities -> Integrations and Abilities
    op.execute('''
        ALTER TABLE vault.integration_abilities
        DROP CONSTRAINT IF EXISTS integration_abilities_integration_id_fkey,
        ADD CONSTRAINT integration_abilities_integration_id_fkey 
        FOREIGN KEY (integration_id) REFERENCES vault.integrations(integration_id)
    ''')

    op.execute('''
        ALTER TABLE vault.integration_abilities
        DROP CONSTRAINT IF EXISTS integration_abilities_ability_id_fkey,
        ADD CONSTRAINT integration_abilities_ability_id_fkey 
        FOREIGN KEY (ability_id) REFERENCES vault.abilities(id)
    ''')

    # AbilityBehaviours -> Abilities and Behaviours
    op.execute('''
        ALTER TABLE vault.ability_behaviours
        DROP CONSTRAINT IF EXISTS ability_behaviours_ability_id_fkey,
        ADD CONSTRAINT ability_behaviours_ability_id_fkey 
        FOREIGN KEY (ability_id) REFERENCES vault.abilities(id)
    ''')

    op.execute('''
        ALTER TABLE vault.ability_behaviours
        DROP CONSTRAINT IF EXISTS ability_behaviours_behaviour_id_fkey,
        ADD CONSTRAINT ability_behaviours_behaviour_id_fkey 
        FOREIGN KEY (behaviour_id) REFERENCES vault.behaviours(id)
    ''')

    # BehaviourVPs -> VirtualParalegals and Behaviours
    op.execute('''
        ALTER TABLE vault.behaviour_vps
        DROP CONSTRAINT IF EXISTS behaviour_vps_vp_id_fkey,
        ADD CONSTRAINT behaviour_vps_vp_id_fkey 
        FOREIGN KEY (vp_id) REFERENCES vault.virtual_paralegals(id)
    ''')

    op.execute('''
        ALTER TABLE vault.behaviour_vps
        DROP CONSTRAINT IF EXISTS behaviour_vps_behaviour_id_fkey,
        ADD CONSTRAINT behaviour_vps_behaviour_id_fkey 
        FOREIGN KEY (behaviour_id) REFERENCES vault.behaviours(id)
    ''')

def downgrade() -> None:
    # Revert foreign key constraints (reverse order)

    # BehaviourVPs
    op.execute('''
        ALTER TABLE vault.behaviour_vps
        DROP CONSTRAINT IF EXISTS behaviour_vps_behaviour_id_fkey,
        ADD CONSTRAINT behaviour_vps_behaviour_id_fkey 
        FOREIGN KEY (behaviour_id) REFERENCES public.behaviours(id)
    ''')

    op.execute('''
        ALTER TABLE vault.behaviour_vps
        DROP CONSTRAINT IF EXISTS behaviour_vps_vp_id_fkey,
        ADD CONSTRAINT behaviour_vps_vp_id_fkey 
        FOREIGN KEY (vp_id) REFERENCES public.virtual_paralegals(id)
    ''')

    # AbilityBehaviours
    op.execute('''
        ALTER TABLE vault.ability_behaviours
        DROP CONSTRAINT IF EXISTS ability_behaviours_behaviour_id_fkey,
        ADD CONSTRAINT ability_behaviours_behaviour_id_fkey 
        FOREIGN KEY (behaviour_id) REFERENCES public.behaviours(id)
    ''')

    op.execute('''
        ALTER TABLE vault.ability_behaviours
        DROP CONSTRAINT IF EXISTS ability_behaviours_ability_id_fkey,
        ADD CONSTRAINT ability_behaviours_ability_id_fkey 
        FOREIGN KEY (ability_id) REFERENCES public.abilities(id)
    ''')

    # IntegrationAbilities
    op.execute('''
        ALTER TABLE vault.integration_abilities
        DROP CONSTRAINT IF EXISTS integration_abilities_ability_id_fkey,
        ADD CONSTRAINT integration_abilities_ability_id_fkey 
        FOREIGN KEY (ability_id) REFERENCES public.abilities(id)
    ''')

    op.execute('''
        ALTER TABLE vault.integration_abilities
        DROP CONSTRAINT IF EXISTS integration_abilities_integration_id_fkey,
        ADD CONSTRAINT integration_abilities_integration_id_fkey 
        FOREIGN KEY (integration_id) REFERENCES public.integrations(integration_id)
    ''')

    # Credentials
    op.execute('''
        ALTER TABLE vault.credentials
        DROP CONSTRAINT IF EXISTS credentials_integration_id_fkey,
        ADD CONSTRAINT credentials_integration_id_fkey 
        FOREIGN KEY (integration_id) REFERENCES public.integrations(integration_id)
    ''')

    op.execute('''
        ALTER TABLE vault.credentials
        DROP CONSTRAINT IF EXISTS credentials_user_id_fkey,
        ADD CONSTRAINT credentials_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES public.users(id)
    ''')

    # ReceiveEmailAbility
    op.execute('''
        ALTER TABLE vault.ability_receive_email
        DROP CONSTRAINT IF EXISTS ability_receive_email_ability_id_fkey,
        ADD CONSTRAINT ability_receive_email_ability_id_fkey 
        FOREIGN KEY (ability_id) REFERENCES public.abilities(id)
    ''')

    # TaskManagementAbility
    op.execute('''
        ALTER TABLE vault.task_management_abilities
        DROP CONSTRAINT IF EXISTS task_management_abilities_ability_id_fkey,
        ADD CONSTRAINT task_management_abilities_ability_id_fkey 
        FOREIGN KEY (ability_id) REFERENCES public.abilities(id)
    ''')

    # VirtualParalegals
    op.execute('''
        ALTER TABLE vault.virtual_paralegals
        DROP CONSTRAINT IF EXISTS virtual_paralegals_profile_picture_id_fkey,
        ADD CONSTRAINT virtual_paralegals_profile_picture_id_fkey 
        FOREIGN KEY (profile_picture_id) REFERENCES public.vp_profile_pictures(id)
    ''')

    op.execute('''
        ALTER TABLE vault.virtual_paralegals
        DROP CONSTRAINT IF EXISTS virtual_paralegals_owner_id_fkey,
        ADD CONSTRAINT virtual_paralegals_owner_id_fkey 
        FOREIGN KEY (owner_id) REFERENCES public.users(id)
    ''')

    # Users
    op.execute('''
        ALTER TABLE vault.users
        DROP CONSTRAINT IF EXISTS users_paralegal_id_fkey,
        ADD CONSTRAINT users_paralegal_id_fkey 
        FOREIGN KEY (paralegal_id) REFERENCES public.virtual_paralegals(id)
    ''')

    # Move tables back to public schema (reverse order of dependencies)
    op.execute('ALTER TABLE vault.behaviour_vps SET SCHEMA public')
    op.execute('ALTER TABLE vault.ability_behaviours SET SCHEMA public')
    op.execute('ALTER TABLE vault.integration_abilities SET SCHEMA public')
    op.execute('ALTER TABLE vault.credentials SET SCHEMA public')
    op.execute('ALTER TABLE vault.ability_receive_email SET SCHEMA public')
    op.execute('ALTER TABLE vault.task_management_abilities SET SCHEMA public')
    op.execute('ALTER TABLE vault.users SET SCHEMA public')
    op.execute('ALTER TABLE vault.virtual_paralegals SET SCHEMA public')
    op.execute('ALTER TABLE vault.integrations SET SCHEMA public')
    op.execute('ALTER TABLE vault.behaviours SET SCHEMA public')
    op.execute('ALTER TABLE vault.abilities SET SCHEMA public')
    op.execute('ALTER TABLE vault.vp_profile_pictures SET SCHEMA public')