# 🚀 Deployment Guide - How to Run the Enhanced System

## ⚠️ IMPORTANT: Database Migration Required!

The new features require database schema changes. You **MUST** recreate the database.

---

## 🔧 Quick Start (Development)

### Step 1: Stop Current Servers
```bash
# Stop any running backend servers
# Press Ctrl+C in terminal or close terminal windows
```

### Step 2: Recreate Database
```bash
cd backend

# Delete old database
del retroearperp.db  # Windows
# or
rm retroearperp.db   # Linux/Mac

# Recreate with new schema and seed data
python seed_data.py
```

**Expected Output:**
```
Creating seed data...
✓ Created 3 users (admin/manager/user)
✓ Created company settings
✓ Created 3 license packages
✓ Created 2 warehouses
✓ Created 4 sample items
✓ Created 2 business partners

✅ Seed data created successfully!

Login credentials:
  Admin:   username=admin,   password=admin123
  Manager: username=manager, password=manager123
  User:    username=user,    password=user123
```

### Step 3: Start Backend Server
```bash
# Make sure you're in the backend directory
cd D:\git\G-ERP-New\RetroEarthERP\backend

# Start with the virtual environment Python
D:\git\G-ERP-New\RetroEarthERP\backend\venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['D:\\git\\G-ERP-New\\RetroEarthERP\\backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXXX] using StatReload
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 4: Verify Backend is Running
Open browser: http://localhost:8000/docs

You should see the Swagger API documentation with **8 routers**:
- Authentication
- Items
- Partners
- Warehouses
- Inventory
- WMS
- **Planning** (NEW!)
- **Quality** (NEW!)

### Step 5: Start Frontend (Optional)
```bash
cd D:\git\G-ERP-New\RetroEarthERP\frontend
npm run dev
```

---

## 🧪 Quick Test - Verify Everything Works

### Test 1: Check Health
```bash
curl http://localhost:8000/api/health
```
**Expected:** `{"status":"healthy"}`

### Test 2: Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```
**Expected:** JSON with `access_token`

### Test 3: Get Items (with new fields)
```bash
curl http://localhost:8000/api/items
```
**Expected:** JSON array with items including `storage_condition` and `security_level` fields

### Test 4: Check Cost Layers
```bash
curl http://localhost:8000/api/inventory/cost-layers/1
```
**Expected:** Cost layer information (may be empty initially)

### Test 5: View API Documentation
Open: http://localhost:8000/docs

Navigate to:
- **planning** section - Should see 5 endpoints
- **quality** section - Should see 7 endpoints
- **wms** section - Should see enhanced endpoints
- **inventory** section - Should see cost-layers and valuation endpoints

---

## 📊 Verify Database Schema

### Option 1: SQLite Browser
1. Download DB Browser for SQLite: https://sqlitebrowser.org/
2. Open `backend/retroearperp.db`
3. Check "Database Structure" tab

**Expected Tables (32 total)**:
- ✅ `inventory_cost_layer` (NEW)
- ✅ `production_plan` (NEW)
- ✅ `draft_purchase_requisition` (NEW)
- ✅ `quality_inspection_header` (NEW)
- ✅ `quality_inspection_defects` (NEW)
- ✅ `packaging_bom` (NEW)

### Option 2: Python Script
```python
import sqlite3
conn = sqlite3.connect('backend/retroearperp.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Total tables: {len(tables)}")
for table in tables:
    print(f"  - {table[0]}")

# Check master_items for new fields
cursor.execute("PRAGMA table_info(master_items)")
columns = [col[1] for col in cursor.fetchall()]
print("\nmaster_items columns:")
print(columns)

# Should include: storage_condition, security_level
```

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'planning'"
**Solution:** Backend didn't restart. Restart the server.

### Problem: "Column not found: storage_condition"
**Solution:** Database wasn't recreated. Delete and recreate:
```bash
cd backend
del retroearperp.db
python seed_data.py
```

### Problem: "Port 8000 already in use"
**Solution:** Stop existing server:
```bash
# Windows
Get-Process python* | Stop-Process -Force

# Linux/Mac
killall python
```

### Problem: API returns "Internal Server Error"
**Solution:** Check backend terminal for detailed error. Common issues:
- Database schema mismatch → Recreate database
- Missing dependencies → Run `pip install -r requirements.txt`

### Problem: Frontend can't connect to backend
**Solution:** 
1. Check backend is running on port 8000
2. Check CORS is enabled (already configured in main.py)
3. Check frontend API base URL in `App.vue` or `main.js`

---

## 📝 Post-Deployment Checklist

- [ ] Backend server running on port 8000
- [ ] Can access Swagger docs at `/docs`
- [ ] Database has 32 tables
- [ ] `master_items` has `storage_condition` and `security_level` fields
- [ ] `master_business_partners` has lead time fields
- [ ] Can login with admin/admin123
- [ ] Can view items in API
- [ ] Planning endpoints visible in Swagger
- [ ] Quality endpoints visible in Swagger
- [ ] Frontend running (optional)

---

## 🎓 Next Steps After Deployment

### 1. Test FIFO Costing
```bash
# See IMPLEMENTATION_SUMMARY.md section "Testing the New Features"
```

### 2. Test Production Planning
```bash
# Create a sales order first, then run planning
# See API_REFERENCE.md for examples
```

### 3. Test Quality Management
```bash
# Create a goods receipt, then trigger QC
# See API_REFERENCE.md for QC workflow
```

### 4. Explore New APIs
- Open http://localhost:8000/docs
- Try the "Try it out" feature in Swagger
- Test different scenarios

---

## 🔗 Quick Links

- **Swagger API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health
- **Frontend**: http://localhost:5173 (if running)

---

## 📞 Need Help?

1. Check `PROGRESS.md` for feature status
2. Check `IMPLEMENTATION_SUMMARY.md` for what was built
3. Check `API_REFERENCE.md` for API examples
4. Check terminal logs for error messages

---

## 🎉 Success Indicators

If everything is working, you should see:

✅ Backend starts without errors  
✅ 8 routers in Swagger docs  
✅ 40+ API endpoints available  
✅ Database has 32 tables  
✅ Login works  
✅ Can create planning scenarios  
✅ Can create QC inspections  
✅ FIFO costing calculates correctly  

---

**Good luck! 🚀**

