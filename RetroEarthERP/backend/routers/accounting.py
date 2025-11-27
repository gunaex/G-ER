from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from decimal import Decimal

from database import get_db
import models
from routers.auth import get_current_active_user

router = APIRouter(
    prefix="/api/accounting",
    tags=["Accounting"],
    responses={404: {"description": "Not found"}},
)

# Schemas
class AccountResponse(BaseModel):
    id: int
    code: str
    name: str
    account_type: str
    parent_id: Optional[int]
    
    class Config:
        from_attributes = True

class JournalLinePreview(BaseModel):
    account_code: str
    account_name: str
    debit: Decimal
    credit: Decimal

class JournalPreview(BaseModel):
    date: date
    description: str
    lines: List[JournalLinePreview]
    total_debit: Decimal
    total_credit: Decimal

# Endpoints

@router.get("/chart-of-accounts", response_model=List[AccountResponse])
def get_chart_of_accounts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get the full Chart of Accounts"""
    return db.query(models.MasterAccount).filter(models.MasterAccount.is_active == True).order_by(models.MasterAccount.code).all()

@router.get("/preview/invoice/{invoice_id}", response_model=JournalPreview)
def preview_invoice_journal(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Simulate the Journal Entry for a Tax Invoice.
    This does NOT save to the database, just returns what WOULD be saved.
    """
    # 1. Fetch the Invoice
    invoice = db.query(models.TrnTaxInvoiceHead).filter(models.TrnTaxInvoiceHead.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Tax Invoice not found")
    
    # 2. Define Standard Accounts (In a real app, these would be from settings)
    # Using the codes we seeded in seed_data.py
    ACC_AR = "1120"      # Accounts Receivable
    ACC_SALES = "4100"   # Sales Revenue
    ACC_VAT = "2130"     # VAT Payable
    
    # 3. Calculate Amounts
    total_amount = invoice.total_amount
    vat_amount = invoice.tax_amount
    net_amount = total_amount - vat_amount
    
    # 4. Build Lines
    lines = []
    
    # Debit AR (Total Amount)
    ar_acc = db.query(models.MasterAccount).filter(models.MasterAccount.code == ACC_AR).first()
    lines.append(JournalLinePreview(
        account_code=ar_acc.code if ar_acc else "???",
        account_name=ar_acc.name if ar_acc else "Unknown Account",
        debit=total_amount,
        credit=0
    ))
    
    # Credit Sales (Net Amount)
    sales_acc = db.query(models.MasterAccount).filter(models.MasterAccount.code == ACC_SALES).first()
    lines.append(JournalLinePreview(
        account_code=sales_acc.code if sales_acc else "???",
        account_name=sales_acc.name if sales_acc else "Unknown Account",
        debit=0,
        credit=net_amount
    ))
    
    # Credit VAT (VAT Amount)
    if vat_amount > 0:
        vat_acc = db.query(models.MasterAccount).filter(models.MasterAccount.code == ACC_VAT).first()
        lines.append(JournalLinePreview(
            account_code=vat_acc.code if vat_acc else "???",
            account_name=vat_acc.name if vat_acc else "Unknown Account",
            debit=0,
            credit=vat_amount
        ))
        
    return JournalPreview(
        date=invoice.invoice_date,
        description=f"Invoice #{invoice.invoice_no} for {invoice.customer_name}",
        lines=lines,
        total_debit=sum(l.debit for l in lines),
        total_credit=sum(l.credit for l in lines)
    )
