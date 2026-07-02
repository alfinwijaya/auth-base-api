from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.action import Action
from app.schemas.action import ActionCreate, ActionUpdate


class ActionService:
    @staticmethod
    def create_action(db: Session, action_data: ActionCreate) -> Action:
        action = Action(**action_data.model_dump())
        db.add(action)
        db.commit()
        db.refresh(action)
        return action

    @staticmethod
    def get_action_by_id(db: Session, action_id: int) -> Optional[Action]:
        return db.query(Action).filter(Action.id == action_id).first()

    @staticmethod
    def get_action_by_name(db: Session, action_name: str) -> Optional[Action]:
        return db.query(Action).filter(Action.action_name == action_name).first()

    @staticmethod
    def get_all_actions(db: Session, skip: int = 0, limit: int = 100) -> List[Action]:
        return db.query(Action).offset(skip).limit(limit).all()

    @staticmethod
    def update_action(db: Session, action_id: int, action_data: ActionUpdate) -> Optional[Action]:
        action = db.query(Action).filter(Action.id == action_id).first()
        if not action:
            return None
        for key, value in action_data.model_dump(exclude_unset=True).items():
            setattr(action, key, value)
        db.commit()
        db.refresh(action)
        return action

    @staticmethod
    def delete_action(db: Session, action_id: int) -> bool:
        action = db.query(Action).filter(Action.id == action_id).first()
        if not action:
            return False
        db.delete(action)
        db.commit()
        return True
