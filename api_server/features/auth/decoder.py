# app/auth.py
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from constants import ALGORITHM, SECRET_KEY
from features.user.user_fetch import fetch_user_by_name

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username == "":
            credentials_exception.detail = "invalid token"
            raise credentials_exception
    except JWTError:
        credentials_exception.detail = "error decoding token"
        raise credentials_exception
    expiry: datetime = payload.get("exp")
    if expiry is None or expiry < datetime.now():
        credentials_exception.detail = "token expired"
        raise credentials_exception
    return True