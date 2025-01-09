# /backend/services/workflow/behaviour_workflow.py

from typing import List, Optional
from uuid import UUID
from models.domain.behaviour import BehaviourDomain
from models.schemas.behaviour import BehaviourCreate, BehaviourUpdate
from core.database import get_supabase_client


class BehaviourWorkflow:
    def __init__(self):
        self.supabase = get_supabase_client()

    async def get_behaviour(self, behaviour_id: UUID) -> Optional[BehaviourDomain]:
        """Get a specific behaviour from Supabase"""
        try:
            result = await self.supabase.table('behaviours') \
                .select('*') \
                .eq('id', str(behaviour_id)) \
                .single() \
                .execute()

            if result.data:
                return BehaviourDomain.from_db(result.data)
            return None
        except Exception as e:
            print(f"Error fetching behaviour: {e}")
            return None

    async def list_behaviours(self, status: str = None) -> List[BehaviourDomain]:
        """List behaviours from Supabase with optional status filter"""
        try:
            query = self.supabase.table('behaviours').select('*')
            if status:
                query = query.eq('status', status)

            result = await query.execute()
            return [BehaviourDomain.from_db(item) for item in result.data]
        except Exception as e:
            print(f"Error listing behaviours: {e}")
            return []

    async def get_ability_behaviours(self, ability_id: UUID) -> List[BehaviourDomain]:
        """Get all behaviours associated with an ability"""
        try:
            result = await self.supabase.table('ability_behaviours') \
                .select('behaviours!inner(*)') \
                .eq('ability_id', str(ability_id)) \
                .eq('is_active', True) \
                .execute()

            return [BehaviourDomain.from_db(item['behaviours']) for item in result.data]
        except Exception as e:
            print(f"Error fetching ability behaviours: {e}")
            return []
