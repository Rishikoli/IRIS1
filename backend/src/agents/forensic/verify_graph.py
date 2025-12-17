import sys
import os
import logging

# Add backend root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.abspath(os.path.join(current_dir, "../../../../backend"))
sys.path.insert(0, backend_root)

from src.agents.forensic.graph_analyzer import GraphAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_graph_analysis():
    logger.info("Starting Graph Analysis Verification...")
    
    analyzer = GraphAnalyzer()
    
    # 1. Generate Mock Network
    logger.info("Generating mock network for 'HIGHRISK'...")
    graph_data = analyzer.generate_mock_network("HIGHRISK")
    
    node_count = len(graph_data["nodes"])
    edge_count = len(graph_data["links"])
    logger.info(f"Generated graph with {node_count} nodes and {edge_count} edges")
    
    if node_count == 0 or edge_count == 0:
        logger.error("FAILED: Graph is empty")
        return False

    # 2. Detect Circular Trading
    logger.info("Detecting circular trading loops...")
    cycles = analyzer.detect_circular_trading(graph_data)
    
    logger.info(f"Found {len(cycles)} cycles: {cycles}")
    
    # We expect at least one cycle involving HIGHRISK and Shells
    if len(cycles) > 0:
        logger.info("SUCCESS: Circular trading detected!")
        return True
    else:
        logger.error("FAILED: No circular trading detected (expected at least one)")
        return False

if __name__ == "__main__":
    success = verify_graph_analysis()
    sys.exit(0 if success else 1)
