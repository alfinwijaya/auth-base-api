from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.schemas.action import ActionCreate, ActionUpdate, ActionResponse
from app.services.action_service import ActionService

router = APIRouter()

@router.post("/", response_model=ActionResponse, status_code=status.HTTP_201_CREATED)
def create_action(action_data: ActionCreate, db: Session = Depends(get_db)):
    existing_action = ActionService.get_action_by_name(db, action_data.action_name)
    if existing_action:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action with this name already exists"
        )
    return ActionService.create_action(db, action_data)

@router.get("/{action_id}", response_model=ActionResponse)
def get_action(action_id: int, db: Session = Depends(get_db)):
    action = ActionService.get_action_by_id(db, action_id)
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )
    return action

@router.get("/", response_model=List[ActionResponse])
def get_all_actions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ActionService.get_all_actions(db, skip, limit)

@router.put("/{action_id}", response_model=ActionResponse)
def update_action(action_id: int, action_data: ActionUpdate, db: Session = Depends(get_db)):
    action = ActionService.update_action(db, action_id, action_data)
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )
    return action

@router.delete("/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_action(action_id: int, db: Session = Depends(get_db)):
    success = ActionService.delete_action(db, action_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )
