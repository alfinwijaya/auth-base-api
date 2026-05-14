from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("menus.id"), nullable=True)
    menu_name = Column(String(100), nullable=False)
    menu_slug = Column(String(100), unique=True, nullable=False)
    menu_url = Column(String(255), nullable=True)
    icon = Column(String(100), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    parent = relationship("Menu", remote_side=[id], backref="children")
    role_permissions = relationship("RolePermission", back_populates="menu")
