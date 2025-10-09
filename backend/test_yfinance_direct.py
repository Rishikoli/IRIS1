#!/usr/bin/env python3
"""
Fetch Vertical and Horizontal Analysis directly from Yahoo Finance
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yfinance as yf
from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent

def fetch_company_data_yfinance(symbol):
    """Fetch real financial data from Yahoo Finance"""
    print(f"📊 Fetching real data for {symbol} from Yahoo Finance...")

    try:
        ticker = yf.Ticker(f"{symbol}.NS")  # NSE symbol

        # Get financial statements (latest 2 years)
        income_stmt = ticker.financials
        balance_sheet = ticker.balance_sheet

        if income_stmt is None or balance_sheet is None:
            print(f"❌ Insufficient data for {symbol}")
            return None

        # Convert to format expected by forensic agent
        financial_statements = []

        # Add income statements
        for i in range(min(2, len(income_stmt.columns))):
            stmt_data = income_stmt.iloc[:, i].to_dict()
            stmt_data['date'] = str(income_stmt.columns[i].date())
            financial_statements.append({
                'statement_type': 'income_statement',
                'period_end': stmt_data['date'],
                'data': stmt_data
            })

        # Add balance sheets
        for i in range(min(2, len(balance_sheet.columns))):
            stmt_data = balance_sheet.iloc[:, i].to_dict()
            stmt_data['date'] = str(balance_sheet.columns[i].date())
            financial_statements.append({
                'statement_type': 'balance_sheet',
                'period_end': stmt_data['date'],
                'data': stmt_data
            })

        print(f"✅ Retrieved {len(financial_statements)} financial statements")
        return financial_statements

    except Exception as e:
        print(f"❌ Error fetching data for {symbol}: {e}")
        return None

def run_vertical_horizontal_analysis(symbol, financial_statements):
    """Run vertical and horizontal analysis on real Yahoo Finance data"""
    print(f"\n🔍 Running Vertical & Horizontal Analysis for {symbol}")
    print("=" * 60)

    agent = ForensicAnalysisAgent()

    # Vertical Analysis
    print("\n📊 VERTICAL ANALYSIS (Common-Size Analysis)")
    print("-" * 45)

    vertical_result = agent.vertical_analysis(financial_statements)
    if vertical_result.get('success'):
        va = vertical_result.get('vertical_analysis', {})

        print("Income Statement (as % of Total Revenue):")
        income_data = va.get('income_statement', {})
        if income_data:
            for key, value in income_data.items():
                if isinstance(value, (int, float)):
                    print(f"  {key.replace('_pct', '').replace('_', ' ').title()}: {value:.2f}%")
        else:
            print("  No income statement data available")

        print("\nBalance Sheet (as % of Total Assets):")
        balance_data = va.get('balance_sheet', {})
        if balance_data:
            for key, value in balance_data.items():
                if isinstance(value, (int, float)):
                    print(f"  {key.replace('_pct', '').replace('_', ' ').title()}: {value:.2f}%")
        else:
            print("  No balance sheet data available")
    else:
        print(f"❌ Vertical analysis failed: {vertical_result.get('error')}")

    # Horizontal Analysis
    print("\n\n📈 HORIZONTAL ANALYSIS (Year-over-Year Growth)")
    print("-" * 47)

    horizontal_result = agent.horizontal_analysis(financial_statements)
    if horizontal_result.get('success'):
        ha = horizontal_result.get('horizontal_analysis', {})

        if ha:
            for period, metrics in ha.items():
                print(f"\nPeriod: {period}")
                print("Growth Rates:")
                for key, value in metrics.items():
                    if value is not None:
                        metric_name = key.replace('_growth_pct', '').replace('_', ' ').title()
                        print(f"  {metric_name}: {value:.2f}%")
                    else:
                        print(f"  {key}: N/A")
        else:
            print("No growth data available")
    else:
        print(f"❌ Horizontal analysis failed: {horizontal_result.get('error')}")

def main():
    """Test with multiple companies"""
    companies = [
        ("HCLTECH", "HCL Technologies"),
        ("TCS", "Tata Consultancy Services"),
        ("INFY", "Infosys"),
        ("WIPRO", "Wipro")
    ]

    print("🚀 REAL MARKET DATA: Yahoo Finance → Forensic Analysis")
    print("=" * 65)

    for symbol, name in companies:
        print(f"\n🏢 {name} ({symbol})")
        print("=" * 50)

        # Fetch real data
        financial_statements = fetch_company_data_yfinance(symbol)
        if financial_statements:
            # Run analysis
            run_vertical_horizontal_analysis(symbol, financial_statements)
            print("\n" + "=" * 65)

    print("\n✅ ANALYSIS COMPLETE: Real Yahoo Finance data processed successfully!")

if __name__ == "__main__":
    main()
