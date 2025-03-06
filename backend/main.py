# backend/main.py

from fastapi import FastAPI, Depends, HTTPException
import psycopg2
from dotenv import load_dotenv
import os
from logging import getLogger
from typing import List
from core.database import get_session

from api.routes import router as api_router

logger = getLogger(__name__)
app = FastAPI()

app.include_router(api_router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Load environment variables from .env
load_dotenv()

# Connect to the database
try:
    # Use the DATABASE_URL environment variable
    DATABASE_URL = os.getenv("DATABASE_URL")
    # Connect with GSSAPI disabled to avoid authentication errors
    connection = psycopg2.connect(
        DATABASE_URL,
        sslmode='require',
        gssencmode='disable'
    )
    print("Connection successful!")
    
    # Create a cursor to execute SQL queries
    cursor = connection.cursor()
    
    # Example query
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print("Current Time:", result)

    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("Connection closed.")

except Exception as e:
    print(f"Failed to connect: {e}")


# Error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {"detail": str(exc.detail), "status_code": exc.status_code}

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return {"detail": "Internal server error", "status_code": 500}
