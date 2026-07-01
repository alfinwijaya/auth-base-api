from app.core.config import settings
from app.core.logger import logger
from app.core.security import create_access_token, create_refresh_token
from app.crud.role import get_role_by_name
from app.crud.user import get_user_by_email, create_user
from app.utils.hash import hash_password, verify_password
from fastapi import HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session

def register_user(db: Session, email: str, password: str, name: str, phone: str = None, address: str = None):
    existing = get_user_by_email(db, email)

    if existing:
        raise HTTPException(400, "Email already registered")
    
    role = get_role_by_name(db, "user")
    
    user = create_user(db, email, password, name, role, phone, address)
    logger.info(f"User registered: {email}")

    return user


def login_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)

    if not user or not verify_password(password, user.password):
        logger.warning(f"Failed login attempt for: {email}")
        raise HTTPException(401, "Invalid credentials")

    access_token = create_access_token({
        "sub": user.email,
        "role": user.role.role_name if user.role else "user"
    })

    refresh_token = create_refresh_token({
        "sub": user.email
    })

    logger.info(f"User logged in: {email}")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

def refresh_access_token(refresh_token: str, db: Session):
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")

        if not email:
            raise HTTPException(401, "Invalid refresh token")

    except JWTError:
        raise HTTPException(401, "Invalid refresh token")

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(401, "User not found")

    new_access = create_access_token({
        "sub": user.email,
        "role": user.role.role_name if user.role else "user"
    })
    new_refresh = create_refresh_token({"sub": user.email})

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }