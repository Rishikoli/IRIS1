from src.agents.forensic.agent10_auditor import AuditorAgent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_auditor():
    agent = AuditorAgent()
    print("Starting Auditor Agent Test for TCS...")
    
    result = agent.analyze_annual_report("TCS")
    
    print("\n--- Analysis Result ---")
    print(result)

if __name__ == "__main__":
    test_auditor()
