Reorganize the codebase with a cleaner, modular structure
Optimize the architecture for better maintainability and scalability
Preserve all existing functionality
Add modular app store architecture (like Play Store/App Store)
Implement comprehensive activity logging with timezone support
Build traceability "Spider Web" module for complete document tracking
Create approval workflow engine for all critical documents
Add KPI tracking and user reminder system
Enable UI/UX customization (icon packs, backgrounds)
Improve code quality and documentation
Enhance deployment readiness



Technology Stack Changes:

Database: Currently using SQLite → Switching to PostgreSQL for production-readiness
If you want to keep SQLite for development, please let me know
Frontend Build: The rebuild will use Vite with better optimization settings

Multi-level BOM explosion with circular reference detection
Revision control
Scrap factor calculation
Optional/By-product flags
Module 4: Inventory Management

 - Stock balance, transactions

 - FIFO/FEFO logic

Multi-warehouse support
Lot/batch tracking can be setting enable/disable in each item ,default enable
Stock movements (receipt, issue, transfer, adjustment)
Real-time balance calculation
Module 5: Production Management

 - Work Order, Production Plan

 - MRP engine

Key Features:

temp PR /Work Order generation from BOM
Material requirement planning (MRP)
Shop floor tracking
Production calendar integration


Module 6: Sales & Distribution
Files to create:


 - Quotation, Sales Order, Delivery, Invoice

Key Features:

Quotation → Sales Order → Delivery → Tax Invoice flow
Credit limit checking
Document number generation
Inventory reservation
Module 7: Purchasing

 - PR, PO, GRN

Module 8: Finance & Accounting

 - Chart of Accounts, Journal Entry, thai tax,etc

Module 9: Quality Management (QMS)

Module 8: Finance & Accounting (Express Software Style)

Key Features (Thai Standards):

Chart of Accounts: Pre-configured Thai standard accounts (Assets, Liabilities, Equity, Revenue, Expenses).
Journal Entries: Double-entry bookkeeping with debit/credit validation.
Tax Management:
VAT (7%) can be setting later in case VAT rate increase: Input/Output VAT reports (Por Por 30).
Withholding Tax: WHT certificates (3%, 5%, 1%) and reports (Por Ngor Dor 3/53).
Financial Statements:
Trial Balance (Ngob Tod Long)
Profit & Loss (Ngob Kam Rai Kard Tun)
Balance Sheet (Ngob Dul)
Period Closing: Month-end and year-end closing processes.
Module 9: Quality Management

Key Features:

Inspection Plans & Checklists
Quality Control (QC) at Receipt/Production
Non-Conformance Reports (NCR)
Module 12: Fixed Asset Management
Files to create:


Asset Register: Comprehensive tracking of asset details (Code, Name, Serial No, Location, Custodian).
Acquisition: Purchase cost, date, vendor, warranty tracking.
Depreciation Engine:
Methods: Straight-line (standard in Thailand), Declining Balance, Sum-of-Years.
Automatic monthly depreciation calculation and journal posting.
Lifecycle Management:
Transfer: Move assets between locations/departments.
Disposal: Sale or write-off with gain/loss calculation.
Revaluation: Adjust asset value.
Maintenance Log: Track repair history and costs.
Labeling: QR Code/Barcode generation for asset tagging.
Module 10: Costing Analytics & AI Optimization
Files to create:

 - Cost records, variance tracking

 - Cost calculation engine

 - ML forecasting

 - Optimization recommendations

Key Features:

Real-Time Costing Dashboard:

Material cost breakdown by item/BOM
Labor cost tracking by work order
Overhead allocation
Total product cost calculation
Cost trends over time
Variance Analysis:

Standard cost vs Actual cost comparison
Material price variance
Material usage variance
Labor rate variance
Labor efficiency variance
Overhead variance
Visual variance reports
AI Cost Forecasting:

Time-series forecasting using Prophet/ARIMA
Material price prediction (next 3/6/12 months)
Production cost trends
Seasonal pattern detection
Confidence intervals
Forecast accuracy metrics
AI Cost Optimization:

Supplier cost comparison & recommendations
Alternative material suggestions
Production batch size optimization
Waste reduction opportunities
Process efficiency improvements
Make vs Buy analysis
Inventory holding cost optimization
Management Insights:

Top 10 cost drivers
Cost reduction opportunities ranked by impact
ROI calculator for improvements
What-if scenario modeling
Cost benchmarking
Profitability analysis by product
Dashboards:

Executive cost summary
Material cost dashboard
Labor cost dashboard
Variance dashboard
Forecast dashboard
Optimization recommendations dashboard
Module 11: Activity Logging & Audit Trail

Key Features:

Log every user action (create, update, delete, view)
Log system events (auto-calculations, scheduled tasks)
Store client timezone and server timezone
Record IP address, user agent, session info
Searchable audit trail with filters
Module 11: Traceability "Spider Web" Module

Key Features:

Forward Trace: RM Lot → WO → FG Lot → SO → Customer → Delivery
Backward Trace: Customer Complaint → SO → FG Lot → WO → Machine/Operator → RM Lot → Supplier
Centralized document search (any Doc ID: Lot, SO, WO, PO, etc.)
Graph data structure for relationships
API endpoints for trace queries
Module 12: Approval Workflow Engine
Files to create:

 - WorkflowDefinition, WorkflowInstance, ApprovalStep

Key Features:

Configurable approval workflows (single/multi-level)
Document types: Sales Order, Quotation, PR, PO, Work Order
Approval rules based on:
Document value threshold
User role
Custom conditions
Email/in-app notifications
Approval history and comments
Delegate approval to another user
Module 13: KPI Tracking & Reminders

 - KPIDefinition, KPIValue, Reminder

Key Features:

Predefined KPIs:
On-time delivery rate
Production efficiency
Inventory turnover
Purchase order cycle time
Sales order fulfillment time
Custom KPI definitions
Real-time KPI calculation
Dashboard widgets
Reminder system:
Pending approvals
Overdue deliveries
Low stock alerts
Maintenance schedules

Module 14: Modular App Store & Customization
Files to create:

 - App, IconPack, Background, UserPurchase

Key Features:

App Marketplace:
Browse available apps/modules
Purchase apps (applies to entire factory tier)
App activation/deactivation
Icon Pack Store:
Purchase icon packs
Preview before purchase
Apply to user profile
Background Store:
Purchase desktop backgrounds
Upload custom backgrounds
User Preferences:
Save per-user icon mappings
Save per-user background choice
Save window positions/sizes
Save favorite apps/quick access


Window management (WindowFrame, Desktop, Taskbar, StartMenu)
Form components (ItemForm, PartnerForm, etc.)
Table components (ItemsTable, PartnersTable, etc.)
Specialized components (BOMMaster, CalendarWidget, etc.)
New Advanced Components:

Traceability UI
 - Interactive node graph using D3.js or Cytoscape.js

Approval Workflow UI

 - Pending approvals dashboard

 - Approve/Reject with comments

App Store UI

KPI & Dashboard
e
Tablet-Optimized Views
 - Large touch targets
Enhanced UI Elements
 - Tooltips for all Incoterms
 - One-click conversions (Quote → SO)
Phase 5: Database & Migrations
[NEW] 

Alembic configuration for database migrations
Auto-generate initial migration from models
[NEW] 

Seed script for development data
Admin user creation
Sample master data (items, warehouses, partners)
Phase 6: Deployment & DevOps
[NEW] 
docker-compose.yml
PostgreSQL service
Backend service
Frontend service
Nginx reverse proxy
[NEW] 
docker-compose.dev.yml
Development override with hot-reload
Volume mounts for code
[NEW] 
.github/workflows/ci.yml
 (optional)
Automated testing on push
Docker build verification
Verification Plan
Automated Tests
Backend Tests
Test Command:

## Microservices Migration Plan

### Phase 1: Foundation (Completed)
- [x] Create `services` directory structure
- [x] Implement **Auth Service** (Authentication & User Management)
- [x] Implement **API Gateway** (Routing)
- [x] Update `docker-compose.yml` to support microservices
- [x] Configure Gateway to route traffic to Auth Service and Legacy Backend

### Phase 2: Core Services Migration
- [ ] **Inventory Service**
    - [ ] Extract Inventory, Warehouse, Item models and logic
    - [ ] Create independent database/schema
    - [ ] Implement API endpoints
    - [ ] Update Gateway routing
- [ ] **Production Service**
    - [ ] Extract BOM, Work Order, Planning logic
    - [ ] Create independent database/schema
    - [ ] Implement API endpoints
    - [ ] Update Gateway routing
- [ ] **Sales Service**
    - [ ] Extract Partner, Sales Order logic
    - [ ] Create independent database/schema
    - [ ] Implement API endpoints
    - [ ] Update Gateway routing

### Phase 3: Support Services Migration
- [ ] **Finance Service**
    - [ ] Extract Accounting, Tax logic
    - [ ] Create independent database/schema
    - [ ] Implement API endpoints
- [ ] **Notification/Logging Service**
    - [ ] Centralized logging
    - [ ] Notification system

### Phase 4: Cleanup & Optimization
- [ ] Remove migrated code from Legacy Backend
- [ ] Decommission Legacy Backend when empty
- [ ] Optimize inter-service communication (consider gRPC or Message Queue)
- [ ] Implement centralized monitoring (Prometheus/Grafana)

