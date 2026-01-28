"""
Data Collection Module for FinBERT Fine-tuning

This module contains web scrapers and data collectors for gathering
Indian market-specific financial text data from various sources.
"""

from .scrape_sebi import SEBIScraper
from .scrape_bse_nse import BSENSEScraper
from .scrape_news import FinancialNewsScraper
from .process_pdfs import PDFProcessor

__all__ = [
    'SEBIScraper',
    'BSENSEScraper', 
    'FinancialNewsScraper',
    'PDFProcessor'
]
