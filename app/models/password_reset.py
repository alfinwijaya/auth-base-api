from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.db.base import Base

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String(255), index=True)
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)
    user = relationship("User")

    def is_expired(self):
        expires = self.expires_at
        if expires is None:
            return True

        expires = expires.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > expires