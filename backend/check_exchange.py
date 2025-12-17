from src.agents.forensic.agent11_exchange import ExchangeAgent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_exchange():
    agent = ExchangeAgent()
    print("Starting Exchange Agent Test for RELIANCE...")
    
    result = agent.get_shareholding_pattern("RELIANCE")
    
    print("\n--- Shareholding Pattern ---")
    print(result)

if __name__ == "__main__":
    test_exchange()
