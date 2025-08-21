# app/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime



class API_Resolution(BaseModel):
    status: int
    error_code: str
    message: str

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
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
    # this is the most important id to get the user from the database
    app_user_id: int
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    hashed_password: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
    app_user_id: str

class TokenData(BaseModel):
    username: Optional[str] 

class User(BaseModel):
    username: str
    email: Optional[str] 
    full_name: Optional[str] 
    disabled: Optional[bool] 


class UserUpdate(UserBase):
    new_username: Optional[str] 
    app_user_id: int
    new_password: str