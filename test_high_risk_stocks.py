#!/usr/bin/env python3
"""
Test Agent 3 with Real-Time Yahoo Finance Data - Multiple High-Risk Stocks
"""

import sys
import os
import json
from datetime import datetime

# Add the backend source to Python path
sys.path.append('/home/aditya/I.R.I.S./backend/src')
sys.path.append('/home/aditya/I.R.I.S./backend')

# Set environment variables
os.environ['GEMINI_API_KEY'] = 'test_key'
os.environ['SUPABASE_URL'] = 'test_url'
os.environ['SUPABASE_KEY'] = 'test_key'
os.environ['FMP_API_KEY'] = 'test_key'
os.environ['SUPABASE_DB_PASSWORD'] = 'test_password'

try:
    import yfinance as yf
    from agents.forensic.agent3_risk_scoring import RiskScoringAgent
    from agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent

    def test_high_risk_stocks():
        """Test Agent 3 with multiple high-risk stocks"""
        print("🚨 Testing Agent 3 with HIGH-RISK STOCKS for Anomaly Detection...")

        # Test with stocks known for high risk/volatility
        test_stocks = [
            "YESBANK.BO",    # Bank that had major crisis in 2020
            "IDEA.NS",       # Telecom with massive debt
            "SUZLON.BO",     # Wind energy company with volatility
            "JPPOWER.BO",    # Power company with issues
        ]

        risky_stocks_found = []

        for company_symbol in test_stocks:
            print(f"\n{'='*70}")
            print(f"🔥 ANALYZING HIGH-RISK STOCK: {company_symbol}")
            print(f"{'='*70}")

            try:
                # Fetch real data from Yahoo Finance
                ticker = yf.Ticker(company_symbol)
                financials = ticker.financials
                balance_sheet = ticker.balance_sheet

                if financials is None or balance_sheet is None or len(financials.columns) == 0:
                    print(f"❌ No financial data available for {company_symbol}")
                    continue

                print(f"✅ Successfully fetched real data for {company_symbol}")
                print(f"   - Income statements: {len(financials.columns)} periods")
                print(f"   - Balance sheets: {len(balance_sheet.columns)} periods")

                # Convert to our expected format
                financial_statements = []

                # Process income statements
                for i in range(min(3, len(financials.columns))):
                    stmt_data = financials.iloc[:, i].to_dict()
                    stmt_data['date'] = str(financials.columns[i].date())

                    financial_statements.append({
                        'statement_type': 'income_statement',
                        'period_end': str(financials.columns[i].date()),
                        'data': stmt_data
                    })

                # Process balance sheets
                for i in range(min(3, len(balance_sheet.columns))):
                    stmt_data = balance_sheet.iloc[:, i].to_dict()
                    stmt_data['date'] = str(balance_sheet.columns[i].date())

                    financial_statements.append({
                        'statement_type': 'balance_sheet',
                        'period_end': str(balance_sheet.columns[i].date()),
                        'data': stmt_data
                    })

                print(f"✅ Processed {len(financial_statements)} financial statements")

                # Run forensic analysis
                forensic_agent = ForensicAnalysisAgent()
                forensic_result = forensic_agent.comprehensive_forensic_analysis(
                    company_symbol, financial_statements
                )

                if not forensic_result['success']:
                    print(f"❌ Forensic analysis failed: {forensic_result.get('error')}")
                    continue

                print("✅ Forensic analysis completed successfully")

                # Test Agent 3 risk scoring
                risk_agent = RiskScoringAgent()
                risk_assessment = risk_agent.calculate_risk_score(company_symbol, forensic_result)

                # Display results
                print("\n🎯 RISK ASSESSMENT RESULTS:")
                print(f"   Company: {risk_assessment.company_symbol}")
                print(f"   Overall Risk Score: {risk_assessment.overall_risk_score}/100")
                print(f"   Risk Level: {risk_assessment.risk_level}")

                # Check if this is a high-risk stock
                if risk_assessment.overall_risk_score > 50:
                    risky_stocks_found.append({
                        'symbol': company_symbol,
                        'risk_score': risk_assessment.overall_risk_score,
                        'risk_level': risk_assessment.risk_level,
                        'key_factors': risk_assessment.risk_factors[:3]
                    })

                print("\n📈 CATEGORY BREAKDOWN:")
                for category, risk_score in risk_assessment.risk_category_scores.items():
                    print(f"   {category.value}: {risk_score.score}/100")

                    if risk_score.factors:
                        print(f"     Factors: {', '.join(risk_score.factors[:2])}")

                print("\n🔍 KEY RISK FACTORS:")
                for factor in risk_assessment.risk_factors[:5]:
                    print(f"   • {factor}")

                # Generate report
                report = risk_agent.generate_risk_report(risk_assessment)
                print(f"\n📋 Report generated for {company_symbol}")

                print(f"❌ Error analyzing {company_symbol}: {e}")
                continue

        # Show summary of risky stocks found
        print(f"\n{'='*70}")
        print("🚨 HIGH-RISK STOCKS SUMMARY")
        print(f"{'='*70}")

        if risky_stocks_found:
            print(f"\n🎯 Found {len(risky_stocks_found)} high-risk stocks:")
            for stock in sorted(risky_stocks_found, key=lambda x: x['risk_score'], reverse=True):
                print(f"\n🔴 {stock['symbol']}:")
                print(f"   Risk Score: {stock['risk_score']}/100")
                print(f"   Risk Level: {stock['risk_level']}")
                print(f"   Key Factors: {', '.join(stock['key_factors'])}")

            # Show the MOST risky stock
            most_risky = max(risky_stocks_found, key=lambda x: x['risk_score'])
            print(f"\n🏆 MOST RISKY STOCK: {most_risky['symbol']}")
            print(f"   Risk Score: {most_risky['risk_score']}/100")
            print(f"   Risk Level: {most_risky['risk_level']}")
            print(f"   Recommendation: {most_risky['key_factors']}")
        else:
            print("\n❌ No highly risky stocks found in the test set")
            print("💡 Try these known high-risk stocks:")
            print("   - YESBANK.BO (Banking crisis)")
            print("   - IDEA.NS (Massive telecom debt)")
            print("   - SUZLON.BO (Wind energy volatility)")

        return len(risky_stocks_found) > 0

    if __name__ == "__main__":
        success = test_high_risk_stocks()
        if success:
            print("\n🎉 HIGH-RISK STOCK ANALYSIS COMPLETED!")
            print("✅ Successfully identified risky stocks with anomalies")
            print("✅ Real-time anomaly detection working")
            print("✅ Investment recommendations generated")
        else:
            print("\n❌ No high-risk stocks found in analysis")
            sys.exit(1)

except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Install required packages: pip install yfinance")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
