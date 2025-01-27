# backend/scripts/initialize_taskmanagement_abilities.py
import os
import sys
from pathlib import Path
from sqlalchemy import select
from sqlalchemy import text
from typing import Optional
from sqlalchemy.orm import Session

# Add the project root to Python path
current_dir = Path(__file__).resolve()
project_root = str(current_dir.parent.parent.parent)
sys.path.append(project_root)

from core.database import get_session
from models.database.abilities.ability import Ability
from services.initializers.abilities.op_taskmanagement_initializer import TaskManagementInitializer


def test_database_connection() -> bool:
    """Test database connection and return connection status"""
    print("Testing database connection...")
    try:
        with get_session() as session:
            session.execute(text("SELECT 1"))
            print("Database connection successful!")
            return True
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        return False


def get_or_create_base_ability(session: Session) -> Optional[Ability]:
    """Get or create the base task management ability"""
    try:
        # Using modern select() syntax
        stmt = select(Ability).where(Ability.name == "task_management")
        base_ability = session.scalar(stmt)
        
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
        else:
            print(f"Found existing task management ability with id {base_ability.id}")

        return base_ability
    except Exception as e:
        print(f"Error getting/creating base ability: {str(e)}")
        session.rollback()
        return None


def initialize_task_management():
    """Initialize task management operations in database"""
    if not test_database_connection():
        raise Exception("Database connection test failed")

    try:
        with get_session() as session:
            print("Successfully got database session")

            # Get or create base ability
            base_ability = get_or_create_base_ability(session)
            if not base_ability:
                raise Exception("Failed to get or create base ability")

            # Initialize operations
            initializer = TaskManagementInitializer(session)
            operation_ids = initializer.initialize_operations(base_ability.id)

            print(f"Successfully initialized {len(operation_ids)} operations")
            for op_name, op_id in operation_ids.items():
                print(f"- {op_name}: {op_id}")

    except Exception as e:
        print(f"Error during initialization: {str(e)}")
        raise


def check_environment():
    """Check and validate environment variables"""
    required_vars = ['DATABASE_URL']
    missing_vars = [var for var in required_vars if var not in os.environ]

    if missing_vars:
        print("WARNING: Missing required environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        return False

    print("All required environment variables found")
    return True


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Check environment
    if not check_environment():
        sys.exit(1)

    # Run initialization
    try:
        initialize_task_management()
    except KeyboardInterrupt:
        print("\nInitialization interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nInitialization failed: {str(e)}")
        sys.exit(1)