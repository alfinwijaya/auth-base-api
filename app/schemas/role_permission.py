from pydantic import BaseModel, ConfigDict
from datetime import datetime

# RolePermission Schemas
class RolePermissionBase(BaseModel):
    role_id: int
    menu_id: int
    action_id: int

class RolePermissionCreate(RolePermissionBase):
    pass

class RolePermissionResponse(RolePermissionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
