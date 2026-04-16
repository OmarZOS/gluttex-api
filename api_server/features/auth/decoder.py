# app/auth.py
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional
from fastapi import Depends,  status
from sqlalchemy.orm import Session
from core.messages import *
from core.exception_handler import APIException
from constants import ALGORITHM, SECRET_KEY
from features.app.user.user_fetch import fetch_user_by_name

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = APIException(
        
        status=status.HTTP_401_UNAUTHORIZED,
        message="Could not validate credentials",
        # headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username == "":
            credentials_exception.detail = "invalid token"
            raise credentials_exception
    except JWTError:
        credentials_exception.code = AUTH_DECODE_FAILED
        credentials_exception.detail = "error decoding token"
        raise credentials_exception
    expiry: datetime = payload.get("exp")
    if expiry is None or expiry < datetime.now():
        credentials_exception.code = AUTH_UNAUTHORIZED
        credentials_exception.detail = "token expired"
        raise credentials_exception
    return True