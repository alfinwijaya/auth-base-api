from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.db.base import Base

class UserStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    status = Column(Enum(UserStatus), default=UserStatus.active, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    role = relationship("Role", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")