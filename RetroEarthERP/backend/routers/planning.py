"""
Production Planning & MRP Engine
Implements the planning calculation logic to generate PRs and Work Orders
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal
from utils.datetime_utils import get_utc_now
import models
import schemas
from database import get_db
from routers.auth import get_current_active_user

router = APIRouter(
    prefix="/api/planning",
    tags=["planning"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.ProductionPlanResponse, status_code=status.HTTP_201_CREATED)
def create_production_plan(
    plan: schemas.ProductionPlanCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new Production Plan (DRAFT).
    If items are provided (for MANUAL/CALENDAR mode), they are added.
    """
    db_plan = models.ProductionPlan(
        plan_name=plan.plan_name,
        plan_type=getattr(plan, 'plan_type', 'PRODUCTION'),
        source_type=plan.source_type,
        sales_order_id=getattr(plan, 'sales_order_id', None),
        status='DRAFT',
        created_by=current_user.id
    )
    db.add(db_plan)
    db.flush()
    
    # Add items if provided
    if plan.items:
        for item in plan.items:
            # Validate item exists
            db_item = db.query(models.MasterItem).filter(models.MasterItem.id == item.item_id).first()
            if not db_item:
                continue # Or raise error
                
            db_item_plan = models.ProductionPlanItem(
                plan_id=db_plan.id,
                item_id=item.item_id,
                quantity=item.quantity,
                delivery_date=item.delivery_date
            )
            db.add(db_item_plan)
    
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.post("/{plan_id}/items", response_model=schemas.ProductionPlanResponse)
def add_plan_items(
    plan_id: int,
    items: List[schemas.ProductionPlanItemCreate],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Add items to an existing DRAFT plan"""
    db_plan = db.query(models.ProductionPlan).filter(models.ProductionPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if db_plan.status != 'DRAFT':
        raise HTTPException(status_code=400, detail="Cannot add items to a calculated/processed plan")
    
    for item in items:
        db_item_plan = models.ProductionPlanItem(
            plan_id=db_plan.id,
            item_id=item.item_id,
            quantity=item.quantity,
            delivery_date=item.delivery_date
        )
        db.add(db_item_plan)
    
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.post("/{plan_id}/calculate", response_model=schemas.ProductionPlanResponse)
def calculate_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Pre-Calculation: Run MRP Calculation for a specific plan.
    Generates MRP Results (Material Availability Report) but does NOT create PRs/WOs.
    """
    db_plan = db.query(models.ProductionPlan).filter(models.ProductionPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if db_plan.status != 'DRAFT':
        raise HTTPException(status_code=400, detail="Plan already calculated")
    
    # Clear existing results if any (though status check prevents this)
    db.query(models.MRPResult).filter(models.MRPResult.plan_id == plan_id).delete()
    
    # Step 1: Get Demand
    demands = []
    
    if db_plan.source_type == 'ACTUAL':
        # Get from Confirmed Sales Orders
        sales_orders = db.query(models.TrnSalesOrderHead).filter(
            models.TrnSalesOrderHead.status.in_(['CONFIRMED', 'PARTIAL_DELIVERED'])
        ).all()
        
        for so in sales_orders:
            for detail in so.details:
                remaining_qty = detail.qty_ordered - detail.qty_delivered
                if remaining_qty > 0:
                    demands.append({
                        'item_id': detail.item_id,
                        'required_qty': remaining_qty,
                        'required_date': so.delivery_date or so.so_date
                    })
                    
    elif db_plan.source_type == 'MANUAL' or db_plan.source_type == 'FORECAST':
        # Get from Plan Items
        for item in db_plan.items:
            demands.append({
                'item_id': item.item_id,
                'required_qty': item.quantity,
                'required_date': item.delivery_date
            })
    
    # Step 2: Calculate Net Requirements
    for demand in demands:
        item = db.query(models.MasterItem).filter(
            models.MasterItem.id == demand['item_id']
        ).first()
        
        if not item:
            continue
        
        # Get current inventory (all warehouses)
        on_hand = db.query(func.sum(models.InventoryBalance.qty_on_hand)).filter(
            models.InventoryBalance.item_id == demand['item_id']
        ).scalar() or Decimal(0)
        
        # Get incoming PO qty (not yet received)
        incoming_po = db.query(func.sum(models.TrnPurchaseOrderDetail.qty_ordered - models.TrnPurchaseOrderDetail.qty_received)).filter(
            models.TrnPurchaseOrderDetail.item_id == demand['item_id'],
            models.TrnPurchaseOrderDetail.qty_ordered > models.TrnPurchaseOrderDetail.qty_received
        ).scalar() or Decimal(0)
        
        # Net Requirement
        net_requirement = demand['required_qty'] - (on_hand + incoming_po)
        
        if net_requirement > 0:
            # Check if item is produced or purchased
            has_bom = db.query(models.MasterBOM).filter(
                models.MasterBOM.parent_item_id == demand['item_id'],
                models.MasterBOM.is_active == True
            ).first()
            
            action = models.SuggestedAction.MAKE if has_bom else models.SuggestedAction.BUY
            
            # Create MRP Result
            mrp_result = models.MRPResult(
                plan_id=db_plan.id,
                item_id=demand['item_id'],
                required_date=demand['required_date'],
                gross_requirement=demand['required_qty'],
                on_hand_qty=on_hand,
                open_po_qty=incoming_po,
                net_requirement=net_requirement,
                suggested_action=action,
                suggested_qty=net_requirement
            )
            db.add(mrp_result)
        else:
            # Requirement met
            mrp_result = models.MRPResult(
                plan_id=db_plan.id,
                item_id=demand['item_id'],
                required_date=demand['required_date'],
                gross_requirement=demand['required_qty'],
                on_hand_qty=on_hand,
                open_po_qty=incoming_po,
                net_requirement=Decimal(0),
                suggested_action=models.SuggestedAction.NONE,
                suggested_qty=Decimal(0)
            )
            db.add(mrp_result)
            
    # Update plan status
    db_plan.status = 'CALCULATED'
    db_plan.calculated_date = get_utc_now()
    
    db.commit()
    db.refresh(db_plan)
    
    # Prepare temp WOs and PRs for response
    temp_work_orders = []
    temp_purchase_reqs = []
    
    for result in db_plan.mrp_results:
        item = db.query(models.MasterItem).filter(models.MasterItem.id == result.item_id).first()
        if result.suggested_action == models.SuggestedAction.MAKE:
            temp_work_orders.append({
                'item_code': item.item_code if item else f'Item-{result.item_id}',
                'item_name': item.item_name if item else '',
                'quantity': float(result.suggested_qty),
                'required_date': result.required_date.isoformat() if result.required_date else None
            })
        elif result.suggested_action == models.SuggestedAction.BUY:
            temp_purchase_reqs.append({
                'item_code': item.item_code if item else f'Item-{result.item_id}',
                'item_name': item.item_name if item else '',
                'quantity': float(result.suggested_qty),
                'required_date': result.required_date.isoformat() if result.required_date else None
            })
    
    return {
        **schemas.ProductionPlanResponse.from_orm(db_plan).dict(),
        'temp_work_orders': temp_work_orders,
        'temp_purchase_reqs': temp_purchase_reqs
    }


@router.post("/{plan_id}/process", response_model=schemas.ProductionPlanResponse)
def process_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Post-Calculation: Process MRP Results to create PRs and WOs.
    """
    db_plan = db.query(models.ProductionPlan).filter(models.ProductionPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if db_plan.status != 'CALCULATED':
        raise HTTPException(status_code=400, detail="Plan must be calculated first")
    
    results = db.query(models.MRPResult).filter(
        models.MRPResult.plan_id == plan_id,
        models.MRPResult.suggested_action.in_([models.SuggestedAction.BUY, models.SuggestedAction.MAKE])
    ).all()
    
    pr_counter = 1
    wo_counter = 1
    
    for result in results:
        if result.suggested_action == models.SuggestedAction.BUY:
            # Create Draft PR
            vendor = db.query(models.MasterBusinessPartner).filter(
                models.MasterBusinessPartner.partner_type.in_(['VENDOR', 'BOTH']),
                models.MasterBusinessPartner.is_active == True
            ).first()
            
            if vendor:
                total_lead_time = (vendor.lead_time_production_days or 0) + (vendor.lead_time_transit_days or 0)
                suggested_order_date = result.required_date - timedelta(days=int(total_lead_time))
                
                pr_no = f"PR-{get_utc_now().strftime('%Y%m%d')}-{db_plan.id}-{pr_counter:04d}"
                db_pr = models.DraftPurchaseRequisition(
                    pr_no=pr_no,
                    plan_id=db_plan.id,
                    vendor_id=vendor.id,
                    item_id=result.item_id,
                    required_qty=result.suggested_qty,
                    required_date=result.required_date,
                    suggested_order_date=suggested_order_date,
                    status='DRAFT'
                )
                db.add(db_pr)
                pr_counter += 1
                
        elif result.suggested_action == models.SuggestedAction.MAKE:
            # Create Planned Work Order
            # Generate Job No
            job_count = db.query(func.count(models.TrnJobOrderHead.id)).scalar()
            job_no = f"WO-{get_utc_now().strftime('%Y%m%d')}-{job_count + wo_counter:05d}"
            
            # Default warehouse (Main)
            warehouse = db.query(models.MasterWarehouse).filter(models.MasterWarehouse.warehouse_type == 'Main').first()
            warehouse_id = warehouse.id if warehouse else 1
            
            wo = models.TrnJobOrderHead(
                job_no=job_no,
                item_id=result.item_id,
                qty_planned=result.suggested_qty,
                qty_produced=Decimal(0),
                start_date=date.today(), # Should be calculated based on lead time
                end_date=result.required_date,
                status=models.JobStatus.PLANNED,
                warehouse_id=warehouse_id,
                created_by=current_user.id
            )
            db.add(wo)
            wo_counter += 1
            
    # Update plan status
    db_plan.status = 'PROCESSED'
    
    db.commit()
    db.refresh(db_plan)
    
    # Prepare created WOs and PRs for response
    created_work_orders = []
    created_purchase_reqs = []
    
    # Get the PRs and WOs that were just created
    prs = db.query(models.DraftPurchaseRequisition).filter(
        models.DraftPurchaseRequisition.plan_id == plan_id
    ).all()
    
    wos = db.query(models.TrnJobOrderHead).filter(
        models.TrnJobOrderHead.status == models.JobStatus.PLANNED
    ).order_by(models.TrnJobOrderHead.id.desc()).limit(wo_counter).all()
    
    for pr in prs:
        item = db.query(models.MasterItem).filter(models.MasterItem.id == pr.item_id).first()
        created_purchase_reqs.append({
            'pr_no': pr.pr_no,
            'item_code': item.item_code if item else f'Item-{pr.item_id}',
            'item_name': item.item_name if item else '',
            'quantity': float(pr.quantity),
            'required_date': pr.required_date.isoformat() if pr.required_date else None
        })
    
    for wo in wos:
        item = db.query(models.MasterItem).filter(models.MasterItem.id == wo.item_id).first()
        created_work_orders.append({
            'job_no': wo.job_no,
            'item_code': item.item_code if item else f'Item-{wo.item_id}',
            'item_name': item.item_name if item else '',
            'quantity': float(wo.qty_planned),
            'required_date': wo.end_date.isoformat() if wo.end_date else None
        })
    
    return {
        **schemas.ProductionPlanResponse.from_orm(db_plan).dict(),
        'work_orders_created': created_work_orders,
        'prs_created': created_purchase_reqs
    }


@router.get("/plans", response_model=List[schemas.ProductionPlanResponse])
def get_production_plans(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all production plans"""
    plans = db.query(models.ProductionPlan).order_by(models.ProductionPlan.created_date.desc()).all()
    return plans


@router.get("/plans/{plan_id}", response_model=schemas.ProductionPlanResponse)
def get_production_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get a specific production plan"""
    plan = db.query(models.ProductionPlan).filter(models.ProductionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.get("/plans/{plan_id}/prs", response_model=List[schemas.DraftPRResponse])
def get_plan_prs(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get draft PRs generated from a plan"""
    prs = db.query(models.DraftPurchaseRequisition).filter(
        models.DraftPurchaseRequisition.plan_id == plan_id
    ).all()
    return prs


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_production_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Delete a production plan"""
    db_plan = db.query(models.ProductionPlan).filter(models.ProductionPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Production plan not found")
        
    # Only allow deleting DRAFT plans or check logic
    # For now, allow deleting any plan, cascading delete handles items/results
    
    db.delete(db_plan)
    db.commit()
    return None


@router.post("/prs/{pr_id}/approve")
def approve_purchase_requisition(
    pr_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Approve a draft PR (Manager/Admin only)"""
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    pr = db.query(models.DraftPurchaseRequisition).filter(
        models.DraftPurchaseRequisition.id == pr_id
    ).first()
    
    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")
    
    if pr.status != 'DRAFT':
        raise HTTPException(status_code=400, detail="PR is not in DRAFT status")
    
    pr.status = 'APPROVED'
    pr.approved_at = get_utc_now()
    pr.approved_by = current_user.id
    
    db.commit()
    
    return {"message": "PR approved successfully", "pr_no": pr.pr_no}


@router.post("/prs/{pr_id}/convert-to-po")
def convert_pr_to_po(
    pr_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Convert approved PR to Purchase Order"""
    pr = db.query(models.DraftPurchaseRequisition).filter(
        models.DraftPurchaseRequisition.id == pr_id
    ).first()
    
    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")
    
    if pr.status != 'APPROVED':
        raise HTTPException(status_code=400, detail="PR must be approved first")
    
    # Create PO
    po_no = f"PO-{get_utc_now().strftime('%Y%m%d')}-{db.query(func.count(models.TrnPurchaseOrderHead.id)).scalar() + 1:04d}"
    
    db_po = models.TrnPurchaseOrderHead(
        po_no=po_no,
        vendor_id=pr.vendor_id,
        po_date=date.today(),
        delivery_date=pr.required_date,
        status='DRAFT',
        created_by=current_user.id
    )
    db.add(db_po)
    db.flush()
    
    # Get item cost
    item = db.query(models.MasterItem).filter(models.MasterItem.id == pr.item_id).first()
    unit_price = item.standard_cost if item else Decimal(0)
    
    # Create PO Detail
    db_po_detail = models.TrnPurchaseOrderDetail(
        po_id=db_po.id,
        line_no=1,
        item_id=pr.item_id,
        qty_ordered=pr.required_qty,
        unit_price=unit_price
    )
    db.add(db_po_detail)
    
    # Update PR status
    pr.status = 'CONVERTED_TO_PO'
    
    db.commit()
    
    return {"message": "PR converted to PO successfully", "po_no": po_no}
