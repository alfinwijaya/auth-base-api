from sqlalchemy.orm import Session
from app.core.logger import logger
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.services.notification_service import send_reset_notification
from app.utils.hash import hash_password
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
import secrets

RESET_TOKEN_EXPIRE_MINUTES = 15


class PasswordService:
    @staticmethod
    def request_password_reset(db: Session, email: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return

        token = secrets.token_urlsafe(32)
        reset = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
        )
        db.add(reset)
        db.commit()

        send_reset_notification(email, token)
        logger.info(f"Password reset requested for: {email}")

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str):
        record = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
        if not record or record.is_used or record.is_expired():
            logger.warning("Invalid or expired password reset token used")
            raise HTTPException(400, "Invalid or expired token")

        record.user.password = hash_password(new_password)
        record.is_used = True
        db.commit()

        return {"message": "Password updated"}
