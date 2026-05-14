from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogCreate
from datetime import datetime

class AuditLogService:
    @staticmethod
    def create_log(db: Session, log_data: AuditLogCreate) -> AuditLog:
        log = AuditLog(**log_data.model_dump())
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def get_log_by_id(db: Session, log_id: int) -> Optional[AuditLog]:
        return db.query(AuditLog).filter(AuditLog.id == log_id).first()

    @staticmethod
    def get_logs_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        return db.query(AuditLog).filter(AuditLog.user_id == user_id).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_logs_by_module(db: Session, module: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        return db.query(AuditLog).filter(AuditLog.module == module).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_all_logs(db: Session, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        return db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_logs_by_date_range(db: Session, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        return db.query(AuditLog).filter(
            AuditLog.created_at >= start_date,
            AuditLog.created_at <= end_date
        ).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
