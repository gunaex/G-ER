# 🧪 RetroEarthERP - Test Plan

**Created**: November 26, 2025  
**Version**: 1.0  
**Status**: Ready for Testing  
**Backend Port**: 8002  
**Frontend Port**: 5173

---

## 📋 Test Overview

This test plan covers all features implemented on **November 25, 2025**:
- BOM Explosion Algorithm
- Work Order Automation
- Enhanced BOM Master (Frontend)
- User Master Module
- Integration Testing

---

## 🔧 Prerequisites

### Environment Setup
- ✅ Backend running on `http://localhost:8000`
- ✅ Frontend running on `http://localhost:5173`
- ✅ Database seeded with test data
- ✅ API Documentation accessible at `http://localhost:8000/docs`

### Test Credentials
```
Admin:    username=admin,    password=admin123
Manager:  username=manager,  password=manager123
User:     username=user,     password=user123
```

### Test Data Requirements
- At least 1 Finished Good item (ID: 3, ENGINE-001 recommended)
- Multi-level BOM structure (parent → child → grandchild)
- At least 1 Warehouse (ID: 1)
- At least 1 Location in warehouse

---

## 🎯 Test Suite 1: BOM Explosion Algorithm

### Test Case 1.1: Simple Single-Level BOM Explosion
**Priority**: High  
**Type**: API Test

**Steps**:
1. Open API docs: `http://localhost:8000/docs`
2. Navigate to: `Bill of Materials` → `GET /api/bom/explode/{parent_item_id}`
3. Click "Try it out"
4. Enter `parent_item_id = 3` (or any FG item with BOM)
5. Click "Execute"

**Expected Results**:
- ✅ Status Code: 200 OK
- ✅ Response contains:
  - `detailed_breakdown`: Array of all BOM lines with hierarchy
  - `consolidated_view`: Grouped by item with total quantities
  - `raw_materials_only`: Only raw materials (no sub-assemblies)
- ✅ Quantities calculated correctly (including scrap factors)
- ✅ Circular references detected (if any)

**Validation Points**:
- [ ] Response structure matches schema
- [ ] Quantities are positive numbers
- [ ] Scrap factors applied correctly
- [ ] Multi-level hierarchy preserved
- [ ] No infinite loops (circular reference detection works)

---

### Test Case 1.2: Multi-Level BOM Explosion with Options
**Priority**: High  
**Type**: API Test

**Steps**:
1. Navigate to: `POST /api/bom/explode`
2. Click "Try it out"
3. Enter request body:
```json
{
  "parent_item_id": 3,
  "quantity": 10,
  "max_levels": 5,
  "include_optional": false,
  "include_byproducts": true
}
```
4. Click "Execute"

**Expected Results**:
- ✅ Status Code: 200 OK
- ✅ Response includes all levels up to max_levels
- ✅ Optional components excluded (if `include_optional: false`)
- ✅ By-products included (if `include_byproducts: true`)
- ✅ Quantities multiplied by requested quantity (10x)

**Validation Points**:
- [ ] Quantity multiplication correct
- [ ] Max levels respected
- [ ] Optional filtering works
- [ ] By-product flag respected

---

### Test Case 1.3: BOM Explosion with Circular Reference Detection
**Priority**: Medium  
**Type**: API Test

**Steps**:
1. Create a circular BOM (Item A → Item B → Item A)
2. Attempt to explode Item A
3. Check response for error handling

**Expected Results**:
- ✅ Status Code: 400 Bad Request OR 200 with warning
- ✅ Error message indicates circular reference detected
- ✅ No infinite loop occurs

**Validation Points**:
- [ ] Circular reference detected
- [ ] System doesn't hang or crash
- [ ] Error message is clear

---

## 🏭 Test Suite 2: Work Order Automation

### Test Case 2.1: Generate Work Order from BOM
**Priority**: High  
**Type**: API Test

**Steps**:
1. Navigate to: `POST /api/workorders/generate-from-bom`
2. Click "Try it out"
3. Enter request body:
```json
{
  "item_id": 3,
  "qty_planned": 5,
  "start_date": "2025-11-26",
  "warehouse_id": 1,
  "auto_generate_material_lines": true
}
```
4. Click "Execute"

**Expected Results**:
- ✅ Status Code: 200 OK or 201 Created
- ✅ Response contains:
  - `job_id`: New work order ID
  - `status`: "PLANNED"
  - `material_lines`: Array of materials from BOM explosion
- ✅ Material lines populated automatically
- ✅ Quantities calculated from BOM explosion

**Validation Points**:
- [ ] Work Order created successfully
- [ ] Material lines auto-generated
- [ ] Quantities match BOM explosion
- [ ] Status is "PLANNED"

---

### Test Case 2.2: List Work Orders with Filters
**Priority**: Medium  
**Type**: API Test

**Steps**:
1. Navigate to: `GET /api/workorders/`
2. Test different query parameters:
   - `?status=PLANNED`
   - `?item_id=3`
   - `?warehouse_id=1`
   - `?start_date_from=2025-11-26&start_date_to=2025-11-30`
3. Click "Execute" for each

**Expected Results**:
- ✅ Status Code: 200 OK
- ✅ Filtered results match criteria
- ✅ Response includes pagination info (if implemented)
- ✅ All work orders include required fields

**Validation Points**:
- [ ] Status filter works
- [ ] Item filter works
- [ ] Warehouse filter works
- [ ] Date range filter works
- [ ] All filters can be combined

---

### Test Case 2.3: Get Single Work Order Details
**Priority**: Medium  
**Type**: API Test

**Steps**:
1. Create a Work Order (from Test 2.1)
2. Note the `job_id`
3. Navigate to: `GET /api/workorders/{id}`
4. Enter the `job_id`
5. Click "Execute"

**Expected Results**:
- ✅ Status Code: 200 OK
- ✅ Response includes:
  - Work Order header information
  - Material lines with details
  - Status and dates
  - Progress information

**Validation Points**:
- [ ] All fields present
- [ ] Material lines included
- [ ] Status accurate
- [ ] Dates formatted correctly

---

### Test Case 2.4: Issue Materials (Single Item)
**Priority**: High  
**Type**: API Test

**Steps**:
1. Get a Work Order ID (from Test 2.1)
2. Get a material item ID from the Work Order's material lines
3. Navigate to: `POST /api/workorders/consume-material`
4. Enter request body:
```json
{
  "job_id": <work_order_id>,
  "item_id": <material_item_id>,
  "qty_consumed": 2.5,
  "batch_number": "BATCH-001",
  "remarks": "Test material issue"
}
```
5. Click "Execute"

**Expected Results**:
- ✅ Status Code: 200 OK
- ✅ Material consumption recorded
- ✅ Work Order status changes to "IN_PROGRESS" (if first issue)
- ✅ Inventory balance decreased
- ✅ Consumption tracked in Work Order details

**Validation Points**:
- [ ] Material consumption recorded
- [ ] Status updated correctly
- [ ] Inventory updated
- [ ] Batch number stored (if provided)

---

### Test Case 2.5: Batch Material Issue
**Priority**: High  
**Type**: API Test

**Steps**:
1. Get a Work Order ID
2. Navigate to: `POST /api/workorders/issue-materials`
3. Enter request body:
```json
{
  "job_id": <work_order_id>,
  "materials": [
    {
      "item_id": <item_id_1>,
      "qty_consumed": 5.0
    },
    {
      "item_id": <item_id_2>,
      "qty_consumed": 3.0
    }
  ],
  "remarks": "Batch issue test"
}
```
4. Click "Execute"

**Expected Results**:
- ✅ Status Code: 200 OK
- ✅ All materials consumed in single transaction
- ✅ All inventory balances updated
- ✅ All consumptions tracked

**Validation Points**:
- [ ] Multiple materials processed
- [ ] All inventory updated
- [ ] Transaction atomicity (all or nothing)

---

### Test Case 2.6: Complete Work Order
**Priority**: High  
**Type**: API Test

**Steps**:
1. Get a Work Order ID with materials issued
2. Navigate to: `POST /api/workorders/complete`
3. Enter request body:
```json
{
  "job_id": <work_order_id>,
  "qty_produced": 5,
  "auto_consume_remaining": true,
  "completion_remarks": "Production completed successfully"
}
```
4. Click "Execute"

**Expected Results**:
- ✅ Status Code: 200 OK
- ✅ Work Order status changes to "COMPLETED"
- ✅ Finished goods posted to inventory
- ✅ Remaining materials auto-consumed (if `auto_consume_remaining: true`)
- ✅ Completion date set

**Validation Points**:
- [ ] Status updated to COMPLETED
- [ ] FG inventory increased
- [ ] Remaining materials consumed
- [ ] Completion date recorded

---

### Test Case 2.7: Work Order Statistics
**Priority**: Low  
**Type**: API Test

**Steps**:
1. Navigate to: `GET /api/workorders/stats/summary`
2. Click "Execute"

**Expected Results**:
- ✅ Status Code: 200 OK
- ✅ Response includes:
  - Total work orders count
  - Count by status (PLANNED, IN_PROGRESS, COMPLETED)
  - Overdue count
  - Other relevant statistics

**Validation Points**:
- [ ] Statistics accurate
- [ ] All statuses counted
- [ ] Overdue detection works

---

## 🎨 Test Suite 3: BOM Master (Frontend)

### Test Case 3.1: Access BOM Master Module
**Priority**: High  
**Type**: UI Test

**Steps**:
1. Open frontend: `http://localhost:5173`
2. Login as Admin
3. Click "Master Data" menu
4. Click "BOM Master" button

**Expected Results**:
- ✅ BOM Master screen loads
- ✅ Split-panel view displayed:
  - Left: Parent items list
  - Right: BOM components/details
- ✅ No errors in browser console

**Validation Points**:
- [ ] Screen loads without errors
- [ ] UI layout correct
- [ ] No console errors

---

### Test Case 3.2: Search Functionality
**Priority**: Medium  
**Type**: UI Test

**Steps**:
1. In BOM Master, locate search fields
2. Enter parent item name/code in "Parent Item" search
3. Click "Go" button
4. Clear search and try "Child Item" search

**Expected Results**:
- ✅ Search filters parent items list
- ✅ Results update in real-time
- ✅ Clear button resets search
- ✅ Both parent and child searches work

**Validation Points**:
- [ ] Parent search works
- [ ] Child search works
- [ ] Clear button works
- [ ] Results accurate

---

### Test Case 3.3: Select Parent Item and View BOM
**Priority**: High  
**Type**: UI Test

**Steps**:
1. In parent items list, click on an item
2. Observe right panel

**Expected Results**:
- ✅ Right panel shows BOM components
- ✅ Revision number displayed
- ✅ Status badge shown (Active/Inactive)
- ✅ Component table populated
- ✅ All component fields visible (Qty, UOM, Scrap%, Prod Loc, Stor Loc, By-Prod, Remark)

**Validation Points**:
- [ ] Components load correctly
- [ ] Revision displayed
- [ ] Status badge visible
- [ ] All columns shown

---

### Test Case 3.4: Create New Revision
**Priority**: High  
**Type**: UI Test

**Steps**:
1. Select a parent item with existing BOM
2. Click "+ New Revision" button
3. Confirm action (if prompted)
4. Check revision number

**Expected Results**:
- ✅ New revision created
- ✅ Revision number incremented
- ✅ Previous revision auto-deactivated
- ✅ New revision is active
- ✅ Components copied from previous revision

**Validation Points**:
- [ ] Revision created
- [ ] Number incremented correctly
- [ ] Previous revision deactivated
- [ ] Components copied

---

### Test Case 3.5: Toggle Revision Status
**Priority**: Medium  
**Type**: UI Test

**Steps**:
1. Select a parent item with active revision
2. Click "Deactivate" button
3. Verify status changes
4. Click "Activate" button
5. Verify status changes back

**Expected Results**:
- ✅ Status changes to Inactive
- ✅ Status badge updates (green → red)
- ✅ Status changes back to Active
- ✅ Status badge updates (red → green)

**Validation Points**:
- [ ] Deactivate works
- [ ] Activate works
- [ ] Badge updates correctly
- [ ] Status persists after refresh

---

### Test Case 3.6: Add New Component
**Priority**: High  
**Type**: UI Test

**Steps**:
1. Select a parent item
2. Click "Add Component" or "+" button
3. Fill in form:
   - Component item (select from dropdown)
   - Quantity: 10
   - UOM: PCS
   - Scrap %: 5
   - Production Location: Select from dropdown
   - Storage Location: Select from dropdown
   - By-product: Check/uncheck
   - Remark: "Test component"
   - Status: ACTIVE
   - Active Date: Today
4. Click "Save" or "Add"

**Expected Results**:
- ✅ Component added to BOM
- ✅ Appears in component table
- ✅ All fields saved correctly
- ✅ Form resets for next entry

**Validation Points**:
- [ ] Component added
- [ ] All fields saved
- [ ] Table updates
- [ ] Form validation works

---

### Test Case 3.7: Edit Component
**Priority**: Medium  
**Type**: UI Test

**Steps**:
1. Click on an existing component in the table
2. Modify fields (quantity, locations, etc.)
3. Click "Save" or "Update"

**Expected Results**:
- ✅ Changes saved
- ✅ Table updates with new values
- ✅ No duplicate entries

**Validation Points**:
- [ ] Edit works
- [ ] Changes persist
- [ ] No duplicates

---

### Test Case 3.8: Delete Component
**Priority**: Medium  
**Type**: UI Test

**Steps**:
1. Select a component in the table
2. Click "Delete" button
3. Confirm deletion

**Expected Results**:
- ✅ Component removed from table
- ✅ Confirmation dialog shown
- ✅ Deletion successful

**Validation Points**:
- [ ] Delete works
- [ ] Confirmation shown
- [ ] Component removed

---

### Test Case 3.9: Export to CSV
**Priority**: Low  
**Type**: UI Test

**Steps**:
1. Click "Export CSV" button
2. Choose export options (if available):
   - Selected item only
   - All items
   - Include all revisions
3. Download file
4. Open CSV in Excel/editor

**Expected Results**:
- ✅ CSV file downloaded
- ✅ File contains expected columns
- ✅ Data matches screen display
- ✅ All revisions included (if selected)

**Validation Points**:
- [ ] File downloads
- [ ] Format correct
- [ ] Data accurate
- [ ] All columns present

---

## 👥 Test Suite 4: User Master (Frontend)

### Test Case 4.1: Access User Master
**Priority**: High  
**Type**: UI Test

**Steps**:
1. Login as Admin
2. Click desktop "Settings" icon (gear icon)
3. Click "Factory Settings"
4. Click "User Master"

**Expected Results**:
- ✅ User Master screen loads
- ✅ User table displayed
- ✅ Statistics bar visible (total users, by role, by status)
- ✅ No console errors

**Validation Points**:
- [ ] Screen loads
- [ ] Table displayed
- [ ] Stats visible
- [ ] No errors

---

### Test Case 4.2: View User List
**Priority**: High  
**Type**: UI Test

**Steps**:
1. In User Master, observe user table
2. Check columns: Username, Role, Status, Created Date
3. Verify role badges (Admin=red, Manager=blue, User=gray)
4. Verify status badges (Active=green, Inactive=red)

**Expected Results**:
- ✅ All users listed
- ✅ Role badges color-coded correctly
- ✅ Status badges color-coded correctly
- ✅ Dates formatted correctly

**Validation Points**:
- [ ] All users shown
- [ ] Badges correct
- [ ] Dates formatted

---

### Test Case 4.3: Create New User
**Priority**: High  
**Type**: UI Test

**Steps**:
1. Click "Add User" or "+" button
2. Fill in form:
   - Username: testuser
   - Password: testpass123
   - Role: User
   - Theme: Light
   - Language: English
3. Click "Save" or "Create"

**Expected Results**:
- ✅ User created successfully
- ✅ Success message shown
- ✅ User appears in table
- ✅ Form closes/resets

**Validation Points**:
- [ ] User created
- [ ] Success message
- [ ] Appears in list
- [ ] Validation works (duplicate username, etc.)

---

### Test Case 4.4: Edit User
**Priority**: Medium  
**Type**: UI Test

**Steps**:
1. Click on a user in the table
2. Click "Edit" button
3. Modify fields:
   - Role: Change to Manager
   - Theme: Change to Dark
   - Language: Change to Thai
4. Click "Save"

**Expected Results**:
- ✅ Changes saved
- ✅ Table updates
- ✅ Success message shown

**Validation Points**:
- [ ] Changes saved
- [ ] Table updates
- [ ] All fields editable

---

### Test Case 4.5: Toggle User Status
**Priority**: High  
**Type**: UI Test

**Steps**:
1. Find an active user
2. Click "Deactivate" button
3. Verify status changes
4. Click "Activate" button
5. Verify status changes back

**Expected Results**:
- ✅ Status changes to Inactive
- ✅ Badge updates (green → red)
- ✅ Status changes back to Active
- ✅ Badge updates (red → green)
- ✅ User cannot login when inactive

**Validation Points**:
- [ ] Deactivate works
- [ ] Activate works
- [ ] Badge updates
- [ ] Login blocked when inactive

---

### Test Case 4.6: Reset User Password
**Priority**: Medium  
**Type**: UI Test

**Steps**:
1. Select a user
2. Click "Reset Password" button
3. Enter new password (if prompted)
4. Confirm action

**Expected Results**:
- ✅ Password reset successfully
- ✅ Success message shown
- ✅ User can login with new password

**Validation Points**:
- [ ] Password reset
- [ ] Success message
- [ ] New password works

---

### Test Case 4.7: Delete User
**Priority**: Low  
**Type**: UI Test

**Steps**:
1. Select a user (not yourself)
2. Click "Delete" button
3. Confirm deletion

**Expected Results**:
- ✅ Confirmation dialog shown
- ✅ User deleted
- ✅ Removed from table
- ✅ Success message shown

**Validation Points**:
- [ ] Confirmation shown
- [ ] User deleted
- [ ] Removed from list
- [ ] Cannot delete self

---

## 🔗 Test Suite 5: Integration Testing

### Test Case 5.1: Complete Production Flow
**Priority**: Critical  
**Type**: End-to-End Test

**Steps**:
1. **Item Master**: Create items
   - Create Raw Material: RM-001 (Steel)
   - Create WIP: WIP-001 (Sub-assembly)
   - Create Finished Good: FG-001 (Final Product)

2. **BOM Master**: Create multi-level BOM
   - Create BOM for WIP-001:
     - Component: RM-001, Qty: 2, Scrap: 5%
   - Create BOM for FG-001:
     - Component: WIP-001, Qty: 1, Scrap: 2%
     - Component: RM-001, Qty: 1, Scrap: 0%

3. **BOM Explosion**: Verify calculations
   - Explode FG-001, Qty: 10
   - Verify total RM-001 required: (10 * 1.02 * 1) + (10 * 1 * 1) = 20.2 + 10 = 30.2
   - Verify WIP-001 required: 10 * 1.02 = 10.2

4. **Work Orders**: Generate from BOM
   - Generate WO for FG-001, Qty: 10
   - Verify material lines match explosion

5. **Material Issue**: Track consumption
   - Issue materials for WO
   - Verify inventory decreased

6. **Complete WO**: Post finished goods
   - Complete Work Order
   - Verify FG inventory increased
   - Verify WO status = COMPLETED

**Expected Results**:
- ✅ All steps complete successfully
- ✅ Quantities calculated correctly
- ✅ Inventory balances accurate
- ✅ Work Order statuses update correctly
- ✅ No data inconsistencies

**Validation Points**:
- [ ] Multi-level BOM created
- [ ] Explosion calculations correct
- [ ] WO generated correctly
- [ ] Materials issued correctly
- [ ] Inventory updated correctly
- [ ] WO completed successfully

---

### Test Case 5.2: BOM Revision Workflow
**Priority**: High  
**Type**: Integration Test

**Steps**:
1. Create BOM for FG-001 with Component A
2. Create Work Order using this BOM
3. Create new BOM revision with Component B (instead of A)
4. Activate new revision
5. Generate new Work Order
6. Verify new WO uses new revision

**Expected Results**:
- ✅ Old WO uses old revision
- ✅ New WO uses new revision
- ✅ Revisions tracked correctly
- ✅ Status changes work

**Validation Points**:
- [ ] Revision control works
- [ ] Old WO unaffected
- [ ] New WO uses new revision
- [ ] Status management works

---

### Test Case 5.3: Material Consumption Validation
**Priority**: High  
**Type**: Integration Test

**Steps**:
1. Create Work Order with material requirements
2. Check current inventory levels
3. Issue materials exceeding available inventory
4. Verify error handling
5. Issue materials within available inventory
6. Verify success

**Expected Results**:
- ✅ System prevents over-consumption
- ✅ Error message clear
- ✅ Valid consumption succeeds
- ✅ Inventory updated correctly

**Validation Points**:
- [ ] Validation works
- [ ] Error messages clear
- [ ] Valid transactions succeed
- [ ] Inventory accurate

---

## 📊 Test Execution Summary

### Test Results Template

```
Test Suite 1: BOM Explosion
├── Test 1.1: Simple Explosion          [ ] PASS [ ] FAIL [ ] SKIP
├── Test 1.2: Multi-Level with Options  [ ] PASS [ ] FAIL [ ] SKIP
└── Test 1.3: Circular Reference        [ ] PASS [ ] FAIL [ ] SKIP

Test Suite 2: Work Order Automation
├── Test 2.1: Generate WO from BOM      [ ] PASS [ ] FAIL [ ] SKIP
├── Test 2.2: List with Filters        [ ] PASS [ ] FAIL [ ] SKIP
├── Test 2.3: Get WO Details           [ ] PASS [ ] FAIL [ ] SKIP
├── Test 2.4: Issue Materials         [ ] PASS [ ] FAIL [ ] SKIP
├── Test 2.5: Batch Material Issue    [ ] PASS [ ] FAIL [ ] SKIP
├── Test 2.6: Complete WO             [ ] PASS [ ] FAIL [ ] SKIP
└── Test 2.7: Statistics              [ ] PASS [ ] FAIL [ ] SKIP

Test Suite 3: BOM Master (Frontend)
├── Test 3.1: Access Module            [ ] PASS [ ] FAIL [ ] SKIP
├── Test 3.2: Search                   [ ] PASS [ ] FAIL [ ] SKIP
├── Test 3.3: View BOM                 [ ] PASS [ ] FAIL [ ] SKIP
├── Test 3.4: New Revision              [ ] PASS [ ] FAIL [ ] SKIP
├── Test 3.5: Toggle Status           [ ] PASS [ ] FAIL [ ] SKIP
├── Test 3.6: Add Component            [ ] PASS [ ] FAIL [ ] SKIP
├── Test 3.7: Edit Component           [ ] PASS [ ] FAIL [ ] SKIP
├── Test 3.8: Delete Component         [ ] PASS [ ] FAIL [ ] SKIP
└── Test 3.9: Export CSV               [ ] PASS [ ] FAIL [ ] SKIP

Test Suite 4: User Master (Frontend)
├── Test 4.1: Access Module            [ ] PASS [ ] FAIL [ ] SKIP
├── Test 4.2: View List                [ ] PASS [ ] FAIL [ ] SKIP
├── Test 4.3: Create User              [ ] PASS [ ] FAIL [ ] SKIP
├── Test 4.4: Edit User                [ ] PASS [ ] FAIL [ ] SKIP
├── Test 4.5: Toggle Status            [ ] PASS [ ] FAIL [ ] SKIP
├── Test 4.6: Reset Password           [ ] PASS [ ] FAIL [ ] SKIP
└── Test 4.7: Delete User              [ ] PASS [ ] FAIL [ ] SKIP

Test Suite 5: Integration Testing
├── Test 5.1: Complete Production Flow [ ] PASS [ ] FAIL [ ] SKIP
├── Test 5.2: BOM Revision Workflow    [ ] PASS [ ] FAIL [ ] SKIP
└── Test 5.3: Material Validation      [ ] PASS [ ] FAIL [ ] SKIP
```

---

## 🐛 Known Issues to Watch For

1. **BOM Explosion**: Check for circular references
2. **Work Orders**: Verify inventory updates are atomic
3. **Frontend**: Check browser console for errors
4. **DateTime**: Verify UTC conversion works correctly
5. **Revisions**: Ensure old WOs aren't affected by new revisions

---

## 📝 Test Notes Section

### Test Execution Date: _______________
### Tester Name: _______________
### Environment: _______________

### Issues Found:
1. 
2. 
3. 

### Blockers:
1. 
2. 

### Recommendations:
1. 
2. 

---

## ✅ Sign-Off

**Test Plan Approved By**: _______________  
**Date**: _______________  
**Version**: 1.0

---

**Next Steps After Testing**:
1. Document all test results
2. Report bugs/issues found
3. Update PROGRESS.md with test results
4. Plan fixes for failed tests
5. Re-test after fixes

