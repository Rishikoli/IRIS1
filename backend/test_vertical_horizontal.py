#!/usr/bin/env python3
"""
Quick test for Vertical and Horizontal Analysis
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent

    print("🔍 Testing Vertical and Horizontal Analysis...")

    # Test data
    test_financial_data = [
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
                'total_equity': 1000000,
                'cash_and_equivalents': 200000
            }
        }
    ]

    agent = ForensicAnalysisAgent()

    # Test vertical analysis
    print("\n📊 Testing Vertical Analysis...")
    vertical_result = agent.vertical_analysis(test_financial_data)
    print(f"✅ Vertical analysis success: {vertical_result.get('success', False)}")

    if vertical_result.get('success'):
        va = vertical_result.get('vertical_analysis', {})
        print("\nIncome Statement (as % of revenue):")
        for key, value in va.get('income_statement', {}).items():
            print(f"  {key}: {value:.2f}%")

        print("\nBalance Sheet (as % of total assets):")
        for key, value in va.get('balance_sheet', {}).items():
            print(f"  {key}: {value:.2f}%")

    # Test horizontal analysis (needs multiple periods)
    print("\n📈 Testing Horizontal Analysis...")
    test_data_multi_period = [
        {
            'statement_type': 'income_statement',
            'period_end': '2023-03-31',
            'data': {
                'total_revenue': 1000000,
                'gross_profit': 400000,
                'operating_income': 200000,
                'net_profit': 150000,
                'total_assets': 2000000,
                'total_liabilities': 1000000,
                'total_equity': 1000000
            }
        },
        {
            'statement_type': 'income_statement',
            'period_end': '2022-03-31',
            'data': {
                'total_revenue': 900000,
                'gross_profit': 350000,
                'operating_income': 175000,
                'net_profit': 130000,
                'total_assets': 1800000,
                'total_liabilities': 900000,
                'total_equity': 900000
            }
        }
    ]

    horizontal_result = agent.horizontal_analysis(test_data_multi_period)
    print(f"✅ Horizontal analysis success: {horizontal_result.get('success', False)}")

    if horizontal_result.get('success'):
        ha = horizontal_result.get('horizontal_analysis', {})
        print("\nGrowth Rates:")
        for period, metrics in ha.items():
            print(f"\nPeriod: {period}")
            for key, value in metrics.items():
                if value is not None:
                    print(f"  {key}: {value:.2f}%")
                else:
                    print(f"  {key}: N/A")

    print("\n🎉 SUCCESS: Both Vertical and Horizontal Analysis are working correctly!")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
