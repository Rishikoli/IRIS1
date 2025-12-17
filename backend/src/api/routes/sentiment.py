from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from src.agents.agent8_market_sentiment import market_sentiment_agent
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class SentimentRequest(BaseModel):
    company_symbol: str

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_sentiment(request: SentimentRequest):
    """
    Analyze market sentiment for a company using Google Trends and News
    """
    try:
        logger.info(f"Sentiment analysis request for: {request.company_symbol}")
        
        if not request.company_symbol.strip():
            raise HTTPException(status_code=400, detail="Company symbol cannot be empty")

        result = market_sentiment_agent.get_sentiment_analysis(request.company_symbol)
        
        if "error" in result:
             logger.error(f"Sentiment analysis failed: {result['error']}")
             # Return partial success or error depending on severity
             # For now, return what we have, frontend handles errors
        
        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        logger.error(f"Error in sentiment endpoint: {str(e)}")
        # Return a safe fallback instead of 500 to prevent frontend crash
        return {
            "success": False,
            "data": {
                "company": request.company_symbol,
                "error": str(e),
                "overall_sentiment": "Neutral",
                "trends": {"status": "error", "data": []},
                "news_sentiment": {"status": "error", "sentiment": "neutral"}
            }
        }
