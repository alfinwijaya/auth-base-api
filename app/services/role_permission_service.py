from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.role_permission import RolePermission
from app.schemas.role_permission import RolePermissionCreate

class RolePermissionService:
    @staticmethod
    def create_permission(db: Session, permission_data: RolePermissionCreate) -> RolePermission:
        permission = RolePermission(**permission_data.model_dump())
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission

    @staticmethod
    def get_permission_by_id(db: Session, permission_id: int) -> Optional[RolePermission]:
        return db.query(RolePermission).filter(RolePermission.id == permission_id).first()

    @staticmethod
    def get_permissions_by_role(db: Session, role_id: int) -> List[RolePermission]:
        return db.query(RolePermission).filter(RolePermission.role_id == role_id).all()

    @staticmethod
    def get_permissions_by_menu(db: Session, menu_id: int) -> List[RolePermission]:
        return db.query(RolePermission).filter(RolePermission.menu_id == menu_id).all()

    @staticmethod
    def check_permission(db: Session, role_id: int, menu_id: int, action_id: int) -> bool:
        permission = db.query(RolePermission).filter(
            RolePermission.role_id == role_id,
            RolePermission.menu_id == menu_id,
            RolePermission.action_id == action_id
        ).first()
        return permission is not None

    @staticmethod
    def delete_permission(db: Session, permission_id: int) -> bool:
        permission = db.query(RolePermission).filter(RolePermission.id == permission_id).first()
        if not permission:
            return False
        
        db.delete(permission)
        db.commit()
        return True

    @staticmethod
    def delete_permissions_by_role(db: Session, role_id: int) -> bool:
        db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
        db.commit()
        return True

    @staticmethod
    def bulk_create_permissions(db: Session, permissions_data: List[RolePermissionCreate]) -> List[RolePermission]:
        permissions = [RolePermission(**perm.model_dump()) for perm in permissions_data]
        db.add_all(permissions)
        db.commit()
        for perm in permissions:
            db.refresh(perm)
        return permissions
