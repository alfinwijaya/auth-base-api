from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.api.deps import get_db
from app.schemas.audit_log import AuditLogCreate, AuditLogResponse
from app.services.audit_log_service import AuditLogService

router = APIRouter()

@router.post("/", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
def create_log(log_data: AuditLogCreate, db: Session = Depends(get_db)):
    return AuditLogService.create_log(db, log_data)

@router.get("/{log_id}", response_model=AuditLogResponse)
def get_log(log_id: int, db: Session = Depends(get_db)):
    log = AuditLogService.get_log_by_id(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    return log

@router.get("/", response_model=List[AuditLogResponse])
def get_all_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return AuditLogService.get_all_logs(db, skip, limit)

@router.get("/user/{user_id}", response_model=List[AuditLogResponse])
def get_logs_by_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return AuditLogService.get_logs_by_user(db, user_id, skip, limit)

@router.get("/module/{module}", response_model=List[AuditLogResponse])
def get_logs_by_module(module: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return AuditLogService.get_logs_by_module(db, module, skip, limit)

@router.get("/date-range/", response_model=List[AuditLogResponse])
def get_logs_by_date_range(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return AuditLogService.get_logs_by_date_range(db, start_date, end_date, skip, limit)
