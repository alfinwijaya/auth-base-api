from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

# Menu Schemas
class MenuBase(BaseModel):
    menu_name: str = Field(..., max_length=100)
    menu_slug: str = Field(..., max_length=100)
    menu_url: Optional[str] = Field(None, max_length=255)
    icon: Optional[str] = Field(None, max_length=100)
    parent_id: Optional[int] = None
    sort_order: int = 0
    is_active: bool = True

class MenuCreate(MenuBase):
    pass

class MenuUpdate(BaseModel):
    menu_name: Optional[str] = Field(None, max_length=100)
    menu_slug: Optional[str] = Field(None, max_length=100)
    menu_url: Optional[str] = Field(None, max_length=255)
    icon: Optional[str] = Field(None, max_length=100)
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class MenuResponse(MenuBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
