# core/auth.py

from typing import List
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models.database.auth_user import AuthUser
from models.database.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    # Example: Decode token, fetch AuthUser, then return related vault.user
    auth_user = db.query(AuthUser).filter(AuthUser.email == "decoded_email@example.com").first()
    if auth_user and auth_user.vault_user:
        return auth_user.vault_user
    raise HTTPException(status_code=401, detail="Invalid credentials")

async def get_user_permissions(token: str = Depends(oauth2_scheme)) -> List[str]:
    # Placeholder for your permission logic
    pass