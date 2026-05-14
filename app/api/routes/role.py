from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.services.role_service import RoleService

router = APIRouter()

@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(role_data: RoleCreate, db: Session = Depends(get_db)):
    existing_role = RoleService.get_role_by_name(db, role_data.role_name)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists"
        )
    return RoleService.create_role(db, role_data)

@router.get("/{role_id}", response_model=RoleResponse)
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = RoleService.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role

@router.get("/", response_model=List[RoleResponse])
def get_all_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return RoleService.get_all_roles(db, skip, limit)

@router.put("/{role_id}", response_model=RoleResponse)
def update_role(role_id: int, role_data: RoleUpdate, db: Session = Depends(get_db)):
    role = RoleService.update_role(db, role_id, role_data)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    success = RoleService.delete_role(db, role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
