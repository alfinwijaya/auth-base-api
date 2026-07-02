from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User


class UserService:
    @staticmethod
    def get_all_users(db: Session):
        return db.query(User).all()

    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = db.query(User).get(user_id)

        if not user:
            raise HTTPException(404, "User not found")

        db.delete(user)
        db.commit()

        return {"message": "deleted"}
