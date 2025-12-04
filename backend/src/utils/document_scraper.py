"""
Project IRIS - Document Scraper
Web scraping utilities for disclosure documents from NSE/BSE
"""

import logging
import os
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from pathlib import Path
import time
import hashlib

from src.api_clients import NSEClient, BSEClient
from src.utils.ocr_processor import OCRProcessor
from src.config import settings

logger = logging.getLogger(__name__)


class DocumentScraper:
    """Scraper for corporate disclosure documents"""
    
    def __init__(self):
        self.nse_client = NSEClient()
        self.bse_client = BSEClient()
        self.ocr_processor = OCRProcessor()
        
        # Create directories if they don't exist
        self.pdf_folder = Path(settings.pdf_folder)
        self.pdf_folder.mkdir(parents=True, exist_ok=True)
        
        self.upload_folder = Path(settings.upload_folder)
        self.upload_folder.mkdir(parents=True, exist_ok=True)
    
    def fetch_disclosure_documents(self, symbol: str, exchange: str = "nse", 
                                 days_back: int = 365) -> List[Dict[str, Any]]:
        """Fetch disclosure documents for a company"""
        try:
            logger.info(f"Fetching disclosure documents for {symbol} from {exchange}")
            
            documents = []
            
            if exchange.lower() == "nse":
                documents.extend(self._fetch_nse_documents(symbol, days_back))
            elif exchange.lower() == "bse":
                documents.extend(self._fetch_bse_documents(symbol, days_back))
            else:
                # Fetch from both exchanges
                documents.extend(self._fetch_nse_documents(symbol, days_back))
                documents.extend(self._fetch_bse_documents(symbol, days_back))
            
            logger.info(f"Found {len(documents)} disclosure documents for {symbol}")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to fetch disclosure documents for {symbol}: {e}")
            return []
    
    def _fetch_nse_documents(self, symbol: str, days_back: int) -> List[Dict[str, Any]]:
        """Fetch documents from NSE"""
        try:
            from_date = datetime.now() - timedelta(days=days_back)
            to_date = datetime.now()
            
            documents = []
            
            # Get corporate announcements
            announcements = self.nse_client.get_corporate_announcements(symbol, from_date, to_date)
            for announcement in announcements:
                if announcement.get("attachment"):
                    documents.append({
                        "symbol": symbol,
                        "exchange": "NSE",
                        "document_type": "announcement",
                        "title": announcement.get("subject", ""),
                        "date": announcement.get("announcement_date", ""),
                        "url": announcement.get("attachment", ""),
                        "source_data": announcement
                    })
            
            # Get financial results
            financial_results = self.nse_client.get_financial_results(symbol)
            for result in financial_results:
                if result.get("attachment"):
                    documents.append({
                        "symbol": symbol,
                        "exchange": "NSE",
                        "document_type": "financial_result",
                        "title": f"Financial Result - {result.get('period', '')} {result.get('year_ending', '')}",
                        "date": result.get("result_date", ""),
                        "url": result.get("attachment", ""),
                        "source_data": result
                    })
            
            # Get shareholding patterns
            shareholding = self.nse_client.get_shareholding_pattern(symbol)
            for pattern in shareholding:
                if pattern.get("attachment"):
                    documents.append({
                        "symbol": symbol,
                        "exchange": "NSE",
                        "document_type": "shareholding_pattern",
                        "title": f"Shareholding Pattern - {pattern.get('period', '')}",
                        "date": pattern.get("year_ending", ""),
                        "url": pattern.get("attachment", ""),
                        "source_data": pattern
                    })
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to fetch NSE documents for {symbol}: {e}")
            return []
    
    def _fetch_bse_documents(self, scrip_code: str, days_back: int) -> List[Dict[str, Any]]:
        """Fetch documents from BSE"""
        try:
            from_date = datetime.now() - timedelta(days=days_back)
            to_date = datetime.now()
            
            documents = []
            
            # Get corporate announcements
            announcements = self.bse_client.get_corporate_announcements(scrip_code, from_date, to_date)
            for announcement in announcements:
                if announcement.get("attachment"):
                    documents.append({
                        "symbol": scrip_code,
                        "exchange": "BSE",
                        "document_type": "announcement",
                        "title": announcement.get("subject", ""),
                        "date": announcement.get("date", ""),
                        "url": announcement.get("attachment", ""),
                        "source_data": announcement
                    })
            
            # Get financial results
            financial_results = self.bse_client.get_financial_results(scrip_code)
            for result in financial_results:
                if result.get("attachment"):
                    documents.append({
                        "symbol": scrip_code,
                        "exchange": "BSE",
                        "document_type": "financial_result",
                        "title": f"Financial Result - {result.get('period', '')} {result.get('year', '')}",
                        "date": result.get("result_date", ""),
                        "url": result.get("attachment", ""),
                        "source_data": result
                    })
            
            # Get shareholding patterns
            shareholding = self.bse_client.get_shareholding_pattern(scrip_code)
            for pattern in shareholding:
                if pattern.get("attachment"):
                    documents.append({
                        "symbol": scrip_code,
                        "exchange": "BSE",
                        "document_type": "shareholding_pattern",
                        "title": f"Shareholding Pattern - {pattern.get('quarter', '')} {pattern.get('year', '')}",
                        "date": pattern.get("submission_date", ""),
                        "url": pattern.get("attachment", ""),
                        "source_data": pattern
                    })
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to fetch BSE documents for {scrip_code}: {e}")
            return []
    
    def download_document(self, document_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Download a document and return file information"""
        try:
            url = document_info.get("url", "")
            if not url:
                logger.warning("No URL provided for document download")
                return None
            
            symbol = document_info.get("symbol", "unknown")
            doc_type = document_info.get("document_type", "document")
            exchange = document_info.get("exchange", "unknown")
            
            logger.info(f"Downloading document: {url}")
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f"{exchange}_{symbol}_{doc_type}_{timestamp}_{url_hash}.pdf"
            filepath = self.pdf_folder / filename
            
            # Download file
            response = requests.get(url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Save file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Get file info
            file_size = filepath.stat().st_size
            
            logger.info(f"Downloaded document: {filepath} ({file_size} bytes)")
            
            return {
                "success": True,
                "filepath": str(filepath),
                "filename": filename,
                "file_size": file_size,
                "download_date": datetime.now().isoformat(),
                "source_url": url,
                "document_info": document_info
            }
            
        except Exception as e:
            logger.error(f"Failed to download document {url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "source_url": url,
                "document_info": document_info
            }
    
    def process_downloaded_document(self, download_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process downloaded document with OCR"""
        try:
            if not download_result.get("success"):
                return download_result
            
            filepath = download_result.get("filepath")
            if not filepath or not os.path.exists(filepath):
                return {
                    "success": False,
                    "error": "File not found",
                    "filepath": filepath
                }
            
            logger.info(f"Processing document with OCR: {filepath}")
            
            # Extract text using OCR
            ocr_result = self.ocr_processor.extract_text_from_pdf(filepath)
            
            # If it's an annual report, do additional processing
            document_info = download_result.get("document_info", {})
            doc_type = document_info.get("document_type", "")
            
            if "annual" in doc_type.lower() or "result" in doc_type.lower():
                annual_report_result = self.ocr_processor.process_annual_report(filepath)
                if annual_report_result.get("success"):
                    ocr_result.update(annual_report_result)
            
            # Combine results
            result = {
                **download_result,
                "ocr_result": ocr_result,
                "processing_date": datetime.now().isoformat()
            }
            
            if ocr_result.get("success"):
                result["text_extracted"] = True
                result["extracted_text"] = ocr_result.get("text", "")
                result["extraction_method"] = ocr_result.get("method", "unknown")
            else:
                result["text_extracted"] = False
                result["extraction_error"] = ocr_result.get("error", "Unknown error")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process document: {e}")
            return {
                **download_result,
                "processing_error": str(e),
                "text_extracted": False
            }
    
    def parse_annual_report_sections(self, extracted_text: str) -> Dict[str, Any]:
        """Parse annual report into structured sections"""
        try:
            logger.info("Parsing annual report sections")
            
            sections = {}
            
            # Management Discussion & Analysis
            mda_section = self._extract_section(
                extracted_text, 
                ["management discussion", "md&a", "management analysis"],
                max_length=5000
            )
            if mda_section:
                sections["management_discussion_analysis"] = mda_section
            
            # Auditor's Report
            auditor_section = self._extract_section(
                extracted_text,
                ["auditor report", "independent auditor", "audit report"],
                max_length=3000
            )
            if auditor_section:
                sections["auditor_report"] = auditor_section
            
            # Financial Highlights
            highlights_section = self._extract_section(
                extracted_text,
                ["financial highlights", "key financial", "performance highlights"],
                max_length=2000
            )
            if highlights_section:
                sections["financial_highlights"] = highlights_section
            
            # Risk Factors
            risk_section = self._extract_section(
                extracted_text,
                ["risk factors", "risks and concerns", "risk management"],
                max_length=3000
            )
            if risk_section:
                sections["risk_factors"] = risk_section
            
            # Corporate Governance
            governance_section = self._extract_section(
                extracted_text,
                ["corporate governance", "governance report", "board of directors"],
                max_length=2000
            )
            if governance_section:
                sections["corporate_governance"] = governance_section
            
            return {
                "success": True,
                "sections": sections,
                "sections_found": len(sections)
            }
            
        except Exception as e:
            logger.error(f"Failed to parse annual report sections: {e}")
            return {
                "success": False,
                "error": str(e),
                "sections": {}
            }
    
    def _extract_section(self, text: str, keywords: List[str], max_length: int = 2000) -> Optional[str]:
        """Extract a specific section from text based on keywords"""
        try:
            import re
            
            text_lower = text.lower()
            
            for keyword in keywords:
                # Find the keyword in text
                pattern = re.escape(keyword.lower())
                match = re.search(pattern, text_lower)
                
                if match:
                    start_pos = match.start()
                    
                    # Find the actual position in original text
                    original_start = start_pos
                    
                    # Extract section (next max_length characters)
                    end_pos = min(original_start + max_length, len(text))
                    section_text = text[original_start:end_pos]
                    
                    # Clean up the section
                    section_text = section_text.strip()
                    
                    if len(section_text) > 100:  # Minimum length check
                        return section_text
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract section with keywords {keywords}: {e}")
            return None
    
    def get_comprehensive_documents(self, symbol: str, exchange: str = "both", 
                                  days_back: int = 365, download_and_process: bool = True) -> Dict[str, Any]:
        """Get comprehensive document analysis for a company"""
        try:
            logger.info(f"Getting comprehensive documents for {symbol}")
            
            # Fetch document list
            documents = self.fetch_disclosure_documents(symbol, exchange, days_back)
            
            if not documents:
                return {
                    "symbol": symbol,
                    "documents_found": 0,
                    "documents": [],
                    "processed_documents": []
                }
            
            processed_documents = []
            
            if download_and_process:
                # Download and process documents (limit to prevent overload)
                max_documents = 10
                for i, doc in enumerate(documents[:max_documents]):
                    try:
                        logger.info(f"Processing document {i+1}/{min(len(documents), max_documents)}")
                        
                        # Download document
                        download_result = self.download_document(doc)
                        
                        if download_result and download_result.get("success"):
                            # Process with OCR
                            processed_result = self.process_downloaded_document(download_result)
                            processed_documents.append(processed_result)
                            
                            # Rate limiting
                            time.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"Failed to process document {i+1}: {e}")
                        continue
            
            return {
                "symbol": symbol,
                "exchange": exchange,
                "documents_found": len(documents),
                "documents": documents,
                "processed_documents": processed_documents,
                "processing_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive documents for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": str(e),
                "documents_found": 0,
                "documents": [],
                "processed_documents": []
            }
