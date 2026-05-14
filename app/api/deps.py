from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from fastapi.security import HTTPAuthorizationCredentials
from app.core.security import security
from app.services.role_permission_service import RolePermissionService

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise HTTPException(401, "Invalid token")

    except JWTError:
        raise HTTPException(401, "Invalid token")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(401, "User not found")

    return user

def require_role(role_names: list[str]):
    def checker(current_user: User = Depends(get_current_user)):
        if not current_user.role or current_user.role.role_name not in role_names:
            raise HTTPException(403, "Forbidden")
        return current_user

    return checker

def require_permission(menu_id: int, action_id: int):
    """
    Dependency to check if the current user has permission to perform an action on a menu.
    
    Args:
        menu_id: The menu ID to check permission for
        action_id: The action ID to check permission for
    """
    def checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not current_user.role:
            raise HTTPException(403, "User has no role assigned")
        
        has_permission = RolePermissionService.check_permission(
            db, 
            current_user.role_id, 
            menu_id, 
            action_id
        )
        
        if not has_permission:
            raise HTTPException(403, "You don't have permission to perform this action")
        
        return current_user
    
    return checker