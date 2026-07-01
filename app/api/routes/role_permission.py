from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User
from app.schemas.role_permission import RolePermissionCreate, RolePermissionResponse
from app.services.role_permission_service import RolePermissionService

router = APIRouter()

@router.post("/", response_model=RolePermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(permission_data: RolePermissionCreate, db: Session = Depends(get_db), _: User = Depends(require_role(["admin"]))):
    return RolePermissionService.create_permission(db, permission_data)

@router.post("/bulk", response_model=List[RolePermissionResponse], status_code=status.HTTP_201_CREATED)
def bulk_create_permissions(permissions_data: List[RolePermissionCreate], db: Session = Depends(get_db), _: User = Depends(require_role(["admin"]))):
    return RolePermissionService.bulk_create_permissions(db, permissions_data)

@router.get("/{permission_id}", response_model=RolePermissionResponse)
def get_permission(permission_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    permission = RolePermissionService.get_permission_by_id(db, permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return permission

@router.get("/role/{role_id}", response_model=List[RolePermissionResponse])
def get_permissions_by_role(role_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return RolePermissionService.get_permissions_by_role(db, role_id)

@router.get("/menu/{menu_id}", response_model=List[RolePermissionResponse])
def get_permissions_by_menu(menu_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return RolePermissionService.get_permissions_by_menu(db, menu_id)

@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(permission_id: int, db: Session = Depends(get_db), _: User = Depends(require_role(["admin"]))):
    success = RolePermissionService.delete_permission(db, permission_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )

@router.delete("/role/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permissions_by_role(role_id: int, db: Session = Depends(get_db), _: User = Depends(require_role(["admin"]))):
    RolePermissionService.delete_permissions_by_role(db, role_id)
