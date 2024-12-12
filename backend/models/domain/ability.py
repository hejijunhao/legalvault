from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class AbilityCategory(Enum):
    COMMUNICATION = "communication"
    TASK_MANAGEMENT = "task_management"
    DOCUMENT_HANDLING = "document_handling"
    RESEARCH = "research"
    ANALYTICS = "analytics"


@dataclass
class AbilityNode:
    id: str
    name: str
    category: AbilityCategory
    level: int
    description: str
    prerequisites: List[str]  # List of node IDs required
    unlock_conditions: Dict[str, any]
    metadata: Dict[str, any]


class AbilityProgress:
    def __init__(self, paralegal_id: str):
        self.paralegal_id = paralegal_id
        self.unlocked_nodes: Dict[str, datetime] = {}
        self.progress: Dict[str, float] = {}  # Node ID -> completion percentage

    def unlock_node(self, node_id: str) -> bool:
        pass

    def get_available_nodes(self) -> List[str]:
        pass

    def calculate_progress(self, category: Optional[AbilityCategory] = None) -> float:
        pass


class AbilityManager:
    def __init__(self):
        self.nodes: Dict[str, AbilityNode] = {}

    def add_node(self, node: AbilityNode) -> None:
        self.nodes[node.id] = node

    def check_prerequisites(self, node_id: str, unlocked_nodes: List[str]) -> bool:
        if node_id not in self.nodes:
            return False
        return all(prereq in unlocked_nodes for prereq in self.nodes[node_id].prerequisites)

    def get_available_upgrades(self, progress: AbilityProgress) -> List[AbilityNode]:
        pass

    def get_category_progress(self, progress: AbilityProgress, category: AbilityCategory) -> float:
        pass