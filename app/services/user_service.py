from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User


def get_all_users_service(db: Session):
    return db.query(User).all()


def delete_user_service(db: Session, user_id: int):
    user = db.query(User).get(user_id)

    if not user:
        raise HTTPException(404, "User not found")

    db.delete(user)
    db.commit()

    return {"message": "deleted"}