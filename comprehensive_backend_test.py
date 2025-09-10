#!/usr/bin/env python3
"""
BannkMint AI Backend Test Suite
Tests all critical success criteria for the 48-hour deadline
"""

import requests
import sys
import json
from datetime import datetime
import time

class BannkMintTester:
    def __init__(self, base_url="https://reconcile-forecast.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failures = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
            self.failures.append(f"{name}: {details}")
        
        if details and success:
            print(f"   Details: {details}")

    def test_health_check(self):
        """Test basic backend connectivity"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Service: {data.get('service', 'Unknown')}"
            self.log_test("Backend Health Check", success, details)
            return success
        except Exception as e:
            self.log_test("Backend Health Check", False, str(e))
            return False

    def test_csv_upload(self, csv_file_path, expected_transactions=None):
        """Test CSV upload functionality"""
        try:
            with open(csv_file_path, 'rb') as f:
                files = {'file': (csv_file_path.split('/')[-1], f, 'text/csv')}
                data = {'account_id': 'test-account'}
                
                response = requests.post(
                    f"{self.base_url}/api/ingest", 
                    files=files, 
                    data=data,
                    timeout=30
                )
            
            success = response.status_code == 200
            if success:
                result = response.json()
                if result.get('success'):
                    details = f"Imported: {result.get('imported', 0)}, Skipped: {result.get('skipped', 0)}"
                    if expected_transactions:
                        actual_imported = result.get('imported', 0)
                        if actual_imported != expected_transactions:
                            success = False
                            details += f" (Expected {expected_transactions}, got {actual_imported})"
                else:
                    success = False
                    details = f"Upload failed: {result.get('error', 'Unknown error')}"
            else:
                details = f"HTTP {response.status_code}: {response.text[:200]}"
            
            test_name = f"CSV Upload ({csv_file_path.split('/')[-1]})"
            self.log_test(test_name, success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test(f"CSV Upload ({csv_file_path.split('/')[-1]})", False, str(e))
            return False, {}

    def test_reconciliation_data(self, expected_descriptions=None):
        """Test reconciliation endpoint returns real data"""
        try:
            response = requests.get(f"{self.base_url}/api/reconcile/inbox", timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                transactions = data.get('transactions', [])
                total = data.get('total', 0)
                
                details = f"Found {len(transactions)} transactions, Total: {total}"
                
                # Check if we have real transaction data
                if expected_descriptions and transactions:
                    found_descriptions = [t.get('description', '') for t in transactions]
                    matches = 0
                    for expected in expected_descriptions:
                        if any(expected.lower() in desc.lower() for desc in found_descriptions):
                            matches += 1
                    
                    if matches > 0:
                        details += f", Matched {matches}/{len(expected_descriptions)} expected transactions"
                    else:
                        success = False
                        details += " - No expected transactions found (possible hardcoded data)"
                
                # Check for obvious placeholder data
                if transactions:
                    first_desc = transactions[0].get('description', '').lower()
                    if 'sample' in first_desc or 'demo' in first_desc or 'placeholder' in first_desc:
                        success = False
                        details += " - Contains placeholder/demo data"
            else:
                details = f"HTTP {response.status_code}: {response.text[:200]}"
            
            self.log_test("Reconciliation Data", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("Reconciliation Data", False, str(e))
            return False, {}

    def test_forecast_data(self, expected_cash_range=None):
        """Test forecast endpoint returns dynamic data"""
        try:
            response = requests.get(f"{self.base_url}/api/forecast", timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                current_cash = data.get('current_cash', 0)
                projections = data.get('daily_projections', [])
                
                details = f"Current cash: ${current_cash:.2f}, Projections: {len(projections)} days"
                
                # Check if cash flow matches expected range
                if expected_cash_range:
                    min_cash, max_cash = expected_cash_range
                    if not (min_cash <= current_cash <= max_cash):
                        success = False
                        details += f" - Cash ${current_cash:.2f} outside expected range ${min_cash:.2f}-${max_cash:.2f}"
                
                # Check for obvious hardcoded values
                if current_cash in [25000, 32500, 0, 1000, 5000, 10000]:
                    success = False
                    details += " - Appears to be hardcoded value"
                    
            else:
                details = f"HTTP {response.status_code}: {response.text[:200]}"
            
            self.log_test("Forecast Data", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("Forecast Data", False, str(e))
            return False, {}

    def clear_database(self):
        """Attempt to clear database (if endpoint exists)"""
        try:
            # This might not exist, but try anyway
            response = requests.delete(f"{self.base_url}/api/transactions", timeout=10)
            print(f"Database clear attempt: {response.status_code}")
        except:
            print("No database clear endpoint available")

    def run_comprehensive_test(self):
        """Run all tests according to success criteria"""
        print("🚀 Starting BannkMint AI Comprehensive Test Suite")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test 1: Basic connectivity
        if not self.test_health_check():
            print("❌ Backend not accessible - stopping tests")
            return False
        
        print("\n📁 Testing CSV Upload Functionality...")
        
        # Test 2: Restaurant CSV upload
        restaurant_success, restaurant_result = self.test_csv_upload(
            "/app/restaurant_transactions.csv", 
            expected_transactions=10
        )
        
        if restaurant_success:
            # Wait a moment for processing
            time.sleep(2)
            
            # Test 3: Check reconciliation shows restaurant data
            print("\n🔄 Testing Reconciliation Data...")
            expected_restaurants = [
                "McDonald's", "Starbucks", "Pizza Palace", "Subway", 
                "Olive Garden", "Chipotle", "Domino's", "KFC", "Taco Bell", "Buffalo Wild Wings"
            ]
            
            reconcile_success, reconcile_data = self.test_reconciliation_data(expected_restaurants)
            
            # Test 4: Check forecast shows negative cash flow
            print("\n📊 Testing Forecast Data (Restaurant Expenses)...")
            # Expected range: around $1001.79 (ending balance from CSV)
            forecast_success, forecast_data = self.test_forecast_data(expected_cash_range=(900, 1300))
            
            if forecast_success:
                restaurant_cash = forecast_data.get('current_cash', 0)
                
                # Test 5: Upload different CSV and verify different forecast
                print("\n💼 Testing Business CSV Upload...")
                business_success, business_result = self.test_csv_upload(
                    "/app/business_transactions.csv",
                    expected_transactions=6
                )
                
                if business_success:
                    time.sleep(2)
                    
                    print("\n📈 Testing Forecast Data (Business Income)...")
                    # Expected range: around $1318.52 (ending balance from business CSV)
                    business_forecast_success, business_forecast_data = self.test_forecast_data(
                        expected_cash_range=(1200, 1400)
                    )
                    
                    if business_forecast_success:
                        business_cash = business_forecast_data.get('current_cash', 0)
                        
                        # Verify forecasts are different
                        cash_difference = abs(business_cash - restaurant_cash)
                        if cash_difference > 100:  # Significant difference
                            self.log_test("Different CSV = Different Forecast", True, 
                                        f"Restaurant: ${restaurant_cash:.2f}, Business: ${business_cash:.2f}, Diff: ${cash_difference:.2f}")
                        else:
                            self.log_test("Different CSV = Different Forecast", False,
                                        f"Forecasts too similar: ${cash_difference:.2f} difference")
        
        # Final Results
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"Tests Passed: {self.tests_passed}/{self.tests_run} ({success_rate:.1f}%)")
        
        if self.failures:
            print("\n❌ FAILURES:")
            for failure in self.failures:
                print(f"  • {failure}")
        
        # Determine overall success
        critical_tests = [
            "Backend Health Check",
            "CSV Upload (restaurant_transactions.csv)", 
            "Reconciliation Data",
            "Forecast Data (Restaurant Expenses)",
            "Different CSV = Different Forecast"
        ]
        
        critical_failures = [f for f in self.failures if any(ct in f for ct in critical_tests)]
        
        if not critical_failures and self.tests_passed >= 5:
            print("\n🎉 ALL CRITICAL SUCCESS CRITERIA MET!")
            return True
        else:
            print(f"\n⚠️  CRITICAL FAILURES DETECTED ({len(critical_failures)} issues)")
            return False

def main():
    tester = BannkMintTester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())