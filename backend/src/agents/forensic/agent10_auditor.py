import logging
import os
import requests
import json
from typing import Dict, Any, List, Optional
from duckduckgo_search import DDGS

import google.generativeai as genai
from PyPDF2 import PdfReader
from io import BytesIO
from src.config import settings
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuditorAgent:
    """Agent 10: The Auditor - Analyzes Annual Report PDFs for RPTs"""

    def __init__(self):
        self._initialize_gemini()

    def _initialize_gemini(self):
        """Initialize Gemini model"""
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.error("GEMINI_API_KEY not found")
                return
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("Gemini model initialized for Auditor Agent")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")

    def analyze_annual_report(self, company_symbol: str) -> Dict[str, Any]:
        """
        Orchestrates the process: Search -> Download -> Analyze
        """
        try:
            company_name = company_symbol.split('.')[0] # Simple cleanup
            
            # 1. Search for PDF
            pdf_url = self._search_annual_report_url(company_name)
            if not pdf_url:
                return {"status": "error", "message": "Annual Report PDF not found"}
            
            # 2. Download PDF
            logger.info(f"Downloading Annual Report from: {pdf_url}")
            pdf_content = self._download_pdf(pdf_url)
            if not pdf_content:
                return {"status": "error", "message": "Failed to download PDF"}
            
            # 3. Extract Text (First 50 pages + Search for 'Related Party')
            # Full PDF might be too large, so we'll be smart about extraction
            text_content = self._extract_relevant_text(pdf_content)
            
            # 4. Analyze with Gemini
            analysis_result = self._analyze_text_with_gemini(text_content, company_name)
            
            return {
                "status": "success",
                "source_url": pdf_url,
                "analysis": analysis_result
            }

        except Exception as e:
            logger.error(f"Auditor analysis failed: {e}")
            return {"status": "error", "message": str(e)}

    def _search_annual_report_url(self, company_name: str) -> Optional[str]:
        """Search DuckDuckGo for the latest Annual Report PDF"""
        try:
            # 0. Check Hardcoded Fallbacks (for demo reliability)
            HARDCODED_PDF_URLS = {
                "RELIANCE": "https://www.ril.com/ar2023-24/pdf/Reliance-Integrated-Annual-Report-2023-24.pdf",
                "TCS": "https://www.tcs.com/content/dam/tcs/investor-relations/financial-statements/2023-24/ar/annual-report-2023-2024.pdf",
                "HDFCBANK": "https://www.hdfcbank.com/content/api/contentstream-id/723fb80a-2dde-42a3-9793-7ae1be57c87f/056c986e-657c-45fb-a4c6-2638c2f03561/Investor/Investor%20Relations/Financial%20Information/Annual%20Reports/2023-2024/Annual_Report_2023_24.pdf"
            }
            
            # Check if company name matches any key
            for key, url in HARDCODED_PDF_URLS.items():
                if key in company_name.upper():
                    logger.info(f"Using hardcoded PDF URL for {key}")
                    return url

            # Try a more specific query
            query = f"{company_name} Integrated Annual Report 2023-24 pdf"
            logger.info(f"Searching for: {query}")
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=10))
            
            potential_landing_pages = []
            
            for r in results:
                url = r['href']
                logger.info(f"Found URL: {url}")
                
                # 1. Direct PDF link
                if url.lower().endswith('.pdf'):
                    return url
                
                # 2. Store potential landing pages (official sites)
                if 'bseindia' not in url and 'moneycontrol' not in url:
                    # Prioritize Investor Relations pages
                    if 'investor' in url.lower() or 'report' in url.lower():
                        potential_landing_pages.insert(0, url)
                    else:
                        potential_landing_pages.append(url)
            
            # If no direct PDF, try scraping landing pages
            logger.info("No direct PDF found. Scraping landing pages...")
            for page_url in potential_landing_pages[:5]: # Check top 5
                pdf_link = self._find_pdf_on_page(page_url)
                if pdf_link:
                    logger.info(f"Found PDF on landing page {page_url}: {pdf_link}")
                    return pdf_link

            # Fallback Search
            query = f"{company_name} Annual Report 2023 pdf"
            logger.info(f"Fallback searching for: {query}")
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                
            for r in results:
                url = r['href']
                if url.lower().endswith('.pdf'):
                    return url
                    
            return None
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return None

    def _find_pdf_on_page(self, url: str) -> Optional[str]:
        """Scrape a webpage to find Annual Report PDF links"""
        try:
            from bs4 import BeautifulSoup
            from urllib.parse import urljoin
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for links containing "Annual Report" and ending in .pdf
            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.text.lower()
                full_url = urljoin(url, href)
                
                if full_url.lower().endswith('.pdf'):
                    # Check if text suggests it's the right report
                    if 'annual report' in text or 'integrated report' in text or '2024' in text or '2023' in text:
                        return full_url
                        
            return None
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
            return None

    def _download_pdf(self, url: str) -> Optional[BytesIO]:
        """Download PDF content to memory"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/pdf,application/octet-stream,*/*'
            }
            logger.info(f"Requesting URL: {url}")
            response = requests.get(url, headers=headers, timeout=30, verify=False, allow_redirects=True)
            
            logger.info(f"Download Status: {response.status_code}")
            logger.info(f"Content-Type: {response.headers.get('Content-Type')}")
            
            if response.status_code == 200:
                if 'application/pdf' in response.headers.get('Content-Type', '').lower() or url.lower().endswith('.pdf'):
                    return BytesIO(response.content)
                else:
                    logger.warning("Content-Type is not PDF, but status is 200. Trying to parse anyway...")
                    return BytesIO(response.content)
            
            logger.error(f"Download failed with status {response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None

    def _extract_relevant_text(self, pdf_file: BytesIO) -> str:
        """Extract text relevant to RPTs from the PDF"""
        try:
            reader = PdfReader(pdf_file)
            total_pages = len(reader.pages)
            extracted_text = ""
            
            logger.info(f"PDF has {total_pages} pages. Scanning for RPT keywords...")
            
            # Strategy:
            # 1. Read Table of Contents (first 10 pages)
            # 2. Search for "Related Party" in the whole doc (or sampled)
            # For efficiency, we'll scan pages containing "Related Party"
            
            rpt_pages = []
            
            for i in range(total_pages):
                # Simple heuristic: Check every page? Too slow for 400 pages.
                # Let's check first 20, then scan for keywords
                if i < 20: 
                    text = reader.pages[i].extract_text()
                    extracted_text += text + "\n"
                    continue
                
                # For remaining pages, we might need a faster way or just skip for MVP
                # Reading 400 pages with PyPDF2 is actually reasonably fast for text extraction
                # Let's try reading all but limit total characters to context window
                
                try:
                    text = reader.pages[i].extract_text()
                    if "related party" in text.lower() or "related parties" in text.lower():
                        extracted_text += f"\n--- Page {i+1} ---\n" + text
                except:
                    pass
                    
                # Limit to ~50k characters to fit in context window comfortably
                if len(extracted_text) > 100000:
                    break
            
            return extracted_text
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return ""

    def _analyze_text_with_gemini(self, text: str, company: str) -> Dict[str, Any]:
        """Analyze extracted text for RPTs"""
        import time
        max_retries = 3
        retry_delay = 10
        
        for attempt in range(max_retries):
            try:
                prompt = f"""
                You are a forensic auditor. I have extracted text from the Annual Report of '{company}'.
                Your job is to find the "Related Party Transactions" (RPT) disclosures.
                
                Extracted Text:
                {text[:50000]}... (truncated)
                
                Task:
                1. Identify the names of Related Parties (Subsidiaries, Associates, Key Management Personnel).
                2. Identify specific transactions (Loans, Guarantees, Sales, Purchases) with these parties.
                3. Flag any suspicious or high-value transactions.
                
                Return JSON format ONLY:
                {{
                    "related_parties": [
                        {{"name": "Entity Name", "relationship": "Subsidiary/Associate/Director", "risk_score": 10-100}}
                    ],
                    "transactions": [
                        {{"source": "{company}", "target": "Entity Name", "type": "Loan/Sale/etc", "amount": "Value if found", "is_suspicious": boolean, "reason": "Why?"}}
                    ]
                }}
                """
                
                response = self.model.generate_content(prompt)
                text_resp = response.text.strip()
                
                # Clean markdown
                if text_resp.startswith("```json"):
                    text_resp = text_resp[7:-3]
                elif text_resp.startswith("```"):
                    text_resp = text_resp[3:-3]
                    
                return json.loads(text_resp)
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    logger.warning(f"Rate limit hit, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"Gemini analysis failed: {e}")
                    if attempt == max_retries - 1:
                         return {"related_parties": [], "transactions": [], "error": "Rate Limit Exceeded"}
        
        return {"related_parties": [], "transactions": []}
