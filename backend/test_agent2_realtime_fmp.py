#!/usr/bin/env python3
"""
HCL Technologies Real-Time Forensic Analysis using FMP API
Tests Agent 2 with real HCL Technologies data from Financial Modeling Prep API
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api_clients.fmp_client import FMPAPIClient
from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent
from src.database.connection import get_db_client

def fetch_hcl_data_from_fmp():
    """Fetch real HCL Technologies data from FMP API"""

    print("🔍 Fetching Real HCL Technologies Data from FMP API...")
    print("=" * 60)

    # Initialize FMP client
    fmp_client = FMPAPIClient()

    try:
        # Test connection first
        if not fmp_client.test_connection():
            print("❌ FMP API connection failed")
            return None

        print("✅ FMP API connection successful")

        # Search for HCL Technologies
        search_results = fmp_client.search_company("HCL Technologies")
        print(f"🔍 Found {len(search_results)} companies matching 'HCL Technologies'")

        # Find NSE/BSE listed HCL
        hcl_stock = None
        for company in search_results:
            if (company.get('symbol', '').endswith('.NS') or  # NSE
                company.get('symbol', '').endswith('.BO') or  # BSE
                'HCL' in company.get('name', '').upper()):
                hcl_stock = company
                break

        if not hcl_stock:
            print("❌ HCL Technologies not found in FMP database")
            return None

        print(f"✅ Found HCL: {hcl_stock.get('name')} ({hcl_stock.get('symbol')})")

        symbol = hcl_stock.get('symbol')
        profile = fmp_client.get_company_profile(symbol)

        if profile and len(profile) > 0:
            company_profile = profile[0]
            print("📊 Company Profile:")
            print(f"  - Sector: {company_profile.get('sector', 'N/A')}")
            print(f"  - Industry: {company_profile.get('industry', 'N/A')}")
            print(f"  - Market Cap: {company_profile.get('marketCap', 'N/A')}")
            print(f"  - Employees: {company_profile.get('fullTimeEmployees', 'N/A')}")

        # Get financial statements (latest 2 years for comparison)
        print("\n📈 Fetching Financial Statements...")
        income_statements = fmp_client.get_income_statements(symbol, limit=2)
        balance_sheets = fmp_client.get_balance_sheets(symbol, limit=2)
        cash_flows = fmp_client.get_cash_flows(symbol, limit=2)

        print(f"✅ Retrieved {len(income_statements)} income statements")
        print(f"✅ Retrieved {len(balance_sheets)} balance sheets")
        print(f"✅ Retrieved {len(cash_flows)} cash flow statements")

        return {
            'company_info': hcl_stock,
            'profile': profile[0] if profile else {},
            'income_statements': income_statements,
            'balance_sheets': balance_sheets,
            'cash_flows': cash_flows
        }

    except Exception as e:
        print(f"❌ Error fetching FMP data: {e}")
        return None

def store_real_hcl_data_in_db(hcl_data):
    """Store real HCL data in our database"""

    if not hcl_data:
        return None

    print("\n💾 Storing Real HCL Data in Database...")
    print("=" * 60)

    db_client = get_db_client()

    try:
        # Insert company data
        company_info = hcl_data['company_info']
        profile = hcl_data['profile']

        company_data = {
            'cin': company_info.get('cik', 'UNKNOWN'),  # FMP uses CIK instead of CIN
            'name': company_info.get('name', 'HCL Technologies'),
            'sector': profile.get('sector', 'Information Technology'),
            'industry': profile.get('industry', 'IT Services'),
            'incorporation_date': None,  # Not available in FMP
            'registered_address': profile.get('address', 'N/A'),
            'email': 'N/A',
            'phone': 'N/A',
            'website': profile.get('website', 'N/A'),
            'face_value': 2.0,
            'paid_up_capital': 0,  # Not available in FMP
            'market_cap': profile.get('marketCap', 0),
            'currency': profile.get('currency', 'INR'),
            'nse_symbol': 'HCLTECH' if company_info.get('exchangeShortName') == 'NASDAQ' else company_info.get('symbol', 'HCLTECH'),
            'bse_symbol': '532281',
            'isin': 'INE860A01027',
            'is_active': True,
            'is_listed': True,
            'is_suspended': False,
            'data_source': 'fmp_api',
            'last_updated': None,
            'api_response': json.dumps(company_info)
        }

        # Insert company
        db_client.execute_query('''
            INSERT INTO companies (
                cin, name, sector, industry, incorporation_date, registered_address,
                email, phone, website, face_value, paid_up_capital, market_cap,
                currency, nse_symbol, bse_symbol, isin, is_active, is_listed,
                is_suspended, data_source, last_updated, api_response
            ) VALUES (
                :cin, :name, :sector, :industry, :incorporation_date, :registered_address,
                :email, :phone, :website, :face_value, :paid_up_capital, :market_cap,
                :currency, :nse_symbol, :bse_symbol, :isin, :is_active, :is_listed,
                :is_suspended, :data_source, :last_updated, :api_response
            )
        ''', company_data)

        # Get company ID
        company = db_client.execute_query(
            'SELECT id FROM companies WHERE name = :name',
            {'name': company_data['name']}
        )

        if not company:
            print("❌ Failed to insert company")
            return None

        company_id = company[0]['id']
        print(f"✅ Company stored with ID: {company_id}")

        # Store financial statements
        statements_stored = 0

        # Store income statements
        for stmt in hcl_data['income_statements']:
            try:
                statement_data = {
                    'company_id': company_id,
                    'statement_type': 'income_statement',
                    'period_end': stmt.get('date'),
                    'data': json.dumps({
                        'total_revenue': stmt.get('revenue', 0),
                        'cost_of_revenue': stmt.get('costOfRevenue', 0),
                        'gross_profit': stmt.get('grossProfit', 0),
                        'operating_income': stmt.get('operatingIncome', 0),
                        'net_profit': stmt.get('netIncome', 0),
                        'ebitda': stmt.get('ebitda', 0),
                        'interest_expense': stmt.get('interestExpense', 0),
                        'tax_expense': stmt.get('incomeTaxExpense', 0),
                        'sga_expenses': stmt.get('sellingGeneralAdministrative', 0),
                        'cost_of_goods_sold': stmt.get('costOfRevenue', 0),
                        'operating_cash_flow': 0,  # Will be updated from cash flow
                        'total_accruals': 0
                    })
                }

                db_client.execute_query('''
                    INSERT INTO financial_statements (company_id, statement_type, period_end, data)
                    VALUES (:company_id, :statement_type, :period_end, :data)
                ''', statement_data)
                statements_stored += 1

            except Exception as e:
                print(f"⚠️  Error storing income statement: {e}")

        # Store balance sheets
        for stmt in hcl_data['balance_sheets']:
            try:
                statement_data = {
                    'company_id': company_id,
                    'statement_type': 'balance_sheet',
                    'period_end': stmt.get('date'),
                    'data': json.dumps({
                        'total_assets': stmt.get('totalAssets', 0),
                        'current_assets': stmt.get('totalCurrentAssets', 0),
                        'non_current_assets': stmt.get('totalAssets', 0) - stmt.get('totalCurrentAssets', 0),
                        'current_liabilities': stmt.get('totalCurrentLiabilities', 0),
                        'non_current_liabilities': stmt.get('totalLiabilities', 0) - stmt.get('totalCurrentLiabilities', 0),
                        'total_equity': stmt.get('totalStockholdersEquity', 0),
                        'cash_and_equivalents': stmt.get('cashAndCashEquivalents', 0),
                        'accounts_receivable': stmt.get('netReceivables', 0),
                        'inventory': stmt.get('inventory', 0),
                        'property_plant_equipment': stmt.get('propertyPlantEquipmentNet', 0),
                        'retained_earnings': stmt.get('retainedEarnings', 0),
                        'total_liabilities': stmt.get('totalLiabilities', 0)
                    })
                }

                db_client.execute_query('''
                    INSERT INTO financial_statements (company_id, statement_type, period_end, data)
                    VALUES (:company_id, :statement_type, :period_end, :data)
                ''', statement_data)
                statements_stored += 1

            except Exception as e:
                print(f"⚠️  Error storing balance sheet: {e}")

        print(f"✅ Stored {statements_stored} financial statements")

        return company_id

    except Exception as e:
        print(f"❌ Error storing data in database: {e}")
        return None

async def run_realtime_analysis_with_real_hcl_data():
    """Run Agent 2 real-time analysis with real HCL data from FMP API"""

    print("🚀 Agent 2 Real-Time Forensic Analysis with Real HCL Data")
    print("=" * 70)

    # Step 1: Fetch real HCL data from FMP API
    hcl_data = fetch_hcl_data_from_fmp()

    if not hcl_data:
        print("❌ Failed to fetch HCL data from FMP API")
        return

    # Step 2: Store in database
    company_id = store_real_hcl_data_in_db(hcl_data)

    if not company_id:
        print("❌ Failed to store HCL data in database")
        return

    print(f"\n🎯 Running Real-Time Forensic Analysis on Real HCL Data (ID: {company_id})...")
    print("=" * 70)

    # Step 3: Initialize Agent 2 and run analysis
    forensic_agent = ForensicAnalysisAgent()
    db_client = get_db_client()

    # Get stored financial statements
    financial_statements = db_client.execute_query(
        """
        SELECT statement_type, period_end, data
        FROM financial_statements
        WHERE company_id = :company_id
        ORDER BY period_end DESC
        """,
        {"company_id": company_id}
    )

    if not financial_statements:
        print("❌ No financial statements found in database")
        return

    # Convert to expected format
    statements = []
    for stmt in financial_statements:
        statements.append({
            "statement_type": stmt["statement_type"],
            "period_end": stmt["period_end"].isoformat() if stmt["period_end"] else None,
            "data": stmt["data"] if stmt["data"] else {}
        })

    print(f"📊 Analyzing {len(statements)} real financial statements from FMP API...")

    # Track progress
    progress_updates = []

    def progress_callback(progress_data: dict):
        """Callback to track progress updates"""
        progress_updates.append(progress_data.copy())
        progress = progress_data.get("progress", 0)
        step = progress_data.get("current_step", "Unknown")
        print(f"📈 Progress: {progress:3.0f}% - {step}")

    # Run real-time analysis
    try:
        async for result in forensic_agent.comprehensive_forensic_analysis_realtime(
            str(company_id),
            statements,
            progress_callback
        ):
            final_result = result
            break

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return

    print("\n" + "=" * 70)
    print("📋 REAL HCL TECHNOLOGIES ANALYSIS RESULTS")
    print("=" * 70)

    # Display results
    if final_result.get("success", False):
        print("✅ Real-time forensic analysis completed successfully!")

        # Show key metrics
        print("\n🏢 Company: HCL Technologies Limited")
        print(f"📊 Data Source: FMP API (Real Market Data)")
        print(f"📅 Analysis Date: {final_result.get('analysis_date', 'Unknown')}")

        # Altman Z-Score
        altman = final_result.get("altman_z_score", {})
        if altman.get("success"):
            z_score = altman.get("altman_z_score", {})
            score = z_score.get("z_score", 0)
            classification = z_score.get("classification", "UNKNOWN")
            print(f"\n🎯 Altman Z-Score: {score:.3f} ({classification})")

        # Beneish M-Score
        beneish = final_result.get("beneish_m_score", {})
        if beneish.get("success"):
            m_score = beneish.get("beneish_m_score", {})
            score = m_score.get("m_score", 0)
            risk = "⚠️ HIGH" if m_score.get("is_likely_manipulator", False) else "✅ LOW"
            print(f"🎭 Beneish M-Score: {score:.3f} (Manipulation Risk: {risk})")

        # Benford's Law
        benford = final_result.get("benford_analysis", {})
        if benford.get("success"):
            analysis = benford.get("benford_analysis", {})
            status = "⚠️ ANOMALOUS" if analysis.get("is_anomalous", False) else "✅ NORMAL"
            print(f"🔍 Benford's Law: {status}")

        # Anomalies
        anomalies = final_result.get("anomaly_detection", {})
        if anomalies.get("success"):
            count = anomalies.get("anomalies_detected", 0)
            print(f"🚨 Anomalies Detected: {count}")

        print(f"\n⏱️  Analysis completed in {len(progress_updates)} progress steps")
        print("📈 All results based on REAL market data from FMP API")

    else:
        print(f"❌ Analysis failed: {final_result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(run_realtime_analysis_with_real_hcl_data())
