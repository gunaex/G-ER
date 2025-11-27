# 🔌 API Reference - New Endpoints

## Quick Access
- **Production Planning**: `/api/planning/*`
- **Quality Management**: `/api/qms/*`
- **Enhanced WMS**: `/api/wms/*`
- **Enhanced Inventory**: `/api/inventory/*`

---

## 🏭 Production Planning Endpoints

### Calculate MRP
```http
POST /api/planning/calculate
Authorization: Bearer {token}
Content-Type: application/json

{
  "plan_name": "December 2025 Production Plan",
  "source_type": "ACTUAL"  // or "FORECAST"
}

Response 200:
{
  "id": 1,
  "plan_name": "December 2025 Production Plan",
  "source_type": "ACTUAL",
  "status": "CALCULATED",
  "created_date": "2025-11-25T10:00:00",
  "calculated_date": "2025-11-25T10:01:30"
}
```

### Get All Plans
```http
GET /api/planning/plans
Authorization: Bearer {token}

Response 200: [
  {
    "id": 1,
    "plan_name": "December 2025 Production Plan",
    "status": "CALCULATED",
    ...
  }
]
```

### Get Draft PRs from Plan
```http
GET /api/planning/plans/{plan_id}/prs
Authorization: Bearer {token}

Response 200: [
  {
    "id": 1,
    "pr_no": "PR-20251125-0001",
    "vendor_id": 1,
    "item_id": 3,
    "required_qty": 500.0,
    "required_date": "2025-12-15",
    "suggested_order_date": "2025-11-20",
    "status": "DRAFT"
  }
]
```

### Approve Purchase Requisition
```http
POST /api/planning/prs/{pr_id}/approve
Authorization: Bearer {token}
Requires: Manager or Admin role

Response 200:
{
  "message": "PR approved successfully",
  "pr_no": "PR-20251125-0001"
}
```

### Convert PR to PO
```http
POST /api/planning/prs/{pr_id}/convert-to-po
Authorization: Bearer {token}

Response 200:
{
  "message": "PR converted to PO successfully",
  "po_no": "PO-20251125-0012"
}
```

---

## 🔬 Quality Management Endpoints

### Create Inspection
```http
POST /api/qms/inspections
Authorization: Bearer {token}
Content-Type: application/json

{
  "inspection_type": "INCOMING",  // INCOMING, IN_PROCESS, OUTGOING
  "ref_document_type": "GR",      // GR, WO, DO
  "ref_document_id": 5,
  "remarks": "Routine incoming inspection"
}

Response 201:
{
  "id": 1,
  "qc_no": "QC-20251125-0001",
  "inspection_type": "INCOMING",
  "status": "PENDING",
  "inspection_date": "2025-11-25T14:30:00",
  "defects": []
}
```

### List Inspections
```http
GET /api/qms/inspections?inspection_type=INCOMING&status=PENDING
Authorization: Bearer {token}

Response 200: [...]
```

### Get Inspection Details
```http
GET /api/qms/inspections/{qc_id}
Authorization: Bearer {token}

Response 200:
{
  "id": 1,
  "qc_no": "QC-20251125-0001",
  "status": "PENDING",
  "defects": [...]
}
```

### Add Defect
```http
POST /api/qms/inspections/{qc_id}/defects
Authorization: Bearer {token}
Content-Type: application/json

{
  "defect_description": "Surface scratches visible on 3 units",
  "severity": "MINOR",  // MINOR, MAJOR, CRITICAL
  "qty_affected": 3,
  "photo_url": "/files/defect-20251125-001.jpg"
}

Response 200:
{
  "id": 1,
  "qc_id": 1,
  "defect_description": "Surface scratches visible on 3 units",
  "severity": "MINOR",
  "qty_affected": 3,
  "created_at": "2025-11-25T14:35:00"
}
```

### Complete Inspection
```http
POST /api/qms/inspections/{qc_id}/complete?result=PASS&remarks=All tests passed
Authorization: Bearer {token}

result: PASS | FAIL | CONDITIONAL

Response 200:
{
  "message": "Inspection completed",
  "qc_no": "QC-20251125-0001",
  "status": "PASS"
}
```

### Upload Photo Evidence
```http
POST /api/qms/inspections/{qc_id}/upload-photo
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [binary data]

Response 200:
{
  "message": "Photo uploaded successfully",
  "url": "/api/files/qc/1/defect-photo.jpg",
  "filename": "defect-photo.jpg"
}
```

### Auto-Trigger Incoming QC
```http
GET /api/qms/inspections/trigger/incoming-qc/{gr_id}
Authorization: Bearer {token}

Response 200:
{
  "message": "Incoming QC created",
  "qc_no": "QC-INC-20251125-0001",
  "qc_id": 1
}
```

---

## 📦 Enhanced WMS Endpoints

### AI Put-Away Suggestion (Enhanced)
```http
POST /api/wms/put-away-suggestion?item_id=1&qty=100&warehouse_id=1
Authorization: Bearer {token}

Response 200:
{
  "suggested_location_id": 15,
  "location_code": "WH01-A-01-01",
  "zone_type": "STORE",
  "condition_type": "GENERAL",
  "is_secure_cage": false,
  "floor_level": 1,
  "reason": "Standard storage location",
  "requires_witness": false
}

Response 400 (if blocked):
{
  "detail": "❌ BLOCKED: Item requires COLD storage, but target location is GENERAL"
}
```

### Move Inventory (NEW)
```http
POST /api/wms/inventory/move
Authorization: Bearer {token}
Content-Type: application/json

{
  "item_id": 5,
  "from_location_id": 10,
  "to_location_id": 15,
  "qty": 50,
  "witness_supervisor_id": 2  // Required if secure cage involved
}

Response 200:
{
  "message": "✅ Inventory moved successfully",
  "item_code": "ENGINE-001",
  "from_location": "WH01-A-01-01",
  "to_location": "WH01-SECURE-01",
  "qty": 50,
  "witness_logged": true
}

Response 400 (validation failures):
{
  "detail": "❌ BLOCKED: Item requires COLD storage, but target location is GENERAL"
}
// or
{
  "detail": "❌ BLOCKED: High-value item must be stored in secure cage"
}
// or
{
  "detail": "❌ WITNESS REQUIRED: Secure cage access requires supervisor witness"
}
```

### Verify Witness (NEW)
```http
POST /api/wms/security/witness-verify
Authorization: Bearer {token}
Content-Type: application/json

{
  "location_id": 15,
  "supervisor_id": 2
}

Response 200:
{
  "verified": true,
  "message": "Witness verified: John Manager",
  "requires_witness": true,
  "supervisor_name": "John Manager",
  "supervisor_role": "manager"
}

Response 403 (if not authorized):
{
  "detail": "User is not authorized as witness (must be Manager or Admin)"
}
```

---

## 📊 Enhanced Inventory Endpoints

### Get Cost Layers (NEW)
```http
GET /api/inventory/cost-layers/{item_id}?warehouse_id=1
Authorization: Bearer {token}

Response 200:
{
  "item_id": 1,
  "total_layers": 3,
  "total_qty": 150,
  "weighted_avg_cost": 25125.50,
  "layers": [
    {
      "id": 1,
      "receipt_date": "2025-11-01",
      "qty_remaining": 50,
      "unit_cost": 25000.00,
      "total_value": 1250000.00,
      "warehouse_id": 1,
      "location_id": 10
    },
    {
      "id": 2,
      "receipt_date": "2025-11-15",
      "qty_remaining": 100,
      "unit_cost": 25200.00,
      "total_value": 2520000.00,
      "warehouse_id": 1,
      "location_id": 10
    }
  ]
}
```

### Get Inventory Valuation (NEW)
```http
GET /api/inventory/valuation?warehouse_id=1
Authorization: Bearer {token}

Response 200:
{
  "summary": {
    "total_items": 15,
    "total_fifo_value": 12500000.00,
    "total_moving_avg_value": 12450000.00,
    "total_variance": 50000.00,
    "variance_pct": 0.40
  },
  "details": [
    {
      "item_id": 1,
      "warehouse_id": 1,
      "qty_on_hand": 150,
      "fifo_unit_cost": 25125.50,
      "fifo_total_value": 3768825.00,
      "moving_avg_unit_cost": 25100.00,
      "moving_avg_total_value": 3765000.00,
      "variance": 3825.00,
      "variance_pct": 0.10
    }
  ]
}
```

### Create Transaction (Enhanced with FIFO)
```http
POST /api/inventory/transactions
Authorization: Bearer {token}
Content-Type: application/json

// RECEIPT (creates cost layer)
{
  "type": "receipt",
  "transaction_date": "2025-11-25T10:00:00",
  "reference_no": "GR-20251125-001",
  "items": [
    {
      "item_code": "ENGINE-001",
      "warehouse_code": "WH01",
      "location_code": "A-01-01",
      "qty": 50
    }
  ]
}

// ISSUE (consumes cost layers via FIFO)
{
  "type": "issue",
  "transaction_date": "2025-11-25T14:00:00",
  "reference_no": "WO-20251125-005",
  "items": [
    {
      "item_code": "ENGINE-001",
      "warehouse_code": "WH01",
      "qty": 30
    }
  ]
}

Response 201:
{
  "message": "Transaction recorded successfully"
}

Response 400 (FIFO validation failure):
{
  "detail": "Insufficient inventory for FIFO costing. Short by 10"
}
```

---

## 🔐 Authentication

All endpoints require Bearer token authentication:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Get Token
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {...}
}
```

---

## ⚠️ Error Responses

### 400 Bad Request - Validation Error
```json
{
  "detail": "❌ BLOCKED: Item requires COLD storage, but target location is GENERAL"
}
```

### 403 Forbidden - Permission Denied
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Item not found: ENGINE-999"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## 🧪 Testing with cURL

### Example: Run MRP Planning
```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. Run Planning (use token from step 1)
curl -X POST http://localhost:8000/api/planning/calculate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_name":"Test Plan","source_type":"ACTUAL"}'

# 3. Get Generated PRs
curl -X GET http://localhost:8000/api/planning/plans/1/prs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Example: Quality Inspection Flow
```bash
# 1. Create Inspection
curl -X POST http://localhost:8000/api/qms/inspections \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inspection_type":"INCOMING",
    "ref_document_type":"GR",
    "ref_document_id":1
  }'

# 2. Add Defect
curl -X POST http://localhost:8000/api/qms/inspections/1/defects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "defect_description":"Minor scratches",
    "severity":"MINOR",
    "qty_affected":2
  }'

# 3. Complete Inspection
curl -X POST "http://localhost:8000/api/qms/inspections/1/complete?result=CONDITIONAL" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📚 Additional Resources

- **Full API Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

---

**Last Updated**: November 25, 2025

