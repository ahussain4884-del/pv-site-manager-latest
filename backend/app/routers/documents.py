import sys
sys.path.insert(0, r'E:\pv-clean\backend')

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import os
import shutil
from ..database import get_db
from ..models import Document, DailyLog, Material
from ..routers.auth import get_current_user

router = APIRouter(prefix="/documents", tags=["documents"])

class DocumentCreate(BaseModel):
    log_id: Optional[int] = None
    material_id: Optional[int] = None
    notes: Optional[str] = None

@router.post("/", response_model=None)
async def create_document(
    file: UploadFile = File(...),
    doc_data: DocumentCreate = Depends(),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["Operator", "SiteManager", "PM", "Admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    if doc_data.log_id:
        log = db.query(DailyLog).filter(DailyLog.id == doc_data.log_id).first()
        if not log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily log not found")
    if doc_data.material_id:
        material = db.query(Material).filter(Material.id == doc_data.material_id).first()
        if not material:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
    
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PNG/JPG/PDF supported")
    
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    db_doc = Document(
        file_path=file_path,
        file_type="photo" if file.filename.lower().endswith(('.png', '.jpg', '.jpeg')) else "pdf",
        notes=doc_data.notes,
        log_id=doc_data.log_id,
        material_id=doc_data.material_id
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return {"message": "Document uploaded", "id": db_doc.id, "file_path": file_path}

@router.get("/", response_model=None)
def read_documents(skip: int = 0, limit: int = 100, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.query(Document).offset(skip).limit(limit).all()
    return [{
        "id": d.id,
        "file_path": d.file_path,
        "file_type": d.file_type,
        "notes": d.notes,
        "log_id": d.log_id,
        "material_id": d.material_id
    } for d in docs]

@router.get("/{document_id}", response_model=None)
def read_document(document_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return {
        "id": doc.id,
        "file_path": doc.file_path,
        "file_type": doc.file_type,
        "notes": doc.notes,
        "log_id": doc.log_id,
        "material_id": doc.material_id
    }

@router.delete("/{document_id}", response_model=None)
def delete_document(document_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["PM", "Admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted", "id": document_id}