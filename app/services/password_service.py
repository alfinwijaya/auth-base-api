from app.core.logger import logger
from app.crud.user import get_user_by_email
from app.models.password_reset import PasswordResetToken
from app.services.notification_service import send_reset_notification
from app.utils.hash import hash_password
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
import secrets

RESET_TOKEN_EXPIRE_MINUTES = 15


def request_password_reset(db: Session, email: str):
    user = get_user_by_email(db, email)

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


def reset_password(db: Session, token: str, new_password: str):
    record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token
    ).first()

    if not record or record.is_used or record.is_expired():
        logger.warning("Invalid or expired password reset token used")
        raise HTTPException(400, "Invalid or expired token")

    user = record.user
    user.password = hash_password(new_password)

    record.is_used = True

    db.commit()

    return {"message": "Password updated"}