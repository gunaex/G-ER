from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import MasterItem, User
from schemas import ItemResponse, ItemCreate
from auth import get_current_active_manager

router = APIRouter()

@router.get("/", response_model=List[ItemResponse])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve items with optional pagination."""
    items = db.query(MasterItem).offset(skip).limit(limit).all()
    return items

@router.post("/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_manager)):
    """Create a new item (Manager/Admin only)."""
    db_item = MasterItem(**item.dict())
    db.add(db_item)
    try:
        db.commit()
        db.refresh(db_item)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_item

@router.put("/{item_code}", response_model=ItemResponse)
def update_item(item_code: str, item: ItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_manager)):
    """Update an existing item (Manager/Admin only)."""
    db_item = db.query(MasterItem).filter(MasterItem.item_code == item_code).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_code}", response_model=ItemResponse)
def disable_item(item_code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_manager)):
    """Soft delete (disable) an item (Manager/Admin only)."""
    db_item = db.query(MasterItem).filter(MasterItem.item_code == item_code).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.is_active = False
    db.commit()
    db.refresh(db_item)
    return db_item
