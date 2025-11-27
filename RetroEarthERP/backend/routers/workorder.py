"""
Work Order Router - Production Order Management
Features: Auto-generation from BOM, material tracking, completion workflow
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from decimal import Decimal
from datetime import date, timedelta
from utils.datetime_utils import get_utc_now

from database import get_db
import models
import schemas
import auth as auth_utils

router = APIRouter()


# ==================== HELPER FUNCTIONS ====================
def _generate_job_no(db: Session) -> str:
    """Generate unique job number"""
    count = db.query(models.TrnJobOrderHead).count()
    now = get_utc_now()
    return f"WO-{now.strftime('%Y%m%d')}-{count + 1:05d}"


def _get_work_order_response(db: Session, wo: models.TrnJobOrderHead) -> dict:
    """Convert Work Order model to response dict with enriched data"""
    # Get item info
    item = db.query(models.MasterItem).filter(models.MasterItem.id == wo.item_id).first()
    
    # Get warehouse info
    warehouse = db.query(models.MasterWarehouse).filter(
        models.MasterWarehouse.id == wo.warehouse_id
    ).first()
    
    # Get creator info
    creator = db.query(models.User).filter(models.User.id == wo.created_by).first()
    
    # Get material details
    details = db.query(models.TrnJobOrderDetail).filter(
        models.TrnJobOrderDetail.job_id == wo.id
    ).all()
    
    material_details = []
    total_consumed_percent = Decimal("0")
    
    for detail in details:
        detail_item = db.query(models.MasterItem).filter(
            models.MasterItem.id == detail.item_id
        ).first()
        
        qty_remaining = detail.qty_required - detail.qty_consumed
        percent_consumed = (detail.qty_consumed / detail.qty_required * 100) if detail.qty_required > 0 else Decimal("0")
        total_consumed_percent += percent_consumed
        
        material_details.append({
            "id": detail.id,
            "job_id": detail.job_id,
            "item_id": detail.item_id,
            "item_code": detail_item.item_code if detail_item else "",
            "item_name": detail_item.item_name if detail_item else "",
            "unit_of_measure": detail_item.unit_of_measure if detail_item else "",
            "qty_required": float(detail.qty_required),
            "qty_consumed": float(detail.qty_consumed),
            "qty_remaining": float(qty_remaining),
            "percent_consumed": float(percent_consumed)
        })
    
    # Calculate statistics
    percent_complete = (wo.qty_produced / wo.qty_planned * 100) if wo.qty_planned > 0 else Decimal("0")
    materials_consumed_avg = (total_consumed_percent / len(details)) if details else Decimal("0")
    
    # Check if overdue
    today = date.today()
    is_overdue = wo.end_date and today > wo.end_date and wo.status != models.JobStatus.COMPLETED
    days_remaining = (wo.end_date - today).days if wo.end_date else None
    
    return {
        "id": wo.id,
        "job_no": wo.job_no,
        "item_id": wo.item_id,
        "item_code": item.item_code if item else "",
        "item_name": item.item_name if item else "",
        "unit_of_measure": item.unit_of_measure if item else "",
        "qty_planned": float(wo.qty_planned),
        "qty_produced": float(wo.qty_produced),
        "start_date": wo.start_date,
        "end_date": wo.end_date,
        "status": wo.status.value if hasattr(wo.status, 'value') else str(wo.status),
        "warehouse_id": wo.warehouse_id,
        "warehouse_code": warehouse.warehouse_code if warehouse else "",
        "warehouse_name": warehouse.warehouse_name if warehouse else "",
        "created_by": wo.created_by,
        "created_by_name": creator.full_name if creator else "",
        "created_at": wo.created_at,
        "created_at": wo.created_at,
        "lot_number": wo.lot_number,
        "materials": material_details,
        "percent_complete": float(percent_complete),
        "materials_consumed_percent": float(materials_consumed_avg),
        "is_overdue": is_overdue,
        "days_remaining": days_remaining
    }


# ==================== GENERATE WORK ORDER FROM BOM ====================
@router.post("/generate-from-bom", response_model=dict, status_code=status.HTTP_201_CREATED)
def generate_work_order_from_bom(
    request: schemas.WorkOrderGenerateFromBOM,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_active_admin)
):
    """
    Generate Work Order with material requirements from BOM explosion.
    
    This endpoint:
    1. Validates the item has a BOM
    2. Runs BOM explosion to get all material requirements
    3. Creates Work Order header
    4. Creates Work Order detail lines for materials
    5. Returns the complete Work Order with material list
    """
    # Validate item exists
    item = db.query(models.MasterItem).filter(models.MasterItem.id == request.item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {request.item_id} not found"
        )
    
    # Validate warehouse exists
    warehouse = db.query(models.MasterWarehouse).filter(
        models.MasterWarehouse.id == request.warehouse_id
    ).first()
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Warehouse with ID {request.warehouse_id} not found"
        )
    
    # Check if item has a BOM
    bom_exists = db.query(models.MasterBOM).filter(
        models.MasterBOM.parent_item_id == request.item_id,
        models.MasterBOM.is_active == True
    ).first()
    
    if not bom_exists and request.auto_generate_material_lines:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Item {item.item_code} does not have a BOM. Cannot auto-generate material lines."
        )
    
    # Create Work Order header
    job_no = _generate_job_no(db)
    
    work_order = models.TrnJobOrderHead(
        job_no=job_no,
        item_id=request.item_id,
        qty_planned=request.qty_planned,
        qty_produced=Decimal("0"),
        start_date=request.start_date,
        end_date=request.end_date,
        status=models.JobStatus.PLANNED,
        warehouse_id=request.warehouse_id,
        created_by=current_user.id
    )
    db.add(work_order)
    db.flush()  # Get ID without committing
    
    # Generate material lines from BOM explosion
    if request.auto_generate_material_lines:
        # Import BOM explosion function
        from routers import bom as bom_router
        
        explosion_request = schemas.BOMExplosionRequest(
            parent_item_id=request.item_id,
            quantity=request.qty_planned,
            revision=request.bom_revision,
            include_optional=request.include_optional,
            include_byproducts=False,  # Don't include by-products in material requirements
            max_levels=10
        )
        
        explosion_result = bom_router.explode_bom(explosion_request, db, current_user)
        
        # Use consolidated view to avoid duplicate materials
        for material in explosion_result.get("consolidated", []):
            # Only add if it's a raw material (doesn't have its own BOM)
            if material.get("is_raw_material", False):
                detail = models.TrnJobOrderDetail(
                    job_id=work_order.id,
                    item_id=material["item_id"],
                    qty_required=Decimal(str(material["total_quantity"])),
                    qty_consumed=Decimal("0")
                )
                db.add(detail)
    
    db.commit()
    db.refresh(work_order)
    
    return _get_work_order_response(db, work_order)


# ==================== CRUD OPERATIONS ====================
@router.get("/", response_model=List[dict])
def list_work_orders(
    status: Optional[str] = None,
    item_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    start_date_from: Optional[date] = None,
    start_date_to: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """List Work Orders with optional filters"""
    query = db.query(models.TrnJobOrderHead)
    
    if status:
        try:
            status_enum = models.JobStatus[status.upper()]
            query = query.filter(models.TrnJobOrderHead.status == status_enum)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}. Valid values: {[s.name for s in models.JobStatus]}"
            )
    
    if item_id:
        query = query.filter(models.TrnJobOrderHead.item_id == item_id)
    
    if warehouse_id:
        query = query.filter(models.TrnJobOrderHead.warehouse_id == warehouse_id)
    
    if start_date_from:
        query = query.filter(models.TrnJobOrderHead.start_date >= start_date_from)
    
    if start_date_to:
        query = query.filter(models.TrnJobOrderHead.start_date <= start_date_to)
    
    work_orders = query.order_by(models.TrnJobOrderHead.created_at.desc()).offset(skip).limit(limit).all()
    
    return [_get_work_order_response(db, wo) for wo in work_orders]


@router.get("/{job_id}", response_model=dict)
def get_work_order(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Get single Work Order by ID"""
    wo = db.query(models.TrnJobOrderHead).filter(models.TrnJobOrderHead.id == job_id).first()
    
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order with ID {job_id} not found"
        )
    
    return _get_work_order_response(db, wo)


@router.put("/{job_id}", response_model=dict)
def update_work_order(
    job_id: int,
    request: schemas.WorkOrderUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_active_admin)
):
    """Update Work Order"""
    wo = db.query(models.TrnJobOrderHead).filter(models.TrnJobOrderHead.id == job_id).first()
    
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order with ID {job_id} not found"
        )
    
    # Update fields
    if request.qty_planned is not None:
        wo.qty_planned = request.qty_planned
    
    if request.qty_produced is not None:
        wo.qty_produced = request.qty_produced
    
    if request.start_date is not None:
        wo.start_date = request.start_date
    
    if request.end_date is not None:
        wo.end_date = request.end_date
    
    if request.status is not None:
        try:
            wo.status = models.JobStatus[request.status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {request.status}"
            )
    
    db.commit()
    db.refresh(wo)
    
    return _get_work_order_response(db, wo)


# ==================== MATERIAL CONSUMPTION ====================
@router.post("/consume-material", status_code=status.HTTP_200_OK)
def consume_material(
    request: schemas.MaterialConsumption,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """
    Record material consumption for a Work Order.
    Updates the qty_consumed in work order detail line.
    """
    # Validate work order exists
    wo = db.query(models.TrnJobOrderHead).filter(models.TrnJobOrderHead.id == request.job_id).first()
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order with ID {request.job_id} not found"
        )
    
    # Find material line
    detail = db.query(models.TrnJobOrderDetail).filter(
        and_(
            models.TrnJobOrderDetail.job_id == request.job_id,
            models.TrnJobOrderDetail.item_id == request.item_id
        )
    ).first()
    
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material item {request.item_id} not found in Work Order {request.job_id}"
        )
    
    # Update consumed quantity
    new_consumed = detail.qty_consumed + request.qty_consumed
    
    if new_consumed > detail.qty_required:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot consume {request.qty_consumed}. Would exceed required quantity. " +
                   f"Required: {detail.qty_required}, Already consumed: {detail.qty_consumed}"
        )
    
    detail.qty_consumed = new_consumed
    if request.lot_number:
        detail.lot_number = request.lot_number
    
    # Update Work Order status to IN_PROGRESS if still PLANNED
    if wo.status == models.JobStatus.PLANNED:
        wo.status = models.JobStatus.IN_PROGRESS
    
    db.commit()
    
    return {
        "message": "Material consumed successfully",
        "job_id": request.job_id,
        "item_id": request.item_id,
        "qty_consumed": float(request.qty_consumed),
        "total_consumed": float(new_consumed),
        "qty_required": float(detail.qty_required),
        "qty_remaining": float(detail.qty_required - new_consumed)
    }


@router.post("/issue-materials", status_code=status.HTTP_200_OK)
def issue_materials(
    request: schemas.MaterialIssue,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """
    Issue multiple materials to Work Order at once.
    Batch version of consume_material.
    """
    wo = db.query(models.TrnJobOrderHead).filter(models.TrnJobOrderHead.id == request.job_id).first()
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order with ID {request.job_id} not found"
        )
    
    results = []
    errors = []
    
    for item in request.items:
        item_id = item.get("item_id")
        qty = item.get("qty")
        
        if not item_id or not qty:
            errors.append(f"Invalid item format: {item}")
            continue
        
        detail = db.query(models.TrnJobOrderDetail).filter(
            and_(
                models.TrnJobOrderDetail.job_id == request.job_id,
                models.TrnJobOrderDetail.item_id == item_id
            )
        ).first()
        
        if not detail:
            errors.append(f"Item {item_id} not found in Work Order")
            continue
        
        new_consumed = detail.qty_consumed + Decimal(str(qty))
        
        if new_consumed > detail.qty_required:
            errors.append(f"Item {item_id}: Would exceed required quantity")
            continue
        
        detail.qty_consumed = new_consumed
        results.append({
            "item_id": item_id,
            "qty_consumed": qty,
            "total_consumed": float(new_consumed)
        })
    
    # Update WO status
    if wo.status == models.JobStatus.PLANNED:
        wo.status = models.JobStatus.IN_PROGRESS
    
    db.commit()
    
    return {
        "message": f"Issued {len(results)} materials successfully",
        "results": results,
        "errors": errors if errors else None
    }


# ==================== WORK ORDER COMPLETION ====================
@router.post("/complete", status_code=status.HTTP_200_OK)
def complete_work_order(
    request: schemas.WorkOrderCompletion,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """
    Complete Work Order:
    1. Update qty_produced
    2. Optionally consume remaining materials
    3. Optionally post finished goods to inventory
    4. Update status to COMPLETED
    """
    wo = db.query(models.TrnJobOrderHead).filter(models.TrnJobOrderHead.id == request.job_id).first()
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order with ID {request.job_id} not found"
        )
    
    if wo.status == models.JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Work Order {wo.job_no} is already completed"
        )
    
    # Update produced quantity
    wo.qty_produced = request.qty_produced
    
    # Auto-consume remaining materials if requested
    if request.auto_consume_remaining:
        details = db.query(models.TrnJobOrderDetail).filter(
            models.TrnJobOrderDetail.job_id == request.job_id
        ).all()
        
        for detail in details:
            if detail.qty_consumed < detail.qty_required:
                detail.qty_consumed = detail.qty_required
    
    # Update status
    wo.status = models.JobStatus.COMPLETED
    if request.lot_number:
        wo.lot_number = request.lot_number
    
    # Post to inventory (create inventory transaction)
    if request.post_to_inventory:
        # Create FG Receipt
        fg_txn = models.InventoryTransaction(
            transaction_date=get_utc_now(),
            item_id=wo.item_id,
            warehouse_id=wo.warehouse_id,
            location_id=None, # Should ideally be from BOM storage_location or default
            lot_number=wo.lot_number,
            transaction_type="receipt",
            reference_no=wo.job_no,
            qty=wo.qty_produced,
            created_by=current_user.id
        )
        db.add(fg_txn)
        
        # Update Balance
        balance = db.query(models.InventoryBalance).filter(
            models.InventoryBalance.item_id == wo.item_id,
            models.InventoryBalance.warehouse_id == wo.warehouse_id,
            models.InventoryBalance.lot_number == wo.lot_number
        ).first()
        
        if not balance:
            balance = models.InventoryBalance(
                item_id=wo.item_id,
                warehouse_id=wo.warehouse_id,
                lot_number=wo.lot_number,
                qty_on_hand=0,
                avg_cost=0
            )
            db.add(balance)
            
        # Update balance and cost layer (standard cost)
        item = db.query(models.MasterItem).filter(models.MasterItem.id == wo.item_id).first()
        unit_cost = item.standard_cost or Decimal(0)
        
        balance.qty_on_hand += wo.qty_produced
        # Simplified avg cost update
        balance.avg_cost = unit_cost 
        
        # Create Cost Layer
        cost_layer = models.InventoryCostLayer(
            item_id=wo.item_id,
            warehouse_id=wo.warehouse_id,
            receipt_date=date.today(),
            qty_remaining=wo.qty_produced,
            unit_cost=unit_cost,
            receipt_transaction_id=None, # Linked via reference? Or need flush
            lot_number=wo.lot_number
        )
        db.add(cost_layer)
    
    db.commit()
    
    return {
        "message": f"Work Order {wo.job_no} completed successfully",
        "job_no": wo.job_no,
        "qty_produced": float(request.qty_produced),
        "status": "COMPLETED"
    }


# ==================== STATISTICS ====================
@router.get("/stats/summary", response_model=dict)
def get_work_order_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Get Work Order statistics"""
    total = db.query(func.count(models.TrnJobOrderHead.id)).scalar()
    planned = db.query(func.count(models.TrnJobOrderHead.id)).filter(
        models.TrnJobOrderHead.status == models.JobStatus.PLANNED
    ).scalar()
    in_progress = db.query(func.count(models.TrnJobOrderHead.id)).filter(
        models.TrnJobOrderHead.status == models.JobStatus.IN_PROGRESS
    ).scalar()
    completed = db.query(func.count(models.TrnJobOrderHead.id)).filter(
        models.TrnJobOrderHead.status == models.JobStatus.COMPLETED
    ).scalar()
    cancelled = db.query(func.count(models.TrnJobOrderHead.id)).filter(
        models.TrnJobOrderHead.status == models.JobStatus.CANCELLED
    ).scalar()
    
    # Find overdue
    today = date.today()
    overdue = db.query(func.count(models.TrnJobOrderHead.id)).filter(
        and_(
            models.TrnJobOrderHead.end_date < today,
            models.TrnJobOrderHead.status != models.JobStatus.COMPLETED,
            models.TrnJobOrderHead.status != models.JobStatus.CANCELLED
        )
    ).scalar()
    
    return {
        "total": total,
        "by_status": {
            "planned": planned,
            "in_progress": in_progress,
            "completed": completed,
            "cancelled": cancelled
        },
        "overdue": overdue
    }

