from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging
from src.agents.forensic.graph_analyzer import GraphAnalyzer

router = APIRouter(prefix="/api/forensic/graph", tags=["forensic-graph"])
logger = logging.getLogger(__name__)

# Initialize analyzer
graph_analyzer = GraphAnalyzer()

@router.get("/{company_symbol}")
async def get_forensic_graph(company_symbol: str):
    """
    Generate a forensic network graph for a specific company.
    Includes shell company detection and circular trading flags.
    """
    try:
        logger.info(f"Generating forensic graph for {company_symbol}")
        
        # Generate the graph data
        graph_data = graph_analyzer.generate_mock_network(company_symbol)
        
        # Run analysis algorithms
        cycles = graph_analyzer.detect_circular_trading(graph_data)
        
        # Add analysis metadata
        response = {
            "company_symbol": company_symbol,
            "graph_data": graph_data,
            "analysis": {
                "circular_trading_loops": cycles,
                "shell_company_count": sum(1 for n in graph_data["nodes"] if n["data"].get("isShell")),
                "risk_flags": len(cycles) + sum(1 for n in graph_data["nodes"] if n["data"].get("isShell"))
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))
