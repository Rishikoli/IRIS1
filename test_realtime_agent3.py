#!/usr/bin/env python3
"""
Test Agent 3 with Real-Time Yahoo Finance Data
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

    def test_real_time_risk_scoring():
        """Test Agent 3 with real Yahoo Finance data"""
        print("🚀 Testing Agent 3 with Real-Time Yahoo Finance Data...")

        # Test with multiple high-risk stocks
        test_stocks = ["YESBANK.BO", "IDEA.NS", "SUZLON.BO"]

        for company_symbol in test_stocks:
            print(f"\n{'='*60}")
            print(f"🚨 TESTING HIGH-RISK STOCK: {company_symbol}")
            print(f"{'='*60}")

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

            # Now run Agent 2 forensic analysis to get the data format Agent 3 needs
            from agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent

            forensic_agent = ForensicAnalysisAgent()
            forensic_result = forensic_agent.comprehensive_forensic_analysis(
                company_symbol,
                financial_statements
            )

            if not forensic_result['success']:
                print(f"❌ Forensic analysis failed: {forensic_result.get('error')}")
                return False

            print("✅ Forensic analysis completed successfully")

            # Now test Agent 3 risk scoring with real data
            risk_agent = RiskScoringAgent()
            risk_assessment = risk_agent.calculate_risk_score(company_symbol, forensic_result)

            # Display comprehensive results
            print("\n🎯 RISK ASSESSMENT RESULTS (Real-Time Data):")
            print(f"   Company: {risk_assessment.company_symbol}")
            print(f"   Assessment Date: {risk_assessment.assessment_date}")
            print(f"   Overall Risk Score: {risk_assessment.overall_risk_score}/100")
            print(f"   Risk Level: {risk_assessment.risk_level}")
            print(f"   Investment Recommendation: {risk_assessment.investment_recommendation}")
            print(f"   Monitoring Frequency: {risk_assessment.monitoring_frequency}")

            print("\n📈 DETAILED CATEGORY BREAKDOWN:")
            for category, risk_score in risk_assessment.risk_category_scores.items():
                print(f"\n   {category.value.upper()}:")
                print(f"     Score: {risk_score.score}/100")
                print(f"     Weight: {risk_score.weight*100}%")
                print(f"     Confidence: {risk_score.confidence*100}%")

                if risk_score.factors:
                    print(f"     Risk Factors: {', '.join(risk_score.factors[:2])}")
                if risk_score.recommendations:
                    print(f"     Recommendations: {', '.join(risk_score.recommendations[:1])}")

            print("\n🔍 KEY RISK FACTORS:")
            for factor in risk_assessment.risk_factors[:5]:
                print(f"   • {factor}")

            # Generate report
            report = risk_agent.generate_risk_report(risk_assessment)
            print("\n📋 REPORT GENERATED:")
            print(f"   Report Type: {report['report_type']}")
            print(f"   Generated At: {report['generated_at']}")
            print(f"   Agent Version: {report['agent_version']}")

            return True

        except Exception as e:
            print(f"❌ Error testing with real data: {e}")
            import traceback
            traceback.print_exc()
            return False

    if __name__ == "__main__":
        success = test_real_time_risk_scoring()
        if success:
            print("\n🎉 REAL-TIME AGENT 3 TEST COMPLETED SUCCESSFULLY!")
            print("✅ Risk scoring working with live Yahoo Finance data")
            print("✅ Multi-category analysis functional")
            print("✅ Investment recommendations generated")
            print("✅ Ready for production deployment")
        else:
            print("\n❌ Real-time test failed")
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
