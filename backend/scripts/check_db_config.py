# scripts/check_db_config.py
import os
from urllib.parse import urlparse
from dotenv import load_dotenv


def check_database_url():
    """Validate DATABASE_URL format and configuration"""
    load_dotenv()

    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL not found in environment variables")
        return False

    try:
        parsed = urlparse(db_url)

        # Check URL structure
        if not all([parsed.scheme, parsed.hostname, parsed.path]):
            print("ERROR: Invalid DATABASE_URL structure")
            return False

        # Print configuration (without password)
        print(f"Database Configuration:")
        print(f"- Scheme: {parsed.scheme}")
        print(f"- Host: {parsed.hostname}")
        print(f"- Port: {parsed.port or 'default'}")
        print(f"- Database: {parsed.path[1:]}")  # Remove leading '/'
        print(f"- Username: {parsed.username}")
        print(f"- SSL Required: {'sslmode' in db_url}")

        return True

    except Exception as e:
        print(f"ERROR parsing DATABASE_URL: {str(e)}")
        return False


if __name__ == "__main__":
    check_database_url()