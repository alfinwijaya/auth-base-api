from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    @staticmethod
    def create_role(db: Session, role_data: RoleCreate) -> Role:
        role = Role(**role_data.model_dump())
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
        return db.query(Role).filter(Role.id == role_id).first()

    @staticmethod
    def get_role_by_name(db: Session, role_name: str) -> Optional[Role]:
        return db.query(Role).filter(Role.role_name == role_name).first()

    @staticmethod
    def get_all_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
        return db.query(Role).offset(skip).limit(limit).all()

    @staticmethod
    def update_role(db: Session, role_id: int, role_data: RoleUpdate) -> Optional[Role]:
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return None
        for key, value in role_data.model_dump(exclude_unset=True).items():
            setattr(role, key, value)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def delete_role(db: Session, role_id: int) -> bool:
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return False
        db.delete(role)
        db.commit()
        return True
