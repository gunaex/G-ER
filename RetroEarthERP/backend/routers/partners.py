from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import MasterBusinessPartner, User, PartnerAddress
from schemas import PartnerResponse, PartnerCreate, PartnerAddressCreate, PartnerAddressResponse
from auth import get_current_active_manager

router = APIRouter()

@router.get("/", response_model=List[PartnerResponse])
def read_partners(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve business partners (vendors/customers)."""
    partners = db.query(MasterBusinessPartner).offset(skip).limit(limit).all()
    return partners

@router.get("/{code}", response_model=PartnerResponse)
def read_partner(code: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific partner by code.
    """
    partner = db.query(MasterBusinessPartner).filter(MasterBusinessPartner.partner_code == code).first()
    if partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner

@router.post("/", response_model=PartnerResponse)
def create_partner(partner: PartnerCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_manager)):
    """
    Create a new partner (Manager/Admin only).
    """
    db_partner = MasterBusinessPartner(**partner.dict())
    db.add(db_partner)
    try:
        db.commit()
        db.refresh(db_partner)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_partner

@router.put("/{partner_code}", response_model=PartnerResponse)
def update_partner(partner_code: str, partner: PartnerCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_manager)):
    """
    Update a partner (Manager/Admin only).
    """
    db_partner = db.query(MasterBusinessPartner).filter(MasterBusinessPartner.partner_code == partner_code).first()
    if not db_partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    for key, value in partner.dict().items():
        setattr(db_partner, key, value)
    
    db.commit()
    db.refresh(db_partner)
    return db_partner

@router.delete("/{partner_code}", response_model=PartnerResponse)
def disable_partner(partner_code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_manager)):
    """
    Disable (soft delete) a partner (Manager/Admin only).
    """
    db_partner = db.query(MasterBusinessPartner).filter(MasterBusinessPartner.partner_code == partner_code).first()
    if not db_partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    db_partner.is_active = False
    db.commit()
    db.refresh(db_partner)
    return db_partner

@router.post("/{partner_id}/addresses", response_model=PartnerAddressResponse)
def create_address(partner_id: int, address: PartnerAddressCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_manager)):
    """
    Add a new address to a partner.
    """
    db_partner = db.query(MasterBusinessPartner).filter(MasterBusinessPartner.id == partner_id).first()
    if not db_partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    new_address = PartnerAddress(**address.dict())
    if new_address.partner_id != partner_id:
        raise HTTPException(status_code=400, detail="Partner ID mismatch")
        
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address

@router.get("/{partner_id}/addresses", response_model=List[PartnerAddressResponse])
def read_addresses(partner_id: int, db: Session = Depends(get_db)):
    """
    Get all addresses for a partner.
    """
    addresses = db.query(PartnerAddress).filter(PartnerAddress.partner_id == partner_id).all()
    return addresses

@router.delete("/addresses/{address_id}", status_code=204)
def delete_address(address_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_manager)):
    """
    Delete an address.
    """
    address = db.query(PartnerAddress).filter(PartnerAddress.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    db.delete(address)
    db.commit()
    return None

