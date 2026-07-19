from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

# Action Schemas
class ActionBase(BaseModel):
    action_name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=255)

class ActionCreate(ActionBase):
    pass

class ActionUpdate(BaseModel):
    action_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=255)

class ActionResponse(ActionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
