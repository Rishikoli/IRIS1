"""
Project IRIS - FastAPI Main Application
Financial Forensics Analysis Platform
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.config import settings
from src.api.routes import companies, forensic, auth_router
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(companies.router)
app.include_router(forensic.router)
app.include_router(auth_router)

# Ensure tables exist on startup
@app.on_event("startup")
def on_startup():
    create_tables()

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )
