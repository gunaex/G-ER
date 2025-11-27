from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from decimal import Decimal
from datetime import date
import models
import schemas
from database import get_db
from routers.auth import get_current_active_user

router = APIRouter(
    prefix="/api/inventory",
    tags=["inventory"],
    responses={404: {"description": "Not found"}},
)


def apply_fifo_costing(db: Session, item_id: int, warehouse_id: int, location_id: int, qty: Decimal):
    """
    Apply FIFO (First-In, First-Out) costing when issuing inventory
    Returns: total_cost, avg_cost
    """
    # Get all cost layers for this item/warehouse/location, ordered by receipt date (FIFO)
    cost_layers = db.query(models.InventoryCostLayer).filter(
        models.InventoryCostLayer.item_id == item_id,
        models.InventoryCostLayer.warehouse_id == warehouse_id,
        models.InventoryCostLayer.location_id == location_id,
        models.InventoryCostLayer.qty_remaining > 0
    ).order_by(models.InventoryCostLayer.receipt_date).all()
    
    if not cost_layers:
        raise HTTPException(
            status_code=400,
            detail=f"No cost layers available for FIFO calculation. Item may not have been received yet."
        )
    
    remaining_to_issue = qty
    total_cost = Decimal(0)
    
    for layer in cost_layers:
        if remaining_to_issue <= 0:
            break
        
        # Take from this layer
        qty_to_take = min(layer.qty_remaining, remaining_to_issue)
        cost_from_layer = qty_to_take * layer.unit_cost
        
        total_cost += cost_from_layer
        layer.qty_remaining -= qty_to_take
        remaining_to_issue -= qty_to_take
    
    if remaining_to_issue > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient inventory for FIFO costing. Short by {remaining_to_issue}"
        )
    
    avg_cost = total_cost / qty if qty > 0 else Decimal(0)
    return total_cost, avg_cost


def create_cost_layer(db: Session, item_id: int, warehouse_id: int, location_id: int, 
                      qty: Decimal, unit_cost: Decimal, receipt_date: date, transaction_id: int, lot_number: str = None):
    """Create a new cost layer when receiving inventory"""
    cost_layer = models.InventoryCostLayer(
        item_id=item_id,
        warehouse_id=warehouse_id,
        location_id=location_id,
        receipt_date=receipt_date,
        qty_remaining=qty,
        unit_cost=unit_cost,
        receipt_transaction_id=transaction_id,
        lot_number=lot_number
    )
    db.add(cost_layer)
    return cost_layer

@router.post("/transactions", status_code=status.HTTP_201_CREATED)
def create_inventory_transaction(
    transaction: schemas.StockTransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Validate items and warehouses exist
    for item in transaction.items:
        # Lookup Item
        db_item = db.query(models.MasterItem).filter(models.MasterItem.item_code == item.item_code).first()
        if not db_item:
            # Try by ID if code fails (frontend sends ID as value)
            try:
                item_id = int(item.item_code)
                db_item = db.query(models.MasterItem).filter(models.MasterItem.id == item_id).first()
            except ValueError:
                pass
            
            if not db_item:
                raise HTTPException(status_code=404, detail=f"Item not found: {item.item_code}")
        
        # Lookup Warehouse
        db_warehouse = db.query(models.MasterWarehouse).filter(models.MasterWarehouse.warehouse_code == item.warehouse_code).first()
        if not db_warehouse:
             raise HTTPException(status_code=404, detail=f"Warehouse not found: {item.warehouse_code}")

        # Lookup Location (Optional)
        db_location = None
        if item.location_code:
            db_location = db.query(models.LocationMaster).filter(
                models.LocationMaster.warehouse_id == db_warehouse.id,
                models.LocationMaster.location_code == item.location_code
            ).first()
            if not db_location:
                raise HTTPException(status_code=404, detail=f"Location not found: {item.location_code} in warehouse {db_warehouse.warehouse_code}")

        # Validate Lot Control
        if db_item.lot_control and not item.lot_number:
            raise HTTPException(status_code=400, detail=f"Item {item.item_code} requires Lot Number")

        # Create Transaction Record
        db_txn = models.InventoryTransaction(
            transaction_date=transaction.transaction_date,
            item_id=db_item.id,
            warehouse_id=db_warehouse.id,
            location_id=db_location.id if db_location else None,
            lot_number=item.lot_number,
            transaction_type=transaction.type,
            reference_no=transaction.reference_no,
            qty=item.qty, 
            created_by=current_user.id
        )
        db.add(db_txn)
        db.flush()  # Get transaction ID

        # Update Balance (by Lot)
        balance_query = db.query(models.InventoryBalance).filter(
            models.InventoryBalance.item_id == db_item.id,
            models.InventoryBalance.warehouse_id == db_warehouse.id,
            models.InventoryBalance.location_id == (db_location.id if db_location else None)
        )
        
        if item.lot_number:
            balance_query = balance_query.filter(models.InventoryBalance.lot_number == item.lot_number)
        else:
            balance_query = balance_query.filter(models.InventoryBalance.lot_number == None)
            
        balance = balance_query.first()

        if not balance:
            balance = models.InventoryBalance(
                item_id=db_item.id,
                warehouse_id=db_warehouse.id,
                location_id=db_location.id if db_location else None,
                lot_number=item.lot_number,
                qty_on_hand=0,
                avg_cost=0
            )
            db.add(balance)
        
        if transaction.type == 'receipt':
            # RECEIPT: Create cost layer and update balance
            unit_cost = db_item.standard_cost or Decimal(0)  # Use standard cost or get from PO
            
            create_cost_layer(
                db, 
                db_item.id, 
                db_warehouse.id, 
                db_location.id if db_location else None,
                item.qty,
                unit_cost,
                transaction.transaction_date.date() if hasattr(transaction.transaction_date, 'date') else transaction.transaction_date,
                db_txn.id,
                item.lot_number
            )
            
            # Update balance with moving average
            old_total_cost = balance.qty_on_hand * balance.avg_cost
            new_total_cost = old_total_cost + (item.qty * unit_cost)
            balance.qty_on_hand += item.qty
            balance.avg_cost = new_total_cost / balance.qty_on_hand if balance.qty_on_hand > 0 else Decimal(0)
            
        elif transaction.type == 'issue':
            # ISSUE: Apply FIFO costing
            if balance.qty_on_hand < item.qty:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient inventory. Available: {balance.qty_on_hand}, Requested: {item.qty}"
                )
            
            try:
                total_cost, avg_cost_issued = apply_fifo_costing(
                    db,
                    db_item.id,
                    db_warehouse.id,
                    db_location.id if db_location else None,
                    item.qty
                )
                
                # Update balance quantity (avg_cost stays same - it's the overall average)
                balance.qty_on_hand -= item.qty
                
            except HTTPException:
                # If FIFO fails (no cost layers), just update quantity with warning
                balance.qty_on_hand -= item.qty
            
    db.commit()
    return {"message": "Transaction recorded successfully"}


@router.get("/cost-layers/{item_id}")
def get_cost_layers(
    item_id: int,
    warehouse_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get FIFO cost layers for an item"""
    query = db.query(models.InventoryCostLayer).filter(
        models.InventoryCostLayer.item_id == item_id,
        models.InventoryCostLayer.qty_remaining > 0
    )
    
    if warehouse_id:
        query = query.filter(models.InventoryCostLayer.warehouse_id == warehouse_id)
    
    layers = query.order_by(models.InventoryCostLayer.receipt_date).all()
    
    return {
        "item_id": item_id,
        "total_layers": len(layers),
        "total_qty": sum(layer.qty_remaining for layer in layers),
        "weighted_avg_cost": sum(layer.qty_remaining * layer.unit_cost for layer in layers) / sum(layer.qty_remaining for layer in layers) if layers else 0,
        "layers": [
            {
                "id": layer.id,
                "receipt_date": layer.receipt_date,
                "qty_remaining": float(layer.qty_remaining),
                "unit_cost": float(layer.unit_cost),
                "total_value": float(layer.qty_remaining * layer.unit_cost),
                "warehouse_id": layer.warehouse_id,
                "location_id": layer.location_id
            }
            for layer in layers
        ]
    }


@router.get("/valuation")
def get_inventory_valuation(
    warehouse_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get inventory valuation report
    Shows: FIFO Cost vs Moving Average comparison
    """
    query = db.query(models.InventoryBalance).filter(
        models.InventoryBalance.qty_on_hand > 0
    )
    
    if warehouse_id:
        query = query.filter(models.InventoryBalance.warehouse_id == warehouse_id)
    
    balances = query.all()
    
    valuation_data = []
    total_fifo = Decimal(0)
    total_moving_avg = Decimal(0)
    
    for balance in balances:
        # Get FIFO cost
        cost_layers = db.query(models.InventoryCostLayer).filter(
            models.InventoryCostLayer.item_id == balance.item_id,
            models.InventoryCostLayer.warehouse_id == balance.warehouse_id,
            models.InventoryCostLayer.location_id == balance.location_id,
            models.InventoryCostLayer.qty_remaining > 0
        ).all()
        
        fifo_value = sum(layer.qty_remaining * layer.unit_cost for layer in cost_layers)
        moving_avg_value = balance.qty_on_hand * balance.avg_cost
        variance = fifo_value - moving_avg_value
        
        total_fifo += fifo_value
        total_moving_avg += moving_avg_value
        
        valuation_data.append({
            "item_id": balance.item_id,
            "warehouse_id": balance.warehouse_id,
            "qty_on_hand": float(balance.qty_on_hand),
            "fifo_unit_cost": float(fifo_value / balance.qty_on_hand) if balance.qty_on_hand > 0 else 0,
            "fifo_total_value": float(fifo_value),
            "moving_avg_unit_cost": float(balance.avg_cost),
            "moving_avg_total_value": float(moving_avg_value),
            "variance": float(variance),
            "variance_pct": float((variance / moving_avg_value * 100) if moving_avg_value > 0 else 0)
        })
    
    return {
        "summary": {
            "total_items": len(valuation_data),
            "total_fifo_value": float(total_fifo),
            "total_moving_avg_value": float(total_moving_avg),
            "total_variance": float(total_fifo - total_moving_avg),
            "variance_pct": float(((total_fifo - total_moving_avg) / total_moving_avg * 100) if total_moving_avg > 0 else 0)
        },
        "details": valuation_data
    }
