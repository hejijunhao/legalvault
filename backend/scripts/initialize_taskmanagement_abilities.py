# backend/scripts/initialize_taskmanagement_abilities.py
import sys
import os
from pathlib import Path

# Add root to Python path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from sqlmodel import Session, create_engine
from core.database import get_database_url
from models.database.ability import Ability
from services.initializers.op_taskmanagement_initializer import TaskManagementInitializer


def initialize_task_management():
    """Initialize task management operations in database"""
    engine = create_engine(get_database_url())

    with Session(engine) as session:
        # First ensure base ability exists
        base_ability = session.query(Ability).filter_by(
            name="task_management"
        ).first()

        if not base_ability:
            base_ability = Ability(
                name="task_management",
                description="Manages tasks and todo items",
                version="1.0.0",
                enabled=True
            )
            session.add(base_ability)
            session.commit()
            print(f"Created base task management ability with id {base_ability.id}")

        # Initialize operations
        initializer = TaskManagementInitializer(session)
        try:
            operation_ids = initializer.initialize_operations(base_ability.id)
            print(f"Successfully initialized {len(operation_ids)} operations")
            for op_name, op_id in operation_ids.items():
                print(f"- {op_name}: {op_id}")
        except Exception as e:
            print(f"Error initializing operations: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    initialize_task_management()