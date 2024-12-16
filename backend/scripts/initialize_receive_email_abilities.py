import os
import sys
import asyncio
from pathlib import Path
from sqlalchemy import text
from typing import Optional

# Add project root to path
current_dir = Path(__file__).resolve()
project_root = str(current_dir.parent.parent.parent)
sys.path.append(project_root)

from backend.core.database import get_session
from backend.models.database.ability import Ability
from backend.services.initializers.op_receive_email_initializer import ReceiveEmailInitializer

async def test_database_connection() -> bool:
    print("Testing database connection...")
    async for session in get_session():
        try:
            await session.execute(text("SELECT 1"))
            print("Database connection successful!")
            await session.close()
            return True
        except Exception as e:
            print(f"Database connection failed: {str(e)}")
            return False

async def get_or_create_base_ability(session) -> Optional[Ability]:
    from sqlalchemy import select
    try:
        stmt = select(Ability).where(Ability.name == "receive_email")
        result = await session.execute(stmt)
        base_ability = result.scalar_one_or_none()

        if not base_ability:
            base_ability = Ability(
                name="receive_email",
                description="Handles inbound emails and routes them for processing",
                version="1.0.0",
                enabled=True
            )
            session.add(base_ability)
            await session.commit()
            print(f"Created base receive_email ability with id {base_ability.id}")
        else:
            print(f"Found existing receive_email ability with id {base_ability.id}")

        return base_ability
    except Exception as e:
        print(f"Error getting/creating base ability: {str(e)}")
        await session.rollback()
        return None

async def initialize_receive_email():
    if not await test_database_connection():
        raise Exception("Database connection test failed")

    async for session in get_session():
        try:
            print("Successfully got database session")
            base_ability = await get_or_create_base_ability(session)
            if not base_ability:
                raise Exception("Failed to get or create base ability")

            initializer = ReceiveEmailInitializer(session)
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

def check_environment():
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
    from dotenv import load_dotenv
    load_dotenv()

    if not check_environment():
        sys.exit(1)

    try:
        asyncio.run(initialize_receive_email())
    except KeyboardInterrupt:
        print("\nInitialization interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nInitialization failed: {str(e)}")
        sys.exit(1)
