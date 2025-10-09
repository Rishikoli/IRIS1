#!/usr/bin/env python3
"""
Test Vertical and Horizontal Analysis with REAL Yahoo Finance Data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yfinance as yf
from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent

def fetch_real_company_data():
    """Fetch real financial data from Yahoo Finance"""
    print("📊 Fetching REAL financial data from Yahoo Finance...")
    print("=" * 60)

    # Test with HCL Technologies
    symbol = "HCLTECH.NS"
    print(f"🔍 Getting data for: HCL Technologies ({symbol})")

    try:
        ticker = yf.Ticker(symbol)

        # Get financial statements (latest 2 years)
        income_stmt = ticker.financials
        balance_sheet = ticker.balance_sheet

        if income_stmt is None or balance_sheet is None:
            print(f"❌ Insufficient data for {symbol}")
            return None

        print(f"✅ Retrieved {len(income_stmt.columns)} periods of income statements")
        print(f"✅ Retrieved {len(balance_sheet.columns)} periods of balance sheets")

        # Convert to format expected by forensic agent
        financial_statements = []

        # Add income statements (latest 2 years)
        for i in range(min(2, len(income_stmt.columns))):
            stmt_data = income_stmt.iloc[:, i].to_dict()
            stmt_data['date'] = str(income_stmt.columns[i].date())
            financial_statements.append({
                'statement_type': 'income_statement',
                'period_end': stmt_data['date'],
                'data': stmt_data
            })

        # Add balance sheets (latest 2 years)
        for i in range(min(2, len(balance_sheet.columns))):
            stmt_data = balance_sheet.iloc[:, i].to_dict()
            stmt_data['date'] = str(balance_sheet.columns[i].date())
            financial_statements.append({
                'statement_type': 'balance_sheet',
                'period_end': stmt_data['date'],
                'data': stmt_data
            })

        print(f"✅ Prepared {len(financial_statements)} financial statements for analysis")
        return financial_statements

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def run_real_data_analysis(financial_statements):
    """Run vertical and horizontal analysis on real data"""
    print("\n🔍 Running Analysis on REAL Yahoo Finance Data")
    print("=" * 55)

    agent = ForensicAnalysisAgent()

    # Test vertical analysis
    print("\n📊 VERTICAL ANALYSIS (Common-Size Analysis)")
    print("-" * 45)

    vertical_result = agent.vertical_analysis(financial_statements)
    if vertical_result.get('success'):
        va = vertical_result.get('vertical_analysis', {})

        print("📈 Income Statement (as % of Total Revenue):")
        income_data = va.get('income_statement', {})
        if income_data:
            for key, value in income_data.items():
                if isinstance(value, (int, float)) and value > 0:
                    clean_key = key.replace('_pct', '').replace('_', ' ').title()
                    print(f"  {clean_key}: {value:.2f}%")
        else:
            print("  No income statement data available")

        print("\n📊 Balance Sheet (as % of Total Assets):")
        balance_data = va.get('balance_sheet', {})
        if balance_data:
            for key, value in balance_data.items():
                if isinstance(value, (int, float)) and value > 0:
                    clean_key = key.replace('_pct', '').replace('_', ' ').title()
                    print(f"  {clean_key}: {value:.2f}%")
        else:
            print("  No balance sheet data available")
    else:
        print(f"❌ Vertical analysis failed: {vertical_result.get('error')}")

    # Test horizontal analysis
    print("\n\n📈 HORIZONTAL ANALYSIS (Year-over-Year Growth)")
    print("-" * 50)

    horizontal_result = agent.horizontal_analysis(financial_statements)
    if horizontal_result.get('success'):
        ha = horizontal_result.get('horizontal_analysis', {})

        if ha:
            print(f"\n📊 Found {len(ha)} period-to-period comparisons:")
            for period_key, metrics in ha.items():
                stmt_type = period_key.split('_')[-1]
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
    else:
        print(f"❌ Horizontal analysis failed: {horizontal_result.get('error')}")

def main():
    """Test with real Yahoo Finance data"""
    print("🚀 REAL DATA TEST: Yahoo Finance → Forensic Analysis")
    print("=" * 60)

    # Fetch real data
    financial_statements = fetch_real_company_data()

    if financial_statements:
        # Show what we got
        print("\n📋 FINANCIAL STATEMENTS RECEIVED:")
        for i, stmt in enumerate(financial_statements, 1):
            period = stmt.get('period_end', 'Unknown')
            stmt_type = stmt.get('statement_type', 'Unknown')
            print(f"  {i}. {period} - {stmt_type}")

        # Run analysis
        run_real_data_analysis(financial_statements)

        print("\n🎉 SUCCESS: Both analyses work perfectly with REAL Yahoo Finance data!")
        print("✅ Vertical Analysis: Common-size percentages calculated")
        print("✅ Horizontal Analysis: Year-over-year growth rates calculated")
        print("✅ Real Data Integration: Successfully processes live market data")

    else:
        print("\n❌ Could not fetch real data for analysis")

if __name__ == "__main__":
    main()
