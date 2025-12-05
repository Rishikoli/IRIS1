"""
Project IRIS - FastAPI Main Application
Financial Forensics Analysis Platform
"""
import sys
import os

# Add backend root directory to Python path
# This file is at: backend/src/api/main.py
# We need to add: backend/ to the path
current_file = os.path.abspath(__file__)
api_dir = os.path.dirname(current_file)  # backend/src/api
src_dir = os.path.dirname(api_dir)  # backend/src
backend_root = os.path.dirname(src_dir)  # backend

# Insert at the beginning to prioritize our modules
sys.path.insert(0, backend_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.config import settings
from src.api.routes import companies, forensic, auth, realtime, reports, qa, sentiment, connectors
from src.models import create_tables

# Configure logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
if settings.log_format == 'json':
    # For JSON logging, use a simple format for now
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=log_format
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="IRIS Forensic Analysis API",
    description="Financial forensics platform for Indian companies",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
# Allow common local dev origins explicitly and also via regex
app.add_middleware(
    CORSMiddleware,
    allow_origins=(settings.cors_origins_list + [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:45505",
        "http://127.0.0.1:45505",
    ]),
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(companies.router)
app.include_router(forensic.ingestion_router)
app.include_router(forensic.forensic_router)
app.include_router(forensic.risk_router)
app.include_router(forensic.companies_router)
app.include_router(auth.router)
app.include_router(realtime.router)
app.include_router(reports.reports_router)
app.include_router(qa.router, prefix="/api/v1/qa", tags=["qa"])
app.include_router(sentiment.router, prefix="/api/v1/sentiment", tags=["sentiment"])
app.include_router(connectors.router, prefix="/api/v1/connectors", tags=["connectors"])

# Ensure tables exist on startup (but don't fail if DB is unavailable)
@app.on_event("startup")
def on_startup():
    try:
        create_tables()
        logger.info("Database tables verified/created successfully")
    except Exception as e:
        logger.warning(f"Database connection failed during startup: {e}")
        logger.warning("API will start without database connectivity - some endpoints may not work")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "module": "forensic",
        "version": "1.0.0",
        "environment": settings.environment
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Project IRIS - Financial Forensics Analysis Platform",
        "docs": "/docs",
        "health": "/health"
    }

# Companies list endpoint for CLI
@app.get("/api/companies")
async def list_companies():
    """List companies available for analysis"""
    try:
        # For now, return a list of commonly analyzed Indian companies
        companies = [
            {"symbol": "RELIANCE.BO", "name": "Reliance Industries Limited", "sector": "Conglomerate"},
            {"symbol": "TCS.BO", "name": "Tata Consultancy Services Limited", "sector": "IT Services"},
            {"symbol": "HDFCBANK.BO", "name": "HDFC Bank Limited", "sector": "Banking"},
            {"symbol": "ICICIBANK.BO", "name": "ICICI Bank Limited", "sector": "Banking"},
            {"symbol": "INFY.BO", "name": "Infosys Limited", "sector": "IT Services"},
            {"symbol": "HINDUNILVR.BO", "name": "Hindustan Unilever Limited", "sector": "Consumer Goods"},
            {"symbol": "ITC.BO", "name": "ITC Limited", "sector": "Consumer Goods"},
            {"symbol": "KOTAKBANK.BO", "name": "Kotak Mahindra Bank Limited", "sector": "Banking"},
            {"symbol": "LT.BO", "name": "Larsen & Toubro Limited", "sector": "Engineering"},
            {"symbol": "AXISBANK.BO", "name": "Axis Bank Limited", "sector": "Banking"}
        ]

        return {
            "success": True,
            "companies": companies,
            "count": len(companies)
        }

    except Exception as e:
        logger.error(f"Error listing companies: {e}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )
