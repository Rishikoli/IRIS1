"""
Project IRIS - Real-time Forensic Analysis API Routes
WebSocket endpoints for real-time forensic analysis streaming
"""

import logging
import json
from typing import Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from datetime import datetime

from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent
from src.database.connection import get_db_client

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/realtime",
    tags=["realtime"],
    responses={404: {"description": "Not found"}}
)

# Initialize agents
forensic_agent = ForensicAnalysisAgent()

@router.websocket("/analysis/{company_id}")
async def realtime_forensic_analysis(websocket: WebSocket, company_id: str):
    """Real-time forensic analysis via WebSocket"""
    await websocket.accept()

    try:
        # Verify company exists
        db_client = get_db_client()
        company_check = db_client.execute_query(
            "SELECT cin FROM companies WHERE cin = :company_id",
            {"company_id": company_id}
        )

        if not company_check:
            await websocket.send_text(json.dumps({
                "error": f"Company {company_id} not found",
                "success": False
            }))
            await websocket.close()
            return

        # Get financial statements for the company
        financial_statements = db_client.execute_query(
            """
            SELECT statement_type, period_end, data
            FROM financial_statements
            WHERE company_id = :company_id
            ORDER BY period_end DESC
            LIMIT 10
            """,
            {"company_id": company_id}
        )

        if not financial_statements:
            await websocket.send_text(json.dumps({
                "error": f"No financial statements found for company {company_id}",
                "success": False
            }))
            await websocket.close()
            return

        # Convert database results to expected format
        statements = []
        for stmt in financial_statements:
            statements.append({
                "statement_type": stmt["statement_type"],
                "period_end": stmt["period_end"].isoformat() if stmt["period_end"] else None,
                "data": stmt["data"] if stmt["data"] else {}
            })

        logger.info(f"Starting real-time analysis for {company_id} with {len(statements)} statements")

        # Define progress callback
        async def progress_callback(progress_data: Dict[str, Any]):
            try:
                await websocket.send_text(json.dumps(progress_data))
            except WebSocketDisconnect:
                raise
            except Exception as e:
                logger.error(f"Error sending progress: {e}")

        # Run real-time analysis
        async for result in forensic_agent.run_realtime_analysis(company_id, statements):
            await websocket.send_text(json.dumps(result))

        # Send final completion message
        await websocket.send_text(json.dumps({
            "type": "analysis_complete",
            "message": "Real-time forensic analysis completed",
            "timestamp": datetime.now().isoformat()
        }))

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for company {company_id}")
    except Exception as e:
        logger.error(f"Real-time analysis error for {company_id}: {e}")
        try:
            await websocket.send_text(json.dumps({
                "error": f"Analysis failed: {str(e)}",
                "success": False,
                "timestamp": datetime.now().isoformat()
            }))
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass

@router.get("/analysis/{company_id}/status")
async def get_analysis_status(company_id: str):
    """Get current analysis status (for polling fallback)"""
    return {
        "company_id": company_id,
        "status": "ready",
        "message": "Ready for real-time analysis",
        "supported_features": [
            "vertical_analysis",
            "horizontal_analysis",
            "financial_ratios",
            "benford_law",
            "altman_z_score",
            "beneish_m_score",
            "anomaly_detection"
        ]
    }
