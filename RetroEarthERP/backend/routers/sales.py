"""
Sales Quotation & Tax Invoice Router
Implements Quotation → SO → DO → Tax Invoice workflow
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, timedelta
from decimal import Decimal
from utils.datetime_utils import get_utc_now
import models
import schemas
from database import get_db
from routers.auth import get_current_active_user

router = APIRouter(
    prefix="/api/sales",
    tags=["sales"],
    responses={404: {"description": "Not found"}},
)


# ==================== QUOTATION MANAGEMENT ====================

@router.post("/quotations", status_code=status.HTTP_201_CREATED)
def create_quotation(
    customer_id: int,
    items: List[dict],
    valid_days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new sales quotation.
    
    Items format: [{"item_id": 1, "qty": 10, "unit_price": 100, "discount_percent": 5}]
    """
    # Validate customer
    customer = db.query(models.MasterBusinessPartner).filter(
        models.MasterBusinessPartner.id == customer_id,
        models.MasterBusinessPartner.partner_type.in_(['CUSTOMER', 'BOTH'])
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Generate quotation number
    count = db.query(func.count(models.TrnQuotationHead.id)).scalar()
    quotation_no = f"QT-{get_utc_now().strftime('%Y%m%d')}-{count + 1:05d}"
    
    # Create quotation header
    quotation = models.TrnQuotationHead(
        quotation_no=quotation_no,
        customer_id=customer_id,
        quotation_date=date.today(),
        valid_until=date.today() + timedelta(days=valid_days),
        status='DRAFT',
        total_amount=0,
        created_by=current_user.id
    )
    db.add(quotation)
    db.flush()
    
    # Create quotation details
    total_amount = Decimal(0)
    line_no = 1
    
    for item_data in items:
        item = db.query(models.MasterItem).filter(
            models.MasterItem.id == item_data['item_id']
        ).first()
        
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {item_data['item_id']} not found")
        
        qty = Decimal(str(item_data['qty']))
        unit_price = Decimal(str(item_data['unit_price']))
        discount = Decimal(str(item_data.get('discount_percent', 0)))
        
        line_amount = qty * unit_price * (1 - discount / 100)
        total_amount += line_amount
        
        detail = models.TrnQuotationDetail(
            quotation_id=quotation.id,
            line_no=line_no,
            item_id=item_data['item_id'],
            qty=qty,
            unit_price=unit_price,
            discount_percent=discount
        )
        db.add(detail)
        line_no += 1
    
    quotation.total_amount = total_amount
    db.commit()
    db.refresh(quotation)
    
    return {
        "message": "Quotation created successfully",
        "quotation_no": quotation_no,
        "quotation_id": quotation.id,
        "total_amount": float(total_amount)
    }


@router.get("/quotations")
def list_quotations(
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """List quotations with optional filters"""
    query = db.query(models.TrnQuotationHead)
    
    if customer_id:
        query = query.filter(models.TrnQuotationHead.customer_id == customer_id)
    
    if status:
        query = query.filter(models.TrnQuotationHead.status == status.upper())
    
    quotations = query.order_by(models.TrnQuotationHead.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for qt in quotations:
        customer = db.query(models.MasterBusinessPartner).filter(
            models.MasterBusinessPartner.id == qt.customer_id
        ).first()
        
        result.append({
            "id": qt.id,
            "quotation_no": qt.quotation_no,
            "customer_id": qt.customer_id,
            "customer_name": customer.partner_name if customer else "",
            "quotation_date": qt.quotation_date,
            "valid_until": qt.valid_until,
            "status": qt.status,
            "total_amount": float(qt.total_amount),
            "created_at": qt.created_at
        })
    
    return result


@router.get("/quotations/{quotation_id}")
def get_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get quotation details with line items"""
    quotation = db.query(models.TrnQuotationHead).filter(
        models.TrnQuotationHead.id == quotation_id
    ).first()
    
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    customer = db.query(models.MasterBusinessPartner).filter(
        models.MasterBusinessPartner.id == quotation.customer_id
    ).first()
    
    details = db.query(models.TrnQuotationDetail).filter(
        models.TrnQuotationDetail.quotation_id == quotation_id
    ).all()
    
    items = []
    for detail in details:
        item = db.query(models.MasterItem).filter(
            models.MasterItem.id == detail.item_id
        ).first()
        
        items.append({
            "line_no": detail.line_no,
            "item_id": detail.item_id,
            "item_code": item.item_code if item else "",
            "item_name": item.item_name if item else "",
            "qty": float(detail.qty),
            "unit_price": float(detail.unit_price),
            "discount_percent": float(detail.discount_percent),
            "line_amount": float(detail.qty * detail.unit_price * (1 - detail.discount_percent / 100))
        })
    
    return {
        "id": quotation.id,
        "quotation_no": quotation.quotation_no,
        "customer_id": quotation.customer_id,
        "customer_name": customer.partner_name if customer else "",
        "quotation_date": quotation.quotation_date,
        "valid_until": quotation.valid_until,
        "status": quotation.status,
        "total_amount": float(quotation.total_amount),
        "created_at": quotation.created_at,
        "items": items
    }


@router.post("/quotations/{quotation_id}/send")
def send_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Mark quotation as SENT"""
    quotation = db.query(models.TrnQuotationHead).filter(
        models.TrnQuotationHead.id == quotation_id
    ).first()
    
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    if quotation.status != 'DRAFT':
        raise HTTPException(status_code=400, detail="Only DRAFT quotations can be sent")
    
    quotation.status = 'SENT'
    db.commit()
    
    return {"message": "Quotation sent successfully", "quotation_no": quotation.quotation_no}


@router.post("/quotations/{quotation_id}/convert-to-so")
def convert_quotation_to_so(
    quotation_id: int,
    delivery_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Convert ACCEPTED quotation to Sales Order.
    One-click conversion.
    """
    quotation = db.query(models.TrnQuotationHead).filter(
        models.TrnQuotationHead.id == quotation_id
    ).first()
    
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    if quotation.status not in ['SENT', 'ACCEPTED']:
        raise HTTPException(status_code=400, detail="Only SENT or ACCEPTED quotations can be converted")
    
    # Check if already converted
    if quotation.status == 'CONVERTED':
        raise HTTPException(status_code=400, detail="Quotation already converted to SO")
    
    # Generate SO number
    count = db.query(func.count(models.TrnSalesOrderHead.id)).scalar()
    so_no = f"SO-{get_utc_now().strftime('%Y%m%d')}-{count + 1:05d}"
    
    # Create SO Header
    sales_order = models.TrnSalesOrderHead(
        so_no=so_no,
        customer_id=quotation.customer_id,
        so_date=date.today(),
        delivery_date=delivery_date or quotation.valid_until,
        status='DRAFT',
        total_amount=quotation.total_amount,
        created_by=current_user.id
    )
    db.add(sales_order)
    db.flush()
    
    # Copy quotation details to SO details
    qt_details = db.query(models.TrnQuotationDetail).filter(
        models.TrnQuotationDetail.quotation_id == quotation_id
    ).all()
    
    for qt_detail in qt_details:
        so_detail = models.TrnSalesOrderDetail(
            so_id=sales_order.id,
            line_no=qt_detail.line_no,
            item_id=qt_detail.item_id,
            qty_ordered=qt_detail.qty,
            qty_delivered=0,
            unit_price=qt_detail.unit_price * (1 - qt_detail.discount_percent / 100)
        )
        db.add(so_detail)
    
    # Update quotation status
    quotation.status = 'CONVERTED'
    
    db.commit()
    
    return {
        "message": "Quotation converted to Sales Order successfully",
        "quotation_no": quotation.quotation_no,
        "so_no": so_no,
        "so_id": sales_order.id
    }


# ==================== TAX INVOICE MANAGEMENT ====================

@router.post("/invoices/from-do/{do_id}", status_code=status.HTTP_201_CREATED)
def create_invoice_from_do(
    do_id: int,
    tax_rate: float = 7.0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Generate Tax Invoice from Delivery Order.
    Automatically calculates tax and totals.
    """
    # Get DO
    do = db.query(models.TrnDeliveryOrderHead).filter(
        models.TrnDeliveryOrderHead.id == do_id
    ).first()
    
    if not do:
        raise HTTPException(status_code=404, detail="Delivery Order not found")
    
    if do.status != 'POSTED':
        raise HTTPException(status_code=400, detail="Only POSTED delivery orders can be invoiced")
    
    # Check if already invoiced
    existing_invoice = db.query(models.TrnTaxInvoiceHead).filter(
        models.TrnTaxInvoiceHead.do_id == do_id
    ).first()
    
    if existing_invoice:
        raise HTTPException(status_code=400, detail="Delivery Order already invoiced")
    
    # Get SO to find customer
    so = db.query(models.TrnSalesOrderHead).filter(
        models.TrnSalesOrderHead.id == do.so_id
    ).first()
    
    if not so:
        raise HTTPException(status_code=404, detail="Sales Order not found")
    
    # Generate invoice number
    count = db.query(func.count(models.TrnTaxInvoiceHead.id)).scalar()
    invoice_no = f"INV-{get_utc_now().strftime('%Y%m%d')}-{count + 1:05d}"
    
    # Get customer payment terms
    customer = db.query(models.MasterBusinessPartner).filter(
        models.MasterBusinessPartner.id == so.customer_id
    ).first()
    
    payment_days = 30  # Default
    if customer and customer.payment_terms:
        # Extract days from "Net 30" format
        try:
            payment_days = int(customer.payment_terms.split()[-1])
        except:
            payment_days = 30
    
    # Calculate amounts
    do_details = db.query(models.TrnDeliveryOrderDetail).filter(
        models.TrnDeliveryOrderDetail.do_id == do_id
    ).all()
    
    subtotal = Decimal(0)
    for detail in do_details:
        subtotal += detail.qty_delivered * detail.unit_price
    
    tax_amount = subtotal * Decimal(str(tax_rate)) / 100
    total_amount = subtotal + tax_amount
    
    # Create invoice header
    invoice = models.TrnTaxInvoiceHead(
        invoice_no=invoice_no,
        do_id=do_id,
        customer_id=so.customer_id,
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=payment_days),
        status='DRAFT',
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
        created_by=current_user.id
    )
    db.add(invoice)
    db.flush()
    
    # Create invoice details
    for detail in do_details:
        inv_detail = models.TrnTaxInvoiceDetail(
            invoice_id=invoice.id,
            line_no=detail.line_no,
            item_id=detail.item_id,
            qty=detail.qty_delivered,
            unit_price=detail.unit_price,
            amount=detail.qty_delivered * detail.unit_price
        )
        db.add(inv_detail)
    
    db.commit()
    db.refresh(invoice)
    
    return {
        "message": "Tax Invoice created successfully",
        "invoice_no": invoice_no,
        "invoice_id": invoice.id,
        "subtotal": float(subtotal),
        "tax_amount": float(tax_amount),
        "total_amount": float(total_amount),
        "due_date": invoice.due_date
    }


@router.get("/invoices")
def list_invoices(
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """List tax invoices with optional filters"""
    query = db.query(models.TrnTaxInvoiceHead)
    
    if customer_id:
        query = query.filter(models.TrnTaxInvoiceHead.customer_id == customer_id)
    
    if status:
        query = query.filter(models.TrnTaxInvoiceHead.status == status.upper())
    
    invoices = query.order_by(models.TrnTaxInvoiceHead.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for inv in invoices:
        customer = db.query(models.MasterBusinessPartner).filter(
            models.MasterBusinessPartner.id == inv.customer_id
        ).first()
        
        result.append({
            "id": inv.id,
            "invoice_no": inv.invoice_no,
            "customer_id": inv.customer_id,
            "customer_name": customer.partner_name if customer else "",
            "invoice_date": inv.invoice_date,
            "due_date": inv.due_date,
            "status": inv.status,
            "subtotal": float(inv.subtotal),
            "tax_amount": float(inv.tax_amount),
            "total_amount": float(inv.total_amount),
            "created_at": inv.created_at
        })
    
    return result


@router.get("/invoices/{invoice_id}")
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get invoice details with line items"""
    invoice = db.query(models.TrnTaxInvoiceHead).filter(
        models.TrnTaxInvoiceHead.id == invoice_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    customer = db.query(models.MasterBusinessPartner).filter(
        models.MasterBusinessPartner.id == invoice.customer_id
    ).first()
    
    details = db.query(models.TrnTaxInvoiceDetail).filter(
        models.TrnTaxInvoiceDetail.invoice_id == invoice_id
    ).all()
    
    items = []
    for detail in details:
        item = db.query(models.MasterItem).filter(
            models.MasterItem.id == detail.item_id
        ).first()
        
        items.append({
            "line_no": detail.line_no,
            "item_id": detail.item_id,
            "item_code": item.item_code if item else "",
            "item_name": item.item_name if item else "",
            "qty": float(detail.qty),
            "unit_price": float(detail.unit_price),
            "amount": float(detail.amount)
        })
    
    return {
        "id": invoice.id,
        "invoice_no": invoice.invoice_no,
        "customer_id": invoice.customer_id,
        "customer_name": customer.partner_name if customer else "",
        "invoice_date": invoice.invoice_date,
        "due_date": invoice.due_date,
        "status": invoice.status,
        "subtotal": float(invoice.subtotal),
        "tax_amount": float(invoice.tax_amount),
        "total_amount": float(invoice.total_amount),
        "created_at": invoice.created_at,
        "items": items
    }


@router.post("/invoices/{invoice_id}/post")
def post_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Post invoice (finalize)"""
    invoice = db.query(models.TrnTaxInvoiceHead).filter(
        models.TrnTaxInvoiceHead.id == invoice_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice.status != 'DRAFT':
        raise HTTPException(status_code=400, detail="Only DRAFT invoices can be posted")
    
    invoice.status = 'POSTED'
    db.commit()
    
    return {"message": "Invoice posted successfully", "invoice_no": invoice.invoice_no}


@router.post("/invoices/{invoice_id}/mark-paid")
def mark_invoice_paid(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Mark invoice as PAID"""
    invoice = db.query(models.TrnTaxInvoiceHead).filter(
        models.TrnTaxInvoiceHead.id == invoice_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice.status != 'POSTED':
        raise HTTPException(status_code=400, detail="Only POSTED invoices can be marked as paid")
    
    invoice.status = 'PAID'
    db.commit()
    
    return {"message": "Invoice marked as paid", "invoice_no": invoice.invoice_no}
