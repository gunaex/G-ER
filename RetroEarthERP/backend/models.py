"""
SQLAlchemy Models for RetroEarthERP
Includes all 26 tables with multi-language support
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Numeric,
    ForeignKey, Enum as SQLEnum, Text, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


# Enums
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class ThemePreference(str, enum.Enum):
    RETRO_EARTH = "RETRO_EARTH"
    MODERN_CLEAN = "MODERN_CLEAN"
    SPACE_FUTURE = "SPACE_FUTURE"


class CostingMethod(str, enum.Enum):
    STANDARD = "STANDARD"
    AVERAGE = "AVERAGE"
    FIFO = "FIFO"


class InventorySystem(str, enum.Enum):
    PERPETUAL = "PERPETUAL"
    PERIODIC = "PERIODIC"


class ItemType(str, enum.Enum):
    RAW_MATERIAL = "RAW_MATERIAL"
    COMPONENT = "COMPONENT"
    FINISHED_GOOD = "FINISHED_GOOD"
    WIP = "WIP"  # Work In Progress items
    PACKAGE = "PACKAGE"  # Packaging items
    SERVICE = "SERVICE"


class PartnerType(str, enum.Enum):
    VENDOR = "VENDOR"
    CUSTOMER = "CUSTOMER"
    BOTH = "BOTH"


class POStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    PARTIAL_RECEIVED = "PARTIAL_RECEIVED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class SOStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    PARTIAL_DELIVERED = "PARTIAL_DELIVERED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class DocumentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    CANCELLED = "CANCELLED"


class ConditionType(str, enum.Enum):
    COLD = "COLD"
    HAZMAT = "HAZMAT"
    SECURE = "SECURE"
    GENERAL = "GENERAL"


class JobStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class MRPStatus(str, enum.Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SuggestedAction(str, enum.Enum):
    BUY = "BUY"
    MAKE = "MAKE"
    NONE = "NONE"


class Incoterm(str, enum.Enum):
    EXW = "EXW"
    FOB = "FOB"
    CIF = "CIF"
    DDP = "DDP"
    DAP = "DAP"


class AddressType(str, enum.Enum):
    BILL_TO = "BILL_TO"
    SHIP_TO = "SHIP_TO"


class MachineStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    MAINTENANCE = "MAINTENANCE"
    INACTIVE = "INACTIVE"


class AccountType(str, enum.Enum):
    ASSET = "ASSET"        # 1. สินทรัพย์
    LIABILITY = "LIABILITY" # 2. หนี้สิน
    EQUITY = "EQUITY"       # 3. ส่วนของเจ้าของ
    REVENUE = "REVENUE"     # 4. รายได้
    EXPENSE = "EXPENSE"     # 5. ค่าใช้จ่าย



# System Tables
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    theme_preference = Column(SQLEnum(ThemePreference), default=ThemePreference.RETRO_EARTH)
    language = Column(String(5), default="en")  # 'en' or 'th'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)


class CompanySettings(Base):
    __tablename__ = "company_settings"
    
    id = Column(Integer, primary_key=True)
    company_name = Column(String(200), nullable=False)
    tax_id = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    costing_method = Column(SQLEnum(CostingMethod), default=CostingMethod.AVERAGE)
    inventory_system = Column(SQLEnum(InventorySystem), default=InventorySystem.PERPETUAL)
    base_currency = Column(String(3), default="THB")
    fiscal_year_start = Column(Integer, default=1)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LicensePackage(Base):
    __tablename__ = "license_packages"
    
    id = Column(Integer, primary_key=True, index=True)
    package_code = Column(String(50), unique=True, nullable=False)
    package_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LicenseActivation(Base):
    __tablename__ = "license_activations"
    
    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, ForeignKey("license_packages.id"), nullable=False)
    license_key = Column(String(100), unique=True, nullable=False)
    activated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    activated_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    max_users = Column(Integer, default=5)
    
    package = relationship("LicensePackage")
    user = relationship("User")


class AppMarketplace(Base):
    __tablename__ = "app_marketplace"
    
    id = Column(Integer, primary_key=True, index=True)
    app_code = Column(String(50), unique=True, nullable=False)
    app_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon_name = Column(String(50), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    required_package = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    category = Column(String(50), nullable=True)


class AppDependency(Base):
    __tablename__ = "app_dependencies"
    
    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("app_marketplace.id"), nullable=False)
    required_app_id = Column(Integer, ForeignKey("app_marketplace.id"), nullable=False)
    
    app = relationship("AppMarketplace", foreign_keys=[app_id])
    required_app = relationship("AppMarketplace", foreign_keys=[required_app_id])


class AppActivation(Base):
    __tablename__ = "app_activations"
    
    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("app_marketplace.id"), nullable=False)
    license_key = Column(String(100), unique=True, nullable=False)
    activated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    activated_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    app = relationship("AppMarketplace")
    user = relationship("User")


class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(50), nullable=False)
    table_name = Column(String(50), nullable=True)
    record_id = Column(Integer, nullable=True)
    before_data = Column(JSON, nullable=True)
    after_data = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    user = relationship("User")


# Master Data Tables
class MasterItem(Base):
    __tablename__ = "master_items"
    
    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(50), unique=True, nullable=False, index=True)
    item_name = Column(String(200), nullable=False)
    item_type = Column(SQLEnum(ItemType), nullable=False, index=True)
    category = Column(String(100), nullable=True)
    unit_of_measure = Column(String(20), nullable=False, default="PCS")
    standard_cost = Column(Numeric(15, 4), default=0)
    selling_price = Column(Numeric(15, 4), default=0)
    minimum_price = Column(Numeric(15, 4), nullable=True)
    reorder_point = Column(Integer, default=0)
    reorder_quantity = Column(Integer, default=0)
    safety_stock = Column(Integer, default=0)
    lead_time_days = Column(Integer, default=0)
    weight_kg = Column(Numeric(10, 3), nullable=True)
    length_cm = Column(Numeric(10, 2), nullable=True)
    width_cm = Column(Numeric(10, 2), nullable=True)
    height_cm = Column(Numeric(10, 2), nullable=True)
    barcode = Column(String(100), nullable=True)
    hs_code = Column(String(50), nullable=True)
    storage_condition = Column(SQLEnum(ConditionType), default=ConditionType.GENERAL)
    security_level = Column(Integer, default=1)  # 1=Normal, 2+=High Value
    lot_control = Column(Boolean, default=False)  # New: Mandatory lot control
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MasterBusinessPartner(Base):
    __tablename__ = "master_business_partners"
    
    id = Column(Integer, primary_key=True, index=True)
    partner_code = Column(String(50), unique=True, nullable=False, index=True)
    partner_name = Column(String(200), nullable=False)
    partner_type = Column(SQLEnum(PartnerType), nullable=False, index=True)
    tax_id = Column(String(50), nullable=True)
    business_registration_number = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), default="Thailand")
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    credit_limit = Column(Numeric(15, 2), default=0)
    payment_terms = Column(String(50), default="Net 30")
    currency = Column(String(10), default="THB")
    bank_name = Column(String(200), nullable=True)
    bank_account_number = Column(String(100), nullable=True)
    primary_contact_name = Column(String(100), nullable=True)
    primary_contact_phone = Column(String(20), nullable=True)
    primary_contact_email = Column(String(100), nullable=True)
    lead_time_production_days = Column(Integer, default=0)
    lead_time_transit_days = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    addresses = relationship("PartnerAddress", back_populates="partner")


class PartnerAddress(Base):
    __tablename__ = "partner_addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("master_business_partners.id"), nullable=False)
    address_type = Column(SQLEnum(AddressType), default=AddressType.BILL_TO)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), default="Thailand")
    is_primary = Column(Boolean, default=False)
    
    partner = relationship("MasterBusinessPartner", back_populates="addresses")



class MasterWarehouse(Base):
    __tablename__ = "master_warehouses"
    
    id = Column(Integer, primary_key=True, index=True)
    warehouse_code = Column(String(50), unique=True, nullable=False)
    warehouse_name = Column(String(100), nullable=False)
    warehouse_type = Column(String(50), default="Main")
    location = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), default="Thailand")
    total_area_sqm = Column(Numeric(10, 2), nullable=True)
    storage_capacity_cbm = Column(Numeric(10, 2), nullable=True)
    number_of_zones = Column(Integer, nullable=True)
    max_weight_capacity_tons = Column(Numeric(10, 2), nullable=True)
    operating_hours = Column(String(100), nullable=True)
    security_level = Column(String(50), default="Standard")
    temperature_controlled = Column(Boolean, default=False)
    hazmat_certified = Column(Boolean, default=False)
    manager_name = Column(String(100), nullable=True)
    manager_phone = Column(String(20), nullable=True)
    manager_email = Column(String(100), nullable=True)
    monthly_operating_cost = Column(Numeric(15, 2), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())



class LocationMaster(Base):
    __tablename__ = "location_master"
    
    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("master_warehouses.id"), nullable=False)
    location_code = Column(String(50), unique=True, nullable=False)
    zone_type = Column(String(50), nullable=False) # RECEIVE, STORE, PICK, RM, WIP, FG, QUARANTINE
    zone = Column(String(50), nullable=True)  # New: Zone identifier
    rack = Column(String(50), nullable=True)  # New: Rack identifier
    shelf = Column(String(50), nullable=True)  # New: Shelf identifier
    condition_type = Column(SQLEnum(ConditionType), default=ConditionType.GENERAL)
    is_secure_cage = Column(Boolean, default=False)
    floor_level = Column(Integer, default=1)
    
    warehouse = relationship("MasterWarehouse")


class MasterMachine(Base):
    __tablename__ = "master_machines"
    
    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String(50), unique=True, nullable=False, index=True)
    machine_name = Column(String(100), nullable=False)
    location_id = Column(Integer, ForeignKey("location_master.id"), nullable=True)
    pic_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Person In Charge
    maintenance_vendor_id = Column(Integer, ForeignKey("master_business_partners.id"), nullable=True)
    maintenance_interval_days = Column(Integer, default=30)
    last_maintenance_date = Column(Date, nullable=True)
    next_maintenance_date = Column(Date, nullable=True)
    qa_representative_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(SQLEnum(MachineStatus), default=MachineStatus.ACTIVE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    location = relationship("LocationMaster")
    pic = relationship("User", foreign_keys=[pic_user_id])
    maintenance_vendor = relationship("MasterBusinessPartner")
    qa_rep = relationship("User", foreign_keys=[qa_representative_id])



class SecureAccessLog(Base):
    __tablename__ = "secure_access_log"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(String(20), nullable=False) # PICK, PUT
    location_id = Column(Integer, ForeignKey("location_master.id"), nullable=False)
    operator_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    witness_supervisor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    location = relationship("LocationMaster")
    operator = relationship("User", foreign_keys=[operator_user_id])
    witness = relationship("User", foreign_keys=[witness_supervisor_id])


class CycleCountHeader(Base):
    __tablename__ = "cycle_count_header"
    
    id = Column(Integer, primary_key=True, index=True)
    count_date = Column(Date, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("master_warehouses.id"), nullable=False)
    status = Column(String(20), default="DRAFT") # DRAFT, COMPLETED
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    warehouse = relationship("MasterWarehouse")
    creator = relationship("User")
    details = relationship("CycleCountDetail", back_populates="header")


class CycleCountDetail(Base):
    __tablename__ = "cycle_count_detail"
    
    id = Column(Integer, primary_key=True, index=True)
    header_id = Column(Integer, ForeignKey("cycle_count_header.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("location_master.id"), nullable=True)
    snapshot_system_qty = Column(Numeric(15, 4), nullable=False)
    actual_counted_qty = Column(Numeric(15, 4), nullable=True)
    snapshot_timestamp = Column(DateTime(timezone=True), nullable=False)
    actual_count_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    header = relationship("CycleCountHeader", back_populates="details")
    item = relationship("MasterItem")
    location = relationship("LocationMaster")


# Transaction Tables - Purchase
class TrnPurchaseOrderHead(Base):
    __tablename__ = "trn_purchase_order_head"
    
    id = Column(Integer, primary_key=True, index=True)
    po_no = Column(String(50), unique=True, nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("master_business_partners.id"), nullable=False)
    po_date = Column(Date, nullable=False)
    delivery_date = Column(Date, nullable=True)
    status = Column(SQLEnum(POStatus), default=POStatus.DRAFT, index=True)
    total_amount = Column(Numeric(15, 2), default=0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    incoterm = Column(SQLEnum(Incoterm), nullable=True)  # New: Incoterm
    payment_term = Column(String(50), nullable=True)
    currency = Column(String(10), default="THB")
    
    vendor = relationship("MasterBusinessPartner")
    creator = relationship("User")
    details = relationship("TrnPurchaseOrderDetail", back_populates="po_head")


class TrnPurchaseOrderDetail(Base):
    __tablename__ = "trn_purchase_order_detail"
    
    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("trn_purchase_order_head.id"), nullable=False)
    line_no = Column(Integer, nullable=False)
    item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False)
    qty_ordered = Column(Numeric(15, 4), nullable=False)
    qty_received = Column(Numeric(15, 4), default=0)
    unit_price = Column(Numeric(15, 4), nullable=False)
    
    po_head = relationship("TrnPurchaseOrderHead", back_populates="details")
    item = relationship("MasterItem")


class TrnGoodsReceiptHead(Base):
    __tablename__ = "trn_goods_receipt_head"
    
    id = Column(Integer, primary_key=True, index=True)
    gr_no = Column(String(50), unique=True, nullable=False)
    po_id = Column(Integer, ForeignKey("trn_purchase_order_head.id"), nullable=False)
    gr_date = Column(Date, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("master_warehouses.id"), nullable=False)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.DRAFT)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    posted_at = Column(DateTime(timezone=True), nullable=True)
    
    purchase_order = relationship("TrnPurchaseOrderHead")
    warehouse = relationship("MasterWarehouse")
    creator = relationship("User")
    details = relationship("TrnGoodsReceiptDetail", back_populates="gr_head")


class TrnGoodsReceiptDetail(Base):
    __tablename__ = "trn_goods_receipt_detail"
    
    id = Column(Integer, primary_key=True, index=True)
    gr_id = Column(Integer, ForeignKey("trn_goods_receipt_head.id"), nullable=False)
    line_no = Column(Integer, nullable=False)
    item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False)
    qty_received = Column(Numeric(15, 4), nullable=False)
    unit_cost = Column(Numeric(15, 4), nullable=False)
    lot_number = Column(String(50), nullable=True)  # New: Lot tracking
    expiry_date = Column(Date, nullable=True)  # New: Expiry date
    manufacturing_date = Column(Date, nullable=True)  # New: Mfg date
    
    gr_head = relationship("TrnGoodsReceiptHead", back_populates="details")
    item = relationship("MasterItem")


# Transaction Tables - Sales
class TrnSalesOrderHead(Base):
    __tablename__ = "trn_sales_order_head"
    
    id = Column(Integer, primary_key=True, index=True)
    so_no = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("master_business_partners.id"), nullable=False)
    so_date = Column(Date, nullable=False)
    delivery_date = Column(Date, nullable=True)
    status = Column(SQLEnum(SOStatus), default=SOStatus.DRAFT, index=True)
    total_amount = Column(Numeric(15, 2), default=0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    customer = relationship("MasterBusinessPartner")
    creator = relationship("User")
    details = relationship("TrnSalesOrderDetail", back_populates="so_head")


class TrnSalesOrderDetail(Base):
    __tablename__ = "trn_sales_order_detail"
    
    id = Column(Integer, primary_key=True, index=True)
    so_id = Column(Integer, ForeignKey("trn_sales_order_head.id"), nullable=False)
    line_no = Column(Integer, nullable=False)
    item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False)
    qty_ordered = Column(Numeric(15, 4), nullable=False)
    qty_delivered = Column(Numeric(15, 4), default=0)
    unit_price = Column(Numeric(15, 4), nullable=False)
    
    so_head = relationship("TrnSalesOrderHead", back_populates="details")
    item = relationship("MasterItem")


class TrnDeliveryOrderHead(Base):
    __tablename__ = "trn_delivery_order_head"
    
    id = Column(Integer, primary_key=True, index=True)
    do_no = Column(String(50), unique=True, nullable=False)
    so_id = Column(Integer, ForeignKey("trn_sales_order_head.id"), nullable=False)
    do_date = Column(Date, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("master_warehouses.id"), nullable=False)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.DRAFT)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    posted_at = Column(DateTime(timezone=True), nullable=True)
    
    sales_order = relationship("TrnSalesOrderHead")
    warehouse = relationship("MasterWarehouse")
    creator = relationship("User")
    details = relationship("TrnDeliveryOrderDetail", back_populates="do_head")


class TrnDeliveryOrderDetail(Base):
    __tablename__ = "trn_delivery_order_detail"
    
    id = Column(Integer, primary_key=True, index=True)
    do_id = Column(Integer, ForeignKey("trn_delivery_order_head.id"), nullable=False)
    line_no = Column(Integer, nullable=False)
    item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False)
    qty_delivered = Column(Numeric(15, 4), nullable=False)
    unit_price = Column(Numeric(15, 4), nullable=False)
    lot_number = Column(String(50), nullable=True)  # New: Lot tracking
    
    do_head = relationship("TrnDeliveryOrderHead", back_populates="details")
    item = relationship("MasterItem")


class TrnQuotationHead(Base):
    __tablename__ = "trn_quotation_head"
    
    id = Column(Integer, primary_key=True, index=True)
    quotation_no = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("master_business_partners.id"), nullable=False)
    quotation_date = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=True)
    status = Column(SQLEnum('DRAFT', 'SENT', 'ACCEPTED', 'REJECTED', 'CONVERTED', name='quotation_status_enum'), default='DRAFT')
    total_amount = Column(Numeric(15, 2), default=0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    customer = relationship("MasterBusinessPartner")
    creator = relationship("User")
    details = relationship("TrnQuotationDetail", back_populates="quotation_head")


class TrnQuotationDetail(Base):
    __tablename__ = "trn_quotation_detail"
    
    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("trn_quotation_head.id"), nullable=False)
    line_no = Column(Integer, nullable=False)
    item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False)
    qty = Column(Numeric(15, 4), nullable=False)
    unit_price = Column(Numeric(15, 4), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    
    quotation_head = relationship("TrnQuotationHead", back_populates="details")
    item = relationship("MasterItem")


class TrnTaxInvoiceHead(Base):
    __tablename__ = "trn_tax_invoice_head"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_no = Column(String(50), unique=True, nullable=False, index=True)
    do_id = Column(Integer, ForeignKey("trn_delivery_order_head.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("master_business_partners.id"), nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(SQLEnum('DRAFT', 'POSTED', 'PAID', 'CANCELLED', name='invoice_status_enum'), default='DRAFT')
    subtotal = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), default=0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    delivery_order = relationship("TrnDeliveryOrderHead")
    customer = relationship("MasterBusinessPartner")
    creator = relationship("User")
    details = relationship("TrnTaxInvoiceDetail", back_populates="invoice_head")


class TrnTaxInvoiceDetail(Base):
    __tablename__ = "trn_tax_invoice_detail"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("trn_tax_invoice_head.id"), nullable=False)
    line_no = Column(Integer, nullable=False)
    item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False)
    qty = Column(Numeric(15, 4), nullable=False)
    unit_price = Column(Numeric(15, 4), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    invoice_head = relationship("TrnTaxInvoiceHead", back_populates="details")
    item = relationship("MasterItem")


# BOM Status Enum
class BOMStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


# Production Tables
class MasterBOM(Base):
    __tablename__ = "master_bom"
    
    id = Column(Integer, primary_key=True, index=True)
    parent_item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False, index=True)
    child_item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False)
    bom_type = Column(SQLEnum('ASSEMBLY', 'FORMULA', 'MODULAR', 'TAILOR_MADE', name='bom_type_enum'), default='ASSEMBLY')
    is_template = Column(Boolean, default=True)  # False for tailor-made WO-specific BOMs
    sequence_order = Column(Integer, default=0)  # For ASSEMBLY type
    quantity = Column(Numeric(15, 4), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=True)  # For FORMULA type (e.g., 25.5% of batch)
    is_optional = Column(Boolean, default=False)  # For MODULAR type
    scrap_factor = Column(Numeric(5, 2), default=0)
    
    # New fields for enhanced BOM management
    production_location_id = Column(Integer, ForeignKey("location_master.id"), nullable=True)  # Where item is produced
    storage_location_id = Column(Integer, ForeignKey("location_master.id"), nullable=True)  # Where item is stored
    machine_id = Column(Integer, ForeignKey("master_machines.id"), nullable=True)  # New: Machine assignment
    production_lead_time_days = Column(Numeric(10, 2), default=0)  # New: Lead time
    capacity_per_hour = Column(Numeric(10, 2), default=0)  # New: Capacity
    is_byproduct = Column(Boolean, default=False)  # Is this a by-product
    remark = Column(Text, nullable=True)  # Additional notes
    
    # Revision management
    revision = Column(Integer, default=1, nullable=False)  # BOM revision number
    revision_date = Column(DateTime(timezone=True), server_default=func.now())  # When this revision was created
    
    # Status management
    status = Column(SQLEnum(BOMStatus), default=BOMStatus.ACTIVE)
    active_date = Column(Date, nullable=True)  # When BOM becomes active
    inactive_date = Column(Date, nullable=True)  # When BOM becomes inactive
    
    is_active = Column(Boolean, default=True)  # Soft delete flag
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent_item = relationship("MasterItem", foreign_keys=[parent_item_id])
    child_item = relationship("MasterItem", foreign_keys=[child_item_id])
    production_location = relationship("LocationMaster", foreign_keys=[production_location_id])
    storage_location = relationship("LocationMaster", foreign_keys=[storage_location_id])
    machine = relationship("MasterMachine")
    creator = relationship("User", foreign_keys=[created_by])


class TrnJobOrderHead(Base):
    __tablename__ = "trn_job_order_head"
    
    id = Column(Integer, primary_key=True, index=True)
    job_no = Column(String(50), unique=True, nullable=False)
    item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False)
    qty_planned = Column(Numeric(15, 4), nullable=False)
    qty_produced = Column(Numeric(15, 4), default=0)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PLANNED)
    warehouse_id = Column(Integer, ForeignKey("master_warehouses.id"), nullable=False)
    lot_number = Column(String(50), nullable=True)  # New: Produced Lot Number
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    item = relationship("MasterItem")
    warehouse = relationship("MasterWarehouse")
    creator = relationship("User")
    details = relationship("TrnJobOrderDetail", back_populates="job_head")


class TrnJobOrderDetail(Base):
    __tablename__ = "trn_job_order_detail"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("trn_job_order_head.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False)
    qty_required = Column(Numeric(15, 4), nullable=False)
    qty_consumed = Column(Numeric(15, 4), default=0)
    lot_number = Column(String(50), nullable=True)  # New: Consumed Lot Number
    
    job_head = relationship("TrnJobOrderHead", back_populates="details")
    item = relationship("MasterItem")


# MRP Tables
class MRPScenario(Base):
    __tablename__ = "mrp_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_name = Column(String(100), nullable=False)
    run_date = Column(DateTime(timezone=True), server_default=func.now())
    run_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(MRPStatus), default=MRPStatus.COMPLETED)
    
    user = relationship("User")


class MRPResult(Base):
    __tablename__ = "mrp_results"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("production_plan.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False)
    required_date = Column(Date, nullable=False)
    gross_requirement = Column(Numeric(15, 4), nullable=False)
    on_hand_qty = Column(Numeric(15, 4), default=0)
    open_po_qty = Column(Numeric(15, 4), default=0)
    net_requirement = Column(Numeric(15, 4), nullable=False)
    suggested_action = Column(SQLEnum(SuggestedAction), nullable=True)
    suggested_qty = Column(Numeric(15, 4), nullable=True)
    
    plan = relationship("ProductionPlan", back_populates="mrp_results")
    item = relationship("MasterItem")


# Inventory Tables
class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("master_warehouses.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("location_master.id"), nullable=True)
    lot_number = Column(String(50), nullable=True)  # New: Lot tracking
    transaction_type = Column(String(20), nullable=False)
    reference_no = Column(String(50), nullable=True)
    qty = Column(Numeric(15, 4), nullable=False)
    unit_cost = Column(Numeric(15, 4), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    item = relationship("MasterItem")
    warehouse = relationship("MasterWarehouse")
    location = relationship("LocationMaster") # Added
    user = relationship("User")


class InventoryBalance(Base):
    __tablename__ = "inventory_balance"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("master_warehouses.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("location_master.id"), nullable=True)
    lot_number = Column(String(50), nullable=True)  # New: Lot tracking
    qty_on_hand = Column(Numeric(15, 4), default=0)
    avg_cost = Column(Numeric(15, 4), default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    item = relationship("MasterItem")
    warehouse = relationship("MasterWarehouse")
    location = relationship("LocationMaster") # Added


# FIFO Cost Tracking
class InventoryCostLayer(Base):
    __tablename__ = "inventory_cost_layer"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("master_warehouses.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("location_master.id"), nullable=True)
    receipt_date = Column(Date, nullable=False)
    qty_remaining = Column(Numeric(15, 4), nullable=False)
    unit_cost = Column(Numeric(15, 4), nullable=False)
    receipt_transaction_id = Column(Integer, ForeignKey("inventory_transactions.id"), nullable=True)
    lot_number = Column(String(50), nullable=True)  # New: Lot tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    item = relationship("MasterItem")
    warehouse = relationship("MasterWarehouse")
    location = relationship("LocationMaster")


# Production Planning Tables
class ProductionPlan(Base):
    __tablename__ = "production_plan"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_name = Column(String(100), nullable=False)
    plan_type = Column(SQLEnum('PRODUCTION', 'FORECAST', name='plan_type_enum'), default='PRODUCTION')
    source_type = Column(SQLEnum('ACTUAL', 'FORECAST', 'MANUAL', name='source_type_enum'), nullable=False)
    sales_order_id = Column(Integer, ForeignKey("trn_sales_order_head.id"), nullable=True)  # For traceability
    status = Column(SQLEnum('DRAFT', 'CALCULATED', 'PROCESSED', name='plan_status_enum'), default='DRAFT')
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    calculated_date = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    creator = relationship("User")
    sales_order = relationship("TrnSalesOrderHead", foreign_keys=[sales_order_id])
    items = relationship("ProductionPlanItem", back_populates="plan", cascade="all, delete-orphan")
    mrp_results = relationship("MRPResult", back_populates="plan", cascade="all, delete-orphan")


class ProductionPlanItem(Base):
    __tablename__ = "production_plan_items"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("production_plan.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False)
    quantity = Column(Numeric(15, 4), nullable=False)
    delivery_date = Column(Date, nullable=False)
    
    plan = relationship("ProductionPlan", back_populates="items")
    item = relationship("MasterItem")


class DraftPurchaseRequisition(Base):
    __tablename__ = "draft_purchase_requisition"
    
    id = Column(Integer, primary_key=True, index=True)
    pr_no = Column(String(50), unique=True, nullable=False)
    plan_id = Column(Integer, ForeignKey("production_plan.id"), nullable=True)
    vendor_id = Column(Integer, ForeignKey("master_business_partners.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False)
    required_qty = Column(Numeric(15, 4), nullable=False)
    required_date = Column(Date, nullable=False)
    suggested_order_date = Column(Date, nullable=True)
    status = Column(SQLEnum('DRAFT', 'APPROVED', 'CONVERTED_TO_PO', 'REJECTED', name='pr_status_enum'), default='DRAFT')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    plan = relationship("ProductionPlan")
    vendor = relationship("MasterBusinessPartner")
    item = relationship("MasterItem")
    approver = relationship("User", foreign_keys=[approved_by])


# Quality Management Tables
class QualityInspectionHeader(Base):
    __tablename__ = "quality_inspection_header"
    
    id = Column(Integer, primary_key=True, index=True)
    qc_no = Column(String(50), unique=True, nullable=False)
    inspection_type = Column(SQLEnum('INCOMING', 'IN_PROCESS', 'OUTGOING', name='inspection_type_enum'), nullable=False)
    ref_document_type = Column(String(20), nullable=True)  # 'GR', 'WO', 'DO'
    ref_document_id = Column(Integer, nullable=True)
    status = Column(SQLEnum('PENDING', 'PASS', 'FAIL', 'CONDITIONAL', name='qc_status_enum'), default='PENDING')
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    inspection_date = Column(DateTime(timezone=True), server_default=func.now())
    completed_date = Column(DateTime(timezone=True), nullable=True)
    remarks = Column(Text, nullable=True)
    
    inspector = relationship("User")
    defects = relationship("QualityInspectionDefect", back_populates="inspection")


class QualityInspectionDefect(Base):
    __tablename__ = "quality_inspection_defects"
    
    id = Column(Integer, primary_key=True, index=True)
    qc_id = Column(Integer, ForeignKey("quality_inspection_header.id"), nullable=False)
    defect_description = Column(Text, nullable=False)
    photo_url = Column(String(500), nullable=True)
    severity = Column(SQLEnum('MINOR', 'MAJOR', 'CRITICAL', name='defect_severity_enum'), nullable=False)
    qty_affected = Column(Numeric(15, 4), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    inspection = relationship("QualityInspectionHeader", back_populates="defects")


# Packaging BOM
class PackagingBOM(Base):
    __tablename__ = "packaging_bom"
    
    id = Column(Integer, primary_key=True, index=True)
    fg_item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False)
    packaging_item_id = Column(Integer, ForeignKey("master_items.id"), nullable=False)
    qty_per_fg = Column(Numeric(15, 4), nullable=False)
    is_active = Column(Boolean, default=True)
    
    fg_item = relationship("MasterItem", foreign_keys=[fg_item_id])
    packaging_item = relationship("MasterItem", foreign_keys=[packaging_item_id])


# Accounting Tables
class MasterAccount(Base):
    __tablename__ = "master_account"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)  # e.g., 1001
    name = Column(String(200), nullable=False)  # e.g., Cash on Hand
    account_type = Column(SQLEnum(AccountType), nullable=False)
    parent_id = Column(Integer, ForeignKey("master_account.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    
    parent = relationship("MasterAccount", remote_side=[id], backref="children")
    journal_lines = relationship("TrnJournalEntryLine", back_populates="account")


class TrnJournalEntryHead(Base):
    __tablename__ = "trn_journal_entry_head"
    
    id = Column(Integer, primary_key=True, index=True)
    journal_no = Column(String(50), unique=True, nullable=False)  # e.g., JV-202511001
    date = Column(Date, nullable=False)
    description = Column(String(255), nullable=True)
    reference = Column(String(100), nullable=True)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.DRAFT)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    posted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    creator = relationship("User", foreign_keys=[created_by])
    poster = relationship("User", foreign_keys=[posted_by])
    lines = relationship("TrnJournalEntryLine", back_populates="header", cascade="all, delete-orphan")


class TrnJournalEntryLine(Base):
    __tablename__ = "trn_journal_entry_line"
    
    id = Column(Integer, primary_key=True, index=True)
    journal_id = Column(Integer, ForeignKey("trn_journal_entry_head.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("master_account.id"), nullable=False)
    
    description = Column(String(255), nullable=True)
    debit = Column(Numeric(18, 2), default=0)
    credit = Column(Numeric(18, 2), default=0)
    
    header = relationship("TrnJournalEntryHead", back_populates="lines")
    account = relationship("MasterAccount", back_populates="journal_lines")

