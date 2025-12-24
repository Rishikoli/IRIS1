
import sys
import os
import asyncio
import logging
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Mock Environment Variables
os.environ["FMP_API_KEY"] = "dummy"
os.environ["GEMINI_API_KEY"] = "dummy" 
os.environ["SUPABASE_URL"] = "https://dummy.supabase.co"
os.environ["SUPABASE_KEY"] = "dummy"
os.environ["SUPABASE_DB_PASSWORD"] = "dummy"

# Add backend and src to path
sys.path.append(os.path.abspath('backend'))
sys.path.append(os.path.abspath('backend/src'))

try:
    from src.agents.forensic.agent3_risk_scoring import RiskScoringAgent
    from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent
    from src.agents.forensic.agent11_report_generator import ReportGeneratorAgent
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

async def verify_report_generation():
    print("--- Testing Investigative Report Generation ---")
    
    agent3 = RiskScoringAgent()
    forensic = ForensicAnalysisAgent()
    generator = ReportGeneratorAgent()
    
    symbol = "RELIANCE.NS"
    print(f"1. Fetching data for {symbol}...")
    
    data = forensic.analyze_yahoo_finance_data(symbol, quarters=1)
    
    if not data.get("success"):
        print("Failed to fetch forensic data. Using mock data for report testing.")
        # Create a mock assessment dict structure if data fetch fails
        # This ensures we verify PDF generation even if external APIs flake
        assessment_data = {
            "company_symbol": symbol,
            "overall_risk_score": 45.5,
            "risk_level": "MEDIUM",
            "investment_recommendation": "CAUTION - Moderate risk",
            "category_breakdown": {
                "financial_stability": {"score": 30.0, "factors": ["Solid net margin", "High debt"]},
                "market_risk": {"score": 25.0, "factors": ["Negative sentiment detected: 'investigation'", "Low volatility"]},
                "compliance_risk": {"score": 20.0, "factors": ["Minor reporting delay"]},
                "operational_risk": {"score": 50.0, "factors": ["Declining asset turnover"]}
            }
        }
    else:
        print("2. Calculating Risk Score...")
        assessment_obj = agent3.calculate_risk_score(symbol, data)
        # Convert object to dict for report generator
        # Note: ReportGenerator expects a dict, matching format of generate_risk_report output
        assessment_data = agent3.generate_risk_report(assessment_obj)
    
    print("3. Generating PDF...")
    pdf_bytes = generator.generate_report(symbol, assessment_data)
    
    if pdf_bytes:
        filename = f"backend/investigative_report_{symbol}.pdf"
        with open(filename, "wb") as f:
            f.write(pdf_bytes)
        print(f"✅ SUCCESS: PDF generated successfully at '{filename}' ({len(pdf_bytes)} bytes).")
    else:
        print("❌ FAILURE: PDF generation returned None.")
        # Check for reportlab
        try:
            import reportlab
            print(f"ReportLab is installed: {reportlab.__version__}")
        except ImportError:
            print("⚠️ ReportLab is NOT installed. Verification expected to fail.")

if __name__ == "__main__":
    asyncio.run(verify_report_generation())
