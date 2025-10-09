#!/usr/bin/env python3
"""
Simple Agent Integration Test
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_agent_integration():
    """Test basic integration between Agent 1 and Agent 2"""
    print("AGENT INTEGRATION TEST")
    print("=" * 30)

    try:
        # Import agents
        from src.agents.forensic.agent1_ingestion import DataIngestionAgent
        from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent

        # Initialize agents
        ingestion_agent = DataIngestionAgent()
        forensic_agent = ForensicAnalysisAgent()

        print("Agents initialized successfully")

        # Test 1: Company Search
        print("\nTEST 1: Company Search")
        search_results = ingestion_agent.search_company("HCLTECH.NS")

        if search_results:
            print(f"Found {len(search_results)} companies")
            yahoo_results = [r for r in search_results if r.get("source") == "yahoo"]
            if yahoo_results:
                print("Yahoo Finance results found")
        else:
            print("No search results")
            return False

        # Test 2: Yahoo Finance Data Fetch
        print("\nTEST 2: Yahoo Finance Data")
        yahoo_data = ingestion_agent.get_financials("HCLTECH.NS", "yahoo", periods=2)

        if "error" not in yahoo_data:
            print("Yahoo Finance data fetched successfully")
            quarterly_income = len(yahoo_data.get("quarterly_income_statement", []))
            quarterly_balance = len(yahoo_data.get("quarterly_balance_sheet", []))
            print(f"Quarterly Income: {quarterly_income}, Balance: {quarterly_balance}")
        else:
            print(f"Yahoo Finance failed: {yahoo_data.get('error')}")
            return False

        # Test 3: Data Normalization
        print("\nTEST 3: Data Normalization")
        normalized = ingestion_agent.normalize_financial_statements(yahoo_data, "yahoo")

        if normalized:
            print(f"Normalized {len(normalized)} statements")
            income_count = len([s for s in normalized if s.get("statement_type") == "INCOME_STATEMENT"])
            balance_count = len([s for s in normalized if s.get("statement_type") == "BALANCE_SHEET"])
            print(f"Income: {income_count}, Balance: {balance_count}")
        else:
            print("Normalization failed")
            return False

        # Test 4: Forensic Analysis
        print("\nTEST 4: Forensic Analysis")
        analysis = forensic_agent.analyze_yahoo_finance_data("HCLTECH.NS", quarters=2)

        if analysis.get('success'):
            print("Forensic analysis successful")
            print(f"Vertical analysis: {'success' if analysis.get('vertical_analysis', {}).get('success') else 'failed'}")
            print(f"Horizontal analysis: {'success' if analysis.get('horizontal_analysis', {}).get('success') else 'failed'}")
            print(f"Financial ratios: {'success' if analysis.get('financial_ratios', {}).get('success') else 'failed'}")
        else:
            print(f"Forensic analysis failed: {analysis.get('error')}")
            return False

        print("\nALL TESTS PASSED!")
        print("Agent 1 and Agent 2 integration: SUCCESSFUL")
        return True

    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_agent_integration()
    print(f"\nOverall result: {'PASS' if success else 'FAIL'}")
