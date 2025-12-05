from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from typing import Dict, Any
import shutil
import os
import tempfile
from src.agents.agent7_qa_rag import qa_system

router = APIRouter(prefix="/api/connectors", tags=["connectors"])

@router.post("/ingest/pdf")
async def ingest_pdf(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Ingest a PDF file into the RAG system.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
        
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name
        
    try:
        result = qa_system.ingest_from_connector('pdf', temp_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/ingest/web")
async def ingest_web(url: str = Body(..., embed=True)) -> Dict[str, Any]:
    """
    Ingest a web page into the RAG system.
    """
    try:
        result = qa_system.ingest_from_connector('web', url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
