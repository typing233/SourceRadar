from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserTagsUpdate(BaseModel):
    tags: List[str]


class UserProfileUpdate(BaseModel):
    email_reports: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    tags: List[str]
    email_reports: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
