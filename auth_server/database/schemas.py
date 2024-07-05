# app/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number : Optional[str] = None
    date_of_birth : Optional[datetime] = None
    gender : Optional[str] = None
    profile_picture : Optional[str] = None
    roles : Optional[str] = None
    last_login : Optional[datetime] = None
    login_count : Optional[str] = None
    failed_login_attempts : Optional[str] = None
    account_locked : Optional[bool] = False
    mfa_enabled : Optional[bool] = False

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] 

class User(BaseModel):
    username: str
    email: Optional[str] 
    full_name: Optional[str] 
    disabled: Optional[bool] 

class UserInDB(User):
    hashed_password: str

class UserUpdate(UserBase):
    new_username: Optional[str] 
    new_password: str