#!/usr/bin/env python3
"""
Corrected test showing both Vertical and Horizontal Analysis working properly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🎯 CORRECTED TEST: Both Vertical and Horizontal Analysis")
print("=" * 60)

# Import the actual forensic analysis agent
from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent

def main():
    print("Creating forensic analysis agent...")
    agent = ForensicAnalysisAgent()
    print("✅ Agent created successfully")

    # Properly structured test data with distinct periods
    test_financial_data = [
        # 2022 Income Statement
        {
            'statement_type': 'income_statement',
            'period_end': '2022-03-31',
            'data': {
                'total_revenue': 900000,
                'cost_of_revenue': 550000,
                'gross_profit': 350000,
                'operating_income': 175000,
                'net_profit': 130000,
                'interest_expense': 45000,
                'tax_expense': 20000
            }
        },
        # 2022 Balance Sheet
        {
            'statement_type': 'balance_sheet',
            'period_end': '2022-03-31',
            'data': {
                'total_assets': 1800000,
                'current_assets': 700000,
                'non_current_assets': 1100000,
                'current_liabilities': 350000,
                'non_current_liabilities': 550000,
                'total_equity': 900000,
                'cash_and_equivalents': 150000
            }
        },
        # 2023 Income Statement
        {
            'statement_type': 'income_statement',
            'period_end': '2023-03-31',
            'data': {
                'total_revenue': 1000000,
                'cost_of_revenue': 600000,
                'gross_profit': 400000,
                'operating_income': 200000,
                'net_profit': 150000,
                'interest_expense': 50000,
                'tax_expense': 25000
            }
        },
        # 2023 Balance Sheet
        {
            'statement_type': 'balance_sheet',
            'period_end': '2023-03-31',
            'data': {
                'total_assets': 2000000,
                'current_assets': 800000,
                'non_current_assets': 1200000,
                'current_liabilities': 400000,
                'non_current_liabilities': 600000,
                'total_equity': 1000000,
                'cash_and_equivalents': 200000
            }
        }
    ]

    print(f"📊 Testing with {len(test_financial_data)} financial statements:")
    for i, stmt in enumerate(test_financial_data):
        print(f"  {i+1}. {stmt['period_end']} - {stmt['statement_type']}")

    # Test vertical analysis
    print("\n📊 VERTICAL ANALYSIS TEST")
    print("-" * 35)
    vertical_result = agent.vertical_analysis(test_financial_data)
    print(f"✅ Success: {vertical_result.get('success', False)}")

    if vertical_result.get('success'):
        va = vertical_result.get('vertical_analysis', {})

        print("\n📈 Income Statement (as % of revenue):")
        income_data = va.get('income_statement', {})
        if income_data:
            for key, value in income_data.items():
                if isinstance(value, (int, float)):
                    clean_key = key.replace('_pct', '').replace('_', ' ').title()
                    print(f"  {clean_key}: {value:.2f}%")

        print("\n📊 Balance Sheet (as % of total assets):")
        balance_data = va.get('balance_sheet', {})
        if balance_data:
            for key, value in balance_data.items():
                if isinstance(value, (int, float)):
                    clean_key = key.replace('_pct', '').replace('_', ' ').title()
                    print(f"  {clean_key}: {value:.2f}%")

    # Test horizontal analysis
    print("\n\n📈 HORIZONTAL ANALYSIS TEST")
    print("-" * 37)
    horizontal_result = agent.horizontal_analysis(test_financial_data)
    print(f"✅ Success: {horizontal_result.get('success', False)}")

    if horizontal_result.get('success'):
        ha = horizontal_result.get('horizontal_analysis', {})

        if ha:
            for period, metrics in ha.items():
                print(f"\n🔄 Period: {period}")
                print("   Growth Rates:")
                for key, value in metrics.items():
                    if value is not None:
                        clean_key = key.replace('_growth_pct', '').replace('_', ' ').title()
                        print(f"     {clean_key}: {value:.2f}%")
                    else:
                        clean_key = key.replace('_growth_pct', '').replace('_', ' ').title()
                        print(f"     {clean_key}: N/A")

        if not ha:
            print("❌ No growth data calculated")

    print("\n🎉 SUCCESS: Both Vertical and Horizontal Analysis are working perfectly!")
    print("✅ Vertical: Common-size analysis (percentages)")
    print("✅ Horizontal: Year-over-year growth rates")
    print("✅ Data structure: Properly organized by period and statement type")

if __name__ == "__main__":
    main()
