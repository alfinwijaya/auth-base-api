from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.crud.user import get_user_by_email, create_user
from app.utils.hash import verify_password
from app.core.security import create_access_token, create_refresh_token

from jose import jwt, JWTError
from app.core.config import settings


from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.crud.user import get_user_by_email, create_user
from app.crud.role import get_role_by_name
from app.utils.hash import hash_password, verify_password
from app.core.security import create_access_token, create_refresh_token


def register_user(db: Session, email: str, password: str):
    existing = get_user_by_email(db, email)

    if existing:
        raise HTTPException(400, "Email already registered")

    role = get_role_by_name(db, "user")

    hashed = hash_password(password)

    user = create_user(db, email, hashed, role)

    return user


def login_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)

    if not user or not verify_password(password, user.password):
        raise HTTPException(401, "Invalid credentials")

    access_token = create_access_token({
        "sub": user.email,
        "role": user.role.name if user.role else "user"
    })

    refresh_token = create_refresh_token({
        "sub": user.email
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

def refresh_access_token(refresh_token: str):
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

    new_access = create_access_token({"sub": email})
    new_refresh = create_refresh_token({"sub": email})

    return {
        "access_token": new_access,
        "refresh_token": new_refresh
    }