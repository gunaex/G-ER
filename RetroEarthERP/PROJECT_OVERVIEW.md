# 🏭 RetroEarth ERP - Project Overview

**Version**: 1.0 (Alpha)  
**Last Updated**: November 27, 2025  
**Status**: Core Modules Operational

---

## 📖 Executive Summary

**RetroEarth ERP** is a modern, full-stack manufacturing ERP system with a unique "Retro Windows 3.11" aesthetic. It is designed to handle the end-to-end business processes of a manufacturing company, from raw material procurement to finished goods delivery.

The system is built for **scalability**, **traceability**, and **user experience**, combining nostalgic design with powerful enterprise-grade logic.

---

## ✅ Currently Implemented Features

### 1. 🏭 Production Planning (New!)
*   **Calendar-First Interface**: 4-month view for long-term planning.
*   **Unified Planning**: Manage both Production and Forecast plans in one place.
*   **Traceability**: Create plans directly from Sales Orders with full reference tracking.
*   **MRP Engine**:
    *   **Pre-Calculation**: Preview temporary Work Orders and Purchase Requisitions.
    *   **Post-Calculation**: Auto-generate actual WOs and PRs.
*   **Visual Indicators**: Color-coded status dots (Draft, Calculated, Processed).

### 2. 📦 Inventory Management
*   **Multi-Warehouse**: Support for Main, WIP, and Quarantine warehouses.
*   **Lot Control**: Full lot tracking for raw materials and finished goods (FIFO/FEFO).
*   **Stock Movements**: Receipts, Issues, Transfers, and Adjustments.
*   **Real-time Balance**: Instant view of On-Hand, Allocated, and Available stock.

### 3. 💰 Sales & Distribution
*   **Order Management**: Quotations → Sales Orders → Delivery Orders → Tax Invoices.
*   **Customer Management**: CRM-lite features with multiple addresses.
*   **Document Flow**: One-click conversion between documents.

### 4. 🛒 Purchasing
*   **Procurement**: Purchase Requisitions → Purchase Orders → Goods Receipts.
*   **Vendor Management**: Supplier database with lead times and credit terms.
*   **Approval Workflows**: Manager approval required for high-value POs.

### 5. ⚙️ Master Data
*   **BOM Management**: Multi-level Bill of Materials with version control.
*   **Item Master**: Detailed product definitions (Raw Material, WIP, FG).
*   **Partners**: Centralized customer and vendor registry.

### 6. 📊 Accounting Engine (New!)
*   **Thai Standard Chart of Accounts**: 5 Categories (Assets, Liabilities, Equity, Revenue, Expenses).
*   **One-Way Sync**: Auto-generation of Journal Entries from operational documents.
*   **Journal Preview**: Simulate GL impact before confirming invoices.

---

## 🗺️ Development Roadmap

### Phase 2: Financials & Control (In Progress)
*   [x] **Chart of Accounts**: Implemented Thai Standard 5 Categories.
*   [x] **Journal Entries**: Structure and Preview API ready.
*   [ ] **Cost Accounting**: Real-time job costing and inventory valuation.
*   [ ] **Credit Control**: Automatic credit limit checks during Sales Order entry.
*   [ ] **Invoicing & AP/AR**: Aging reports and payment tracking.

### Phase 3: Advanced Manufacturing
*   [ ] **Shop Floor Control**: Tablet interface for operators to log time/output.
*   [ ] **Quality Control (QMS)**: Inspection plans and defect tracking.
*   [ ] **Machine Maintenance**: Preventive maintenance scheduling.
*   [ ] **Capacity Planning**: Machine load balancing and scheduling.

### Phase 4: Intelligence & Integration
*   [ ] **Dashboards**: PowerBI-style analytics and KPIs.
*   [ ] **API Integrations**: Connectors for e-commerce and shipping providers.
*   [ ] **Mobile App**: Native mobile experience for approvals and alerts.

---

## 💻 Technical Stack

*   **Frontend**: Vue.js 3, Tailwind CSS (Retro Styling)
*   **Backend**: Python FastAPI (High performance, Async)
*   **Database**: PostgreSQL (Reliable, Relational)
*   **ORM**: SQLAlchemy (Robust data modeling)
*   **Deployment**: Docker & Docker Compose (Containerized)

---

## 🚀 Getting Started

To run the system locally:

1.  **Backend**:
    ```bash
    cd backend
    python main.py
    ```

2.  **Frontend**:
    ```bash
    cd frontend
    npm run dev
    ```

3.  **Access**: Open `http://localhost:5173` in your browser.

---

*Generated for internal review and stakeholder sharing.*
