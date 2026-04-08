from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from .config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from .repositories import verify_user, get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(user_id: int, email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "email": email, "exp": expire}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_token(token)
    user_id = int(payload.get("sub"))
    email = payload.get("email")
    user = get_user_by_email(email)
    if not user or user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


def authenticate_user(email: str, password: str) -> Optional[dict]:
    return verify_user(email, password)

