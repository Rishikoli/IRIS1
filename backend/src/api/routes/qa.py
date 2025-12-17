"""
Q&A API Routes for IRIS Financial Analysis Platform
Provides endpoints for natural language Q&A using RAG system
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

from src.agents.agent7_qa_rag import answer_financial_question, index_company_for_qa, get_qa_system_status

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["Q&A System"])

class QuestionRequest(BaseModel):
    """Request model for Q&A queries"""
    query: str = Field(..., description="Natural language question about financial analysis")
    company_symbol: Optional[str] = Field(None, description="Company symbol for context (e.g., RELIANCE.NS)")
    max_context: int = Field(default=5, description="Maximum number of context documents to use")


class IndexRequest(BaseModel):
    """Request model for indexing company data"""
    company_symbol: str = Field(..., description="Company symbol to index")
    company_data: Dict[str, Any] = Field(..., description="Company financial data to index")


class QASystemStatus(BaseModel):
    """Response model for Q&A system status"""
    total_documents: int
    collection_name: str
    embedding_model: str
    status: str


@router.post("/ask", response_model=Dict[str, Any])
async def ask_question(request: QuestionRequest) -> Dict[str, Any]:
    """
    Answer financial questions using RAG system with Gemini AI

    This endpoint provides natural language Q&A capabilities for financial analysis,
    using retrieval-augmented generation with ChromaDB vector storage.
    """
    try:
        logger.info(f"Q&A request: {request.query[:50]}... for {request.company_symbol or 'general'}")

        # Validate query
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # Answer the question
        result = await answer_financial_question(
            query=request.query.strip(),
            company_symbol=request.company_symbol
        )

        if result.get("success"):
            logger.info(f"Question answered successfully: {request.query[:50]}...")
            return {
                "success": True,
                "answer": result["answer"],
                "confidence": result.get("confidence", "Medium"),
                "context_used": result.get("context_used", 0),
                "sources": result.get("sources", []),
                "company_symbol": request.company_symbol,
                "timestamp": result.get("timestamp"),
                "sentiment": result.get("sentiment")
            }
        else:
            logger.error(f"Q&A failed: {result.get('error', 'Unknown error')}")
            return {
                "success": False,
                "error": result.get("error", "Failed to answer question"),
                "answer": result.get("answer", "I apologize, but I couldn't answer your question at this time."),
                "confidence": "Low"
            }

    except Exception as e:
        logger.error(f"Q&A API error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/index", response_model=Dict[str, Any])
async def index_company_data(request: IndexRequest) -> Dict[str, Any]:
    """
    Index company financial data for future Q&A queries

    This endpoint processes and stores company financial data in the vector database
    for use in future Q&A interactions.
    """
    try:
        logger.info(f"Indexing request for company: {request.company_symbol}")

        # Validate request
        if not request.company_symbol.strip():
            raise HTTPException(status_code=400, detail="Company symbol cannot be empty")

        if not request.company_data:
            raise HTTPException(status_code=400, detail="Company data cannot be empty")

        # Index the company data
        success = index_company_for_qa(request.company_symbol, request.company_data)

        if success:
            logger.info(f"Successfully indexed data for {request.company_symbol}")
            return {
                "success": True,
                "message": f"Successfully indexed financial data for {request.company_symbol}",
                "company_symbol": request.company_symbol,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"Failed to index data for {request.company_symbol}")
            return {
                "success": False,
                "error": f"Failed to index data for {request.company_symbol}",
                "company_symbol": request.company_symbol
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Index API error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/status", response_model=QASystemStatus)
async def get_qa_status() -> QASystemStatus:
    """
    Get Q&A system status and statistics

    Returns information about the vector database collection and system health.
    """
    try:
        stats = get_qa_system_status()

        if "error" in stats:
            raise HTTPException(status_code=500, detail=f"Q&A system error: {stats['error']}")

        return QASystemStatus(
            total_documents=stats["total_documents"],
            collection_name=stats["collection_name"],
            embedding_model=stats["embedding_model"],
            status=stats["status"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status API error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch-index", response_model=Dict[str, Any])
async def batch_index_companies(companies_data: List[IndexRequest]) -> Dict[str, Any]:
    """
    Index multiple companies' data in batch

    Useful for bulk data indexing operations.
    """
    try:
        results = []

        for company_request in companies_data:
            try:
                result = await index_company_data(company_request)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch index failed for {company_request.company_symbol}: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "company_symbol": company_request.company_symbol
                })

        successful = sum(1 for r in results if r.get("success"))
        total = len(results)

        return {
            "success": successful > 0,
            "results": results,
            "summary": f"Successfully indexed {successful}/{total} companies",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Batch index API error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health", response_model=Dict[str, Any])
async def qa_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for Q&A system

    Returns basic health status and system information.
    """
    try:
        stats = get_qa_system_status()

        return {
            "status": "healthy",
            "service": "Q&A RAG System (Agent 7)",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "total_documents": stats.get("total_documents", 0),
            "system_info": {
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "vector_database": "ChromaDB",
                "ai_model": "Gemini 2.0 Flash"
            }
        }

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
