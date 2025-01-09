# /backend/services/executors/behaviour_executor.py

from uuid import UUID
from models.domain.operations_behaviour import BehaviourOperationInput, BehaviourOperationOutput
from models.database.behaviour import Behaviour, AbilityBehaviour
from core.database import get_supabase_client


class BehaviourExecutor:
    def __init__(self):
        self.supabase = get_supabase_client()

    async def apply_behaviour(self, input_data: BehaviourOperationInput) -> BehaviourOperationOutput:
        """Apply a behaviour to an ability"""
        try:
            data = {
                'ability_id': str(input_data.ability_id),
                'behaviour_id': str(input_data.behaviour_id),
                'is_active': True
            }

            result = await self.supabase.table('ability_behaviours').insert(data).execute()

            return BehaviourOperationOutput(
                success=True,
                message="Behaviour successfully applied to ability",
                behaviour_id=input_data.behaviour_id
            )
        except Exception as e:
            return BehaviourOperationOutput(
                success=False,
                message=f"Failed to apply behaviour: {str(e)}"
            )

