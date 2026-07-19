from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

# AuditLog Schemas
class AuditLogBase(BaseModel):
    user_id: int
    module: str = Field(..., max_length=100)
    activity: str
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=255)

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogResponse(AuditLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
