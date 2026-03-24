from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from slowapi.util import get_remote_address
from slowapi import Limiter
from app.schemas.user import UserCreate
from app.schemas.auth import Token
from app.crud.user import create_user, get_user_by_email
from app.core.security import (
    create_access_token,
    create_refresh_token,
)
from app.utils.hash import verify_password
from app.api.deps import get_db
from app.core.config import settings
from app.services import auth_service as auth
from app.schemas.auth import RefreshTokenRequest

router = APIRouter(prefix="/auth", tags=["Auth"])

limiter = Limiter(key_func=get_remote_address)

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return auth.register_user(db, user.email, user.password)

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    return auth.login_user(db, user.email, user.password)

@router.post("/refresh", response_model=Token)
def refresh_token(data: RefreshTokenRequest):
    return auth.refresh_access_token(data.refresh_token)