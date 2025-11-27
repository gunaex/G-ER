from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import MasterWarehouse, User
from schemas import WarehouseResponse, WarehouseCreate
from auth import get_current_active_manager

router = APIRouter()

@router.get("/", response_model=List[WarehouseResponse])
def read_warehouses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve warehouses with optional pagination."""
    warehouses = db.query(MasterWarehouse).offset(skip).limit(limit).all()
    return warehouses

@router.get("/{code}", response_model=WarehouseResponse)
def read_warehouse(code: str, db: Session = Depends(get_db)):
    """Retrieve a specific warehouse by code."""
    warehouse = db.query(MasterWarehouse).filter(MasterWarehouse.warehouse_code == code).first()
    if warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse

@router.post("/", response_model=WarehouseResponse)
def create_warehouse(warehouse: WarehouseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_manager)):
    """Create a new warehouse (Manager/Admin only)."""
    db_warehouse = MasterWarehouse(**warehouse.dict())
    db.add(db_warehouse)
    try:
        db.commit()
        db.refresh(db_warehouse)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_warehouse

@router.put("/{warehouse_code}", response_model=WarehouseResponse)
def update_warehouse(warehouse_code: str, warehouse: WarehouseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_manager)):
    """Update a warehouse (Manager/Admin only)."""
    db_warehouse = db.query(MasterWarehouse).filter(MasterWarehouse.warehouse_code == warehouse_code).first()
    if not db_warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    for key, value in warehouse.dict().items():
        setattr(db_warehouse, key, value)
    
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse

@router.delete("/{warehouse_code}", response_model=WarehouseResponse)
def disable_warehouse(warehouse_code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_manager)):
    """Disable (soft delete) a warehouse (Manager/Admin only)."""
    db_warehouse = db.query(MasterWarehouse).filter(MasterWarehouse.warehouse_code == warehouse_code).first()
    if not db_warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    db_warehouse.is_active = False
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse
