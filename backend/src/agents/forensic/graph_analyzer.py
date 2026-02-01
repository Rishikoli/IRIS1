"""
Project IRIS - Forensic Graph Analyzer
Detects shell companies, circular trading, and high-risk network patterns.
"""

import networkx as nx
import logging
from typing import Dict, List, Any, Set
import random

logger = logging.getLogger(__name__)

class GraphAnalyzer:
    def __init__(self):
        logger.info("GraphAnalyzer initialized")

    def generate_network(self, company_symbol: str) -> Dict[str, Any]:
        """
        Generates a network graph for a specific company.
        Attempts to fetch real major shareholders to build the graph.
        Falls back to a minimal graph if no data found.
        """
        try:
            import yfinance as yf
            
            # Handle symbol format for Indian stocks
            symbol = company_symbol
            if not (symbol.endswith(".NS") or symbol.endswith(".BO")):
                symbol = f"{company_symbol}.NS"
            
            logger.info(f"Fetching network data for {symbol}...")
            ticker = yf.Ticker(symbol)
            
            G = nx.DiGraph()
            center_node = company_symbol
            
            # Add center node
            # Determine risk score based on some basic info or default
            risk_score = 50.0 
            try:
                info = ticker.info
                if info and 'auditRisk' in info:
                    risk_score = info['auditRisk']
            except:
                pass
                
            G.add_node(center_node, type="company", risk_score=risk_score, label=center_node)
            
            data_found = False
            
            # 1. Institutional Holders
            try:
                inst_holders = ticker.institutional_holders
                if inst_holders is not None and not inst_holders.empty:
                    data_found = True
                    for index, row in inst_holders.iterrows():
                        holder = row.get('Holder', 'Unknown Inst')
                        shares = row.get('Shares', 0)
                        
                        G.add_node(holder, type="institution", risk_score=10.0, label=holder)
                        G.add_edge(holder, center_node, amount=shares, type="investment")
            except Exception as e:
                logger.warning(f"Could not fetch institutional holders: {e}")

            # 2. Mutual Fund Holders
            try:
                mf_holders = ticker.mutualfund_holders
                if mf_holders is not None and not mf_holders.empty:
                    data_found = True
                    for index, row in mf_holders.iterrows():
                        holder = row.get('Holder', 'Unknown MF')
                        shares = row.get('Shares', 0)
                        
                        G.add_node(holder, type="fund", risk_score=5.0, label=holder)
                        G.add_edge(holder, center_node, amount=shares, type="investment")
            except Exception as e:
                logger.warning(f"Could not fetch mutual fund holders: {e}")
            
            if not data_found:
                logger.info("No real network data found, checking basic info...")
                # If no holders found, try to just add sector/industry nodes from info
                try:
                    info = ticker.info
                    sector = info.get('sector')
                    industry = info.get('industry')
                    
                    if sector:
                        G.add_node(sector, type="sector", risk_score=20.0, label=sector)
                        G.add_edge(center_node, sector, type="belongs_to")
                    if industry:
                        G.add_node(industry, type="industry", risk_score=20.0, label=industry)
                        G.add_edge(center_node, industry, type="belongs_to")
                        
                    data_found = True
                except:
                    pass

            if not data_found:
                 # Fallback to a simple node if absolutely nothing found, but DO NOT show fake shell companies
                logger.warning("Absolutely no data found for graph, returning single node.")
            
            return self._graph_to_json(G)

        except Exception as e:
            logger.error(f"Error generating real network: {e}")
            # Fallback to minimal graph on error
            G = nx.DiGraph()
            G.add_node(company_symbol, type="company", label=company_symbol)
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
