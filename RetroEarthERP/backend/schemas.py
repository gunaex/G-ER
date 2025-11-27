"""
Pydantic schemas for request/response validation

DATETIME CONVENTION:
- All datetime fields are stored and returned in UTC with timezone info
- Frontend should convert to local time for display
- Send 'X-Client-Timezone-Offset' header with minutes from UTC (e.g., 420 for UTC+7)
- Document numbers use client's local date for generation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date, timezone
from decimal import Decimal


# Helper to document UTC fields
def utc_datetime_field(description: str = "") -> datetime:
    """Field for UTC datetime with timezone info"""
    return Field(description=f"{description} (UTC with timezone info)")


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str
    role: str = "user"


class UserResponse(UserBase):
    id: int
    role: str
    theme_preference: str
    language: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user details"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    theme_preference: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None


class PasswordChange(BaseModel):
    """Schema for changing user password"""
    new_password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
    server_time_utc: Optional[datetime] = None  # Server time in UTC for client sync
    active_package: Optional[dict] = None
    active_apps: List[dict] = []


# Item Schemas
class ItemBase(BaseModel):
    item_code: str
    item_name: str
    item_type: str
    category: Optional[str] = None
    unit_of_measure: str = "PCS"
    standard_cost: Optional[Decimal] = 0
    selling_price: Optional[Decimal] = 0
    minimum_price: Optional[Decimal] = None
    reorder_point: Optional[int] = 0
    reorder_quantity: Optional[int] = 0
    safety_stock: Optional[int] = 0
    lead_time_days: Optional[int] = 0
    weight_kg: Optional[Decimal] = None
    length_cm: Optional[Decimal] = None
    width_cm: Optional[Decimal] = None
    height_cm: Optional[Decimal] = None
    barcode: Optional[str] = None
    hs_code: Optional[str] = None
    storage_condition: Optional[str] = "GENERAL"
    security_level: Optional[int] = 1

    lot_control: bool = False  # New
    is_active: bool = True


class ItemCreate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Partner Schemas
class PartnerBase(BaseModel):
    partner_code: str
    partner_name: str
    partner_type: str
    tax_id: Optional[str] = None
    business_registration_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "Thailand"
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    credit_limit: Optional[Decimal] = 0
    payment_terms: str = "Net 30"
    currency: str = "THB"
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    primary_contact_name: Optional[str] = None
    primary_contact_phone: Optional[str] = None
    primary_contact_email: Optional[EmailStr] = None
    lead_time_production_days: Optional[int] = 0
    lead_time_transit_days: Optional[int] = 0
    is_active: bool = True


class PartnerCreate(PartnerBase):
    pass


    class Config:
        from_attributes = True


class PartnerAddressBase(BaseModel):
    address_type: str = "BILL_TO"
    address: str
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "Thailand"
    is_primary: bool = False

class PartnerAddressCreate(PartnerAddressBase):
    partner_id: int

class PartnerAddressResponse(PartnerAddressBase):
    id: int
    partner_id: int
    
    class Config:
        from_attributes = True

class PartnerResponse(PartnerBase):
    id: int
    addresses: List[PartnerAddressResponse] = []
    
    class Config:
        from_attributes = True



# Warehouse Schemas
class WarehouseBase(BaseModel):
    warehouse_code: str
    warehouse_name: str
    warehouse_type: str = "Main"
    location: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "Thailand"
    total_area_sqm: Optional[Decimal] = None
    storage_capacity_cbm: Optional[Decimal] = None
    number_of_zones: Optional[int] = None
    max_weight_capacity_tons: Optional[Decimal] = None
    operating_hours: Optional[str] = None
    security_level: str = "Standard"
    temperature_controlled: bool = False
    hazmat_certified: bool = False
    manager_name: Optional[str] = None
    manager_phone: Optional[str] = None
    manager_email: Optional[EmailStr] = None
    monthly_operating_cost: Optional[Decimal] = None
    is_active: bool = True


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseResponse(WarehouseBase):
    id: int
    
    class Config:
        from_attributes = True


# Machine Schemas
class MachineBase(BaseModel):
    machine_code: str
    machine_name: str
    location_id: Optional[int] = None
    pic_user_id: Optional[int] = None
    maintenance_vendor_id: Optional[int] = None
    maintenance_interval_days: int = 30
    status: str = "ACTIVE"
    is_active: bool = True

class MachineCreate(MachineBase):
    pass

class MachineResponse(MachineBase):
    id: int
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Inventory Schemas
class StockTransactionItem(BaseModel):
    item_code: str
    warehouse_code: str
    location_code: Optional[str] = None
    location_code: Optional[str] = None
    qty: Decimal
    lot_number: Optional[str] = None  # New


class StockTransactionCreate(BaseModel):
    transaction_date: datetime
    reference_no: str
    partner_code: Optional[str] = None
    type: str  # 'issue' or 'receipt'
    items: List[StockTransactionItem]


# WMS Schemas
class LocationBase(BaseModel):
    warehouse_id: int
    location_code: str
    zone_type: str
    zone: Optional[str] = None  # New
    rack: Optional[str] = None  # New
    shelf: Optional[str] = None  # New
    condition_type: str = "GENERAL"
    is_secure_cage: bool = False
    floor_level: int = 1

class LocationCreate(LocationBase):
    pass

class LocationResponse(LocationBase):
    id: int
    class Config:
        from_attributes = True

class SecureAccessLogCreate(BaseModel):
    transaction_type: str
    location_id: int
    operator_user_id: int
    witness_supervisor_id: Optional[int] = None

class CycleCountDetailBase(BaseModel):
    item_id: int
    location_id: Optional[int] = None
    snapshot_system_qty: Decimal
    actual_counted_qty: Optional[Decimal] = None
    snapshot_timestamp: datetime
    actual_count_timestamp: Optional[datetime] = None

class CycleCountHeaderBase(BaseModel):
    count_date: date
    warehouse_id: int
    status: str = "DRAFT"

class CycleCountHeaderCreate(CycleCountHeaderBase):
    pass

class CycleCountDetailUpdate(BaseModel):
    id: int
    actual_counted_qty: Decimal

class CycleCountDetailResponse(CycleCountDetailBase):
    id: int
    header_id: int
    item_code: Optional[str] = None # Helper for frontend
    item_name: Optional[str] = None
    location_code: Optional[str] = None

    class Config:
        from_attributes = True

class CycleCountHeaderResponse(CycleCountHeaderBase):
    id: int
    details: List[CycleCountDetailResponse] = []
    
    class Config:
        from_attributes = True


# Cost Layer Schemas
class CostLayerBase(BaseModel):
    item_id: int
    warehouse_id: int
    location_id: Optional[int] = None
    receipt_date: date
    qty_remaining: Decimal

    unit_cost: Decimal
    lot_number: Optional[str] = None  # New

class CostLayerResponse(CostLayerBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Production Planning Schemas
class MRPResultBase(BaseModel):
    item_id: int
    required_date: date
    gross_requirement: Decimal
    on_hand_qty: Decimal
    open_po_qty: Decimal
    net_requirement: Decimal
    suggested_action: Optional[str] = None
    suggested_qty: Optional[Decimal] = None

class MRPResultResponse(MRPResultBase):
    id: int
    plan_id: int
    item_code: Optional[str] = None
    item_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProductionPlanItemCreate(BaseModel):
    item_id: int
    quantity: Decimal
    delivery_date: date

class ProductionPlanItemResponse(ProductionPlanItemCreate):
    id: int
    plan_id: int
    item_code: Optional[str] = None
    item_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProductionPlanCreate(BaseModel):
    plan_name: str
    plan_type: str = "PRODUCTION"
    source_type: str  # 'ACTUAL', 'FORECAST', 'MANUAL'
    sales_order_id: Optional[int] = None
    items: List[ProductionPlanItemCreate] = []

class ProductionPlanResponse(BaseModel):
    id: int
    plan_name: str
    plan_type: str
    source_type: str
    sales_order_id: Optional[int] = None
    status: str
    created_date: datetime
    calculated_date: Optional[datetime] = None
    items: List[ProductionPlanItemResponse] = []
    mrp_results: List[MRPResultResponse] = []
    
    class Config:
        from_attributes = True


# Purchase Requisition Schemas
class DraftPRCreate(BaseModel):
    vendor_id: int
    item_id: int
    required_qty: Decimal
    required_date: date

class DraftPRResponse(BaseModel):
    id: int
    pr_no: str
    vendor_id: int
    item_id: int
    required_qty: Decimal
    required_date: date
    suggested_order_date: Optional[date] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Quality Management Schemas
class QCInspectionCreate(BaseModel):
    inspection_type: str  # 'INCOMING', 'IN_PROCESS', 'OUTGOING'
    ref_document_type: Optional[str] = None
    ref_document_id: Optional[int] = None
    remarks: Optional[str] = None

class QCDefectCreate(BaseModel):
    defect_description: str
    severity: str  # 'MINOR', 'MAJOR', 'CRITICAL'
    qty_affected: Optional[Decimal] = None
    photo_url: Optional[str] = None

class QCDefectResponse(QCDefectCreate):
    id: int
    qc_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class QCInspectionResponse(BaseModel):
    id: int
    qc_no: str
    inspection_type: str
    status: str
    inspection_date: datetime
    completed_date: Optional[datetime] = None
    remarks: Optional[str] = None
    defects: List[QCDefectResponse] = []
    
    class Config:
        from_attributes = True


# BOM Enhanced Schemas
class BOMCreate(BaseModel):
    parent_item_id: int
    child_item_id: int
    bom_type: str = "ASSEMBLY"  # 'ASSEMBLY', 'FORMULA', 'MODULAR', 'TAILOR_MADE'
    is_template: bool = True
    sequence_order: int = 0
    quantity: Decimal
    percentage: Optional[Decimal] = None
    is_optional: bool = False
    scrap_factor: Optional[Decimal] = 0
    # New fields
    production_location_id: Optional[int] = None
    storage_location_id: Optional[int] = None
    is_byproduct: bool = False

    machine_id: Optional[int] = None  # New
    production_lead_time_days: Optional[Decimal] = 0  # New
    capacity_per_hour: Optional[Decimal] = 0  # New
    is_byproduct: bool = False
    remark: Optional[str] = None
    revision: int = 1
    status: str = "ACTIVE"  # 'ACTIVE', 'INACTIVE'
    active_date: Optional[date] = None
    inactive_date: Optional[date] = None


class BOMUpdate(BaseModel):
    """Schema for updating BOM line"""
    bom_type: Optional[str] = None
    is_template: Optional[bool] = None
    sequence_order: Optional[int] = None
    quantity: Optional[Decimal] = None
    percentage: Optional[Decimal] = None
    is_optional: Optional[bool] = None
    scrap_factor: Optional[Decimal] = None
    production_location_id: Optional[int] = None
    storage_location_id: Optional[int] = None
    is_byproduct: Optional[bool] = None

    machine_id: Optional[int] = None  # New
    production_lead_time_days: Optional[Decimal] = None  # New
    capacity_per_hour: Optional[Decimal] = None  # New
    is_byproduct: Optional[bool] = None
    remark: Optional[str] = None
    status: Optional[str] = None
    active_date: Optional[date] = None
    inactive_date: Optional[date] = None


class BOMResponse(BOMCreate):
    id: int
    is_active: bool
    revision_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class BOMRevisionCreate(BaseModel):
    """Schema for creating a new BOM revision"""
    parent_item_id: int
    source_revision: Optional[int] = None  # If copying from existing revision
    remark: Optional[str] = None


class BOMExportRequest(BaseModel):
    """Schema for export request"""
    parent_item_ids: List[int] = []  # Empty = all items
    include_all_revisions: bool = False
    include_inactive: bool = False


# BOM Explosion Schemas
class BOMExplosionRequest(BaseModel):
    """Request for BOM explosion"""
    parent_item_id: int
    quantity: Decimal = Decimal("1.0")  # Desired production quantity
    revision: Optional[int] = None  # Specific revision, or None for active
    include_optional: bool = False  # Include optional components
    include_byproducts: bool = False  # Include by-products in output
    max_levels: int = 10  # Maximum depth to prevent infinite loops


class BOMExplosionLine(BaseModel):
    """Single line in BOM explosion result"""
    level: int  # 0 = top level, 1 = first sub-level, etc.
    item_id: int
    item_code: str
    item_name: str
    item_type: str
    unit_of_measure: str
    
    # Quantity calculations
    bom_quantity: Decimal  # Quantity per parent
    required_quantity: Decimal  # Total quantity needed (after explosion)
    scrap_factor: Decimal  # Scrap percentage
    scrap_quantity: Decimal  # Quantity lost to scrap
    total_quantity: Decimal  # Required + scrap = Total to produce/purchase
    
    # BOM details
    bom_type: str
    is_optional: bool
    is_byproduct: bool
    sequence_order: int
    percentage: Optional[Decimal] = None
    
    # Location info
    production_location: Optional[str] = None
    storage_location: Optional[str] = None
    
    # Parent reference
    parent_item_id: int
    parent_item_code: str
    
    # Source BOM info
    bom_id: int
    revision: int
    remark: Optional[str] = None
    
    class Config:
        from_attributes = True


class BOMExplosionResponse(BaseModel):
    """Complete BOM explosion result"""
    parent_item_id: int
    parent_item_code: str
    parent_item_name: str
    requested_quantity: Decimal
    revision: int
    explosion_date: datetime
    
    # Summary statistics
    total_levels: int
    total_components: int
    total_raw_materials: int  # Items with no further BOM
    has_optional_items: bool
    has_byproducts: bool
    
    # Detailed breakdown
    lines: List[BOMExplosionLine]
    
    # Grouped by item (consolidated)
    consolidated: Optional[List[dict]] = None  # Same items summed up
    
    class Config:
        from_attributes = True


# Packaging Schemas
class PackagingBOMCreate(BaseModel):
    fg_item_id: int
    packaging_item_id: int
    qty_per_fg: Decimal

class PackagingBOMResponse(PackagingBOMCreate):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True


# Work Order Schemas
class WorkOrderDetailCreate(BaseModel):
    """Material line item for Work Order"""
    item_id: int
    qty_required: Decimal
    

class WorkOrderDetailResponse(BaseModel):
    """Work Order material detail with enriched data"""
    id: int
    job_id: int
    item_id: int
    item_code: str
    item_name: str
    unit_of_measure: str
    qty_required: Decimal

    qty_consumed: Decimal
    lot_number: Optional[str] = None  # New
    qty_remaining: Decimal  # Calculated
    percent_consumed: Decimal  # Calculated
    
    class Config:
        from_attributes = True


class WorkOrderCreate(BaseModel):
    """Create new Work Order"""
    item_id: int  # Item to produce
    qty_planned: Decimal
    start_date: date
    end_date: Optional[date] = None
    warehouse_id: int
    bom_revision: Optional[int] = None  # Specific BOM revision to use
    notes: Optional[str] = None


class WorkOrderGenerateFromBOM(BaseModel):
    """Generate Work Order using BOM explosion"""
    item_id: int
    qty_planned: Decimal
    start_date: date
    end_date: Optional[date] = None
    warehouse_id: int
    bom_revision: Optional[int] = None
    include_optional: bool = False  # Include optional components
    auto_generate_material_lines: bool = True  # Use BOM explosion


class WorkOrderUpdate(BaseModel):
    """Update Work Order"""
    qty_planned: Optional[Decimal] = None
    qty_produced: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None  # PLANNED, IN_PROGRESS, COMPLETED, CANCELLED
    notes: Optional[str] = None


class WorkOrderResponse(BaseModel):
    """Work Order with details"""
    id: int
    job_no: str
    item_id: int
    item_code: str
    item_name: str
    unit_of_measure: str
    qty_planned: Decimal
    qty_produced: Decimal
    start_date: date
    end_date: Optional[date] = None
    status: str
    warehouse_id: int
    warehouse_code: str
    warehouse_name: str
    created_by: int
    created_by_name: str

    created_at: datetime
    lot_number: Optional[str] = None  # New
    
    # Material details
    materials: List[WorkOrderDetailResponse] = []
    
    # Calculated fields
    percent_complete: Decimal  # qty_produced / qty_planned * 100
    materials_consumed_percent: Decimal  # Average of all material consumption
    is_overdue: bool  # Today > end_date and status != COMPLETED
    days_remaining: Optional[int] = None  # end_date - today
    
    class Config:
        from_attributes = True


class MaterialConsumption(BaseModel):
    """Record material consumption"""
    job_id: int
    item_id: int

    qty_consumed: Decimal
    lot_number: Optional[str] = None  # New
    consumed_by: Optional[int] = None  # User ID
    notes: Optional[str] = None


class MaterialIssue(BaseModel):
    """Issue materials to Work Order (multiple items at once)"""
    job_id: int
    items: List[dict]  # [{"item_id": 1, "qty": 10}, ...]
    issued_by: Optional[int] = None
    notes: Optional[str] = None


class WorkOrderCompletion(BaseModel):
    """Complete Work Order and produce finished goods"""
    job_id: int

    qty_produced: Decimal
    lot_number: Optional[str] = None  # New
    completed_by: Optional[int] = None
    auto_consume_remaining: bool = True  # Consume remaining materials
    post_to_inventory: bool = True  # Create inventory transaction
    notes: Optional[str] = None
