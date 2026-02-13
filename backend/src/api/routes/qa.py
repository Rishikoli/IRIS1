"""
Q&A API Routes for IRIS Financial Analysis Platform
Provides endpoints for natural language Q&A using RAG system
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
import os
import shutil

from src.config import settings
from src.agents.agent7_qa_rag import answer_financial_question, index_company_for_qa, get_qa_system_status, qa_system
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["Q&A System"])

@router.post("/upload", response_model=Dict[str, Any])
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """
    Upload and ingest a PDF document into the Knowledge Base
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Ensure upload directory exists
        upload_dir = settings.pdf_folder
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file to disk
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"File saved to {file_path}")

        # Ingest content
        result = qa_system.ingest_from_connector('pdf', file_path)
        
        if result.get("success"):
            return {
                "success": True,
                "message": f"Successfully ingested {file.filename}",
                "documents_added": result.get("documents_ingested", 0),
                "file_path": file_path
            }
        else:
            # Clean up if ingestion failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Ingestion failed: {result.get('error')}")

    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=Dict[str, Any])
async def list_knowledge_base() -> Dict[str, Any]:
    """
    List all documents currently in the Knowledge Base
    """
    try:
        # We need to access the collection directly to get metadata
        if not qa_system.collection:
            return {"documents": [], "total": 0}
            
        # Get all metadata
        # ChromaDB doesn't have a "SELECT DISTINCT" so we fetch all metadata
        # For a local file setup (<100k docs), this is acceptable
        results = qa_system.collection.get(include=['metadatas'])
        
        sources = {}
        
        for m in results['metadatas']:
            if not m: continue
            
            # Identify source
            source_id = m.get('source', 'Unknown')
            if 'company' in m:
                source_id = f"Analysis: {m['company']}"
                doc_type = 'analysis'
            else:
                doc_type = m.get('type', 'document')

            if source_id not in sources:
                sources[source_id] = {
                    "source": source_id,
                    "type": doc_type,
                    "chunk_count": 0,
                    "created_at": datetime.now().isoformat() # Placeholder as Chroma doesn't store timestamps by default
                }
            sources[source_id]['chunk_count'] += 1

        return {
            "documents": list(sources.values()),
            "total_chunks": len(results['ids'])
        }

    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{source_id}", response_model=Dict[str, Any])
async def delete_document(source_id: str) -> Dict[str, Any]:
    """
    Delete a document from the Knowledge Base by source ID
    """
    try:
        if not qa_system.collection:
             raise HTTPException(status_code=500, detail="Database not initialized")

        # Delete where metadata['source'] == source_id
        # OR where 'company' == source_id (for analysis)
        
        # Handle "Analysis: Ticker" format
        target = source_id
        if source_id.startswith("Analysis: "):
            target = source_id.replace("Analysis: ", "")
            qa_system.collection.delete(where={"company": target})
        else:
            qa_system.collection.delete(where={"source": target})
            
        return {"success": True, "message": f"Deleted documents for {source_id}"}

    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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

        # Answer the question using RAG first
        result = await answer_financial_question(
            query=request.query.strip(),
            company_symbol=request.company_symbol
        )

        # If RAG could not answer (e.g., no context), fall back to Gemini direct query
        if not result.get("success"):
            logger.info("RAG fallback: attempting direct Gemini query for question.")
            try:
                # Configure Gemini (already configured in settings)
                genai.configure(api_key=settings.gemini_api_key)
                fallback_model = genai.GenerativeModel(
                    model_name=settings.gemini_model_name,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2,
                        max_output_tokens=1024,
                        top_p=0.9,
                        top_k=40,
                    ),
                )
                fallback_prompt = (
                    f"Answer the following financial question using up‑to‑date public information. "
                    f"If the answer requires recent market data, provide the best estimate.\n\nQuestion: {request.query}"
                )
                response = fallback_model.generate_content(fallback_prompt)
                answer_text = response.text.strip() if response and response.text else "No answer generated."
                return {
                    "success": True,
                    "answer": answer_text,
                    "confidence": "Medium",
                    "context_used": 0,
                    "sources": [],
                    "company_symbol": request.company_symbol,
                    "timestamp": datetime.now().isoformat(),
                    "sentiment": {},
                }
            except Exception as e_fallback:
                logger.error(f"Gemini fallback failed: {e_fallback}")
                return {
                    "success": False,
                    "error": f"Both RAG and Gemini fallback failed: {str(e_fallback)}",
                    "answer": "I could not retrieve an answer.",
                    "confidence": "Low",
                }
        # Original success path
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
                "sentiment": result.get("sentiment"),
            }
        else:
            logger.error(f"Q&A failed: {result.get('error', 'Unknown error')}")
            return {
                "success": False,
                "error": result.get("error", "Failed to answer question"),
                "answer": result.get("answer", "I apologize, but I couldn't answer your question at this time."),
                "confidence": "Low",
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
