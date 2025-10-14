"""
Test Multi-Tenancy Implementation
Tests data isolation between companies
"""
import requests
import json
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
SUPER_ADMIN_USERNAME = "Dylan"  # Change to your super admin username
SUPER_ADMIN_PASSWORD = "your_password"  # Change to your password


class MultiTenancyTester:
    def __init__(self):
        self.super_admin_token = None
        self.company_a_token = None
        self.company_b_token = None
        self.company_a_id = None
        self.company_b_id = None

    def print_section(self, title):
        """Print a section header"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)

    def print_test(self, test_name, passed, details=""):
        """Print test result"""
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"       {details}")

    def login(self, username, password):
        """Login and return token"""
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": username,
            "password": password
        })

        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None

    def test_1_super_admin_login(self):
        """Test 1: Super Admin Can Login"""
        self.print_section("TEST 1: Super Admin Login")

        self.super_admin_token = self.login(SUPER_ADMIN_USERNAME, SUPER_ADMIN_PASSWORD)

        self.print_test(
            "Super admin login",
            self.super_admin_token is not None,
            f"Token: {self.super_admin_token[:20]}..." if self.super_admin_token else "Failed to get token"
        )

        return self.super_admin_token is not None

    def test_2_create_companies(self):
        """Test 2: Super Admin Can Create Companies"""
        self.print_section("TEST 2: Create Two Companies")

        if not self.super_admin_token:
            self.print_test("Create companies", False, "No super admin token")
            return False

        headers = {"Authorization": f"Bearer {self.super_admin_token}"}

        # Create Company A
        response_a = requests.post(f"{BASE_URL}/companies/", headers=headers, json={
            "company_name": "Test Company A",
            "contact_email": "admin@companyA.com",
            "subscription_tier": "premium",
            "max_users": 10
        })

        if response_a.status_code == 201:
            self.company_a_id = response_a.json()["id"]
            self.print_test(
                "Create Company A",
                True,
                f"Company ID: {self.company_a_id}"
            )
        else:
            self.print_test(
                "Create Company A",
                False,
                f"Status: {response_a.status_code}, Error: {response_a.text[:100]}"
            )
            return False

        # Create Company B
        response_b = requests.post(f"{BASE_URL}/companies/", headers=headers, json={
            "company_name": "Test Company B",
            "contact_email": "admin@companyB.com",
            "subscription_tier": "basic",
            "max_users": 5
        })

        if response_b.status_code == 201:
            self.company_b_id = response_b.json()["id"]
            self.print_test(
                "Create Company B",
                True,
                f"Company ID: {self.company_b_id}"
            )
        else:
            self.print_test(
                "Create Company B",
                False,
                f"Status: {response_b.status_code}, Error: {response_b.text[:100]}"
            )
            return False

        return True

    def test_3_create_company_users(self):
        """Test 3: Create Users for Each Company"""
        self.print_section("TEST 3: Create Company Users")

        if not self.super_admin_token or not self.company_a_id or not self.company_b_id:
            self.print_test("Create users", False, "Missing prerequisites")
            return False

        headers = {"Authorization": f"Bearer {self.super_admin_token}"}

        # Create user for Company A
        response_a = requests.post(f"{BASE_URL}/users/", headers=headers, json={
            "username": "user_company_a",
            "email": "user@companyA.com",
            "full_name": "User A",
            "password": "password123",
            "company_id": self.company_a_id,
            "role": "COMPANY_ADMIN"
        })

        self.print_test(
            "Create User for Company A",
            response_a.status_code == 201,
            f"Status: {response_a.status_code}"
        )

        # Create user for Company B
        response_b = requests.post(f"{BASE_URL}/users/", headers=headers, json={
            "username": "user_company_b",
            "email": "user@companyB.com",
            "full_name": "User B",
            "password": "password123",
            "company_id": self.company_b_id,
            "role": "COMPANY_ADMIN"
        })

        self.print_test(
            "Create User for Company B",
            response_b.status_code == 201,
            f"Status: {response_b.status_code}"
        )

        return response_a.status_code == 201 and response_b.status_code == 201

    def test_4_company_users_login(self):
        """Test 4: Company Users Can Login"""
        self.print_section("TEST 4: Company Users Login")

        self.company_a_token = self.login("user_company_a", "password123")
        self.print_test(
            "Company A user login",
            self.company_a_token is not None,
            f"Token: {self.company_a_token[:20]}..." if self.company_a_token else "Failed"
        )

        self.company_b_token = self.login("user_company_b", "password123")
        self.print_test(
            "Company B user login",
            self.company_b_token is not None,
            f"Token: {self.company_b_token[:20]}..." if self.company_b_token else "Failed"
        )

        return self.company_a_token is not None and self.company_b_token is not None

    def test_5_data_isolation_candidates(self):
        """Test 5: Data Isolation - Candidates"""
        self.print_section("TEST 5: Data Isolation - Candidates")

        if not self.company_a_token or not self.company_b_token:
            self.print_test("Data isolation", False, "Missing user tokens")
            return False

        headers_a = {"Authorization": f"Bearer {self.company_a_token}"}
        headers_b = {"Authorization": f"Bearer {self.company_b_token}"}

        # Company A lists candidates (should see only their own)
        response_a = requests.get(f"{BASE_URL}/candidates/", headers=headers_a)
        candidates_a = response_a.json().get("candidates", []) if response_a.status_code == 200 else []

        # Company B lists candidates (should see only their own)
        response_b = requests.get(f"{BASE_URL}/candidates/", headers=headers_b)
        candidates_b = response_b.json().get("candidates", []) if response_b.status_code == 200 else []

        self.print_test(
            "Company A can list candidates",
            response_a.status_code == 200,
            f"Found {len(candidates_a)} candidates"
        )

        self.print_test(
            "Company B can list candidates",
            response_b.status_code == 200,
            f"Found {len(candidates_b)} candidates"
        )

        # Check no overlap (if both have candidates)
        if candidates_a and candidates_b:
            candidate_ids_a = {c["id"] for c in candidates_a}
            candidate_ids_b = {c["id"] for c in candidates_b}
            overlap = candidate_ids_a & candidate_ids_b

            self.print_test(
                "No candidate overlap between companies",
                len(overlap) == 0,
                f"Overlap: {len(overlap)} candidates" if overlap else "No overlap ✓"
            )

        return response_a.status_code == 200 and response_b.status_code == 200

    def test_6_company_cannot_access_other_data(self):
        """Test 6: Company A Cannot Access Company B's Data"""
        self.print_section("TEST 6: Cross-Company Access Prevention")

        if not self.company_a_token:
            self.print_test("Access prevention", False, "Missing Company A token")
            return False

        headers_a = {"Authorization": f"Bearer {self.company_a_token}"}

        # Try to access Company B's details
        response = requests.get(f"{BASE_URL}/companies/{self.company_b_id}", headers=headers_a)

        self.print_test(
            "Company A cannot view Company B",
            response.status_code == 403,
            f"Status: {response.status_code} (403 = Forbidden ✓)"
        )

        return response.status_code == 403

    def test_7_super_admin_can_see_all(self):
        """Test 7: Super Admin Can See All Companies"""
        self.print_section("TEST 7: Super Admin Access to All Companies")

        if not self.super_admin_token:
            self.print_test("Super admin access", False, "Missing super admin token")
            return False

        headers = {"Authorization": f"Bearer {self.super_admin_token}"}

        # List all companies
        response = requests.get(f"{BASE_URL}/companies/", headers=headers)

        if response.status_code == 200:
            companies = response.json().get("companies", [])
            company_names = [c["company_name"] for c in companies]

            self.print_test(
                "Super admin can list all companies",
                len(companies) >= 2,
                f"Found {len(companies)} companies: {', '.join(company_names)}"
            )

            # Can view Company A
            response_a = requests.get(f"{BASE_URL}/companies/{self.company_a_id}", headers=headers)
            self.print_test(
                "Super admin can view Company A",
                response_a.status_code == 200,
                f"Status: {response_a.status_code}"
            )

            # Can view Company B
            response_b = requests.get(f"{BASE_URL}/companies/{self.company_b_id}", headers=headers)
            self.print_test(
                "Super admin can view Company B",
                response_b.status_code == 200,
                f"Status: {response_b.status_code}"
            )

            return True
        else:
            self.print_test("Super admin access", False, f"Status: {response.status_code}")
            return False

    def test_8_company_stats(self):
        """Test 8: Company Statistics"""
        self.print_section("TEST 8: Company Statistics")

        if not self.super_admin_token or not self.company_a_id:
            self.print_test("Company stats", False, "Missing prerequisites")
            return False

        headers = {"Authorization": f"Bearer {self.super_admin_token}"}

        response = requests.get(f"{BASE_URL}/companies/{self.company_a_id}/stats", headers=headers)

        if response.status_code == 200:
            stats = response.json()
            self.print_test(
                "Get company statistics",
                True,
                f"Users: {stats.get('total_users', 0)}, Candidates: {stats.get('total_candidates', 0)}"
            )
            return True
        else:
            self.print_test("Get company statistics", False, f"Status: {response.status_code}")
            return False

    def cleanup(self):
        """Clean up test data"""
        self.print_section("CLEANUP: Removing Test Data")

        if not self.super_admin_token:
            print("Cannot cleanup - no super admin token")
            return

        headers = {"Authorization": f"Bearer {self.super_admin_token}"}

        # Delete test companies (will cascade delete users)
        if self.company_a_id:
            response = requests.delete(f"{BASE_URL}/companies/{self.company_a_id}", headers=headers)
            self.print_test(
                "Delete Company A",
                response.status_code == 204,
                f"Status: {response.status_code}"
            )

        if self.company_b_id:
            response = requests.delete(f"{BASE_URL}/companies/{self.company_b_id}", headers=headers)
            self.print_test(
                "Delete Company B",
                response.status_code == 204,
                f"Status: {response.status_code}"
            )

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 70)
        print("  MULTI-TENANCY TEST SUITE")
        print("  Testing data isolation and company management")
        print("=" * 70)

        tests = [
            ("Super Admin Login", self.test_1_super_admin_login),
            ("Create Companies", self.test_2_create_companies),
            ("Create Company Users", self.test_3_create_company_users),
            ("Company Users Login", self.test_4_company_users_login),
            ("Data Isolation - Candidates", self.test_5_data_isolation_candidates),
            ("Cross-Company Access Prevention", self.test_6_company_cannot_access_other_data),
            ("Super Admin Can See All", self.test_7_super_admin_can_see_all),
            ("Company Statistics", self.test_8_company_stats),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"\n✗ Test failed with error: {e}")
                results.append((test_name, False))

        # Summary
        self.print_section("TEST SUMMARY")
        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status} - {test_name}")

        print(f"\nTotal: {passed}/{total} tests passed")

        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Multi-tenancy is working correctly!")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Review the errors above.")

        # Ask about cleanup
        print("\n" + "=" * 70)
        cleanup_choice = input("Do you want to clean up test data (delete test companies)? (yes/no): ").strip().lower()
        if cleanup_choice in ['yes', 'y']:
            self.cleanup()
        else:
            print("Test data kept. You can delete manually later.")


def main():
    print("\n⚠️  IMPORTANT: Update credentials at the top of this script!")
    print(f"   Current username: {SUPER_ADMIN_USERNAME}")
    print(f"   Current password: {'*' * len(SUPER_ADMIN_PASSWORD)}\n")

    proceed = input("Have you updated the credentials? (yes/no): ").strip().lower()
    if proceed not in ['yes', 'y']:
        print("\nPlease update SUPER_ADMIN_USERNAME and SUPER_ADMIN_PASSWORD in the script.")
        return

    print("\nMake sure your backend server is running on http://localhost:8000")
    proceed = input("Is the backend running? (yes/no): ").strip().lower()
    if proceed not in ['yes', 'y']:
        print("\nStart your backend server first, then run this script again.")
        return

    tester = MultiTenancyTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
