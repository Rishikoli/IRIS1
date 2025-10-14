#!/usr/bin/env python3
import sys, os
sys.path.append('/home/aditya/I.R.I.S./backend/src')
sys.path.append('/home/aditya/I.R.I.S./backend')

os.environ['GEMINI_API_KEY'] = 'test_key'
os.environ['SUPABASE_URL'] = 'test_url'
os.environ['SUPABASE_KEY'] = 'test_key'
os.environ['FMP_API_KEY'] = 'test_key'
os.environ['SUPABASE_DB_PASSWORD'] = 'test_password'

import yfinance as yf
from agents.forensic.agent3_risk_scoring import RiskScoringAgent
from agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent

# Test YESBANK.BO - known to be highly risky
company_symbol = "YESBANK.BO"

ticker = yf.Ticker(company_symbol)
financials = ticker.financials
balance_sheet = ticker.balance_sheet

financial_statements = []
for i in range(min(3, len(financials.columns))):
    stmt_data = financials.iloc[:, i].to_dict()
    stmt_data['date'] = str(financials.columns[i].date())
    financial_statements.append({
        'statement_type': 'income_statement',
        'period_end': str(financials.columns[i].date()),
        'data': stmt_data
    })

for i in range(min(3, len(balance_sheet.columns))):
    stmt_data = balance_sheet.iloc[:, i].to_dict()
    stmt_data['date'] = str(balance_sheet.columns[i].date())
    financial_statements.append({
        'statement_type': 'balance_sheet',
        'period_end': str(balance_sheet.columns[i].date()),
        'data': stmt_data
    })

forensic_agent = ForensicAnalysisAgent()
forensic_result = forensic_agent.comprehensive_forensic_analysis(company_symbol, financial_statements)

risk_agent = RiskScoringAgent()
risk_assessment = risk_agent.calculate_risk_score(company_symbol, forensic_result)

    print(f"🎯 {company_symbol} RISK ANALYSIS:")
    print(f"Overall Risk Score: {risk_assessment.overall_risk_score}/100")
    print(f"Risk Level: {risk_assessment.risk_level}")

    if risk_assessment.overall_risk_score > 60:
        print(f"\n🚨 HIGHLY RISKY STOCK DETECTED!")
        print(f"Investment Recommendation: {risk_assessment.investment_recommendation}")
        print(f"\nKey Risk Factors:")
        for factor in risk_assessment.risk_factors:
            print(f"• {factor}")
    else:
        print("❌ This stock is not highly risky")
        print("💡 Try these known high-risk stocks:")
        print("   - YESBANK.BO (had major banking crisis)")
        print("   - SUZLON.BO (wind energy company with high volatility)")
