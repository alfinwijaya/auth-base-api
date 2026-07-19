from pydantic import BaseModel, EmailStr, Field, ConfigDict
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

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str = Field(..., max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    role_id: Optional[int] = None
    status: Optional[UserStatusEnum] = None

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    phone: Optional[str]
    address: Optional[str]
    role_id: int
    status: str
    created_at: datetime
    updated_at: datetime