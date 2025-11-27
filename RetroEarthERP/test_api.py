#!/usr/bin/env python3
"""
RetroEarthERP - API Test Script
Quick automated tests for critical endpoints
"""

import requests
import json
from typing import Dict, Optional

# Configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

# Test credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token: Optional[str] = None
        self.headers: Dict[str, str] = {}
        self.test_results = []
        
    def login(self) -> bool:
        """Login and get JWT token"""
        print("🔐 Logging in...")
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "username": ADMIN_USERNAME,
                    "password": ADMIN_PASSWORD
                }
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "X-Client-Timezone-Offset": "420"  # UTC+7
                }
                print("✅ Login successful")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_health(self) -> bool:
        """Test health check endpoint"""
        print("\n🏥 Testing health check...")
        try:
            response = requests.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                self.test_results.append(("Health Check", True))
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                self.test_results.append(("Health Check", False))
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            self.test_results.append(("Health Check", False))
            return False
    
    def test_bom_explosion(self, parent_item_id: int = 3) -> bool:
        """Test BOM explosion endpoint"""
        print(f"\n💥 Testing BOM explosion (item_id={parent_item_id})...")
        try:
            response = requests.get(
                f"{self.base_url}/api/bom/explode/{parent_item_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                if "detailed_breakdown" in data:
                    print(f"✅ BOM explosion passed ({len(data['detailed_breakdown'])} items)")
                    self.test_results.append(("BOM Explosion", True))
                    return True
                else:
                    print("❌ BOM explosion: Missing 'detailed_breakdown' in response")
                    self.test_results.append(("BOM Explosion", False))
                    return False
            else:
                print(f"❌ BOM explosion failed: {response.status_code}")
                print(response.text)
                self.test_results.append(("BOM Explosion", False))
                return False
        except Exception as e:
            print(f"❌ BOM explosion error: {e}")
            self.test_results.append(("BOM Explosion", False))
            return False
    
    def test_workorder_list(self) -> bool:
        """Test work order list endpoint"""
        print("\n📋 Testing work order list...")
        try:
            response = requests.get(
                f"{self.base_url}/api/workorders/",
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Work order list passed ({len(data)} work orders)")
                self.test_results.append(("Work Order List", True))
                return True
            else:
                print(f"❌ Work order list failed: {response.status_code}")
                self.test_results.append(("Work Order List", False))
                return False
        except Exception as e:
            print(f"❌ Work order list error: {e}")
            self.test_results.append(("Work Order List", False))
            return False
    
    def test_workorder_generate(self, item_id: int = 3, qty: int = 1) -> Optional[int]:
        """Test work order generation from BOM"""
        print(f"\n🏭 Testing work order generation (item_id={item_id}, qty={qty})...")
        try:
            payload = {
                "item_id": item_id,
                "qty_planned": qty,
                "start_date": "2025-11-26",
                "warehouse_id": 1,
                "auto_generate_material_lines": True
            }
            response = requests.post(
                f"{self.base_url}/api/workorders/generate-from-bom",
                headers=self.headers,
                json=payload
            )
            if response.status_code in [200, 201]:
                data = response.json()
                job_id = data.get("job_id")
                print(f"✅ Work order generated (job_id={job_id})")
                self.test_results.append(("Work Order Generate", True))
                return job_id
            else:
                print(f"❌ Work order generation failed: {response.status_code}")
                print(response.text)
                self.test_results.append(("Work Order Generate", False))
                return None
        except Exception as e:
            print(f"❌ Work order generation error: {e}")
            self.test_results.append(("Work Order Generate", False))
            return None
    
    def test_workorder_stats(self) -> bool:
        """Test work order statistics"""
        print("\n📊 Testing work order statistics...")
        try:
            response = requests.get(
                f"{self.base_url}/api/workorders/stats/summary",
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Work order stats passed")
                print(f"   Total: {data.get('total', 0)}")
                print(f"   Planned: {data.get('planned', 0)}")
                print(f"   In Progress: {data.get('in_progress', 0)}")
                print(f"   Completed: {data.get('completed', 0)}")
                self.test_results.append(("Work Order Stats", True))
                return True
            else:
                print(f"❌ Work order stats failed: {response.status_code}")
                self.test_results.append(("Work Order Stats", False))
                return False
        except Exception as e:
            print(f"❌ Work order stats error: {e}")
            self.test_results.append(("Work Order Stats", False))
            return False
    
    def test_user_list(self) -> bool:
        """Test user list endpoint"""
        print("\n👥 Testing user list...")
        try:
            response = requests.get(
                f"{self.base_url}/api/users/",
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ User list passed ({len(data)} users)")
                self.test_results.append(("User List", True))
                return True
            else:
                print(f"❌ User list failed: {response.status_code}")
                self.test_results.append(("User List", False))
                return False
        except Exception as e:
            print(f"❌ User list error: {e}")
            self.test_results.append(("User List", False))
            return False
    
    def test_bom_list(self) -> bool:
        """Test BOM list endpoint"""
        print("\n📦 Testing BOM list...")
        try:
            response = requests.get(
                f"{self.base_url}/api/bom/",
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ BOM list passed ({len(data)} BOMs)")
                self.test_results.append(("BOM List", True))
                return True
            else:
                print(f"❌ BOM list failed: {response.status_code}")
                self.test_results.append(("BOM List", False))
                return False
        except Exception as e:
            print(f"❌ BOM list error: {e}")
            self.test_results.append(("BOM List", False))
            return False
    
    def run_all_tests(self):
        """Run all automated tests"""
        print("=" * 60)
        print("🧪 RetroEarthERP - API Test Suite")
        print("=" * 60)
        
        # Health check (no auth required)
        self.test_health()
        
        # Login required for other tests
        if not self.login():
            print("\n❌ Cannot proceed without authentication")
            return
        
        # Run all tests
        self.test_bom_list()
        self.test_bom_explosion()
        self.test_workorder_list()
        self.test_workorder_stats()
        job_id = self.test_workorder_generate()
        self.test_user_list()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        
        passed = sum(1 for _, result in self.test_results if result)
        failed = sum(1 for _, result in self.test_results if not result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        print("\n" + "-" * 60)
        print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
        print("=" * 60)
        
        if failed == 0:
            print("🎉 All tests passed!")
        else:
            print(f"⚠️  {failed} test(s) failed")


def main():
    """Main entry point"""
    tester = APITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()

