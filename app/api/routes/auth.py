from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from slowapi.util import get_remote_address
from slowapi import Limiter
from app.schemas.user import UserCreate, UserRegister
from app.schemas.auth import ForgotPasswordRequest, ResetPasswordRequest, Token
from app.api.deps import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import RefreshTokenRequest
from app.services.password_service import PasswordService

router = APIRouter(prefix="/auth", tags=["Auth"])

limiter = Limiter(key_func=get_remote_address)


@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    return AuthService.register_user(db, user.email, user.password, user.name, user.phone, user.address)


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    return AuthService.login_user(db, user.email, user.password)


@router.post("/refresh", response_model=Token)
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return AuthService.refresh_access_token(data.refresh_token, db)


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    PasswordService.request_password_reset(db, data.email)
    return {"message": "If account exists, reset link sent"}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    return PasswordService.reset_password(db, data.token, data.new_password)
