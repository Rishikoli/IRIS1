import asyncio
import logging
from src.agents.forensic.agent5_reporting import ReportingAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_report_generation():
    agent = ReportingAgent()
    
    # Mock analysis data
    analysis_data = {
        "forensic_analysis": {
            "financial_ratios": {
                "financial_ratios": {
                    "2024-03-31": {
                        "net_margin_pct": 12.5,
                        "roe": 18.2,
                        "current_ratio": 1.8,
                        "debt_to_equity": 0.5,
                        "total_revenue": 100000,
                        "net_profit": 12500
                    }
                },
                "success": True
            },
            "vertical_analysis": {"success": True, "vertical_analysis": {}},
            "horizontal_analysis": {"success": True, "horizontal_analysis": {}},
            "beneish_m_score": {"success": True, "beneish_m_score": {"m_score": -2.5, "is_likely_manipulator": False}},
            "altman_z_score": {"success": True, "altman_z_score": {"z_score": 3.5, "classification": "Safe", "risk_level": "LOW"}},
            "benford_analysis": {"success": True, "benford_analysis": {"overall_score": 95}}
        },
        "risk_assessment": {
            "overall_risk_score": 25,
            "risk_level": "LOW",
            "investment_recommendation": "BUY",
            "risk_factors": ["Market Volatility"],
            "monitoring_frequency": "QUARTERLY"
        },
        "compliance_assessment": {
            "overall_compliance_score": 90,
            "compliance_status": "COMPLIANT",
            "violations": [],
            "framework_scores": {"GAAP": 95, "IFRS": 90},
            "next_review_date": "2025-01-01"
        },
        "anomaly_detection": {
            "success": True,
            "anomalies": []
        }
    }

    print("Generating report for TEST_CORP...")
    result = await agent.generate_comprehensive_report("TEST_CORP", analysis_data)
    
    if result["success"]:
        print("\nReport Generation Successful!")
        print(f"Report ID: {result['comprehensive_report']['report_id']}")
        
        # Check executive summary
        if "executive_summary" in result["comprehensive_report"]:
            summary = result["comprehensive_report"]["executive_summary"]
            print("\nExecutive Summary:")
            print(f"Text Length: {len(summary.get('summary_text', ''))}")
            print(f"Text Preview: {summary.get('summary_text', '')[:100]}...")
        else:
            print("\nWARNING: Executive Summary is MISSING in the report data!")
            
        # Check exports
        exports = result["comprehensive_report"]["exports"]
        print("\nExports:")
        for fmt, info in exports.items():
            print(f"- {fmt}: {info['export_info']['filepath']} (Size: {info['export_info']['file_size']} bytes)")
    else:
        print(f"\nReport Generation Failed: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_report_generation())
