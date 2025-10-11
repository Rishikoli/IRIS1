#!/usr/bin/env python3
"""
IRIS Forensic Analysis CLI Tool
Command-line interface for testing and interacting with IRIS agents

Usage:
    python iris_cli.py ingest RELIANCE.BO
    python iris_cli.py analyze RELIANCE.BO
    python iris_cli.py risk-score RELIANCE.BO
    python iris_cli.py comprehensive RELIANCE.BO
    python iris_cli.py list-companies
"""

import argparse
import json
import sys
import requests
from typing import Dict, List, Any
from datetime import datetime
import os

# Add src to path for app imports if needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class IRISCLI:
    """Command-line interface for IRIS forensic analysis agents"""

    def __init__(self):
        # Read API port from environment; default to 8000
        api_port = int(os.environ.get("API_PORT", "8000"))
        self.base_url = f"http://localhost:{api_port}"
        self.session = requests.Session()

    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                response = self.session.get(url, timeout=30)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=30)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Request failed: {e}"}
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Invalid JSON response: {e}"}

    def ingest_data(self, company_symbol: str) -> None:
        """Ingest financial data for a company"""
        print(f"📥 Ingesting data for {company_symbol}...")

        result = self._make_request(f"/api/ingestion/{company_symbol}", "POST")

        if result.get("success"):
            print("✅ Data ingestion successful!")
            print(f"📊 Statements collected: {len(result.get('financial_statements', []))}")
            print(f"📅 Period range: {result.get('period_start')} to {result.get('period_end')}")

            # Show statement types
            statements = result.get('financial_statements', [])
            if statements:
                print("\n📋 Statement Types:")
                for stmt in statements:
                    print(f"  • {stmt.get('statement_type', 'Unknown')}: {stmt.get('period_end', 'Unknown')}")
        else:
            print(f"❌ Ingestion failed: {result.get('error', 'Unknown error')}")

    def analyze_company(self, company_symbol: str) -> None:
        """Run forensic analysis on a company"""
        print(f"🔍 Running forensic analysis for {company_symbol}...")

        # First check if we need to ingest data
        print("📥 Checking for existing data...")
        check_result = self._make_request(f"/api/ingestion/{company_symbol}")

        if not check_result.get("success"):
            print("📥 No existing data found. Ingesting data first...")
            self.ingest_data(company_symbol)
            print()

        # Run analysis
        result = self._make_request(f"/api/forensic/{company_symbol}", "POST")

        if result.get("success"):
            analysis = result.get("analysis", {})

            print("✅ Forensic analysis completed!")
            # Show key metrics
            print("📊 Key Metrics:")
            print(f"  • Risk Score: {analysis.get('overall_risk_score', 'N/A')}")
            print(f"  • Financial Health: {analysis.get('financial_health_grade', 'N/A')}")

            # Show anomalies
            anomalies = analysis.get("anomaly_detection", {}).get("anomalies", [])
            if anomalies:
                print(f"  • Anomalies Detected: {len(anomalies)}")
                for anomaly in anomalies[:3]:  # Show top 3
                    print(f"    - {anomaly['type']}: {anomaly['description']}")
            else:
                print("  • Anomalies Detected: 0")
            # Show analysis types completed
            analysis_types = [k for k in analysis.keys() if k != 'company_id' and k != 'analysis_date']
            print(f"  • Analysis Types: {', '.join(analysis_types)}")
        else:
            print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")

    def calculate_risk_score(self, company_symbol: str) -> None:
        """Calculate risk score for a company"""
        print(f"⚡ Calculating risk score for {company_symbol}...")

        result = self._make_request(f"/api/risk-score/{company_symbol}", "POST")

        if result.get("success"):
            risk_data = result.get("risk_score", {})

            print("✅ Risk scoring completed!")
            print("📊 Risk Assessment:")
            print(f"  • Overall Score: {risk_data.get('overall_score', 'N/A')}/100")
            print(f"  • Risk Level: {risk_data.get('risk_level', 'N/A')}")
            print(f"  • Confidence: {risk_data.get('confidence_score', 'N/A')}%")

            # Show risk factors
            factors = risk_data.get("risk_factors", [])
            if factors:
                print("🚨 Key Risk Factors:")
                for factor in factors[:5]:  # Show top 5
                    print(f"  • {factor}")
        else:
            print(f"❌ Risk scoring failed: {result.get('error', 'Unknown error')}")

    def comprehensive_analysis(self, company_symbol: str) -> None:
        """Run comprehensive analysis (all agents)"""
        print(f"🚀 Running comprehensive analysis for {company_symbol}...")
        print("=" * 60)

        # Step 1: Data Ingestion
        print("📥 Step 1: Data Ingestion")
        self.ingest_data(company_symbol)
        print()

        # Step 2: Forensic Analysis
        print("🔍 Step 2: Forensic Analysis")
        self.analyze_company(company_symbol)
        print()

        # Step 3: Risk Scoring
        print("⚡ Step 3: Risk Scoring")
        self.calculate_risk_score(company_symbol)
        print()

        print("🎉 Comprehensive analysis completed!")
    def list_companies(self) -> None:
        """List companies in the database"""
        print("📋 Listing companies in database...")

        result = self._make_request("/api/companies")

        if result.get("success"):
            companies = result.get("companies", [])
            if companies:
                print(f"\n🏢 Companies ({len(companies)}):")
                for company in companies[:10]:  # Show first 10
                    print(f"  • {company.get('symbol')} - {company.get('name', 'Unknown')}")
            else:
                print("  No companies found in database")
        else:
            print(f"❌ Failed to list companies: {result.get('error', 'Unknown error')}")

    def realtime_analysis(self, company_symbol: str) -> None:
        """Run real-time analysis with progress updates"""
        print(f"⚡ Starting real-time analysis for {company_symbol}...")

        try:
            response = self.session.post(
                f"{self.base_url}/api/forensic/{company_symbol}/realtime",
                json={},
                stream=True,
                timeout=300  # 5 minute timeout
            )

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if "progress" in data:
                            progress = data["progress"]
                            step = data.get("current_step", "")
                            print(f"\r🔄 Progress: {progress}% - {step}", end="", flush=True)

                        if progress == 100:
                            print("\n✅ Real-time analysis completed!")
                            break
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"❌ Real-time analysis failed: {e}")

    def run(self) -> None:
        """Main CLI entry point"""
        parser = argparse.ArgumentParser(
            description="IRIS Forensic Analysis CLI Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python iris_cli.py ingest RELIANCE.BO      # Ingest company data
  python iris_cli.py analyze RELIANCE.BO     # Run forensic analysis
  python iris_cli.py risk-score RELIANCE.BO  # Calculate risk score
  python iris_cli.py comprehensive RELIANCE.BO  # Run all analyses
  python iris_cli.py realtime RELIANCE.BO    # Real-time analysis
  python iris_cli.py list-companies          # List all companies
            """
        )

        parser.add_argument("command", choices=[
            "ingest", "analyze", "risk-score", "comprehensive",
            "realtime", "list-companies"
        ], help="Command to execute")

        parser.add_argument("symbol", nargs="?",
                          help="Company symbol (e.g., RELIANCE.BO)")

        args = parser.parse_args()

        # Validate symbol for commands that need it
        if args.command != "list-companies" and not args.symbol:
            parser.error(f"Command '{args.command}' requires a company symbol")

        print("🚀 IRIS Forensic Analysis CLI Tool")
        print("=" * 50)

        try:
            if args.command == "ingest":
                self.ingest_data(args.symbol)
            elif args.command == "analyze":
                self.analyze_company(args.symbol)
            elif args.command == "risk-score":
                self.calculate_risk_score(args.symbol)
            elif args.command == "comprehensive":
                self.comprehensive_analysis(args.symbol)
            elif args.command == "realtime":
                self.realtime_analysis(args.symbol)
            elif args.command == "list-companies":
                self.list_companies()

        except KeyboardInterrupt:
            print("\n\n👋 Analysis interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")


def main():
    """Main entry point"""
    cli = IRISCLI()
    cli.run()


if __name__ == "__main__":
    main()
