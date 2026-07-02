from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_user, require_role
from app.schemas.user import UserOut
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[UserOut])
def get_all_users(
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    return UserService.get_all_users(db)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    return UserService.delete_user(db, user_id)
