import asyncio
import time
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.forensic.agent9_network_analysis import NetworkAnalysisAgent

async def test_network_performance():
    agent = NetworkAnalysisAgent()
    symbol = "RELIANCE.NS"
    
    print(f"Starting network analysis for {symbol}...")
    start_time = time.time()
    
    result = await agent.build_rpt_network(symbol)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Analysis completed in {duration:.2f} seconds")
    print(f"Success: {result.get('success')}")
    
    if result.get('success'):
        print(f"Nodes: {len(result['graph_data']['nodes'])}")
        print(f"Edges: {len(result['graph_data']['edges'])}")
        print(f"Subsidiaries found: {len(result['gemini_data'].get('subsidiaries', []))}")
    else:
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_network_performance())
