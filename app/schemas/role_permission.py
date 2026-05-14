from pydantic import BaseModel
from datetime import datetime

# RolePermission Schemas
class RolePermissionBase(BaseModel):
    role_id: int
    menu_id: int
    action_id: int

class RolePermissionCreate(RolePermissionBase):
    pass

class RolePermissionResponse(RolePermissionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
