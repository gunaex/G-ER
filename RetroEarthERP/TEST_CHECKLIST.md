# ✅ Quick Test Checklist

**Quick reference for daily testing**  
**Date**: _______________

---

## 🚀 Quick Smoke Tests (5 minutes)

- [x] Backend health check: `GET http://localhost:8000/api/health`
- [x] Frontend loads: `http://localhost:5173`
- [x] Login works (admin/admin123)
- [x] API docs accessible: `http://localhost:8000/docs`

---

## 🎯 Critical Path Tests (15 minutes)

### BOM Explosion
- [ ] `GET /api/bom/explode/3` returns 200 OK
- [ ] Response has `detailed_breakdown` array
- [ ] Quantities calculated correctly

### Work Order
- [ ] `POST /api/workorders/generate-from-bom` creates WO
- [ ] `GET /api/workorders/` lists WOs
- [ ] `POST /api/workorders/consume-material` issues materials
- [ ] `POST /api/workorders/complete` completes WO

### Frontend
- [ ] BOM Master loads (Master Data → BOM Master)
- [ ] User Master loads (Settings → Factory Settings → User Master)
- [ ] Search works in BOM Master
- [ ] Create user works in User Master

---

## 📋 Full Test Run (1 hour)

### API Tests
- [ ] Test Suite 1: BOM Explosion (3 tests)
- [ ] Test Suite 2: Work Order Automation (7 tests)
- [ ] Test Suite 3: BOM Master Frontend (9 tests)
- [ ] Test Suite 4: User Master Frontend (7 tests)
- [ ] Test Suite 5: Integration Tests (3 tests)

**Total**: 29 test cases

---

## 🐛 Common Issues to Check

- [ ] No 500 errors in API responses
- [ ] No console errors in browser
- [ ] Database connections stable
- [ ] DateTime displays correctly (UTC conversion)
- [ ] Inventory balances accurate after transactions

---

## 📊 Test Results Summary

**Total Tests**: 29  
**Passed**: ___  
**Failed**: ___  
**Skipped**: ___

**Critical Failures**: ___

---

## 🔍 Quick API Test Commands

### Using curl (if API docs unavailable):

```bash
# Health check
curl http://localhost:8000/api/health

# BOM Explosion
curl http://localhost:8000/api/bom/explode/3

# List Work Orders
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/workorders/

# Generate Work Order
curl -X POST http://localhost:8000/api/workorders/generate-from-bom \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": 3,
    "qty_planned": 5,
    "start_date": "2025-11-26",
    "warehouse_id": 1,
    "auto_generate_material_lines": true
  }'
```

---

## 📝 Notes

_________________________________________________
_________________________________________________
_________________________________________________

