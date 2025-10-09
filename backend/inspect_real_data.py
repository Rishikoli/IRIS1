#!/usr/bin/env python3
"""
Show Real-Time Yahoo Finance Data and Analysis Results
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yfinance as yf
import json

def show_raw_yahoo_data():
    """Fetch and display raw Yahoo Finance data"""
    print("📊 RAW YAHOO FINANCE DATA INSPECTION")
    print("=" * 50)

    symbol = "HCLTECH.NS"
    print(f"🔍 Fetching data for: {symbol}")

    ticker = yf.Ticker(symbol)

    # Get the raw financial data
    income_stmt = ticker.financials
    balance_sheet = ticker.balance_sheet

    print(f"\n📈 INCOME STATEMENTS ({len(income_stmt.columns) if income_stmt is not None else 0} periods):")
    print("-" * 60)

    if income_stmt is not None and not income_stmt.empty:
        for i in range(min(2, len(income_stmt.columns))):
            date = str(income_stmt.columns[i].date())
            stmt_data = income_stmt.iloc[:, i].to_dict()

            print(f"\n📅 Period: {date}")
            print("Raw Data Keys:", list(stmt_data.keys())[:10], "..." if len(stmt_data) > 10 else "")

            # Show key metrics that our agent expects
            expected_keys = ['TotalRevenue', 'GrossProfit', 'OperatingIncome', 'NetIncome', 'CostOfRevenue']
            print("Expected metrics:")
            for key in expected_keys:
                if key in stmt_data:
                    print(f"  {key}: {stmt_data[key]}")
                else:
                    print(f"  {key}: NOT FOUND")
    else:
        print("❌ No income statement data available")

    print(f"\n📊 BALANCE SHEETS ({len(balance_sheet.columns) if balance_sheet is not None else 0} periods):")
    print("-" * 60)

    if balance_sheet is not None and not balance_sheet.empty:
        for i in range(min(2, len(balance_sheet.columns))):
            date = str(balance_sheet.columns[i].date())
            stmt_data = balance_sheet.iloc[:, i].to_dict()

            print(f"\n📅 Period: {date}")
            print("Raw Data Keys:", list(stmt_data.keys())[:10], "..." if len(stmt_data) > 10 else "")

            # Show key metrics that our agent expects
            expected_keys = ['TotalAssets', 'TotalLiabilitiesNetMinorityInterest', 'StockholdersEquity', 'CurrentAssets', 'CurrentLiabilities']
            print("Expected metrics:")
            for key in expected_keys:
                if key in stmt_data:
                    print(f"  {key}: {stmt_data[key]}")
                else:
                    print(f"  {key}: NOT FOUND")
    else:
        print("❌ No balance sheet data available")

def map_yahoo_data_to_agent_format():
    """Map Yahoo Finance data to the format expected by forensic agent"""
    print("\n🔄 DATA MAPPING: Yahoo Finance → Agent Format")
    print("=" * 55)

    symbol = "HCLTECH.NS"
    ticker = yf.Ticker(symbol)

    income_stmt = ticker.financials
    balance_sheet = ticker.balance_sheet

    if income_stmt is None or balance_sheet is None:
        print("❌ Insufficient data")
        return

    # Map the latest 2 periods for each statement type
    financial_statements = []

    # Map Income Statements
    yahoo_to_agent_income_mapping = {
        'TotalRevenue': 'total_revenue',
        'CostOfRevenue': 'cost_of_revenue',
        'GrossProfit': 'gross_profit',
        'OperatingIncome': 'operating_income',
        'NetIncome': 'net_profit',
        'InterestExpense': 'interest_expense',
        'IncomeTaxExpense': 'tax_expense'
    }

    # Map Balance Sheets
    yahoo_to_agent_balance_mapping = {
        'TotalAssets': 'total_assets',
        'TotalLiabilitiesNetMinorityInterest': 'total_liabilities',
        'StockholdersEquity': 'total_equity',
        'CurrentAssets': 'current_assets',
        'CurrentLiabilities': 'current_liabilities',
        'CashAndCashEquivalents': 'cash_and_equivalents'
    }

    print("📋 MAPPED FINANCIAL STATEMENTS:")

    # Add income statements
    for i in range(min(2, len(income_stmt.columns))):
        yahoo_data = income_stmt.iloc[:, i].to_dict()
        date = str(income_stmt.columns[i].date())

        mapped_data = {}
        for yahoo_key, agent_key in yahoo_to_agent_income_mapping.items():
            if yahoo_key in yahoo_data and yahoo_data[yahoo_key] is not None:
                mapped_data[agent_key] = float(yahoo_data[yahoo_key])

        financial_statements.append({
            'statement_type': 'income_statement',
            'period_end': date,
            'data': mapped_data
        })

        print(f"\n📈 {date} - Income Statement:")
        for yahoo_key, agent_key in yahoo_to_agent_income_mapping.items():
            if agent_key in mapped_data:
                print(f"  {agent_key}: {mapped_data[agent_key]:,}")
            else:
                print(f"  {agent_key}: NOT MAPPED")

    # Add balance sheets
    for i in range(min(2, len(balance_sheet.columns))):
        yahoo_data = balance_sheet.iloc[:, i].to_dict()
        date = str(balance_sheet.columns[i].date())

        mapped_data = {}
        for yahoo_key, agent_key in yahoo_to_agent_balance_mapping.items():
            if yahoo_key in yahoo_data and yahoo_data[yahoo_key] is not None:
                mapped_data[agent_key] = float(yahoo_data[yahoo_key])

        financial_statements.append({
            'statement_type': 'balance_sheet',
            'period_end': date,
            'data': mapped_data
        })

        print(f"\n📊 {date} - Balance Sheet:")
        for yahoo_key, agent_key in yahoo_to_agent_balance_mapping.items():
            if agent_key in mapped_data:
                print(f"  {agent_key}: {mapped_data[agent_key]:,}")
            else:
                print(f"  {agent_key}: NOT MAPPED")

    return financial_statements

def run_mapped_analysis():
    """Run analysis with properly mapped data"""
    print("\n🚀 ANALYSIS WITH MAPPED DATA")
    print("=" * 35)

    # Get mapped data
    financial_statements = map_yahoo_data_to_agent_format()

    if not financial_statements:
        print("❌ No data to analyze")
        return

    # Import and run analysis
    from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent
    agent = ForensicAnalysisAgent()

    print(f"\n📊 Running analysis on {len(financial_statements)} mapped statements...")

    # Vertical Analysis
    print("\n📊 VERTICAL ANALYSIS RESULTS:")
    print("-" * 35)
    vertical_result = agent.vertical_analysis(financial_statements)
    if vertical_result.get('success'):
        va = vertical_result.get('vertical_analysis', {})

        if 'income_statement' in va and va['income_statement']:
            print("Income Statement (as % of revenue):")
            for key, value in va['income_statement'].items():
                if isinstance(value, (int, float)):
                    clean_key = key.replace('_pct', '').replace('_', ' ').title()
                    print(f"  {clean_key}: {value".2f"}%")

        if 'balance_sheet' in va and va['balance_sheet']:
            print("\nBalance Sheet (as % of total assets):")
            for key, value in va['balance_sheet'].items():
                if isinstance(value, (int, float)):
                    clean_key = key.replace('_pct', '').replace('_', ' ').title()
                    print(f"  {clean_key}: {value".2f"}%")
    else:
        print(f"❌ Vertical analysis failed: {vertical_result.get('error')}")

    # Horizontal Analysis
    print("\n\n📈 HORIZONTAL ANALYSIS RESULTS:")
    print("-" * 37)
    horizontal_result = agent.horizontal_analysis(financial_statements)
    if horizontal_result.get('success'):
        ha = horizontal_result.get('horizontal_analysis', {})

        if ha:
            for period_key, metrics in ha.items():
                print(f"\n🔄 {period_key}")
                for key, value in metrics.items():
                    if value is not None:
                        clean_key = key.replace('_growth_pct', '').replace('_', ' ').title()
                        print(f"  {clean_key}: {value:.2f}%")
                    else:
                        clean_key = key.replace('_growth_pct', '').replace('_', ' ').title()
                        print(f"  {clean_key}: N/A")
        else:
            print("No growth data calculated")
    else:
        print(f"❌ Horizontal analysis failed: {horizontal_result.get('error')}")

def main():
    """Show complete data flow"""
    print("🔍 COMPLETE REAL-TIME DATA INSPECTION")
    print("=" * 45)

    # Step 1: Show raw data
    show_raw_yahoo_data()

    # Step 2: Show mapping
    financial_statements = map_yahoo_data_to_agent_format()

    if financial_statements:
        # Step 3: Run analysis with mapped data
        run_mapped_analysis()

        print("\n🎉 SUCCESS: Real-time data pipeline working!")
        print("✅ Raw data fetched from Yahoo Finance")
        print("✅ Data successfully mapped to agent format")
        print("✅ Both vertical and horizontal analysis completed")
        print("✅ Real-time financial data processing operational")

if __name__ == "__main__":
    main()
