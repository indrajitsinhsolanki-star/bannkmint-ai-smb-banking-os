"""
Simple BannkMint AI Backend API Testing Suite
Testing basic endpoints for rebranding verification
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://banking-forecast.preview.emergentagent.com"

class SimpleBannkMintTester:
    """Simple test suite for BannkMint AI rebranding verification"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = []
        
    def run_all_tests(self):
        """Run basic test suite"""
        print("🚀 Starting BannkMint AI Rebranding Tests")
        print("=" * 60)
        
        # Core API Tests
        self.test_health_check()
        self.test_root_endpoint()
        
        # Banking Integration Tests
        self.test_banking_institutions()
        
        # Rules Tests
        self.test_get_rules()
        
        # Forecast Tests
        self.test_cash_flow_forecast()
        
        # Reporting Tests
        self.test_month_end_report()
        
        # Banking Overview Tests
        self.test_banking_overview()
        
        # Print Results
        self.print_test_summary()
        
    def test_health_check(self):
        """Test health check endpoint"""
        print("\n📋 Testing Health Check...")
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                service_name = data.get('service', 'Unknown')
                print(f"✅ Health check passed: {service_name}")
                
                # Check for rebranding
                if "BannkMint AI" in service_name:
                    print("✅ Rebranding verified in health check")
                    self.test_results.append(("Health Check", True, f"Service: {service_name}"))
                else:
                    print(f"⚠️ Rebranding issue: Expected 'BannkMint AI', got '{service_name}'")
                    self.test_results.append(("Health Check", False, f"Rebranding issue: {service_name}"))
            else:
                print(f"❌ Health check failed: {response.status_code}")
                self.test_results.append(("Health Check", False, f"Status: {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            self.test_results.append(("Health Check", False, str(e)))
            
    def test_root_endpoint(self):
        """Test root endpoint"""
        print("\n📋 Testing Root Endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/api/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', 'Unknown')
                print(f"✅ Root endpoint accessible: {message}")
                
                # Check for rebranding
                if "BannkMint AI" in message:
                    print("✅ Rebranding verified in root message")
                    self.test_results.append(("Root Endpoint", True, f"Message: {message}"))
                else:
                    print(f"⚠️ Rebranding issue: Expected 'BannkMint AI', got '{message}'")
                    self.test_results.append(("Root Endpoint", False, f"Rebranding issue: {message}"))
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
                self.test_results.append(("Root Endpoint", False, f"Status: {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
            self.test_results.append(("Root Endpoint", False, str(e)))
            
    def test_banking_institutions(self):
        """Test banking institutions endpoint"""
        print("\n📋 Testing Banking Institutions...")
        try:
            response = self.session.get(f"{self.base_url}/api/banking/institutions", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                banks = result.get('supported_banks', [])
                print(f"✅ Banking institutions retrieved: {len(banks)} supported banks")
                self.test_results.append(("Banking Institutions", True, f"{len(banks)} banks supported"))
            else:
                print(f"❌ Banking institutions failed: {response.status_code}")
                self.test_results.append(("Banking Institutions", False, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Banking institutions error: {e}")
            self.test_results.append(("Banking Institutions", False, str(e)))
            
    def test_get_rules(self):
        """Test rule retrieval"""
        print("\n📋 Testing Rule Retrieval...")
        try:
            response = self.session.get(f"{self.base_url}/api/rules", timeout=10)
            
            if response.status_code == 200:
                rules = response.json()
                print(f"✅ Retrieved {len(rules)} rules")
                self.test_results.append(("Get Rules", True, f"Retrieved {len(rules)} rules"))
            else:
                print(f"❌ Rule retrieval failed: {response.status_code}")
                self.test_results.append(("Get Rules", False, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Rule retrieval error: {e}")
            self.test_results.append(("Get Rules", False, str(e)))
            
    def test_cash_flow_forecast(self):
        """Test cash flow forecasting"""
        print("\n📋 Testing Cash Flow Forecast...")
        try:
            response = self.session.get(f"{self.base_url}/api/forecast?weeks=4&scenario=base", timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                projections = result.get('daily_projections', [])
                print(f"✅ Forecast generated: {len(projections)} day projections")
                self.test_results.append(("Cash Flow Forecast", True, f"{len(projections)} days forecasted"))
            else:
                print(f"❌ Forecast failed: {response.status_code}")
                if response.status_code == 500:
                    try:
                        error_detail = response.json().get('detail', 'Unknown error')
                        print(f"   Error detail: {error_detail}")
                    except:
                        pass
                self.test_results.append(("Cash Flow Forecast", False, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Forecast error: {e}")
            self.test_results.append(("Cash Flow Forecast", False, str(e)))
            
    def test_month_end_report(self):
        """Test month-end reporting"""
        print("\n📋 Testing Month-End Report...")
        try:
            response = self.session.get(f"{self.base_url}/api/reports/month-end", timeout=15)
            
            if response.status_code == 200:
                report = response.json()
                period = report.get('report_period', {})
                print(f"✅ Month-end report generated for {period.get('month_name', 'Unknown')} {period.get('year', 'Unknown')}")
                self.test_results.append(("Month-End Report", True, "Report generated successfully"))
            else:
                print(f"❌ Month-end report failed: {response.status_code}")
                if response.status_code == 500:
                    try:
                        error_detail = response.json().get('detail', 'Unknown error')
                        print(f"   Error detail: {error_detail}")
                    except:
                        pass
                self.test_results.append(("Month-End Report", False, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Month-end report error: {e}")
            self.test_results.append(("Month-End Report", False, str(e)))
            
    def test_banking_overview(self):
        """Test banking overview endpoint"""
        print("\n📋 Testing Banking Overview...")
        try:
            response = self.session.get(f"{self.base_url}/api/banking/overview", timeout=10)
            
            if response.status_code == 200:
                overview = response.json()
                print(f"✅ Banking overview loaded successfully")
                self.test_results.append(("Banking Overview", True, "Overview data loaded"))
            else:
                print(f"❌ Banking overview failed: {response.status_code}")
                if response.status_code == 500:
                    try:
                        error_detail = response.json().get('detail', 'Unknown error')
                        print(f"   Error detail: {error_detail}")
                    except:
                        pass
                self.test_results.append(("Banking Overview", False, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Banking overview error: {e}")
            self.test_results.append(("Banking Overview", False, str(e)))
            
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🏦 BannkMint AI Rebranding Test Results Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed, _ in self.test_results if passed)
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 Overall Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for test_name, passed, message in self.test_results:
                if not passed:
                    print(f"   • {test_name}: {message}")
        
        print(f"\n✅ Passed Tests:")
        for test_name, passed, message in self.test_results:
            if passed:
                print(f"   • {test_name}: {message}")
        
        print("\n" + "=" * 60)
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! BannkMint AI rebranding is successful.")
        else:
            print(f"⚠️  {failed_tests} test(s) failed. Please review and fix issues.")
        
        print("=" * 60)

def main():
    """Run the simple test suite"""
    print("🚀 Starting BannkMint AI Rebranding Verification Tests")
    print("Testing basic API endpoints after rebranding...")
    print("=" * 60)
    
    tester = SimpleBannkMintTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()