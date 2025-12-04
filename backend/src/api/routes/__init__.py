from .auth import router as auth_router
from .companies import router as companies_router
from .forensic import (
    ingestion_router as forensic_ingestion_router,
    forensic_router,
    risk_router,
    companies_router as forensic_companies_router
)
from .realtime import router as realtime_router
from .reports import reports_router
from .qa import router as qa_router

__all__ = [
    "auth_router",
    "companies_router",
    "forensic_ingestion_router",
    "forensic_router",
    "risk_router",
    "forensic_companies_router",
    "realtime_router",
    "reports_router",
    "qa_router",
]





