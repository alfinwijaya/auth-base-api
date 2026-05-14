from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RoleBase(BaseModel):
    role_name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=255)

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    role_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=255)

class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
