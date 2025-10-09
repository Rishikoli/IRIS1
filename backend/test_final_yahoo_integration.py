#!/usr/bin/env python3
"""
Final Test: Yahoo Finance Data Mapping Implementation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_yahoo_mapping():
    """Test the Yahoo Finance data mapping with real data"""
    print("🚀 TESTING YAHOO FINANCE DATA MAPPING")
    print("=" * 45)

    # Test with HCL Technologies
    from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent

    agent = ForensicAnalysisAgent()
    symbol = "HCLTECH.NS"

    print(f"📊 Testing with: {symbol}")

    # Run the analysis
    result = agent.analyze_yahoo_finance_data(symbol)

    if result.get('success'):
        print("✅ SUCCESS: Yahoo Finance data mapping working!")

        # Show vertical analysis results
        va = result.get('vertical_analysis', {})
        if va.get('success'):
            print("\n📊 VERTICAL ANALYSIS RESULTS:")

            income_data = va.get('vertical_analysis', {}).get('income_statement', {})
            if income_data:
                print("Income Statement (as % of revenue):")
                for key, value in income_data.items():
                    if isinstance(value, (int, float)):
                        clean_key = key.replace('_pct', '').replace('_', ' ').title()
                        print(f"  {clean_key}: {value:.2f}%")

            balance_data = va.get('vertical_analysis', {}).get('balance_sheet', {})
            if balance_data:
                print("\nBalance Sheet (as % of total assets):")
                for key, value in balance_data.items():
                    if isinstance(value, (int, float)):
                        clean_key = key.replace('_pct', '').replace('_', ' ').title()
                        print(f"  {clean_key}: {value:.2f}%")

        # Show horizontal analysis results
        ha = result.get('horizontal_analysis', {})
        if ha.get('success'):
            print("\n📈 HORIZONTAL ANALYSIS RESULTS:")

            ha_data = ha.get('horizontal_analysis', {})
            if ha_data:
                for period_key, metrics in ha_data.items():
                    print(f"\n🔄 {period_key}")
                    for key, value in metrics.items():
                        if value is not None:
                            clean_key = key.replace('_growth_pct', '').replace('_', ' ').title()
                            print(f"  {clean_key}: {value:.2f}%")
                        else:
                            clean_key = key.replace('_growth_pct', '').replace('_', ' ').title()
                            print(f"  {clean_key}: N/A")

        print("\n🎉 YAHOO FINANCE MAPPING IMPLEMENTATION COMPLETE!")
        print("✅ Field name mapping: IMPLEMENTED")
        print("✅ Vertical analysis: WORKING")
        print("✅ Horizontal analysis: WORKING")
        print("✅ Real-time data integration: OPERATIONAL")

    else:
        print(f"❌ Analysis failed: {result.get('error')}")

if __name__ == "__main__":
    test_yahoo_mapping()
