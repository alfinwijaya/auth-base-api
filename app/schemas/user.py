from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class UserStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    role_id: int

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    role_id: Optional[int] = None
    status: Optional[UserStatusEnum] = None

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    phone: Optional[str]
    address: Optional[str]
    role_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True