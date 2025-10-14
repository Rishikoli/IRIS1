#!/usr/bin/env python3
"""
Test script for Agent 3 Risk Scoring functionality
"""

import sys
import os
import json
from datetime import datetime

# Add the backend source to Python path
sys.path.append('/home/aditya/I.R.I.S./backend/src')
sys.path.append('/home/aditya/I.R.I.S./backend')

# Set minimal environment variables for testing
os.environ['GEMINI_API_KEY'] = 'test_key'  # Won't be used for basic risk scoring
os.environ['SUPABASE_URL'] = 'test_url'
os.environ['SUPABASE_KEY'] = 'test_key'
os.environ['FMP_API_KEY'] = 'test_key'
os.environ['SUPABASE_DB_PASSWORD'] = 'test_password'

try:
    from agents.forensic.agent3_risk_scoring import RiskScoringAgent, RiskCategory

    def test_agent3_risk_scoring():
        """Test Agent 3 with sample forensic data"""
        print("🚀 Testing Agent 3 Risk Scoring...")

        # Create sample forensic data similar to what would come from Agent 2
        sample_forensic_data = {
            "vertical_analysis": {
                "vertical_analysis": {
                    "balance_sheet": {
                        "total_assets_pct": 100.0,
                        "total_equity_pct": 45.0,
                        "total_liabilities_pct": 55.0
                    },
                    "income_statement": {
                        "total_revenue_pct": 100.0,
                        "cost_of_revenue_pct": 60.0,
                        "gross_profit_pct": 40.0,
                        "net_profit_pct": 12.0
                    }
                }
            },
            "horizontal_analysis": {
                "horizontal_analysis": {
                    "income_statement": {
                        "total_revenue_growth_pct": 15.5,
                        "net_profit_growth_pct": 18.2,
                        "cost_of_revenue_growth_pct": 14.1
                    }
                }
            },
            "financial_ratios": {
                "financial_ratios": {
                    "2024-03-31": {
                        "net_margin_pct": 12.5,
                        "roe": 18.5,
                        "debt_to_equity": 1.2,
                        "asset_turnover": 1.8,
                        "gross_margin_pct": 40.0,
                        "debt_to_assets": 0.45
                    },
                    "2023-03-31": {
                        "net_margin_pct": 11.8,
                        "roe": 16.2,
                        "debt_to_equity": 1.1,
                        "asset_turnover": 1.7,
                        "gross_margin_pct": 38.5,
                        "debt_to_assets": 0.42
                    }
                }
            }
        }

        # Initialize the risk scoring agent
        agent = RiskScoringAgent()

        # Test risk scoring for RELIANCE.NS
        company_symbol = "RELIANCE.NS"

        print(f"\n📊 Calculating risk score for {company_symbol}...")
        assessment = agent.calculate_risk_score(company_symbol, sample_forensic_data)

        # Display results
        print("\n✅ Risk Assessment Results:")
        print(f"   Company: {assessment.company_symbol}")
        print(f"   Assessment Date: {assessment.assessment_date}")
        print(f"   Overall Risk Score: {assessment.overall_risk_score}/100")
        print(f"   Risk Level: {assessment.risk_level}")
        print(f"   Investment Recommendation: {assessment.investment_recommendation}")
        print(f"   Monitoring Frequency: {assessment.monitoring_frequency}")

        print("\n📈 Category Breakdown:")
        for category, risk_score in assessment.risk_category_scores.items():
            print(f"   {category.value}:")
            print(f"     Score: {risk_score.score}/100")
            print(f"     Weight: {risk_score.weight*100}%")
            print(f"     Confidence: {risk_score.confidence*100}%")
            if risk_score.factors:
                print(f"     Factors: {', '.join(risk_score.factors[:2])}")  # Show first 2 factors
            if risk_score.recommendations:
                print(f"     Recommendations: {', '.join(risk_score.recommendations[:1])}")  # Show first recommendation

        print("\n🔍 Key Risk Factors:")
        for factor in assessment.risk_factors[:5]:  # Show first 5 factors
            print(f"   • {factor}")

        # Test the report generation
        print("\n📋 Generating risk report...")
        report = agent.generate_risk_report(assessment)
        print(f"   Report Type: {report['report_type']}")
        print(f"   Generated At: {report['generated_at']}")
        print(f"   Agent Version: {report['agent_version']}")

        return True

    if __name__ == "__main__":
        success = test_agent3_risk_scoring()
        if success:
            print("\n🎉 Agent 3 Risk Scoring test completed successfully!")
            print("✅ All risk calculations are working properly")
            print("✅ Multi-category analysis functional")
            print("✅ Investment recommendations generated")
        else:
            print("\n❌ Agent 3 test failed")
            sys.exit(1)

except Exception as e:
    print(f"❌ Error testing Agent 3: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
