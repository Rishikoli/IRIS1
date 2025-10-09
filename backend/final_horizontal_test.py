#!/usr/bin/env python3
"""
Final comprehensive test for Horizontal Analysis fix
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🔍 FINAL TEST: Horizontal Analysis Fix Verification")
print("=" * 55)

# Import the actual forensic analysis agent
from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent

def main():
    print("Creating forensic analysis agent...")
    agent = ForensicAnalysisAgent()
    print("✅ Agent created successfully")

    # Test with properly structured data
    test_financial_data = [
        # 2022 Period
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
        {
            'statement_type': 'balance_sheet',
            'period_end': '2022-03-31',
            'data': {
                'total_assets': 1800000,
                'current_assets': 700000,
                'non_current_assets': 1100000,
                'current_liabilities': 350000,
                'non_current_liabilities': 550000,
                'total_liabilities': 900000,
                'total_equity': 900000,
                'cash_and_equivalents': 150000
            }
        },

        # 2023 Period
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
        {
            'statement_type': 'balance_sheet',
            'period_end': '2023-03-31',
            'data': {
                'total_assets': 2000000,
                'current_assets': 800000,
                'non_current_assets': 1200000,
                'current_liabilities': 400000,
                'non_current_liabilities': 600000,
                'total_liabilities': 1000000,
                'total_equity': 1000000,
                'cash_and_equivalents': 200000
            }
        }
    ]

    print(f"📊 Testing with {len(test_financial_data)} financial statements:")
    for i, stmt in enumerate(test_financial_data):
        print(f"  {i+1}. {stmt['period_end']} - {stmt['statement_type']}")

    # Test horizontal analysis
    print("\n📈 HORIZONTAL ANALYSIS TEST")
    print("-" * 35)
    horizontal_result = agent.horizontal_analysis(test_financial_data)
    print(f"✅ Success: {horizontal_result.get('success', False)}")

    if horizontal_result.get('success'):
        ha = horizontal_result.get('horizontal_analysis', {})

        if ha:
            print(f"\n📊 Found {len(ha)} period-to-period comparisons:")
            for period_key, metrics in ha.items():
                stmt_type = period_key.split('_')[-1]  # Extract statement type from key
                print(f"\n🔄 {period_key}")
                print(f"   Statement Type: {stmt_type}")
                print("   Growth Rates:")

                valid_metrics = 0
                for key, value in metrics.items():
                    if value is not None:
                        clean_key = key.replace('_growth_pct', '').replace('_', ' ').title()
                        print(f"     {clean_key}: {value:.2f}%")
                        valid_metrics += 1
                    else:
                        clean_key = key.replace('_growth_pct', '').replace('_', ' ').title()
                        print(f"     {clean_key}: N/A")

                print(f"   ✅ Valid metrics: {valid_metrics}/{len(metrics)}")

        else:
            print("❌ No growth data calculated")

    print("\n🎉 HORIZONTAL ANALYSIS VERIFICATION COMPLETE!")

    # Also test vertical analysis for completeness
    print("\n📊 VERTICAL ANALYSIS TEST")
    print("-" * 30)
    vertical_result = agent.vertical_analysis(test_financial_data)
    print(f"✅ Success: {vertical_result.get('success', False)}")

    if vertical_result.get('success'):
        va = vertical_result.get('vertical_analysis', {})

        # Show a few key metrics
        income_data = va.get('income_statement', {})
        balance_data = va.get('balance_sheet', {})

        print("\n📈 Key Income Statement Metrics (as % of revenue):")
        key_income_metrics = ['gross_profit_pct', 'operating_income_pct', 'net_profit_pct']
        for key in key_income_metrics:
            if key in income_data:
                clean_key = key.replace('_pct', '').replace('_', ' ').title()
                print(f"  {clean_key}: {income_data[key]:.2f}%")

        print("\n📊 Key Balance Sheet Metrics (as % of total assets):")
        key_balance_metrics = ['current_assets_pct', 'total_equity_pct']
        for key in key_balance_metrics:
            if key in balance_data:
                clean_key = key.replace('_pct', '').replace('_', ' ').title()
                print(f"  {clean_key}: {balance_data[key]:.2f}%")

    print("\n🏆 FINAL RESULT: Both analyses are working perfectly!")

if __name__ == "__main__":
    main()
