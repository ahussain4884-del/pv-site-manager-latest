import sys
sys.path.insert(0, r'E:\pv-clean\backend')  # Temp fix for imports

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from ..database import get_db
from ..models import DailyLog, User
from ..routers.auth import get_current_user

router = APIRouter(prefix="/logs", tags=["daily-logs"])

class DailyLogCreate(BaseModel):
    workers_count: int
    tasks: str
    hours_worked: float
    equipment_used: str
    fuel_consumed: float

@router.post("/", response_model=None)
def create_daily_log(
    log_data: DailyLogCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Role check: Allow Operator, SiteManager, PM, Admin
    if current_user.role not in ["Operator", "SiteManager", "PM", "Admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    db_log = DailyLog(
        workers_count=log_data.workers_count,
        tasks=log_data.tasks,
        hours_worked=log_data.hours_worked,
        equipment_used=log_data.equipment_used,
        fuel_consumed=log_data.fuel_consumed,
        user_id=current_user.id
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return {"message": "Log created", "id": db_log.id}

@router.get("/", response_model=None)
def read_daily_logs(skip: int = 0, limit: int = 100, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(DailyLog).filter(DailyLog.user_id == current_user.id).offset(skip).limit(limit).all()
    return [{"id": log.id, "date": log.date, "workers_count": log.workers_count} for log in logs]