

import logging
import json
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from datetime import datetime
import asyncio

from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent
from src.database.connection import get_db_client

logger = logging.getLogger(__name__)

class ConnectionManager:
    """WebSocket connection manager for handling multiple connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "analysis": [],
            "market_data": [],
            "notifications": []
        }
    
    async def connect(self, websocket: WebSocket, connection_type: str):
        """Connect a new WebSocket"""
        await websocket.accept()
        if connection_type in self.active_connections:
            self.active_connections[connection_type].append(websocket)
        logger.info(f"New {connection_type} connection. Total: {len(self.active_connections[connection_type])}")
    
    def disconnect(self, websocket: WebSocket, connection_type: str):
        """Disconnect a WebSocket"""
        if connection_type in self.active_connections:
            self.active_connections[connection_type].remove(websocket)
        logger.info(f"{connection_type} connection disconnected")
    
    async def broadcast(self, message: Dict[str, Any], connection_type: str):
        """Broadcast message to all connections of a type"""
        if connection_type in self.active_connections:
            disconnected = []
            for connection in self.active_connections[connection_type]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            # Remove dead connections
            for conn in disconnected:
                self.active_connections[connection_type].remove(conn)
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")

# Global connection manager
manager = ConnectionManager()

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
    await manager.connect(websocket, "analysis")
    
    try:
        # Verify company exists
        db_client = get_db_client()
        company_check = db_client.execute_query(
            "SELECT cin FROM companies WHERE cin = :company_id",
            {"company_id": company_id}
        )

        if not company_check:
            await manager.send_personal_message({
                "error": f"Company {company_id} not found",
                "success": False
            }, websocket)
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
            await manager.send_personal_message({
                "error": f"No financial statements found for company {company_id}",
                "success": False
            }, websocket)
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

        # Run real-time analysis
        async for result in forensic_agent.run_realtime_analysis(company_id, statements):
            await manager.send_personal_message(result, websocket)

        # Send final completion message
        await manager.send_personal_message({
            "type": "analysis_complete",
            "message": "Real-time forensic analysis completed",
            "timestamp": datetime.now().isoformat()
        }, websocket)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for company {company_id}")
    except Exception as e:
        logger.error(f"Real-time analysis error for {company_id}: {e}")
        try:
            await manager.send_personal_message({
                "error": f"Analysis failed: {str(e)}",
                "success": False,
                "timestamp": datetime.now().isoformat()
            }, websocket)
        except Exception as e:
            logger.error(f"Failed to send error message to WebSocket: {e}")
    finally:
        manager.disconnect(websocket, "analysis")
        try:
            await websocket.close()
        except Exception as e:
            logger.warning(f"Failed to close WebSocket gracefully: {e}")

@router.websocket("/market-data/{symbol}")
async def realtime_market_data(websocket: WebSocket, symbol: str):
    """Real-time market data streaming via WebSocket"""
    await manager.connect(websocket, "market_data")
    
    try:
        logger.info(f"Starting market data stream for {symbol}")
        
        # Send initial market data
        initial_data = {
            "type": "market_data",
            "symbol": symbol,
            "price": 0.0,
            "change": 0.0,
            "change_percent": 0.0,
            "volume": 0,
            "timestamp": datetime.now().isoformat(),
            "status": "connected"
        }
        
        await manager.send_personal_message(initial_data, websocket)
        
        # Simulate real-time market data updates
        # In production, this would connect to actual market data feeds
        for i in range(10):  # Send 10 updates as demo
            await asyncio.sleep(2)  # Update every 2 seconds
            
            market_update = {
                "type": "market_data",
                "symbol": symbol,
                "price": 100.0 + (i * 0.5),
                "change": i * 0.5,
                "change_percent": (i * 0.5) / 100.0 * 100,
                "volume": 1000000 + (i * 10000),
                "timestamp": datetime.now().isoformat(),
                "update_id": i + 1
            }
            
            await manager.send_personal_message(market_update, websocket)
        
        # Send completion message
        await manager.send_personal_message({
            "type": "stream_complete",
            "message": "Market data stream completed",
            "symbol": symbol,
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
    except WebSocketDisconnect:
        logger.info(f"Market data WebSocket disconnected for {symbol}")
    except Exception as e:
        logger.error(f"Market data stream error for {symbol}: {e}")
        try:
            await manager.send_personal_message({
                "error": f"Market data stream failed: {str(e)}",
                "success": False,
                "timestamp": datetime.now().isoformat()
            }, websocket)
        except Exception as e:
            logger.error(f"Failed to send market data error message: {e}")
    finally:
        manager.disconnect(websocket, "market_data")
        try:
            await websocket.close()
        except Exception as e:
            logger.warning(f"Failed to close market data WebSocket: {e}")


@router.websocket("/notifications")
async def system_notifications(websocket: WebSocket):
    """System notifications and alerts via WebSocket"""
    await manager.connect(websocket, "notifications")
    
    try:
        logger.info("Client connected to system notifications")
        
        # Send welcome message
        await manager.send_personal_message({
            "type": "notification",
            "message": "Connected to IRIS system notifications",
            "level": "info",
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        # Keep connection alive and send periodic status updates
        for i in range(5):  # Send 5 status updates
            await asyncio.sleep(10)  # Every 10 seconds
            
            notification = {
                "type": "notification",
                "message": f"System status check {i + 1}",
                "level": "info",
                "system_health": "healthy",
                "active_connections": len(manager.active_connections["notifications"]),
                "timestamp": datetime.now().isoformat()
            }
            
            await manager.send_personal_message(notification, websocket)
        
    except WebSocketDisconnect:
        logger.info("System notifications WebSocket disconnected")
    except Exception as e:
        logger.error(f"System notifications error: {e}")
    finally:
        manager.disconnect(websocket, "notifications")
        try:
            await websocket.close()
        except Exception as e:
            logger.warning(f"Failed to close notifications WebSocket: {e}")


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


@router.post("/broadcast/notification")
async def broadcast_notification(notification: Dict[str, Any]):
    """Broadcast notification to all connected notification clients"""
    try:
        message = {
            "type": "notification",
            "message": notification.get("message", "System notification"),
            "level": notification.get("level", "info"),
            "timestamp": datetime.now().isoformat(),
            **notification
        }
        
        await manager.broadcast(message, "notifications")
        
        return {
            "success": True,
            "message": "Notification broadcasted",
            "recipients": len(manager.active_connections["notifications"]),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to broadcast notification: {e}")
        return {"success": False, "error": str(e)}


@router.get("/connections/status")
async def get_connection_status():
    """Get current WebSocket connection status"""
    return {
        "active_connections": {
            "analysis": len(manager.active_connections["analysis"]),
            "market_data": len(manager.active_connections["market_data"]),
            "notifications": len(manager.active_connections["notifications"])
        },
        "total_connections": sum(
            len(connections) for connections in manager.active_connections.values()
        ),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/market-data/{symbol}/status")
async def get_market_data_status(symbol: str):
    """Get market data availability status"""
    return {
        "symbol": symbol,
        "status": "available",
        "data_sources": ["yahoo_finance", "alpha_vantage"],
        "update_frequency": "real-time",
        "supported_features": [
            "price_updates",
            "volume_data",
            "technical_indicators",
            "market_sentiment"
        ]
    }
