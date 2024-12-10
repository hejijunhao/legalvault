from uuid import UUID
from typing import List, Dict, Optional
from datetime import datetime


class AbilityManager:
    def check_prerequisites_met(self, paralegal_id: UUID, ability_id: UUID) -> bool:
        # Check if VP has all required prerequisite abilities
        pass

    def unlock_ability(self, paralegal_id: UUID, ability_id: UUID) -> bool:
        # Attempt to unlock an ability for a VP
        pass

    def get_available_abilities(self, paralegal_id: UUID) -> List[UUID]:
        # Get list of abilities that can be unlocked (prerequisites met)
        pass

    def get_tech_tree(self, paralegal_id: UUID) -> Dict:
        # Return complete tech tree with unlocked/available status
        pass

    def get_tier_progress(self, paralegal_id: UUID, tier: int) -> Dict:
        # Get progress within a specific tier
        pass

    def suggest_next_abilities(self, paralegal_id: UUID) -> List[Dict]:
        # Suggest next abilities to unlock based on current abilities
        pass

    def get_ability_path(self, target_ability_id: UUID) -> List[UUID]:
        # Get the shortest path to unlock a specific ability
        pass

    def calculate_unlock_cost(self, ability_id: UUID, paralegal_id: UUID) -> int:
        # Calculate cost considering various factors (promotions, etc.)
        pass