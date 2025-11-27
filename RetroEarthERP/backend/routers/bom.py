"""
Bill of Materials (BOM) Router - Full CRUD operations with Revision Management
Supports 4 BOM types: ASSEMBLY, FORMULA, MODULAR, TAILOR_MADE
Features: Revision control, export, search, location tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, date, timezone
import csv
from utils.datetime_utils import get_utc_now
import io

from database import get_db
import models
import schemas
import auth as auth_utils

router = APIRouter()

# Maximum revisions to keep per parent item
MAX_REVISIONS = 3


# ==================== HELPER FUNCTIONS ====================
def get_bom_line_dict(bom, db):
    """Convert BOM model to dictionary with enriched data"""
    parent = db.query(models.MasterItem).filter(models.MasterItem.id == bom.parent_item_id).first()
    child = db.query(models.MasterItem).filter(models.MasterItem.id == bom.child_item_id).first()
    prod_loc = db.query(models.LocationMaster).filter(models.LocationMaster.id == bom.production_location_id).first() if bom.production_location_id else None
    stor_loc = db.query(models.LocationMaster).filter(models.LocationMaster.id == bom.storage_location_id).first() if bom.storage_location_id else None
    
    return {
        "id": bom.id,
        "parent_item_id": bom.parent_item_id,
        "parent_item_code": parent.item_code if parent else None,
        "parent_item_name": parent.item_name if parent else None,
        "child_item_id": bom.child_item_id,
        "child_item_code": child.item_code if child else None,
        "child_item_name": child.item_name if child else None,
        "child_uom": child.unit_of_measure if child else None,
        "bom_type": bom.bom_type,
        "is_template": bom.is_template,
        "sequence_order": bom.sequence_order,
        "quantity": float(bom.quantity),
        "percentage": float(bom.percentage) if bom.percentage else None,
        "is_optional": bom.is_optional,
        "scrap_factor": float(bom.scrap_factor) if bom.scrap_factor else 0,
        "production_location_id": bom.production_location_id,
        "production_location_code": prod_loc.location_code if prod_loc else None,
        "storage_location_id": bom.storage_location_id,
        "storage_location_code": stor_loc.location_code if stor_loc else None,
        "machine_id": bom.machine_id,
        "production_lead_time_days": float(bom.production_lead_time_days) if bom.production_lead_time_days else 0,
        "capacity_per_hour": float(bom.capacity_per_hour) if bom.capacity_per_hour else 0,
        "is_byproduct": bom.is_byproduct,
        "remark": bom.remark,
        "revision": bom.revision,
        "revision_date": bom.revision_date,
        "status": bom.status.value if hasattr(bom.status, 'value') else str(bom.status) if bom.status else "ACTIVE",
        "active_date": bom.active_date,
        "inactive_date": bom.inactive_date,
        "is_active": bom.is_active,
        "created_at": bom.created_at,
        "updated_at": bom.updated_at
    }


# ==================== SEARCH BOMs ====================
@router.get("/search", response_model=List[dict])
def search_boms(
    parent_search: Optional[str] = None,
    child_search: Optional[str] = None,
    bom_type: Optional[str] = None,
    status: Optional[str] = None,
    revision: Optional[int] = None,
    include_inactive: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """
    Search BOMs by parent item, child item, type, status, or revision
    """
    query = db.query(models.MasterBOM)
    
    if not include_inactive:
        query = query.filter(models.MasterBOM.is_active == True)
    
    # Search by parent item (code or name)
    if parent_search:
        parent_items = db.query(models.MasterItem.id).filter(
            or_(
                models.MasterItem.item_code.ilike(f"%{parent_search}%"),
                models.MasterItem.item_name.ilike(f"%{parent_search}%")
            )
        ).all()
        parent_ids = [p[0] for p in parent_items]
        if parent_ids:
            query = query.filter(models.MasterBOM.parent_item_id.in_(parent_ids))
        else:
            return []
    
    # Search by child item (code or name)
    if child_search:
        child_items = db.query(models.MasterItem.id).filter(
            or_(
                models.MasterItem.item_code.ilike(f"%{child_search}%"),
                models.MasterItem.item_name.ilike(f"%{child_search}%")
            )
        ).all()
        child_ids = [c[0] for c in child_items]
        if child_ids:
            query = query.filter(models.MasterBOM.child_item_id.in_(child_ids))
        else:
            return []
    
    if bom_type:
        query = query.filter(models.MasterBOM.bom_type == bom_type)
    
    if status:
        query = query.filter(models.MasterBOM.status == status)
    
    if revision:
        query = query.filter(models.MasterBOM.revision == revision)
    
    boms = query.order_by(
        models.MasterBOM.parent_item_id, 
        models.MasterBOM.revision.desc(),
        models.MasterBOM.sequence_order
    ).offset(skip).limit(limit).all()
    
    return [get_bom_line_dict(bom, db) for bom in boms]


# ==================== LIST BOMs ====================
@router.get("/", response_model=List[dict])
def list_boms(
    parent_item_id: Optional[int] = None,
    bom_type: Optional[str] = None,
    is_template: Optional[bool] = None,
    status: Optional[str] = None,
    revision: Optional[int] = None,
    include_inactive: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """
    List all BOMs with optional filtering
    """
    query = db.query(models.MasterBOM)
    
    if not include_inactive:
        query = query.filter(models.MasterBOM.is_active == True)
    
    if parent_item_id:
        query = query.filter(models.MasterBOM.parent_item_id == parent_item_id)
    
    if bom_type:
        query = query.filter(models.MasterBOM.bom_type == bom_type)
    
    if is_template is not None:
        query = query.filter(models.MasterBOM.is_template == is_template)
    
    if status:
        query = query.filter(models.MasterBOM.status == status)
    
    if revision:
        query = query.filter(models.MasterBOM.revision == revision)
    
    boms = query.order_by(
        models.MasterBOM.parent_item_id, 
        models.MasterBOM.revision.desc(),
        models.MasterBOM.sequence_order
    ).offset(skip).limit(limit).all()
    
    return [get_bom_line_dict(bom, db) for bom in boms]


# ==================== GET PARENT ITEMS WITH BOMs ====================
@router.get("/parents", response_model=List[dict])
def get_bom_parents(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Get list of parent items that have BOMs (grouped by parent and revision)"""
    query = db.query(models.MasterBOM)
    
    if not include_inactive:
        query = query.filter(models.MasterBOM.is_active == True)
    
    # Get distinct parent items with their revisions
    bom_parents = query.with_entities(
        models.MasterBOM.parent_item_id,
        models.MasterBOM.revision,
        models.MasterBOM.status,
        models.MasterBOM.revision_date
    ).distinct().all()
    
    result = []
    seen = set()
    
    for parent_id, revision, status, revision_date in bom_parents:
        key = (parent_id, revision)
        if key in seen:
            continue
        seen.add(key)
        
        parent = db.query(models.MasterItem).filter(models.MasterItem.id == parent_id).first()
        if parent:
            # Count components for this revision
            component_count = db.query(models.MasterBOM).filter(
                models.MasterBOM.parent_item_id == parent_id,
                models.MasterBOM.revision == revision,
                models.MasterBOM.is_active == True
            ).count()
            
            # Get BOM type (from first component)
            first_bom = db.query(models.MasterBOM).filter(
                models.MasterBOM.parent_item_id == parent_id,
                models.MasterBOM.revision == revision,
                models.MasterBOM.is_active == True
            ).first()
            
            # Get all revisions for this parent
            all_revisions = db.query(models.MasterBOM.revision).filter(
                models.MasterBOM.parent_item_id == parent_id,
                models.MasterBOM.is_active == True
            ).distinct().all()
            revision_list = sorted([r[0] for r in all_revisions], reverse=True)
            
            result.append({
                "id": parent.id,
                "item_code": parent.item_code,
                "item_name": parent.item_name,
                "item_type": parent.item_type.value if hasattr(parent.item_type, 'value') else str(parent.item_type),
                "bom_type": first_bom.bom_type if first_bom else None,
                "component_count": component_count,
                "is_template": first_bom.is_template if first_bom else True,
                "revision": revision,
                "revision_date": revision_date,
                "status": status.value if hasattr(status, 'value') else str(status) if status else "ACTIVE",
                "all_revisions": revision_list
            })
    
    # Sort by item_code then revision (descending)
    result.sort(key=lambda x: (x['item_code'], -x['revision']))
    
    return result


# ==================== GET REVISIONS FOR PARENT ====================
@router.get("/parent/{parent_item_id}/revisions", response_model=List[dict])
def get_bom_revisions(
    parent_item_id: int,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Get all revisions for a parent item"""
    parent = db.query(models.MasterItem).filter(models.MasterItem.id == parent_item_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent item not found")
    
    query = db.query(models.MasterBOM).filter(
        models.MasterBOM.parent_item_id == parent_item_id
    )
    
    if not include_inactive:
        query = query.filter(models.MasterBOM.is_active == True)
    
    # Get distinct revisions
    revisions = query.with_entities(
        models.MasterBOM.revision,
        models.MasterBOM.revision_date,
        models.MasterBOM.status,
        models.MasterBOM.active_date,
        models.MasterBOM.inactive_date
    ).distinct().all()
    
    result = []
    for rev, rev_date, status, active_date, inactive_date in revisions:
        component_count = db.query(models.MasterBOM).filter(
            models.MasterBOM.parent_item_id == parent_item_id,
            models.MasterBOM.revision == rev,
            models.MasterBOM.is_active == True
        ).count()
        
        result.append({
            "parent_item_id": parent_item_id,
            "parent_item_code": parent.item_code,
            "parent_item_name": parent.item_name,
            "revision": rev,
            "revision_date": rev_date,
            "status": status.value if hasattr(status, 'value') else str(status) if status else "ACTIVE",
            "active_date": active_date,
            "inactive_date": inactive_date,
            "component_count": component_count
        })
    
    result.sort(key=lambda x: x['revision'], reverse=True)
    return result


# ==================== GET BOM BY PARENT AND REVISION ====================
@router.get("/parent/{parent_item_id}", response_model=List[dict])
def get_bom_by_parent(
    parent_item_id: int,
    revision: Optional[int] = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Get all BOM components for a specific parent item and revision"""
    parent = db.query(models.MasterItem).filter(models.MasterItem.id == parent_item_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent item not found")
    
    query = db.query(models.MasterBOM).filter(
        models.MasterBOM.parent_item_id == parent_item_id
    )
    
    if not include_inactive:
        query = query.filter(models.MasterBOM.is_active == True)
    
    # If no revision specified, get the latest active revision
    if revision is None:
        latest = query.filter(
            models.MasterBOM.status == models.BOMStatus.ACTIVE
        ).order_by(models.MasterBOM.revision.desc()).first()
        
        if latest:
            revision = latest.revision
        else:
            # Get any revision if no active one
            any_rev = query.order_by(models.MasterBOM.revision.desc()).first()
            revision = any_rev.revision if any_rev else 1
    
    boms = query.filter(
        models.MasterBOM.revision == revision
    ).order_by(models.MasterBOM.sequence_order).all()
    
    return [get_bom_line_dict(bom, db) for bom in boms]


# ==================== GET BOM LINE ====================
@router.get("/{bom_id}", response_model=dict)
def get_bom(
    bom_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Get a specific BOM line by ID"""
    bom = db.query(models.MasterBOM).filter(models.MasterBOM.id == bom_id).first()
    if not bom:
        raise HTTPException(status_code=404, detail="BOM line not found")
    
    return get_bom_line_dict(bom, db)


# ==================== CREATE BOM LINE ====================
@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_bom(
    bom_data: schemas.BOMCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Create a new BOM line"""
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Only Admin/Manager can create BOMs")
    
    # Validate parent item
    parent = db.query(models.MasterItem).filter(models.MasterItem.id == bom_data.parent_item_id).first()
    if not parent:
        raise HTTPException(status_code=400, detail="Parent item not found")
    
    # Validate child item
    child = db.query(models.MasterItem).filter(models.MasterItem.id == bom_data.child_item_id).first()
    if not child:
        raise HTTPException(status_code=400, detail="Child item not found")
    
    # Check for circular reference
    if bom_data.parent_item_id == bom_data.child_item_id:
        raise HTTPException(status_code=400, detail="Parent and child cannot be the same item")
    
    # Validate locations if provided
    if bom_data.production_location_id:
        prod_loc = db.query(models.LocationMaster).filter(models.LocationMaster.id == bom_data.production_location_id).first()
        if not prod_loc:
            raise HTTPException(status_code=400, detail="Production location not found")
    
    if bom_data.storage_location_id:
        stor_loc = db.query(models.LocationMaster).filter(models.LocationMaster.id == bom_data.storage_location_id).first()
        if not stor_loc:
            raise HTTPException(status_code=400, detail="Storage location not found")
    
    # Check for duplicate in same revision
    existing = db.query(models.MasterBOM).filter(
        models.MasterBOM.parent_item_id == bom_data.parent_item_id,
        models.MasterBOM.child_item_id == bom_data.child_item_id,
        models.MasterBOM.revision == bom_data.revision,
        models.MasterBOM.is_active == True
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"This component already exists in revision {bom_data.revision}")
    
    # Validate BOM type
    valid_types = ['ASSEMBLY', 'FORMULA', 'MODULAR', 'TAILOR_MADE']
    if bom_data.bom_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid BOM type. Must be one of: {valid_types}")
    
    # Validate status
    valid_statuses = ['ACTIVE', 'INACTIVE']
    if bom_data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    # Create BOM line
    db_bom = models.MasterBOM(
        parent_item_id=bom_data.parent_item_id,
        child_item_id=bom_data.child_item_id,
        bom_type=bom_data.bom_type,
        is_template=bom_data.is_template,
        sequence_order=bom_data.sequence_order,
        quantity=bom_data.quantity,
        percentage=bom_data.percentage,
        is_optional=bom_data.is_optional,
        scrap_factor=bom_data.scrap_factor or 0,
        production_location_id=bom_data.production_location_id,
        storage_location_id=bom_data.storage_location_id,
        machine_id=bom_data.machine_id,
        production_lead_time_days=bom_data.production_lead_time_days,
        capacity_per_hour=bom_data.capacity_per_hour,
        is_byproduct=bom_data.is_byproduct,
        remark=bom_data.remark,
        revision=bom_data.revision,
        status=models.BOMStatus(bom_data.status),
        active_date=bom_data.active_date,
        inactive_date=bom_data.inactive_date,
        is_active=True,
        created_by=current_user.id
    )
    
    db.add(db_bom)
    db.commit()
    db.refresh(db_bom)
    
    return get_bom_line_dict(db_bom, db)


# ==================== UPDATE BOM LINE ====================
@router.put("/{bom_id}", response_model=dict)
def update_bom(
    bom_id: int,
    bom_data: schemas.BOMUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Update an existing BOM line"""
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Only Admin/Manager can update BOMs")
    
    db_bom = db.query(models.MasterBOM).filter(models.MasterBOM.id == bom_id).first()
    if not db_bom:
        raise HTTPException(status_code=404, detail="BOM line not found")
    
    # Update only provided fields
    update_data = bom_data.dict(exclude_unset=True, exclude_none=True)
    
    # Handle status enum conversion
    if 'status' in update_data:
        update_data['status'] = models.BOMStatus(update_data['status'])
    
    for field, value in update_data.items():
        setattr(db_bom, field, value)
    
    db.commit()
    db.refresh(db_bom)
    
    return get_bom_line_dict(db_bom, db)


# ==================== CREATE NEW REVISION ====================
@router.post("/revision/new/{parent_item_id}", response_model=dict)
def create_new_revision(
    parent_item_id: int,
    source_revision: Optional[int] = None,
    remark: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """
    Create a new BOM revision for a parent item.
    - Optionally copy from an existing revision
    - Auto-deactivates previous revisions (keeps MAX_REVISIONS)
    """
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Only Admin/Manager can create revisions")
    
    parent = db.query(models.MasterItem).filter(models.MasterItem.id == parent_item_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent item not found")
    
    # Get current max revision
    max_rev = db.query(func.max(models.MasterBOM.revision)).filter(
        models.MasterBOM.parent_item_id == parent_item_id,
        models.MasterBOM.is_active == True
    ).scalar() or 0
    
    new_revision = max_rev + 1
    
    # If copying from existing revision
    if source_revision:
        source_boms = db.query(models.MasterBOM).filter(
            models.MasterBOM.parent_item_id == parent_item_id,
            models.MasterBOM.revision == source_revision,
            models.MasterBOM.is_active == True
        ).all()
        
        if not source_boms:
            raise HTTPException(status_code=404, detail=f"Source revision {source_revision} not found")
        
        # Copy BOM lines to new revision
        for source in source_boms:
            new_bom = models.MasterBOM(
                parent_item_id=parent_item_id,
                child_item_id=source.child_item_id,
                bom_type=source.bom_type,
                is_template=source.is_template,
                sequence_order=source.sequence_order,
                quantity=source.quantity,
                percentage=source.percentage,
                is_optional=source.is_optional,
                scrap_factor=source.scrap_factor,
                production_location_id=source.production_location_id,
                storage_location_id=source.storage_location_id,
                machine_id=source.machine_id,
                production_lead_time_days=source.production_lead_time_days,
                capacity_per_hour=source.capacity_per_hour,
                is_byproduct=source.is_byproduct,
                remark=remark or source.remark,
                revision=new_revision,
                status=models.BOMStatus.ACTIVE,
                is_active=True,
                created_by=current_user.id
            )
            db.add(new_bom)
    
    # Deactivate previous revisions (set status to INACTIVE)
    db.query(models.MasterBOM).filter(
        models.MasterBOM.parent_item_id == parent_item_id,
        models.MasterBOM.revision < new_revision,
        models.MasterBOM.is_active == True
    ).update({
        "status": models.BOMStatus.INACTIVE,
        "inactive_date": date.today()
    })
    
    # Keep only MAX_REVISIONS - soft delete old ones
    all_revisions = db.query(models.MasterBOM.revision).filter(
        models.MasterBOM.parent_item_id == parent_item_id,
        models.MasterBOM.is_active == True
    ).distinct().order_by(models.MasterBOM.revision.desc()).all()
    
    revision_numbers = [r[0] for r in all_revisions]
    if len(revision_numbers) > MAX_REVISIONS:
        old_revisions = revision_numbers[MAX_REVISIONS:]
        db.query(models.MasterBOM).filter(
            models.MasterBOM.parent_item_id == parent_item_id,
            models.MasterBOM.revision.in_(old_revisions)
        ).update({"is_active": False}, synchronize_session=False)
    
    db.commit()
    
    return {
        "message": f"Created revision {new_revision} for {parent.item_code}",
        "parent_item_id": parent_item_id,
        "new_revision": new_revision,
        "copied_from": source_revision
    }


# ==================== COPY BOM TO NEW REVISION ====================
@router.post("/copy-revision/{parent_item_id}", response_model=dict)
def copy_bom_to_revision(
    parent_item_id: int,
    source_revision: int,
    remark: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Copy an existing BOM revision to create a new one"""
    return create_new_revision(
        parent_item_id=parent_item_id,
        source_revision=source_revision,
        remark=remark,
        db=db,
        current_user=current_user
    )


# ==================== SET REVISION STATUS ====================
@router.patch("/revision/status/{parent_item_id}/{revision}", response_model=dict)
def set_revision_status(
    parent_item_id: int,
    revision: int,
    new_status: str,
    active_date: Optional[date] = None,
    inactive_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Set the status of a BOM revision (ACTIVE/INACTIVE)"""
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Only Admin/Manager can change revision status")
    
    if new_status not in ['ACTIVE', 'INACTIVE']:
        raise HTTPException(status_code=400, detail="Status must be ACTIVE or INACTIVE")
    
    boms = db.query(models.MasterBOM).filter(
        models.MasterBOM.parent_item_id == parent_item_id,
        models.MasterBOM.revision == revision,
        models.MasterBOM.is_active == True
    ).all()
    
    if not boms:
        raise HTTPException(status_code=404, detail="Revision not found")
    
    # If activating, deactivate other revisions
    if new_status == 'ACTIVE':
        db.query(models.MasterBOM).filter(
            models.MasterBOM.parent_item_id == parent_item_id,
            models.MasterBOM.revision != revision,
            models.MasterBOM.is_active == True
        ).update({
            "status": models.BOMStatus.INACTIVE,
            "inactive_date": date.today()
        })
    
    # Update the target revision
    for bom in boms:
        bom.status = models.BOMStatus(new_status)
        if new_status == 'ACTIVE':
            bom.active_date = active_date or date.today()
            bom.inactive_date = None
        else:
            bom.inactive_date = inactive_date or date.today()
    
    db.commit()
    
    return {
        "message": f"Revision {revision} set to {new_status}",
        "parent_item_id": parent_item_id,
        "revision": revision,
        "status": new_status
    }


# ==================== DELETE BOM LINE ====================
@router.delete("/{bom_id}", status_code=status.HTTP_200_OK)
def delete_bom(
    bom_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Soft delete a BOM line"""
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Only Admin/Manager can delete BOMs")
    
    db_bom = db.query(models.MasterBOM).filter(models.MasterBOM.id == bom_id).first()
    if not db_bom:
        raise HTTPException(status_code=404, detail="BOM line not found")
    
    db_bom.is_active = False
    db.commit()
    
    return {"message": "BOM line deleted successfully"}


# ==================== DELETE ENTIRE BOM/REVISION ====================
@router.delete("/parent/{parent_item_id}", status_code=status.HTTP_200_OK)
def delete_entire_bom(
    parent_item_id: int,
    revision: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Delete all BOM lines for a parent item (optionally specific revision)"""
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Only Admin/Manager can delete BOMs")
    
    query = db.query(models.MasterBOM).filter(
        models.MasterBOM.parent_item_id == parent_item_id,
        models.MasterBOM.is_active == True
    )
    
    if revision:
        query = query.filter(models.MasterBOM.revision == revision)
    
    boms = query.all()
    
    if not boms:
        raise HTTPException(status_code=404, detail="No BOM found")
    
    count = 0
    for bom in boms:
        bom.is_active = False
        count += 1
    
    db.commit()
    
    msg = f"Deleted {count} BOM lines"
    if revision:
        msg += f" from revision {revision}"
    
    return {"message": msg}


# ==================== COPY BOM TO ANOTHER ITEM ====================
@router.post("/copy/{source_parent_id}/{target_parent_id}", response_model=dict)
def copy_bom(
    source_parent_id: int,
    target_parent_id: int,
    source_revision: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Copy BOM from one parent item to another"""
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Only Admin/Manager can copy BOMs")
    
    # Get source BOMs
    query = db.query(models.MasterBOM).filter(
        models.MasterBOM.parent_item_id == source_parent_id,
        models.MasterBOM.is_active == True
    )
    
    if source_revision:
        query = query.filter(models.MasterBOM.revision == source_revision)
    else:
        # Get latest active revision
        latest = query.filter(models.MasterBOM.status == models.BOMStatus.ACTIVE).order_by(
            models.MasterBOM.revision.desc()
        ).first()
        if latest:
            query = query.filter(models.MasterBOM.revision == latest.revision)
    
    source_boms = query.all()
    
    if not source_boms:
        raise HTTPException(status_code=404, detail="Source BOM not found")
    
    # Validate target
    target_item = db.query(models.MasterItem).filter(models.MasterItem.id == target_parent_id).first()
    if not target_item:
        raise HTTPException(status_code=400, detail="Target item not found")
    
    # Check if target already has BOM
    existing_bom = db.query(models.MasterBOM).filter(
        models.MasterBOM.parent_item_id == target_parent_id,
        models.MasterBOM.is_active == True
    ).first()
    if existing_bom:
        raise HTTPException(status_code=400, detail="Target item already has a BOM. Delete it first.")
    
    # Copy BOM lines
    count = 0
    for source in source_boms:
        new_bom = models.MasterBOM(
            parent_item_id=target_parent_id,
            child_item_id=source.child_item_id,
            bom_type=source.bom_type,
            is_template=source.is_template,
            sequence_order=source.sequence_order,
            quantity=source.quantity,
            percentage=source.percentage,
            is_optional=source.is_optional,
            scrap_factor=source.scrap_factor,
            production_location_id=source.production_location_id,
            storage_location_id=source.storage_location_id,
            machine_id=source.machine_id,
            production_lead_time_days=source.production_lead_time_days,
            capacity_per_hour=source.capacity_per_hour,
            is_byproduct=source.is_byproduct,
            remark=source.remark,
            revision=1,  # Start with revision 1 for new item
            status=models.BOMStatus.ACTIVE,
            is_active=True,
            created_by=current_user.id
        )
        db.add(new_bom)
        count += 1
    
    db.commit()
    
    return {"message": f"Copied {count} BOM lines to {target_item.item_code}"}


# ==================== EXPORT BOMs ====================
@router.post("/export")
def export_boms(
    request: schemas.BOMExportRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Export BOMs to CSV"""
    query = db.query(models.MasterBOM)
    
    if not request.include_inactive:
        query = query.filter(models.MasterBOM.is_active == True)
    
    if request.parent_item_ids:
        query = query.filter(models.MasterBOM.parent_item_id.in_(request.parent_item_ids))
    
    if not request.include_all_revisions:
        # Only get latest active revision per parent
        # This is simplified - in production, use a subquery
        pass
    
    boms = query.order_by(
        models.MasterBOM.parent_item_id,
        models.MasterBOM.revision.desc(),
        models.MasterBOM.sequence_order
    ).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Parent Item Code', 'Parent Item Name', 'Child Item Code', 'Child Item Name',
        'BOM Type', 'Quantity', 'UOM', 'Percentage', 'Scrap Factor', 'Is Optional',
        'Is Byproduct', 'Production Location', 'Storage Location', 'Remark',
        'Revision', 'Revision Date', 'Status', 'Active Date', 'Inactive Date'
    ])
    
    # Data
    for bom in boms:
        parent = db.query(models.MasterItem).filter(models.MasterItem.id == bom.parent_item_id).first()
        child = db.query(models.MasterItem).filter(models.MasterItem.id == bom.child_item_id).first()
        prod_loc = db.query(models.LocationMaster).filter(models.LocationMaster.id == bom.production_location_id).first() if bom.production_location_id else None
        stor_loc = db.query(models.LocationMaster).filter(models.LocationMaster.id == bom.storage_location_id).first() if bom.storage_location_id else None
        
        writer.writerow([
            parent.item_code if parent else '',
            parent.item_name if parent else '',
            child.item_code if child else '',
            child.item_name if child else '',
            bom.bom_type,
            float(bom.quantity),
            child.unit_of_measure if child else '',
            float(bom.percentage) if bom.percentage else '',
            float(bom.scrap_factor) if bom.scrap_factor else 0,
            'Yes' if bom.is_optional else 'No',
            'Yes' if bom.is_byproduct else 'No',
            prod_loc.location_code if prod_loc else '',
            stor_loc.location_code if stor_loc else '',
            bom.remark or '',
            bom.revision,
            bom.revision_date.strftime('%Y-%m-%d %H:%M') if bom.revision_date else '',
            bom.status.value if hasattr(bom.status, 'value') else str(bom.status) if bom.status else 'ACTIVE',
            bom.active_date.strftime('%Y-%m-%d') if bom.active_date else '',
            bom.inactive_date.strftime('%Y-%m-%d') if bom.inactive_date else ''
        ])
    
    output.seek(0)
    
    # Return as downloadable file
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=bom_export_{get_utc_now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )


# ==================== GET LOCATIONS FOR DROPDOWN ====================
@router.get("/locations/list", response_model=List[dict])
def get_locations_for_bom(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Get list of locations for production/storage selection"""
    locations = db.query(models.LocationMaster).all()
    
    return [{
        "id": loc.id,
        "location_code": loc.location_code,
        # LocationMaster does not have dedicated name/type columns yet,
        # so use existing attributes while keeping frontend contract.
        "location_name": getattr(loc, "location_name", loc.location_code),
        "warehouse_id": loc.warehouse_id,
        "location_type": getattr(loc, "zone_type", None),
        "condition_type": getattr(loc, "condition_type", None).value if getattr(loc, "condition_type", None) else None
    } for loc in locations]


# ==================== BOM EXPLOSION ALGORITHM ====================
def _explode_bom_recursive(
    db: Session,
    parent_item_id: int,
    quantity: Decimal,
    revision: Optional[int],
    include_optional: bool,
    include_byproducts: bool,
    max_levels: int,
    current_level: int,
    visited_items: set,
    results: list
) -> None:
    """
    Recursive BOM explosion helper function.
    
    Args:
        db: Database session
        parent_item_id: ID of the parent item to explode
        quantity: Quantity to produce
        revision: Specific revision to use (None = active revision)
        include_optional: Whether to include optional components
        include_byproducts: Whether to include by-products
        max_levels: Maximum recursion depth
        current_level: Current level in the BOM tree
        visited_items: Set of item IDs already visited (circular reference detection)
        results: List to accumulate explosion results
    """
    # Check max depth
    if current_level > max_levels:
        return
    
    # Check for circular reference
    if parent_item_id in visited_items:
        return
    
    # Add to visited set for this branch
    visited_items.add(parent_item_id)
    
    # Get parent item info
    parent_item = db.query(models.MasterItem).filter(
        models.MasterItem.id == parent_item_id
    ).first()
    
    if not parent_item:
        visited_items.discard(parent_item_id)
        return
    
    # Build query for BOM components
    query = db.query(models.MasterBOM).filter(
        models.MasterBOM.parent_item_id == parent_item_id,
        models.MasterBOM.is_active == True
    )
    
    # Filter by revision
    if revision:
        query = query.filter(models.MasterBOM.revision == revision)
    else:
        # Get active revision only
        query = query.filter(models.MasterBOM.status == models.BOMStatus.ACTIVE)
    
    # Filter optional items
    if not include_optional:
        query = query.filter(models.MasterBOM.is_optional == False)
    
    # Filter by-products
    if not include_byproducts:
        query = query.filter(models.MasterBOM.is_byproduct == False)
    
    # Order by sequence
    bom_lines = query.order_by(models.MasterBOM.sequence_order).all()
    
    for bom in bom_lines:
        # Get child item info
        child_item = db.query(models.MasterItem).filter(
            models.MasterItem.id == bom.child_item_id
        ).first()
        
        if not child_item:
            continue
        
        # Calculate quantities based on BOM type
        if bom.bom_type == 'FORMULA' and bom.percentage:
            # Formula: percentage-based calculation
            bom_qty = Decimal(str(bom.percentage)) / Decimal("100")
            required_qty = quantity * bom_qty
        else:
            # Assembly, Modular, Tailor-Made: fixed quantity
            bom_qty = Decimal(str(bom.quantity))
            required_qty = quantity * bom_qty
        
        # Calculate scrap
        scrap_factor = Decimal(str(bom.scrap_factor)) if bom.scrap_factor else Decimal("0")
        scrap_qty = required_qty * (scrap_factor / Decimal("100"))
        total_qty = required_qty + scrap_qty
        
        # Get location info
        prod_loc = None
        stor_loc = None
        if bom.production_location_id:
            loc = db.query(models.LocationMaster).filter(
                models.LocationMaster.id == bom.production_location_id
            ).first()
            prod_loc = loc.location_code if loc else None
        if bom.storage_location_id:
            loc = db.query(models.LocationMaster).filter(
                models.LocationMaster.id == bom.storage_location_id
            ).first()
            stor_loc = loc.location_code if loc else None
        
        # Create explosion line
        explosion_line = {
            "level": current_level,
            "item_id": child_item.id,
            "item_code": child_item.item_code,
            "item_name": child_item.item_name,
            "item_type": child_item.item_type.value if hasattr(child_item.item_type, 'value') else str(child_item.item_type),
            "unit_of_measure": child_item.unit_of_measure,
            "bom_quantity": float(bom_qty),
            "required_quantity": float(required_qty),
            "scrap_factor": float(scrap_factor),
            "scrap_quantity": float(scrap_qty),
            "total_quantity": float(total_qty),
            "bom_type": bom.bom_type,
            "is_optional": bom.is_optional,
            "is_byproduct": bom.is_byproduct,
            "sequence_order": bom.sequence_order,
            "percentage": float(bom.percentage) if bom.percentage else None,
            "production_location": prod_loc,
            "storage_location": stor_loc,
            "parent_item_id": parent_item_id,
            "parent_item_code": parent_item.item_code,
            "bom_id": bom.id,
            "revision": bom.revision,
            "remark": bom.remark
        }
        
        results.append(explosion_line)
        
        # Check if child item has its own BOM (sub-assembly)
        # Only recurse if item is WIP or FINISHED_GOOD (can have sub-BOMs)
        child_has_bom = db.query(models.MasterBOM).filter(
            models.MasterBOM.parent_item_id == child_item.id,
            models.MasterBOM.is_active == True
        ).first()
        
        if child_has_bom and child_item.id not in visited_items:
            # Recursively explode this component
            _explode_bom_recursive(
                db=db,
                parent_item_id=child_item.id,
                quantity=total_qty,  # Use total qty (including scrap) for sub-explosion
                revision=None,  # Use active revision for sub-components
                include_optional=include_optional,
                include_byproducts=include_byproducts,
                max_levels=max_levels,
                current_level=current_level + 1,
                visited_items=visited_items.copy(),  # Copy to allow different branches
                results=results
            )
    
    # Remove from visited set after processing this branch
    visited_items.discard(parent_item_id)


@router.post("/explode", response_model=dict)
def explode_bom(
    request: schemas.BOMExplosionRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """
    Explode a BOM to get all required materials at all levels.
    
    This algorithm:
    1. Takes a parent item and desired quantity
    2. Recursively traverses the BOM tree
    3. Calculates total quantities needed (with scrap factors)
    4. Handles different BOM types (Assembly, Formula, Modular, Tailor-Made)
    5. Returns flat list of all materials needed
    6. Optionally returns consolidated view (same items summed)
    
    BOM Types:
    - ASSEMBLY: Standard BOM with fixed quantities per unit
    - FORMULA: Uses percentages (e.g., 30% of total batch weight)
    - MODULAR: Has optional components that can be included/excluded
    - TAILOR_MADE: Custom configuration (works like ASSEMBLY)
    """
    # Validate parent item exists
    parent_item = db.query(models.MasterItem).filter(
        models.MasterItem.id == request.parent_item_id
    ).first()
    
    if not parent_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent item with ID {request.parent_item_id} not found"
        )
    
    # Check if parent item has a BOM
    bom_exists = db.query(models.MasterBOM).filter(
        models.MasterBOM.parent_item_id == request.parent_item_id,
        models.MasterBOM.is_active == True
    ).first()
    
    if not bom_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No BOM found for item {parent_item.item_code}"
        )
    
    # Determine revision to use
    revision = request.revision
    if not revision:
        # Get active revision
        active_bom = db.query(models.MasterBOM).filter(
            models.MasterBOM.parent_item_id == request.parent_item_id,
            models.MasterBOM.is_active == True,
            models.MasterBOM.status == models.BOMStatus.ACTIVE
        ).first()
        revision = active_bom.revision if active_bom else 1
    
    # Run explosion algorithm
    results = []
    visited = set()
    
    _explode_bom_recursive(
        db=db,
        parent_item_id=request.parent_item_id,
        quantity=request.quantity,
        revision=revision,
        include_optional=request.include_optional,
        include_byproducts=request.include_byproducts,
        max_levels=request.max_levels,
        current_level=1,
        visited_items=visited,
        results=results
    )
    
    # Calculate statistics
    total_levels = max([r["level"] for r in results], default=0)
    total_components = len(results)
    
    # Find raw materials (items that don't have their own BOMs)
    raw_materials = []
    for r in results:
        child_bom = db.query(models.MasterBOM).filter(
            models.MasterBOM.parent_item_id == r["item_id"],
            models.MasterBOM.is_active == True
        ).first()
        if not child_bom:
            raw_materials.append(r)
    
    has_optional = any(r["is_optional"] for r in results)
    has_byproducts = any(r["is_byproduct"] for r in results)
    
    # Create consolidated view (sum quantities for same items)
    consolidated = {}
    for r in results:
        item_key = r["item_id"]
        if item_key in consolidated:
            consolidated[item_key]["total_quantity"] += r["total_quantity"]
            consolidated[item_key]["required_quantity"] += r["required_quantity"]
            consolidated[item_key]["scrap_quantity"] += r["scrap_quantity"]
            consolidated[item_key]["occurrences"] += 1
        else:
            consolidated[item_key] = {
                "item_id": r["item_id"],
                "item_code": r["item_code"],
                "item_name": r["item_name"],
                "item_type": r["item_type"],
                "unit_of_measure": r["unit_of_measure"],
                "total_quantity": r["total_quantity"],
                "required_quantity": r["required_quantity"],
                "scrap_quantity": r["scrap_quantity"],
                "occurrences": 1,
                "is_raw_material": not db.query(models.MasterBOM).filter(
                    models.MasterBOM.parent_item_id == r["item_id"],
                    models.MasterBOM.is_active == True
                ).first()
            }
    
    consolidated_list = sorted(
        consolidated.values(),
        key=lambda x: (not x["is_raw_material"], x["item_code"])
    )
    
    return {
        "parent_item_id": parent_item.id,
        "parent_item_code": parent_item.item_code,
        "parent_item_name": parent_item.item_name,
        "requested_quantity": float(request.quantity),
        "revision": revision,
        "explosion_date": get_utc_now(),
        "total_levels": total_levels,
        "total_components": total_components,
        "total_raw_materials": len(raw_materials),
        "has_optional_items": has_optional,
        "has_byproducts": has_byproducts,
        "lines": results,
        "consolidated": consolidated_list,
        "raw_materials_only": [
            {
                "item_id": c["item_id"],
                "item_code": c["item_code"],
                "item_name": c["item_name"],
                "unit_of_measure": c["unit_of_measure"],
                "total_quantity": c["total_quantity"]
            }
            for c in consolidated_list if c["is_raw_material"]
        ]
    }


@router.get("/explode/{parent_item_id}", response_model=dict)
def explode_bom_simple(
    parent_item_id: int,
    quantity: Decimal = Decimal("1.0"),
    include_optional: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """
    Simple GET endpoint for BOM explosion.
    Uses POST /explode for full control over options.
    """
    request = schemas.BOMExplosionRequest(
        parent_item_id=parent_item_id,
        quantity=quantity,
        include_optional=include_optional
    )
    return explode_bom(request, db, current_user)
