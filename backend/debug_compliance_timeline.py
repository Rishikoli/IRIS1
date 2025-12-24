
import sys
import os
from datetime import datetime

# Mock setups
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.agents.forensic.agent4_compliance import ComplianceValidationAgent, ComplianceAssessment

def debug_timeline():
    agent = ComplianceValidationAgent()
    
    # Mock Financial Data (Similar to what Agent 2 passes)
    financial_data = {
        "financial_ratios": {
            "financial_ratios": {
                "2024-03-31": {"current_ratio": 1.5},
                "2023-12-31": {"current_ratio": 1.2},
                "2023-09-30": {"current_ratio": 1.1}
            }
        }
    }
    
    # Generate History
    print("--- Testing with Ratio Dates ---")
    history = agent._generate_audit_history("COMPLIANT", financial_data)
    for event in history:
        print(f"{event['date']}: {event['title']} ({event['type']})")
        
    # Test Fallback
    print("\n--- Testing Fallback (No Data) ---")
    history_fallback = agent._generate_audit_history("COMPLIANT", {})
    for event in history_fallback:
        print(f"{event['date']}: {event['title']} ({event['type']})")

if __name__ == "__main__":
    debug_timeline()
