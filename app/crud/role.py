from sqlalchemy.orm import Session
from app.models.role import Role

def get_role_by_name(db: Session, name: str):
    return db.query(Role).filter(Role.name == name).first()