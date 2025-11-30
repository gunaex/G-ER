"""
Pydantic schemas for Auth Service
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Helper to document UTC fields
def utc_datetime_field(description: str = "") -> datetime:
    """Field for UTC datetime with timezone info"""
    return Field(description=f"{description} (UTC with timezone info)")


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str
    role: str = "user"


class UserResponse(UserBase):
    id: int
    role: str
    theme_preference: str
    language: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user details"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    theme_preference: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None


class PasswordChange(BaseModel):
    """Schema for changing user password"""
    new_password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
    server_time_utc: Optional[datetime] = None  # Server time in UTC for client sync
    active_package: Optional[dict] = None
    active_apps: List[dict] = []
