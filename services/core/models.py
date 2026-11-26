from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class UserCreate(BaseModel):
    """Schema for creating a user"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    @validator("password")
    def password_valid(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserUpdate(BaseModel):
    """Schema for updating user credentials"""
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None


class UserResponse(BaseModel):
    """Schema for user response (no password)"""
    id: str
    email: str
    is_active: bool
    role: UserRole
    created_at: str

    class Config:
        from_attributes = True


class ProfileCreate(BaseModel):
    """Schema for creating a profile"""
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None


class ProfileUpdate(BaseModel):
    """Schema for updating a profile"""
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class ProfileResponse(BaseModel):
    """Schema for profile response"""
    id: str
    user_id: str
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True


class UserWithProfile(BaseModel):
    """Schema for user with associated profile"""
    id: str
    email: str
    is_active: bool
    role: UserRole
    created_at: str
    profile: Optional[ProfileResponse] = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Schema for login request"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MeResponse(BaseModel):
    """Schema for authenticated user info"""
    email: str
    role: UserRole
    profile: Optional[ProfileResponse] = None
