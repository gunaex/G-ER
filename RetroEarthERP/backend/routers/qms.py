"""
Quality Management System (QMS)
Handles Incoming, In-Process, and Outgoing Quality Inspections
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from decimal import Decimal
from utils.datetime_utils import get_utc_now
import models
import schemas
from database import get_db
from routers.auth import get_current_active_user

router = APIRouter(
    prefix="/api/qms",
    tags=["quality"],
    responses={404: {"description": "Not found"}},
)


@router.post("/inspections", response_model=schemas.QCInspectionResponse, status_code=status.HTTP_201_CREATED)
def create_inspection(
    inspection: schemas.QCInspectionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a Quality Inspection
    
    Triggered by:
    - INCOMING: Goods Receipt (GR)
    - IN_PROCESS: Work Order step completion
    - OUTGOING: Delivery Order (DO) creation
    """
    # Generate QC number
    count = db.query(models.QualityInspectionHeader).count()
    qc_no = f"QC-{get_utc_now().strftime('%Y%m%d')}-{count + 1:04d}"
    
    db_inspection = models.QualityInspectionHeader(
        qc_no=qc_no,
        inspection_type=inspection.inspection_type,
        ref_document_type=inspection.ref_document_type,
        ref_document_id=inspection.ref_document_id,
        status='PENDING',
        inspector_id=current_user.id,
        remarks=inspection.remarks
    )
    
    db.add(db_inspection)
    db.commit()
    db.refresh(db_inspection)
    
    return db_inspection


@router.get("/inspections", response_model=List[schemas.QCInspectionResponse])
def get_inspections(
    inspection_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all quality inspections with optional filters"""
    query = db.query(models.QualityInspectionHeader)
    
    if inspection_type:
        query = query.filter(models.QualityInspectionHeader.inspection_type == inspection_type)
    
    if status:
        query = query.filter(models.QualityInspectionHeader.status == status)
    
    return query.order_by(models.QualityInspectionHeader.inspection_date.desc()).all()


@router.get("/inspections/{qc_id}", response_model=schemas.QCInspectionResponse)
def get_inspection(
    qc_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get specific inspection details"""
    inspection = db.query(models.QualityInspectionHeader).filter(
        models.QualityInspectionHeader.id == qc_id
    ).first()
    
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    return inspection


@router.post("/inspections/{qc_id}/defects", response_model=schemas.QCDefectResponse)
def add_defect(
    qc_id: int,
    defect: schemas.QCDefectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Add a defect to an inspection"""
    inspection = db.query(models.QualityInspectionHeader).filter(
        models.QualityInspectionHeader.id == qc_id
    ).first()
    
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    if inspection.status != 'PENDING':
        raise HTTPException(status_code=400, detail="Can only add defects to pending inspections")
    
    db_defect = models.QualityInspectionDefect(
        qc_id=qc_id,
        defect_description=defect.defect_description,
        severity=defect.severity,
        qty_affected=defect.qty_affected,
        photo_url=defect.photo_url
    )
    
    db.add(db_defect)
    db.commit()
    db.refresh(db_defect)
    
    return db_defect


@router.post("/inspections/{qc_id}/complete")
def complete_inspection(
    qc_id: int,
    result: str,  # 'PASS', 'FAIL', 'CONDITIONAL'
    remarks: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Complete an inspection with result"""
    inspection = db.query(models.QualityInspectionHeader).filter(
        models.QualityInspectionHeader.id == qc_id
    ).first()
    
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    if inspection.status != 'PENDING':
        raise HTTPException(status_code=400, detail="Inspection is not pending")
    
    if result not in ['PASS', 'FAIL', 'CONDITIONAL']:
        raise HTTPException(status_code=400, detail="Invalid result")
    
    inspection.status = result
    inspection.completed_date = get_utc_now()
    if remarks:
        inspection.remarks = (inspection.remarks or "") + f"\nCompletion: {remarks}"
    
    db.commit()
    
    return {
        "message": "Inspection completed",
        "qc_no": inspection.qc_no,
        "status": result
    }


@router.post("/inspections/{qc_id}/upload-photo")
async def upload_defect_photo(
    qc_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Upload photo evidence for defects
    
    In production, this would:
    1. Upload to cloud storage (S3, Azure Blob, etc.)
    2. Return the URL
    3. Store URL in defect record
    
    For now, this is a placeholder that returns a mock URL
    """
    inspection = db.query(models.QualityInspectionHeader).filter(
        models.QualityInspectionHeader.id == qc_id
    ).first()
    
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Mock implementation - in production, upload to cloud storage
    # Example: 
    # file_url = await upload_to_s3(file, bucket="qc-photos")
    
    mock_url = f"/api/files/qc/{qc_id}/{file.filename}"
    
    return {
        "message": "Photo uploaded successfully",
        "url": mock_url,
        "filename": file.filename,
        "content_type": file.content_type
    }


@router.get("/inspections/trigger/incoming-qc/{gr_id}")
def trigger_incoming_qc(
    gr_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Auto-trigger Incoming QC when Goods Receipt is created"""
    gr = db.query(models.TrnGoodsReceiptHead).filter(
        models.TrnGoodsReceiptHead.id == gr_id
    ).first()
    
    if not gr:
        raise HTTPException(status_code=404, detail="Goods Receipt not found")
    
    # Check if QC already exists
    existing = db.query(models.QualityInspectionHeader).filter(
        models.QualityInspectionHeader.inspection_type == 'INCOMING',
        models.QualityInspectionHeader.ref_document_type == 'GR',
        models.QualityInspectionHeader.ref_document_id == gr_id
    ).first()
    
    if existing:
        return {"message": "QC already exists", "qc_no": existing.qc_no}
    
    # Create QC
    count = db.query(models.QualityInspectionHeader).count()
    qc_no = f"QC-INC-{get_utc_now().strftime('%Y%m%d')}-{count + 1:04d}"
    
    db_inspection = models.QualityInspectionHeader(
        qc_no=qc_no,
        inspection_type='INCOMING',
        ref_document_type='GR',
        ref_document_id=gr_id,
        status='PENDING',
        inspector_id=current_user.id,
        remarks=f"Auto-generated for GR {gr.gr_no}"
    )
    
    db.add(db_inspection)
    db.commit()
    db.refresh(db_inspection)
    
    return {
        "message": "Incoming QC created",
        "qc_no": qc_no,
        "qc_id": db_inspection.id
    }

