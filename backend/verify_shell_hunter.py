
import asyncio
import sys
import os
import json

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.agents.forensic.agent_shell_hunter import ShellHunterAgent

async def test_shell_hunter():
    print("--- 🕵️ Testing Shell Hunter Agent ---")
    agent = ShellHunterAgent()
    
    # Analyze a dummy target
    result = agent.analyze_network("TARGET_LTD")
    
    # 1. Verify Nodes & Edges
    node_count = len(result["graph_data"]["nodes"])
    edge_count = len(result["graph_data"]["edges"])
    print(f"Graph Generated: {node_count} nodes, {edge_count} edges")
    
    if node_count < 5:
        print("FAIL: Graph too small")
        return

    # 2. Verify Cycle Detection
    cycles = result["detected_cycles"]
    print(f"Cycles Detected: {len(cycles)}")
    if len(cycles) > 0:
        print(f"Cycle Found: {cycles[0]}")
    else:
        print("FAIL: No Cycle Detected")

    # 3. Verify Director Interlocking
    hidden_directors = result["hidden_directors"]
    print(f"Hidden Directors Detected: {len(hidden_directors)}")
    if hidden_directors:
        print(f"Suspect: {hidden_directors[0]}")
        
    # 4. JSON Serialization Check
    try:
        json_output = json.dumps(result)
        print("JSON Serialization: PASS")
    except Exception as e:
        print(f"JSON Serialization FAIL: {e}")

if __name__ == "__main__":
    asyncio.run(test_shell_hunter())
