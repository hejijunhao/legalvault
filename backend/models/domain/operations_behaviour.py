# /backend/models/domain/operations_behaviour.py

from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from core.database import get_supabase_client


class BehaviourOperationInput(BaseModel):
    ability_id: UUID
    behaviour_id: UUID


class BehaviourVPOperationInput(BaseModel):
    vp_id: UUID
    behaviour_id: UUID


class BehaviourOperationOutput(BaseModel):
    success: bool
    message: str
    behaviour_id: Optional[UUID] = None


@dataclass
class BehaviourOperations:
    @staticmethod
    async def apply_behaviour_to_ability(input_data: BehaviourOperationInput) -> BehaviourOperationOutput:
        """Apply a behaviour to an ability"""
        try:
            supabase = get_supabase_client()
            data = {
                'ability_id': str(input_data.ability_id),
                'behaviour_id': str(input_data.behaviour_id),
                'is_active': True
            }

            result = await supabase.table('ability_behaviours').insert(data).execute()

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

    @staticmethod
    async def remove_behaviour_from_ability(input_data: BehaviourOperationInput) -> BehaviourOperationOutput:
        """Remove a behaviour from an ability"""
        try:
            supabase = get_supabase_client()

            result = await supabase.table('ability_behaviours') \
                .delete() \
                .eq('ability_id', str(input_data.ability_id)) \
                .eq('behaviour_id', str(input_data.behaviour_id)) \
                .execute()

            return BehaviourOperationOutput(
                success=True,
                message="Behaviour successfully removed from ability",
                behaviour_id=input_data.behaviour_id
            )
        except Exception as e:
            return BehaviourOperationOutput(
                success=False,
                message=f"Failed to remove behaviour: {str(e)}"
            )

    @staticmethod
    async def toggle_behaviour_status(behaviour_id: UUID, status: str) -> BehaviourOperationOutput:
        """Toggle the status of a behaviour"""
        try:
            supabase = get_supabase_client()

            result = await supabase.table('behaviours') \
                .update({'status': status}) \
                .eq('id', str(behaviour_id)) \
                .execute()

            return BehaviourOperationOutput(
                success=True,
                message=f"Behaviour status successfully updated to {status}",
                behaviour_id=behaviour_id
            )
        except Exception as e:
            return BehaviourOperationOutput(
                success=False,
                message=f"Failed to update behaviour status: {str(e)}"
            )

    @staticmethod
    async def apply_behaviour_to_vp(input_data: BehaviourVPOperationInput) -> BehaviourOperationOutput:
        """Apply a behaviour to a VP"""
        try:
            supabase = get_supabase_client()
            data = {
                'vp_id': str(input_data.vp_id),
                'behaviour_id': str(input_data.behaviour_id),
                'is_active': True
            }

            result = await supabase.table('behaviour_vps').insert(data).execute()

            return BehaviourOperationOutput(
                success=True,
                message="Behaviour successfully applied to VP",
                behaviour_id=input_data.behaviour_id
            )
        except Exception as e:
            return BehaviourOperationOutput(
                success=False,
                message=f"Failed to apply behaviour: {str(e)}"
            )

    @staticmethod
    async def remove_behaviour_from_vp(input_data: BehaviourVPOperationInput) -> BehaviourOperationOutput:
        """Remove a behaviour from a VP"""
        try:
            supabase = get_supabase_client()

            result = await supabase.table('behaviour_vps') \
                .delete() \
                .eq('vp_id', str(input_data.vp_id)) \
                .eq('behaviour_id', str(input_data.behaviour_id)) \
                .execute()

            return BehaviourOperationOutput(
                success=True,
                message="Behaviour successfully removed from VP",
                behaviour_id=input_data.behaviour_id
            )
        except Exception as e:
            return BehaviourOperationOutput(
                success=False,
                message=f"Failed to remove behaviour: {str(e)}"
            )