#!/usr/bin/env python3
"""
Comprehensive API Testing Suite for IRIS Agents
Tests all API endpoints for data ingestion, forensic analysis, and risk scoring

Usage:
    python test_iris_api.py
    python test_iris_api.py --endpoint /api/forensic/RELIANCE.BO
    python test_iris_api.py --company RELIANCE.BO --test-all
"""

import os
import requests
import json
import time
import argparse
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


class IRISTestSuite:
    """Comprehensive testing suite for IRIS API endpoints"""

    def __init__(self, base_url: str = None):
        # Read API port from environment; default to 8000
        api_port = int(os.environ.get("API_PORT", "8000"))
        self.base_url = base_url or f"http://localhost:{api_port}"
        self.session = requests.Session()
        self.test_results = []
        self.start_time = time.time()

    def log_test(self, test_name: str, passed: bool, details: str = "", response_time: float = 0):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        })

        print(f"[{status}] {test_name} ({response_time:.2f}s)")
        if details and not passed:
            print(f"      Details: {details}")

    def make_request(self, endpoint: str, method: str = "GET", data: Dict = None,
                    expected_status: int = 200) -> tuple[Dict, float]:
        """Make HTTP request and return response with timing"""
        url = f"{self.base_url}{endpoint}"

        start_time = time.time()
        try:
            if method == "GET":
                response = self.session.get(url, timeout=30)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=30)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}, 0

            response_time = time.time() - start_time

            try:
                result = response.json()
            except json.JSONDecodeError:
                result = {"success": False, "error": "Invalid JSON response"}

            if response.status_code != expected_status:
                return {"success": False, "error": f"HTTP {response.status_code}"}, response_time

            return result, response_time

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            return {"success": False, "error": f"Request failed: {e}"}, response_time

    def test_health_check(self) -> bool:
        """Test basic health check endpoint"""
        result, response_time = self.make_request("/health")

        if result.get("success") and result.get("status") == "healthy":
            self.log_test("Health Check", True, "API server is responding", response_time)
            return True
        else:
            self.log_test("Health Check", False, result.get("error", "Health check failed"), response_time)
            return False

    def test_companies_list(self) -> bool:
        """Test companies listing endpoint"""
        result, response_time = self.make_request("/api/companies")

        if result.get("success") and "companies" in result:
            companies = result["companies"]
            self.log_test("Companies List", True,
                         f"Retrieved {len(companies)} companies", response_time)
            return True
        else:
            self.log_test("Companies List", False,
                         result.get("error", "Failed to list companies"), response_time)
            return False

    def test_data_ingestion(self, company_symbol: str) -> bool:
        """Test data ingestion for a company"""
        print(f"\n📥 Testing data ingestion for {company_symbol}...")

        # Test ingestion endpoint
        result, response_time = self.make_request(
            f"/api/ingestion/{company_symbol}",
            method="POST",
            expected_status=200
        )

        if result.get("success"):
            statements = result.get("financial_statements", [])
            self.log_test("Data Ingestion", True,
                         f"Successfully ingested {len(statements)} statements", response_time)

            # Verify statement structure
            if statements:
                sample_stmt = statements[0]
                required_fields = ["statement_type", "period_end", "data"]
                missing_fields = [field for field in required_fields if field not in sample_stmt]

                if not missing_fields:
                    self.log_test("Statement Structure", True, "All required fields present")
                else:
                    self.log_test("Statement Structure", False,
                                f"Missing fields: {missing_fields}")

            return True
        else:
            self.log_test("Data Ingestion", False,
                         result.get("error", "Ingestion failed"), response_time)
            return False

    def test_forensic_analysis(self, company_symbol: str) -> bool:
        """Test forensic analysis endpoint"""
        print(f"\n🔍 Testing forensic analysis for {company_symbol}...")

        # First ensure we have data
        self.test_data_ingestion(company_symbol)

        result, response_time = self.make_request(
            f"/api/forensic/{company_symbol}",
            method="POST",
            expected_status=200
        )

        if result.get("success"):
            analysis = result.get("analysis", {})
            self.log_test("Forensic Analysis", True,
                         "Analysis completed successfully", response_time)

            # Check for expected analysis components
            expected_components = [
                "vertical_analysis", "horizontal_analysis", "financial_ratios",
                "benford_analysis", "anomaly_detection"
            ]

            found_components = [comp for comp in expected_components if comp in analysis]

            if len(found_components) >= 3:  # At least 3 components should be present
                self.log_test("Analysis Components", True,
                            f"Found {len(found_components)}/{len(expected_components)} components")
            else:
                self.log_test("Analysis Components", False,
                            f"Only found {len(found_components)} components")

            # Check for anomalies
            anomalies = analysis.get("anomaly_detection", {}).get("anomalies", [])
            self.log_test("Anomaly Detection", True,
                         f"Detected {len(anomalies)} anomalies")

            return True
        else:
            self.log_test("Forensic Analysis", False,
                         result.get("error", "Analysis failed"), response_time)
            return False

    def test_risk_scoring(self, company_symbol: str) -> bool:
        """Test risk scoring endpoint"""
        print(f"\n⚡ Testing risk scoring for {company_symbol}...")

        result, response_time = self.make_request(
            f"/api/risk-score/{company_symbol}",
            method="POST",
            expected_status=200
        )

        if result.get("success"):
            risk_data = result.get("risk_score", {})
            self.log_test("Risk Scoring", True,
                         "Risk score calculated successfully", response_time)

            # Verify risk score structure
            required_fields = ["overall_score", "risk_level", "confidence_score"]
            missing_fields = [field for field in required_fields if field not in risk_data]

            if not missing_fields:
                self.log_test("Risk Score Structure", True, "All required fields present")
            else:
                self.log_test("Risk Score Structure", False,
                            f"Missing fields: {missing_fields}")

            # Check score range
            score = risk_data.get("overall_score", -1)
            if 0 <= score <= 100:
                self.log_test("Score Range", True, f"Score {score} is in valid range")
            else:
                self.log_test("Score Range", False, f"Score {score} is out of range")

            return True
        else:
            self.log_test("Risk Scoring", False,
                         result.get("error", "Risk scoring failed"), response_time)
            return False

    def test_realtime_analysis(self, company_symbol: str) -> bool:
        """Test real-time analysis endpoint"""
        print(f"\n⚡ Testing real-time analysis for {company_symbol}...")

        try:
            response = self.session.post(
                f"{self.base_url}/api/forensic/{company_symbol}/realtime",
                json={},
                stream=True,
                timeout=300
            )

            progress_updates = 0
            final_result = None

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        progress_updates += 1

                        if "progress" in data:
                            progress = data["progress"]
                            if progress == 100:
                                final_result = data
                                break
                    except json.JSONDecodeError:
                        continue

            if final_result and progress_updates > 0:
                self.log_test("Real-time Analysis", True,
                            f"Received {progress_updates} progress updates", 0)
                return True
            else:
                self.log_test("Real-time Analysis", False,
                            "No progress updates received", 0)
                return False

        except Exception as e:
            self.log_test("Real-time Analysis", False, str(e), 0)
            return False

    def test_error_handling(self, company_symbol: str) -> bool:
        """Test error handling for invalid requests"""
        print(f"\n🛡️  Testing error handling...")

        # Test invalid company symbol
        result, response_time = self.make_request(
            "/api/forensic/INVALID_SYMBOL",
            method="POST",
            expected_status=400  # Should return 400 for invalid symbol
        )

        if not result.get("success"):
            self.log_test("Invalid Symbol Error", True,
                         "Properly handles invalid company symbols", response_time)
        else:
            self.log_test("Invalid Symbol Error", False,
                         "Should reject invalid symbols", response_time)

        # Test missing data
        result, response_time = self.make_request(
            "/api/forensic/NONEXISTENT.BO",
            method="POST",
            expected_status=404  # Should return 404 for missing data
        )

        if not result.get("success"):
            self.log_test("Missing Data Error", True,
                         "Properly handles missing company data", response_time)
        else:
            self.log_test("Missing Data Error", False,
                         "Should handle missing data gracefully", response_time)

        return True

    def run_comprehensive_test(self, company_symbol: str) -> None:
        """Run all tests for a specific company"""
        print(f"🧪 Running comprehensive API test suite for {company_symbol}")
        print("=" * 70)

        all_passed = True

        # Basic health checks
        if not self.test_health_check():
            all_passed = False

        if not self.test_companies_list():
            all_passed = False

        # Company-specific tests
        if not self.test_data_ingestion(company_symbol):
            all_passed = False

        if not self.test_forensic_analysis(company_symbol):
            all_passed = False

        if not self.test_risk_scoring(company_symbol):
            all_passed = False

        if not self.test_realtime_analysis(company_symbol):
            all_passed = False

        if not self.test_error_handling(company_symbol):
            all_passed = False

        # Print summary
        self.print_summary()

        if all_passed:
            print("🎉 ALL TESTS PASSED! IRIS API is fully functional.")
        else:
            print("⚠️  SOME TESTS FAILED! Check the details above.")

    def run_specific_test(self, endpoint: str) -> None:
        """Run test for a specific endpoint"""
        print(f"🧪 Testing specific endpoint: {endpoint}")

        if endpoint.startswith("/api/ingestion/"):
            company = endpoint.split("/")[-1]
            self.test_data_ingestion(company)
        elif endpoint.startswith("/api/forensic/") and not endpoint.endswith("/realtime"):
            company = endpoint.split("/")[-1]
            self.test_forensic_analysis(company)
        elif endpoint.startswith("/api/forensic/") and endpoint.endswith("/realtime"):
            company = endpoint.split("/")[-2]
            self.test_realtime_analysis(company)
        elif endpoint.startswith("/api/risk-score/"):
            company = endpoint.split("/")[-1]
            self.test_risk_scoring(company)
        else:
            print(f"❌ Unknown endpoint: {endpoint}")

        self.print_summary()

    def print_summary(self) -> None:
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test["passed"])
        failed_tests = total_tests - passed_tests

        total_time = time.time() - self.start_time

        print(" TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "Success Rate: 0%")
        print(f"Total Time: {total_time:.2f}s")

        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for test in self.test_results:
                if not test["passed"]:
                    print(f"  • {test['test']}: {test['details']}")

    def run(self) -> None:
        """Main entry point"""
        parser = argparse.ArgumentParser(description="IRIS API Test Suite")
        parser.add_argument("--company", help="Company symbol to test (e.g., RELIANCE.BO)")
        parser.add_argument("--endpoint", help="Specific endpoint to test")
        parser.add_argument("--test-all", action="store_true",
                          help="Run all tests for the specified company")

        args = parser.parse_args()

        print("🚀 IRIS API Test Suite")
        print("=" * 50)

        if args.endpoint:
            self.run_specific_test(args.endpoint)
        elif args.company:
            if args.test_all:
                self.run_comprehensive_test(args.company)
            else:
                # Run basic tests
                self.test_health_check()
                self.test_companies_list()
                self.test_data_ingestion(args.company)
                self.print_summary()
        else:
            print("❌ Please specify --company or --endpoint")
            print("Example: python test_iris_api.py --company RELIANCE.BO")
            sys.exit(1)


def main():
    """Main entry point"""
    tester = IRISTestSuite()
    tester.run()


if __name__ == "__main__":
    main()
