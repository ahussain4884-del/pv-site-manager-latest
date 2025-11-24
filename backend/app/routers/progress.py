import sys
sys.path.insert(0, r'E:\pv-clean\backend')

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from ..database import get_db
from ..models import ProjectProgress
from ..routers.auth import get_current_user

router = APIRouter(prefix="/progress", tags=["progress-dashboard"])

class ProgressCreate(BaseModel):
    kpi_name: str
    progress_percent: float
    target_date: Optional[datetime] = None
    actual_date: Optional[datetime] = None
    notes: Optional[str] = None

class ProgressUpdate(BaseModel):
    progress_percent: Optional[float] = None
    target_date: Optional[datetime] = None
    actual_date: Optional[datetime] = None
    notes: Optional[str] = None

def compute_gantt_data(progress: List[ProjectProgress]) -> dict:
    overall_percent = sum(p.progress_percent for p in progress) / len(progress) if progress else 0
    overdue = [p for p in progress if p.target_date and (p.actual_date or datetime.utcnow()) > p.target_date]
    return {
        "overall_progress_percent": round(overall_percent, 2),
        "overdue_milestones": len(overdue),
        "milestones": [{"name": p.kpi_name, "progress": p.progress_percent, "target": p.target_date.isoformat() if p.target_date else None, "actual": p.actual_date.isoformat() if p.actual_date else None} for p in progress]
    }

@router.post("/", response_model=None)
def create_progress(
    progress_data: ProgressCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["PM", "Admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    if progress_data.progress_percent > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Progress % cannot exceed 100")
    
    db_progress = ProjectProgress(**progress_data.dict())
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return {"message": "KPI created", "id": db_progress.id}

@router.get("/", response_model=None)
def read_progress(skip: int = 0, limit: int = 100, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    progress = db.query(ProjectProgress).offset(skip).limit(limit).all()
    gantt_data = compute_gantt_data(progress)
    return {
        "kpis": [{"id": p.id, "kpi_name": p.kpi_name, "progress_percent": p.progress_percent, "target_date": p.target_date.isoformat() if p.target_date else None, "actual_date": p.actual_date.isoformat() if p.actual_date else None} for p in progress],
        "dashboard_summary": gantt_data
    }

@router.put("/{progress_id}", response_model=None)
def update_progress(
    progress_id: int,
    progress_update: ProgressUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["SiteManager", "PM", "Admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    progress = db.query(ProjectProgress).filter(ProjectProgress.id == progress_id).first()
    if not progress:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KPI not found")
    
    update_data = progress_update.dict(exclude_unset=True)
    if "progress_percent" in update_data and update_data["progress_percent"] > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Progress % cannot exceed 100")
    
    for field, value in update_data.items():
        setattr(progress, field, value)
    
    db.commit()
    db.refresh(progress)
    return {"message": "KPI updated", "id": progress_id}