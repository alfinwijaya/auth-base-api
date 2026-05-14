from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.menu import Menu
from app.schemas.menu import MenuCreate, MenuUpdate

class MenuService:
    @staticmethod
    def create_menu(db: Session, menu_data: MenuCreate) -> Menu:
        menu = Menu(**menu_data.model_dump())
        db.add(menu)
        db.commit()
        db.refresh(menu)
        return menu

    @staticmethod
    def get_menu_by_id(db: Session, menu_id: int) -> Optional[Menu]:
        return db.query(Menu).filter(Menu.id == menu_id).first()

    @staticmethod
    def get_menu_by_slug(db: Session, menu_slug: str) -> Optional[Menu]:
        return db.query(Menu).filter(Menu.menu_slug == menu_slug).first()

    @staticmethod
    def get_all_menus(db: Session, skip: int = 0, limit: int = 100) -> List[Menu]:
        return db.query(Menu).offset(skip).limit(limit).all()

    @staticmethod
    def get_active_menus(db: Session) -> List[Menu]:
        return db.query(Menu).filter(Menu.is_active == True).order_by(Menu.sort_order).all()

    @staticmethod
    def get_menus_by_parent(db: Session, parent_id: Optional[int] = None) -> List[Menu]:
        return db.query(Menu).filter(Menu.parent_id == parent_id).order_by(Menu.sort_order).all()

    @staticmethod
    def update_menu(db: Session, menu_id: int, menu_data: MenuUpdate) -> Optional[Menu]:
        menu = db.query(Menu).filter(Menu.id == menu_id).first()
        if not menu:
            return None
        
        update_data = menu_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(menu, key, value)
        
        db.commit()
        db.refresh(menu)
        return menu

    @staticmethod
    def delete_menu(db: Session, menu_id: int) -> bool:
        menu = db.query(Menu).filter(Menu.id == menu_id).first()
        if not menu:
            return False
        
        db.delete(menu)
        db.commit()
        return True
