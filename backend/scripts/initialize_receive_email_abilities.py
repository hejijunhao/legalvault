# backend/scripts/initialize_receive_email_abilities.py
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
    async with get_session() as session:
        try:
            await session.execute(text("SELECT 1"))
            print("Database connection successful!")
            return True
        except Exception as e:
            print(f"Database connection failed: {str(e)}")
            return False

async def initialize_receive_email():
    if not await test_database_connection():
        raise Exception("Database connection test failed")

    async with get_session() as session:
        try:
            print("Successfully got database session")
            stmt = text("SELECT * FROM abilities WHERE name = 'receive_email'")
            result = await session.execute(stmt)
            base_ability = result.first()

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
                print(f"Found existing receive_email ability")

            await session.commit()

        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            await session.rollback()
            raise

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