"""
Test Work Order workflow end-to-end
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Step 1: Login
print("=== Step 1: Login ===")
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": "admin", "password": "admin123"}
)
assert login_response.status_code == 200, f"Login failed: {login_response.text}"
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("[OK] Logged in successfully")

# Step 2: Check if BOM exists
print("\n=== Step 2: Check BOM Structure ===")
bom_response = requests.get(f"{BASE_URL}/api/bom/parents", headers=headers)
assert bom_response.status_code == 200
boms = bom_response.json()
print(f"Found {len(boms)} parent BOMs")
if boms:
    print(f"  - {boms[0]['item_code']}: {boms[0]['item_name']}")

# Step 3: Explode BOM
print("\n=== Step 3: Test BOM Explosion ===")
if boms:
    parent_item_id = boms[0]['id']  # This is the item ID
    print(f"Using parent_item_id: {parent_item_id}")
    explosion_response = requests.get(
        f"{BASE_URL}/api/bom/explode/{parent_item_id}?quantity=1",
        headers=headers
    )
    if explosion_response.status_code != 200:
        print(f"ERROR: BOM explosion failed with {explosion_response.status_code}")
        print(explosion_response.text)
        exit(1)
    explosion = explosion_response.json()
    print(f"[OK] BOM exploded: {explosion['total_levels']} levels, {explosion['total_components']} components")
    print(f"  Raw materials needed:")
    for rm in explosion['raw_materials_only']:
        print(f"    - {rm['item_code']}: {rm['total_quantity']} {rm['unit_of_measure']}")

# Step 4: Generate Work Order from BOM
print("\n=== Step 4: Generate Work Order from BOM ===")
wo_request = {
    "item_id": parent_item_id,
    "qty_planned": 1,
    "start_date": "2025-11-26",
    "end_date": "2025-12-10",
    "warehouse_id": 1,
    "bom_revision": None,
    "include_optional": False,
    "auto_generate_material_lines": True
}
wo_response = requests.post(
    f"{BASE_URL}/api/workorders/generate-from-bom",
    json=wo_request,
    headers=headers
)

if wo_response.status_code != 201:
    print(f"ERROR: {wo_response.status_code}")
    print(wo_response.text)
    exit(1)

work_order = wo_response.json()
wo_id = work_order['id']
wo_no = work_order['job_no']
print(f"[OK] Work Order generated: {wo_no}")
print(f"  Item: {work_order['item_code']} - {work_order['item_name']}")
print(f"  Qty Planned: {work_order['qty_planned']}")
print(f"  Status: {work_order['status']}")
print(f"  Materials: {len(work_order['materials'])} items")
for mat in work_order['materials'][:5]:  # Show first 5
    print(f"    - {mat['item_code']}: {mat['qty_required']} {mat['unit_of_measure']}")

# Step 5: Issue materials (consume)
print("\n=== Step 5: Issue Materials ===")
if work_order['materials']:
    first_material = work_order['materials'][0]
    consume_request = {
        "job_id": wo_id,
        "item_id": first_material['item_id'],
        "qty_consumed": float(first_material['qty_required']) * 0.5  # Consume 50%
    }
    consume_response = requests.post(
        f"{BASE_URL}/api/workorders/consume-material",
        json=consume_request,
        headers=headers
    )
    assert consume_response.status_code == 200
    result = consume_response.json()
    print(f"[OK] Material consumed: {result['qty_consumed']} (50% of required)")
    print(f"  Item: {first_material['item_code']}")
    print(f"  Remaining: {result['qty_remaining']}")

# Step 6: Check Work Order status
print("\n=== Step 6: Check Work Order Status ===")
wo_status_response = requests.get(
    f"{BASE_URL}/api/workorders/{wo_id}",
    headers=headers
)
assert wo_status_response.status_code == 200
updated_wo = wo_status_response.json()
print(f"[OK] Work Order status: {updated_wo['status']}")
print(f"  Materials consumed: {updated_wo['materials_consumed_percent']:.1f}%")
print(f"  Production complete: {updated_wo['percent_complete']:.1f}%")

# Step 7: Complete Work Order
print("\n=== Step 7: Complete Work Order ===")
complete_request = {
    "job_id": wo_id,
    "qty_produced": float(work_order['qty_planned']),
    "auto_consume_remaining": True,
    "post_to_inventory": True
}
complete_response = requests.post(
    f"{BASE_URL}/api/workorders/complete",
    json=complete_request,
    headers=headers
)
assert complete_response.status_code == 200
completion = complete_response.json()
print(f"[OK] Work Order completed: {completion['job_no']}")
print(f"  Qty produced: {completion['qty_produced']}")
print(f"  Status: {completion['status']}")

# Step 8: Get statistics
print("\n=== Step 8: Work Order Statistics ===")
stats_response = requests.get(
    f"{BASE_URL}/api/workorders/stats/summary",
    headers=headers
)
assert stats_response.status_code == 200
stats = stats_response.json()
print(f"[OK] Statistics:")
print(f"  Total Work Orders: {stats['total']}")
print(f"  Planned: {stats['by_status']['planned']}")
print(f"  In Progress: {stats['by_status']['in_progress']}")
print(f"  Completed: {stats['by_status']['completed']}")
print(f"  Overdue: {stats['overdue']}")

print("\n" + "="*60)
print("[SUCCESS] ALL TESTS PASSED! Work Order workflow is fully functional.")
print("="*60)

