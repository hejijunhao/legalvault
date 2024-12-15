# backend/scripts/initialize_taskmanagement_abilities.py
import os
import sys
import asyncio
from pathlib import Path
from sqlalchemy import select
from sqlalchemy import text

# Add the project root to Python path
current_dir = Path(__file__).resolve()
project_root = str(current_dir.parent.parent.parent)
sys.path.append(project_root)

from backend.core.database import get_session
from backend.models.database.ability import Ability
from backend.services.initializers.op_taskmanagement_initializer import TaskManagementInitializer


async def initialize_task_management():
    """Simple test of database connection"""
    print("Testing database connection...")
    session_generator = get_session()
    async for session in session_generator:
        try:
            # Test query using text()
            result = await session.execute(text("SELECT 1"))
            print("Database connection successful!")
            await session.close()
            break
        except Exception as e:
            print(f"Database connection failed: {str(e)}")
            raise

    """Initialize task management operations in database"""
    try:
        session_generator = get_session()
        async for session in session_generator:
            try:
                print("Successfully got database session")

                # First ensure base ability exists
                stmt = select(Ability).where(Ability.name == "task_management")
                print("Executing query...")
                result = await session.execute(stmt)
                base_ability = result.scalar_one_or_none()

                if not base_ability:
                    base_ability = Ability(
                        name="task_management",
                        description="Manages tasks and todo items",
                        version="1.0.0",
                        enabled=True
                    )
                    session.add(base_ability)
                    await session.commit()
                    print(f"Created base task management ability with id {base_ability.id}")
                else:
                    print(f"Found existing task management ability with id {base_ability.id}")

                # Initialize operations
                initializer = TaskManagementInitializer(session)
                operation_ids = await initializer.initialize_operations(base_ability.id)
                print(f"Successfully initialized {len(operation_ids)} operations")
                for op_name, op_id in operation_ids.items():
                    print(f"- {op_name}: {op_id}")

            except Exception as e:
                print(f"Error during initialization: {str(e)}")
                await session.rollback()
                raise
            finally:
                await session.close()
    except Exception as e:
        print(f"Error setting up session: {str(e)}")
        raise


if __name__ == "__main__":
    # Ensure environment variables are loaded
    from dotenv import load_dotenv

    load_dotenv()

    # Print environment check
    if 'DATABASE_URL' in os.environ:
        print("Found DATABASE_URL in environment")
    else:
        print("WARNING: DATABASE_URL not found in environment!")

    asyncio.run(initialize_task_management())