from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timezone
import models
import schemas
from database import get_db
from routers.auth import get_current_active_user
from utils.datetime_utils import get_utc_now

router = APIRouter(
    prefix="/api/wms",
    tags=["wms"],
    responses={404: {"description": "Not found"}},
)

@router.post("/locations", response_model=schemas.LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(
    location: schemas.LocationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_location = models.LocationMaster(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

@router.get("/locations", response_model=List[schemas.LocationResponse])
def read_locations(
    warehouse_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    query = db.query(models.LocationMaster)
    if warehouse_id:
        query = query.filter(models.LocationMaster.warehouse_id == warehouse_id)
    return query.all()

@router.post("/put-away-suggestion")
def suggest_put_away(
    item_id: int,
    qty: float,
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    AI-Enhanced Put-away Suggestion
    Considers: Safety (condition matching), Security (high value items), Efficiency (weight/floor)
    """
    # 1. Get Item Details
    item = db.query(models.MasterItem).filter(models.MasterItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # 2. Get All Locations in Warehouse
    locations = db.query(models.LocationMaster).filter(models.LocationMaster.warehouse_id == warehouse_id).all()
    
    suitable_locations = []
    warnings = []
    
    for loc in locations:
        score = 0
        is_valid = True
        
        # CRITICAL: Condition Check (BLOCKING)
        # If Item requires special condition, Location MUST match
        if item.storage_condition != models.ConditionType.GENERAL:
            if item.storage_condition != loc.condition_type:
                continue # Strict blocking - cannot store here
        
        # If Item is GENERAL, prefer GENERAL location (don't waste special space)
        if item.storage_condition == models.ConditionType.GENERAL and loc.condition_type != models.ConditionType.GENERAL:
            score -= 50

        # CRITICAL: Security Check (BLOCKING)
        if item.security_level and item.security_level > 1: # High Value
            if not loc.is_secure_cage:
                continue # Must be secure - BLOCKING
        
        # Efficiency (Simple heuristic: Lower floor is better for heavy items)
        if item.weight_kg and item.weight_kg > 10:
            if loc.floor_level == 1:
                score += 20
            else:
                score -= 10 * loc.floor_level
        
        # Zone Preference
        if loc.zone_type == 'STORE':
            score += 10
        elif loc.zone_type == 'PICK':
            score += 5 # Still good for fast-moving items
            
        suitable_locations.append({"location": loc, "score": score})
    
    if not suitable_locations:
        error_msg = f"No suitable location found. Item requires: condition={item.storage_condition.value if item.storage_condition else 'GENERAL'}"
        if item.security_level and item.security_level > 1:
            error_msg += ", secure_cage=True"
        raise HTTPException(status_code=400, detail=error_msg)
        
    # Sort by score desc
    suitable_locations.sort(key=lambda x: x["score"], reverse=True)
    
    best_match = suitable_locations[0]["location"]
    
    # Build reason message
    reason_parts = []
    if item.storage_condition and item.storage_condition != models.ConditionType.GENERAL:
        reason_parts.append(f"Matched storage condition: {item.storage_condition.value}")
    if item.security_level and item.security_level > 1:
        reason_parts.append("High-value item - secure location")
    if item.weight_kg and item.weight_kg > 10:
        reason_parts.append("Heavy item - floor level optimized")
    
    reason = "; ".join(reason_parts) if reason_parts else "Standard storage location"
    
    return {
        "suggested_location_id": best_match.id,
        "location_code": best_match.location_code,
        "zone_type": best_match.zone_type,
        "condition_type": best_match.condition_type.value if best_match.condition_type else None,
        "is_secure_cage": best_match.is_secure_cage,
        "floor_level": best_match.floor_level,
        "reason": reason,
        "requires_witness": best_match.is_secure_cage
    }


@router.post("/inventory/move")
def move_inventory(
    item_id: int,
    from_location_id: int,
    to_location_id: int,
    qty: float,
    witness_supervisor_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Move inventory with validation
    BLOCKS if:
    - Storage condition mismatch
    - High-value item to non-secure location
    - Secure location without witness (if moving FROM secure)
    """
    # Validate item
    item = db.query(models.MasterItem).filter(models.MasterItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Validate locations
    from_loc = db.query(models.LocationMaster).filter(models.LocationMaster.id == from_location_id).first()
    to_loc = db.query(models.LocationMaster).filter(models.LocationMaster.id == to_location_id).first()
    
    if not from_loc or not to_loc:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # VALIDATION 1: Storage condition matching
    if item.storage_condition and item.storage_condition != models.ConditionType.GENERAL:
        if to_loc.condition_type != item.storage_condition:
            raise HTTPException(
                status_code=400,
                detail=f"❌ BLOCKED: Item requires {item.storage_condition.value} storage, but target location is {to_loc.condition_type.value}"
            )
    
    # VALIDATION 2: Security check
    if item.security_level and item.security_level > 1:
        if not to_loc.is_secure_cage:
            raise HTTPException(
                status_code=400,
                detail="❌ BLOCKED: High-value item must be stored in secure cage"
            )
    
    # VALIDATION 3: Witness requirement for secure locations
    if from_loc.is_secure_cage or to_loc.is_secure_cage:
        if not witness_supervisor_id:
            raise HTTPException(
                status_code=400,
                detail="❌ WITNESS REQUIRED: Secure cage access requires supervisor witness"
            )
        
        # Verify witness is a supervisor
        witness = db.query(models.User).filter(models.User.id == witness_supervisor_id).first()
        if not witness or witness.role not in ['manager', 'admin']:
            raise HTTPException(
                status_code=400,
                detail="Witness must be a Manager or Admin"
            )
        
        # Log secure access
        log_entry = models.SecureAccessLog(
            transaction_type='MOVE',
            location_id=from_loc.id if from_loc.is_secure_cage else to_loc.id,
            operator_user_id=current_user.id,
            witness_supervisor_id=witness_supervisor_id
        )
        db.add(log_entry)
    
    # All validations passed - execute move
    # (In production, this would update inventory balance records)
    db.commit()
    
    return {
        "message": "✅ Inventory moved successfully",
        "item_code": item.item_code,
        "from_location": from_loc.location_code,
        "to_location": to_loc.location_code,
        "qty": qty,
        "witness_logged": witness_supervisor_id is not None
    }


@router.post("/security/witness-verify")
def verify_witness(
    location_id: int,
    supervisor_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Verify supervisor for witness authentication
    Used by mobile app before allowing secure cage access
    """
    location = db.query(models.LocationMaster).filter(models.LocationMaster.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    if not location.is_secure_cage:
        return {
            "verified": True,
            "message": "Location does not require witness",
            "requires_witness": False
        }
    
    # Verify supervisor credentials
    supervisor = db.query(models.User).filter(models.User.id == supervisor_id).first()
    if not supervisor:
        raise HTTPException(status_code=404, detail="Supervisor not found")
    
    if supervisor.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=403,
            detail="User is not authorized as witness (must be Manager or Admin)"
        )
    
    if not supervisor.is_active:
        raise HTTPException(status_code=403, detail="Supervisor account is inactive")
    
    return {
        "verified": True,
        "message": f"Witness verified: {supervisor.full_name}",
        "requires_witness": True,
        "supervisor_name": supervisor.full_name,
        "supervisor_role": supervisor.role
    }

@router.post("/cycle-counts/start", response_model=schemas.CycleCountHeaderResponse)
def start_cycle_count(
    cycle_count: schemas.CycleCountHeaderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # 1. Create Header
    db_header = models.CycleCountHeader(
        count_date=cycle_count.count_date,
        warehouse_id=cycle_count.warehouse_id,
        status="DRAFT",
        created_by=current_user.id
    )
    db.add(db_header)
    db.flush() # Get ID

    # 2. Snapshot Logic: Get all inventory balance for this warehouse
    inventory = db.query(models.InventoryBalance).filter(
        models.InventoryBalance.warehouse_id == cycle_count.warehouse_id,
        models.InventoryBalance.qty_on_hand > 0
    ).all()

    for inv in inventory:
        detail = models.CycleCountDetail(
            header_id=db_header.id,
            item_id=inv.item_id,
            location_id=inv.location_id,
            snapshot_system_qty=inv.qty_on_hand,
            snapshot_timestamp=get_utc_now()
        )
        db.add(detail)

    db.commit()
    db.refresh(db_header)
    return db_header

@router.get("/cycle-counts/{id}", response_model=schemas.CycleCountHeaderResponse)
def get_cycle_count(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    header = db.query(models.CycleCountHeader).filter(models.CycleCountHeader.id == id).first()
    if not header:
        raise HTTPException(status_code=404, detail="Cycle Count not found")
    
    # Manual mapping for nested fields
    response = schemas.CycleCountHeaderResponse.from_orm(header)
    details_data = []
    for det in header.details:
        d_schema = schemas.CycleCountDetailResponse.from_orm(det)
        if det.item:
            d_schema.item_code = det.item.item_code
            d_schema.item_name = det.item.item_name
        if det.location:
            d_schema.location_code = det.location.location_code
        details_data.append(d_schema)
    
    response.details = details_data
    return response

@router.post("/cycle-counts/{id}/submit")
def submit_cycle_count(
    id: int,
    details: List[schemas.CycleCountDetailUpdate],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    header = db.query(models.CycleCountHeader).filter(models.CycleCountHeader.id == id).first()
    if not header:
        raise HTTPException(status_code=404, detail="Cycle Count not found")
    
    for det in details:
        db_detail = db.query(models.CycleCountDetail).filter(models.CycleCountDetail.id == det.id).first()
        if db_detail:
            db_detail.actual_counted_qty = det.actual_counted_qty
            db_detail.actual_count_timestamp = get_utc_now()
            
    header.status = "COMPLETED"
    db.commit()
    return {"message": "Cycle Count submitted"}

