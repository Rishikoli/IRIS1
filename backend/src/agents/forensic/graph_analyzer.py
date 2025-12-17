"""
Project IRIS - Forensic Graph Analyzer
Detects shell companies, circular trading, and high-risk network patterns.
"""

import networkx as nx
import logging
from typing import Dict, List, Any, Set
from faker import Faker
import random

logger = logging.getLogger(__name__)

class GraphAnalyzer:
    def __init__(self):
        self.fake = Faker()
        logger.info("GraphAnalyzer initialized")

    def generate_mock_network(self, center_node: str = "HIGHRISK") -> Dict[str, Any]:
        """
        Generates a realistic "Web of Lies" network centered around a target company.
        Includes planted circular trading loops and shell companies.
        """
        G = nx.DiGraph()
        
        # 1. Create the center node
        G.add_node(center_node, type="company", risk_score=78.5, label=center_node)

        # 2. Create a ring of shell companies (Circular Trading Loop)
        # HIGHRISK -> Shell A -> Shell B -> Shell C -> HIGHRISK
        shells = ["Shell Corp A", "Shell Corp B", "Shell Corp C"]
        
        # Add shell nodes with high risk flags
        for shell in shells:
            G.add_node(shell, type="company", risk_score=90.0, label=shell, is_shell=True)

        # Create the loop
        G.add_edge(center_node, shells[0], amount=5000000, type="transfer")
        G.add_edge(shells[0], shells[1], amount=4800000, type="transfer")
        G.add_edge(shells[1], shells[2], amount=4750000, type="transfer")
        G.add_edge(shells[2], center_node, amount=4600000, type="transfer")

        # 3. Add some "Ghost Directors" (Hubs)
        director = "John Doe (Director)"
        G.add_node(director, type="person", risk_score=60.0, label=director)
        
        # Connect director to multiple shells
        G.add_edge(director, center_node, type="director")
        G.add_edge(director, shells[0], type="director")
        G.add_edge(director, shells[2], type="director")

        # 4. Add some normal noise (Legit suppliers)
        for i in range(3):
            supplier = self.fake.company()
            G.add_node(supplier, type="company", risk_score=10.0, label=supplier)
            G.add_edge(supplier, center_node, amount=random.randint(10000, 50000), type="invoice")

        return self._graph_to_json(G)

    def detect_circular_trading(self, graph_data: Dict[str, Any]) -> List[List[str]]:
        """
        Detects cycles in the graph (Circular Trading).
        Returns a list of cycles (list of node IDs).
        """
        G = nx.node_link_graph(graph_data)
        try:
            cycles = list(nx.simple_cycles(G))
            # Filter for cycles of length > 2 to avoid simple A<->B trades if needed
            meaningful_cycles = [c for c in cycles if len(c) > 2]
            return meaningful_cycles
        except Exception as e:
            logger.error(f"Cycle detection failed: {e}")
            return []

    def _graph_to_json(self, G: nx.DiGraph) -> Dict[str, Any]:
        """Convert NetworkX graph to JSON format for frontend (React Flow)"""
        nodes = []
        edges = []

        for node_id, attrs in G.nodes(data=True):
            nodes.append({
                "id": node_id,
                "data": {
                    "label": attrs.get("label", node_id),
                    "riskScore": attrs.get("risk_score", 0),
                    "type": attrs.get("type", "company"),
                    "isShell": attrs.get("is_shell", False)
                },
                # Random positions for now, frontend will layout or we can use nx.spring_layout
                "position": {"x": random.randint(0, 500), "y": random.randint(0, 500)}
            })

        for u, v, attrs in G.edges(data=True):
            edges.append({
                "id": f"e-{u}-{v}",
                "source": u,
                "target": v,
                "data": {
                    "amount": attrs.get("amount", 0),
                    "type": attrs.get("type", "relationship")
                },
                "animated": True if attrs.get("type") == "transfer" else False
            })

        return {"nodes": nodes, "links": edges}
