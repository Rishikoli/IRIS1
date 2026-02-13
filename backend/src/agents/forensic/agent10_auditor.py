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
            self.model = genai.GenerativeModel(settings.gemini_model_name)
            logger.info("Gemini model initialized for Auditor Agent")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")

    async def analyze_annual_report(self, company_symbol: str, pdf_url: Optional[str] = None, financial_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Orchestrates the process: Search -> Download -> Analyze
        If pdf_url is provided, skips search.
        financial_data can be passed to perform 'Semantic Audit' (Management Narrative vs Reality)
        """
        import asyncio
        
        try:
            company_name = company_symbol.split('.')[0] # Simple cleanup
            
            # 1. Determine PDF URL
            if not pdf_url:
                pdf_url = await asyncio.to_thread(self._search_annual_report_url, company_name)
            else:
                logger.info(f"Using provided PDF URL: {pdf_url}")

            if not pdf_url:
                return {"status": "error", "message": "Annual Report PDF not found"}
            
            # 2. Download PDF
            logger.info(f"Downloading Annual Report from: {pdf_url}")
            pdf_content = await asyncio.to_thread(self._download_pdf, pdf_url)
            if not pdf_content:
                return {"status": "error", "message": "Failed to download PDF"}
            
            # 3. Extract Text (First 50 pages + Search for 'Related Party')
            # Full PDF might be too large, so we'll be smart about extraction
            text_content = await asyncio.to_thread(self._extract_relevant_text, pdf_content)
            
            # 4. Analyze with Gemini for RPTs
            rpt_analysis = await self._analyze_text_with_gemini(text_content, company_name)
            
            # 5. Perform Semantic Audit if financial data is provided
            semantic_audit = None
            if financial_data:
                logger.info(f"Performing Semantic Audit for {company_name}...")
                semantic_audit = await self._perform_semantic_audit(text_content, financial_data, company_name)
            
            return {
                "status": "success",
                "source_url": pdf_url,
                "analysis": rpt_analysis,
                "semantic_audit": semantic_audit
            }

        except Exception as e:
            logger.error(f"Auditor analysis failed: {e}")
            return {"status": "error", "message": str(e)}

    # ... (other private methods _search, _download, _extract remain sync and are called via to_thread)

    async def _analyze_text_with_gemini(self, text: str, company: str) -> Dict[str, Any]:
        """Analyze extracted text for RPTs with caching"""
        from src.utils.gemini_client import GeminiClient
        
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
            
            # Use centralized client
            client = GeminiClient()
            text_resp = await client.generate_content(prompt)
            
            # Clean markdown
            if text_resp.startswith("```json"):
                text_resp = text_resp[7:-3]
            elif text_resp.startswith("```"):
                text_resp = text_resp[3:-3]
                
            return json.loads(text_resp)
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return {"related_parties": [], "transactions": [], "error": str(e)}
        
    async def _perform_semantic_audit(self, text: str, financials: Dict[str, Any], company: str) -> Dict[str, Any]:
        """Compare Management Narrative (MDA) against Hard Financial Numbers"""
        from src.utils.gemini_client import GeminiClient
        
        try:
            prompt = f"""
            You are a Senior Forensic Auditor. I have extracted the Management Discussion & Analysis (MDA) section from '{company}''s Annual Report.
            
            I also have the following HARD FINANCIAL DATA for the same period:
            {json.dumps(financials, indent=2)}
            
            Management Narrative (Extracted MDA):
            {text[:50000]}... (truncated)
            
            Task:
            1. Extract key claims from management about Liquidity, Debt, Growth, and Profitability.
            2. Compare these claims against the HARD FINANCIAL DATA.
            3. Identify "Narrative Disconnects" where management uses flowery or positive language to mask negative trends (e.g., claiming "improved liquidity" while Current Ratio dropped).
            4. Assign a "Governance Integrity Score" (0-100) based on how honest the narrative is.
            
            Return JSON format ONLY:
            {{
                "narrative_claims": [
                    {{"topic": "Liquidity/Debt/etc", "claim": "Exact quote or summary", "reality": "What numbers say", "is_disconnect": boolean, "severity": "Low/Medium/High"}}
                ],
                "integrity_score": 0-100,
                "summary": "Overall forensic assessment of management honesty"
            }}
            """
            
            client = GeminiClient()
            text_resp = await client.generate_content(prompt)
            
            # Clean markdown
            if text_resp.startswith("```json"):
                text_resp = text_resp[7:-3]
            elif text_resp.startswith("```"):
                text_resp = text_resp[3:-3]
                
            return json.loads(text_resp)
        except Exception as e:
            logger.error(f"Semantic Audit failed: {e}")
            return {"error": str(e), "integrity_score": 0}
