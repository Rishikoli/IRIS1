import sys
import os
import asyncio
import logging
import traceback

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.forensic.agent9_network_analysis import NetworkAnalysisAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reproduce_error():
    print("Reproducing Network 500 Error...")
    
    agent = NetworkAnalysisAgent()
    company_symbol = "RELIANCE.NS"
    
    try:
        print(f"Calling build_rpt_network for {company_symbol}...")
        result = await agent.build_rpt_network(company_symbol)
        
        if result.get('success'):
            print("SUCCESS: Network built successfully.")
        else:
            print(f"FAILURE: Network build failed. Error: {result.get('error')}")
            
    except Exception as e:
        print(f"EXCEPTION CAUGHT: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(reproduce_error())
