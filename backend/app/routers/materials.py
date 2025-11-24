import sys
sys.path.insert(0, r'E:\pv-clean\backend')

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..database import get_db
from ..models import Material
from ..routers.auth import get_current_user
from PIL import Image
import pytesseract
import re
import io

router = APIRouter(prefix="/materials", tags=["materials"])

class MaterialCreate(BaseModel):
    ddt_number: str
    packing_list: Optional[str] = None
    container_id: Optional[str] = None
    batch_number: str
    non_conformity: bool = False
    notes: Optional[str] = None

class MaterialUpdate(BaseModel):
    non_conformity: Optional[bool] = None
    notes: Optional[str] = None

def parse_ocr_text(text: str) -> dict:
    ddt_match = re.search(r'DDT[:\s]*(\w+)', text, re.IGNORECASE)
    batch_match = re.search(r'BATCH[:\s]*(\w+)', text, re.IGNORECASE)
    return {
        'ddt_number': ddt_match.group(1) if ddt_match else None,
        'batch_number': batch_match.group(1) if batch_match else None,
        'full_text': text
    }

@router.post("/", response_model=None)
def create_material(
    material_data: MaterialCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["Operator", "SiteManager", "PM", "Admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    existing = db.query(Material).filter(Material.ddt_number == material_data.ddt_number).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="DDT number already exists")
    
    db_material = Material(**material_data.dict())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return {"message": "Material created", "id": db_material.id}

@router.post("/ocr/", response_model=None)
async def create_material_from_ocr(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["Operator", "SiteManager", "PM", "Admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only image files supported")
    
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    text = pytesseract.image_to_string(image)
    
    parsed = parse_ocr_text(text)
    if not parsed['ddt_number']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No DDT number detected")
    
    material_data = MaterialCreate(
        ddt_number=parsed['ddt_number'],
        packing_list=parsed['full_text'][:500],
        batch_number=parsed['batch_number'] or "UNKNOWN",
        notes=f"OCR extracted from {file.filename}"
    )
    
    return create_material(material_data, current_user, db)

@router.get("/", response_model=None)
def read_materials(skip: int = 0, limit: int = 100, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    materials = db.query(Material).offset(skip).limit(limit).all()
    return [{"id": m.id, "ddt_number": m.ddt_number, "batch_number": m.batch_number, "non_conformity": m.non_conformity} for m in materials]

@router.get("/{material_id}", response_model=None)
def read_material(material_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
    return {
        "id": material.id,
        "ddt_number": material.ddt_number,
        "packing_list": material.packing_list,
        "container_id": material.container_id,
        "batch_number": material.batch_number,
        "non_conformity": material.non_conformity,
        "notes": material.notes
    }

@router.put("/{material_id}", response_model=None)
def update_material(
    material_id: int,
    material_update: MaterialUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["SiteManager", "PM", "Admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
    
    update_data = material_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(material, field, value)
    
    db.commit()
    db.refresh(material)
    return {"message": "Material updated", "id": material_id}