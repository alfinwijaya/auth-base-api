from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User
from app.schemas.menu import MenuCreate, MenuUpdate, MenuResponse
from app.services.menu_service import MenuService

router = APIRouter()


@router.post("/", response_model=MenuResponse, status_code=status.HTTP_201_CREATED)
def create_menu(menu_data: MenuCreate, db: Session = Depends(get_db), _: User = Depends(require_role(["admin"]))):
    if MenuService.get_menu_by_slug(db, menu_data.menu_slug):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Menu with this slug already exists")
    return MenuService.create_menu(db, menu_data)


@router.get("/{menu_id}", response_model=MenuResponse)
def get_menu(menu_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    menu = MenuService.get_menu_by_id(db, menu_id)
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")
    return menu


@router.get("/", response_model=List[MenuResponse])
def get_all_menus(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return MenuService.get_all_menus(db, skip, limit)


@router.get("/active/list", response_model=List[MenuResponse])
def get_active_menus(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return MenuService.get_active_menus(db)


@router.put("/{menu_id}", response_model=MenuResponse)
def update_menu(menu_id: int, menu_data: MenuUpdate, db: Session = Depends(get_db), _: User = Depends(require_role(["admin"]))):
    menu = MenuService.update_menu(db, menu_id, menu_data)
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")
    return menu


@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu(menu_id: int, db: Session = Depends(get_db), _: User = Depends(require_role(["admin"]))):
    if not MenuService.delete_menu(db, menu_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")
