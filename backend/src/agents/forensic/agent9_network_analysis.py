import logging
import networkx as nx
import yfinance as yf
from typing import Dict, Any, List
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from src.config import settings
from src.agents.forensic.agent10_auditor import AuditorAgent
from src.agents.forensic.agent11_exchange import ExchangeAgent
from src.agents.forensic.agent12_cartographer import CartographerAgent

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkAnalysisAgent:
    """Agent 9: Network Analysis & Cycle Detection"""

    def __init__(self):
        self._initialize_gemini()
        self.auditor = AuditorAgent()
        self.exchange = ExchangeAgent()
        self.cartographer = CartographerAgent()

    def _initialize_gemini(self):
        """Initialize Gemini model"""
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.error("GEMINI_API_KEY not found")
                return
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(settings.gemini_model_name)
            logger.info("Gemini model initialized for RPT analysis")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")

    async def build_rpt_network(self, company_symbol: str) -> Dict[str, Any]:
        """
        Build a network graph of the company, its directors, and related entities.
        Uses Gemini to extract real-world subsidiaries, associates, and potential risks.
        """
        try:
            import asyncio
            
            # 1. Initialize Graph
            G = nx.DiGraph()
            
            # Clean symbol
            clean_symbol = company_symbol.split('.')[0]
            
            # Add central node (The Company)
            G.add_node(clean_symbol, type="company", risk_score=0, label=clean_symbol)
            
            # 2. Run Data Gathering in Parallel
            # We need to fetch insiders first to pass to Gemini, but we can fetch insiders 
            # and run Auditor/Exchange in parallel. 
            # However, Gemini needs insiders. So we can run:
            # Group A: Fetch Insiders
            # Group B: Auditor Analysis
            # Group C: Exchange Data
            
            # Actually, let's fetch insiders first (it's fast usually), then run Gemini, Auditor, Exchange in parallel.
            # Or better: Run Insiders, Auditor, Exchange in parallel. Then run Gemini (using insiders).
            
            # Let's try to be as parallel as possible.
            # Task 1: Fetch Insiders (needed for Gemini)
            # Task 2: Auditor Analysis (Independent)
            # Task 3: Exchange Data (Independent)
            
            logger.info(f"Starting parallel data gathering for {company_symbol}")
            
            # Define wrapper for async execution
            async def get_insiders():
                return await asyncio.to_thread(self._fetch_insiders, company_symbol)
                
            async def run_auditor():
                return await asyncio.to_thread(self.auditor.analyze_annual_report, company_symbol)
                
            async def run_exchange():
                return await asyncio.to_thread(self.exchange.get_shareholding_pattern, company_symbol)

            # Start independent tasks
            # Task 4: Fetch Financial Summary (for Semantic Audit)
            async def get_financials():
                return await asyncio.to_thread(self._fetch_financial_summary, company_symbol)
            
            task_insiders = asyncio.create_task(get_insiders())
            task_auditor_standalone = asyncio.create_task(run_auditor()) # We will re-run or wait?
            # Actually, let's wait for financials then run auditor
            task_exchange = asyncio.create_task(run_exchange())
            task_financials = asyncio.create_task(get_financials())
            
            # Wait for insiders to start Gemini
            insiders = await task_insiders
            financials = await task_financials
            
            # Now start Gemini and Auditor with financials
            async def run_gemini():
                return await asyncio.to_thread(self._analyze_rpt_with_gemini, clean_symbol, insiders)
                
            async def run_auditor_with_financials():
                return await asyncio.to_thread(self.auditor.analyze_annual_report, company_symbol, financial_data=financials)

            task_gemini = asyncio.create_task(run_gemini())
            task_auditor = asyncio.create_task(run_auditor_with_financials())
            
            # Wait for all remaining tasks
            # Wait for all remaining tasks
            results = await asyncio.gather(
                task_auditor, task_exchange, task_gemini,
                return_exceptions=True
            )
            
            auditor_data = results[0] if not isinstance(results[0], Exception) else {"status": "error", "error": str(results[0])}
            exchange_data = results[1] if not isinstance(results[1], Exception) else {"status": "error", "error": str(results[1])}
            gemini_data = results[2] if not isinstance(results[2], Exception) else {"subsidiaries": [], "associates": [], "transactions": []}
            
            # Log specific crash exceptions if any
            if isinstance(results[0], Exception): logger.error(f"Auditor task crashed: {results[0]}")
            if isinstance(results[1], Exception): logger.error(f"Exchange task crashed: {results[1]}")
            if isinstance(results[2], Exception): logger.error(f"Gemini task crashed: {results[2]}")

            logger.info("Parallel data gathering completed")
            
            # 3. Process Results
            
            # Merge Auditor findings into Gemini data
            if auditor_data.get("status") == "success":
                logger.info("Auditor Agent successfully analyzed Annual Report")
                analysis = auditor_data.get("analysis", {})
                subsidiaries = analysis.get("related_parties", [])
                
                # 3.1 Enrich with Geo-Spatial Data (Agent 12) - Run this async too if possible?
                # Cartographer is likely fast or we can just run it here.
                if subsidiaries:
                    logger.info("Cartographer Agent analyzing locations...")
                    # Run cartographer in thread as well
                    subsidiaries = await asyncio.to_thread(self.cartographer.analyze_locations, subsidiaries)
                    
                gemini_data["subsidiaries"].extend(subsidiaries)
                gemini_data["transactions"].extend(analysis.get("transactions", []))
            
            # Add shareholding info
            if exchange_data.get("status") == "success":
                logger.info("Exchange Agent successfully fetched shareholding pattern")
                gemini_data["shareholding"] = exchange_data.get("data", {})
            
            # 5. Build Graph
            self._add_insiders_to_graph(G, clean_symbol, insiders)
            self._add_gemini_entities_to_graph(G, clean_symbol, gemini_data)
            
            # 6. Analyze the Network
            analysis_results = self._analyze_network(G, clean_symbol)
            
            # 7. Format for Frontend (React Flow)
            graph_data = self._format_for_react_flow(G)
            
            return {
                "success": True,
                "company": company_symbol,
                "graph_data": graph_data,
                "analysis": analysis_results,
                "cycles": analysis_results.get("suspicious_loops", []), # Direct access for Shell Hunter 3D
                "gemini_data": gemini_data
            }

        except Exception as e:
            logger.error(f"Error building RPT network: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _fetch_insiders(self, symbol: str) -> List[Dict]:
        """Fetch major holders and insiders from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            insiders = []
            
            # Try to get insider roster
            try:
                roster = ticker.insider_roster_holders
                if roster is not None and not roster.empty:
                    for index, row in roster.iterrows():
                        insiders.append({
                            "name": row['Name'],
                            "position": row['Position'],
                            "latest_transaction": row['Most Recent Transaction']
                        })
            except Exception as e:
                logger.warning(f"Could not fetch insider roster: {e}")

            # If no roster, try institutional holders
            if not insiders:
                try:
                    holders = ticker.institutional_holders
                    if holders is not None and not holders.empty:
                        for index, row in holders.iterrows():
                            insiders.append({
                                "name": row['Holder'],
                                "position": "Institutional Investor",
                                "latest_transaction": "Held"
                            })
                except Exception:
                    pass
            
            return insiders[:10] 
            
        except Exception as e:
            logger.error(f"Error fetching insiders: {e}")
            return []

    def _fetch_financial_summary(self, symbol: str) -> Dict[str, Any]:
        """Fetch a summary of financial ratios for semantic audit"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Calculate basic ratios
            info = ticker.info
            
            summary = {
                "current_ratio": info.get("currentRatio"),
                "debt_to_equity": info.get("debtToEquity"),
                "quick_ratio": info.get("quickRatio"),
                "net_margin": info.get("profitMargins"),
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "return_on_equity": info.get("returnOnEquity")
            }
            
            # Clean up None values
            return {k: v for k, v in summary.items() if v is not None}
        except Exception as e:
            logger.error(f"Error fetching financials: {e}")
            return {}

    def _add_insiders_to_graph(self, G: nx.DiGraph, company: str, insiders: List[Dict]):
        """Add real insiders to the graph"""
        for insider in insiders:
            name = insider['name']
            position = insider['position']
            G.add_node(name, type="person", position=position, label=name)
            G.add_edge(name, company, relation="Director/Officer", weight=1)

    def _analyze_rpt_with_gemini(self, company: str, insiders: List[Dict]) -> Dict[str, Any]:
        """Use Gemini to extract real subsidiaries, associates, and RPT risks"""
        try:
            insider_names = [i['name'] for i in insiders]
            
            prompt = f"""
            You are a forensic financial analyst. Analyze the corporate structure and related party transactions for '{company}'.
            
            Known Insiders/Directors: {', '.join(insider_names[:5])}
            
            Task:
            1. Identify key SUBSIDIARIES (major ones).
            2. Identify key ASSOCIATE companies or Joint Ventures.
            3. Identify any known RELATED PARTY TRANSACTIONS (RPTs) or potential conflict of interest areas based on public knowledge/news.
            4. Flag any entities located in tax havens (Mauritius, Cyprus, etc.) if known.
            
            Return JSON format ONLY:
            {{
                "subsidiaries": [
                    {{"name": "Sub Name", "risk_score": 10-100, "reason": "Why risky?"}}
                ],
                "associates": [
                    {{"name": "Assoc Name", "risk_score": 10-100, "reason": "Why risky?"}}
                ],
                "transactions": [
                    {{"source": "Entity Name", "target": "Entity Name", "relation": "Loan/Investment/Sales", "is_suspicious": boolean}}
                ]
            }}
            
            Focus on REAL entities associated with {company}. If exact details are unavailable, infer likely structure based on industry (e.g., for Reliance, mention Retail, Jio, Petrochemicals subsidiaries).
            """
            
            import time
            
            keys = settings.gemini_keys
            if not keys:
                logger.error("No Gemini API keys found")
                return {"subsidiaries": [], "associates": [], "transactions": []}

            current_key_index = 0
            max_retries = len(keys) * 2  # Allow 2 cycles through all keys
            
            for attempt in range(max_retries):
                try:
                    # Configure with current key
                    current_key = keys[current_key_index]
                    genai.configure(api_key=current_key)
                    model = genai.GenerativeModel(settings.gemini_model_name)

                    response = model.generate_content(prompt)
                    text = response.text.strip()
                    self.last_gemini_response = text
                    logger.info(f"Gemini RPT Raw Response (Key {current_key_index}): {text[:100]}...")
                    
                    # Clean markdown if present
                    if text.startswith("```json"):
                        text = text[7:-3]
                    elif text.startswith("```"):
                        text = text[3:-3]
                    
                    return json.loads(text)

                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "Resource has been exhausted" in error_msg:
                        logger.warning(f"Rate limit hit for key {current_key_index}, switching key...")
                        current_key_index = (current_key_index + 1) % len(keys)
                        time.sleep(1)  # Small delay before retry
                    else:
                        logger.error(f"Gemini API failed: {e}")
                        # If it's not a rate limit, maybe we shouldn't retry indefinitely, but for now let's try next key just in case
                        current_key_index = (current_key_index + 1) % len(keys)
                        
            # Return empty if API fails after all retries
            logger.warning("Gemini API failed after exhausting all keys, returning empty RPT data")
            self.last_gemini_response = "API Failed - No Data"
            return {"subsidiaries": [], "associates": [], "transactions": []}
                        
        except Exception as e:
            logger.error(f"Gemini RPT analysis failed: {e}")
            self.last_gemini_response = f"Error: {str(e)}"
            return {"subsidiaries": [], "associates": [], "transactions": []}

    def _add_gemini_entities_to_graph(self, G, company_node, data):
        """Add entities extracted by Gemini and Exchange Agent to the graph"""
        
        # 1. Add Shareholding Nodes (from Exchange Agent)
        shareholding = data.get("shareholding", {})
        if shareholding:
            # Promoters
            promoter_holding = shareholding.get("promoters", 0)
            if promoter_holding > 0:
                node_id = "Promoter Group"
                G.add_node(node_id, type="shareholder", label=f"Promoters ({promoter_holding}%)", risk_score=10)
                G.add_edge(node_id, company_node, relationship="OWNERSHIP", weight=promoter_holding/100)
            
            # FIIs
            fii_holding = shareholding.get("fii", 0)
            if fii_holding > 0:
                node_id = "FIIs"
                G.add_node(node_id, type="shareholder", label=f"FIIs ({fii_holding}%)", risk_score=5)
                G.add_edge(node_id, company_node, relationship="OWNERSHIP", weight=fii_holding/100)
                
            # DIIs
            dii_holding = shareholding.get("dii", 0)
            if dii_holding > 0:
                node_id = "DIIs"
                G.add_node(node_id, type="shareholder", label=f"DIIs ({dii_holding}%)", risk_score=5)
                G.add_edge(node_id, company_node, relationship="OWNERSHIP", weight=dii_holding/100)

        # 2. Add Subsidiaries & Associates (from Gemini/Auditor)
        for entity in data.get("subsidiaries", []):
            name = entity.get("name")
            if not name: continue
            
            rel_type = entity.get("relationship", "Subsidiary")
            
            # Robustly handle risk_score (handle strings, None, etc.)
            raw_risk = entity.get("risk_score", 50)
            try:
                risk = float(raw_risk)
            except (ValueError, TypeError):
                risk = 50.0
            
            # Location Data (Agent 12)
            location = entity.get("location", {})
            is_tax_haven = entity.get("is_tax_haven", False)
            
            # Add Node with Location Attributes
            node_attrs = {
                "type": "subsidiary",
                "label": name,
                "risk_score": risk,
                "city": location.get("city", "Unknown"),
                "country": location.get("country", "Unknown"),
                "lat": location.get("lat", 0),
                "lng": location.get("lng", 0),
                "is_tax_haven": is_tax_haven
            }
            
            # Boost risk if tax haven
            if is_tax_haven:
                node_attrs["risk_score"] = min(100, risk + 20)
                node_attrs["label"] += " 🚩 (Tax Haven)"
            
            G.add_node(name, **node_attrs)
            
            # Add Edge
            G.add_edge(company_node, name, relationship=rel_type, weight=risk/100.0)

        # 3. Add Transactions (Edges)
        for tx in data.get("transactions", []):
            target = tx.get("target")
            if not target: continue
            
            # Ensure target node exists
            if not G.has_node(target):
                G.add_node(target, type="unknown", label=target, risk_score=70)
            
            # Add Transaction Edge
            edge_attrs = {
                "relationship": tx.get("type", "Transaction"),
                "amount": tx.get("amount", "Unknown"),
                "is_suspicious": tx.get("is_suspicious", False),
                "reason": tx.get("reason", "")
            }
            G.add_edge(company_node, target, **edge_attrs)

    def _analyze_network(self, G: nx.DiGraph, company: str) -> Dict[str, Any]:
        """Analyze the graph for cycles and centrality"""
        try:
            cycles = list(nx.simple_cycles(G))
            company_cycles = [c for c in cycles if company in c]
        except Exception:
            company_cycles = []
            
        degree_centrality = nx.degree_centrality(G)
        sorted_centrality = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "cycles_detected": len(company_cycles),
            "suspicious_loops": company_cycles,
            "key_entities": [x[0] for x in sorted_centrality[:3]]
        }

    def _format_for_react_flow(self, G: nx.DiGraph) -> Dict[str, List]:
        """Convert NetworkX graph to React Flow nodes and edges"""
        nodes = []
        edges = []
        
        import math
        center_x, center_y = 500, 400
        
        # Group nodes by type
        company_node = [n for n, d in G.nodes(data=True) if d.get('type') == 'company']
        insiders = [n for n, d in G.nodes(data=True) if d.get('type') == 'person']
        subsidiaries = [n for n, d in G.nodes(data=True) if d.get('type') == 'subsidiary']
        associates = [n for n, d in G.nodes(data=True) if d.get('type') == 'associate']
        others = [n for n, d in G.nodes(data=True) if n not in company_node + insiders + subsidiaries + associates]
        
        all_nodes = company_node + insiders + subsidiaries + associates + others
        
        for node_id in all_nodes:
            data = G.nodes[node_id]
            
            # Layout Logic
            if data.get('type') == 'company':
                x, y = center_x, center_y
            elif node_id in insiders:
                # Inner Circle: Insiders
                idx = insiders.index(node_id)
                total = len(insiders)
                radius = 250
                angle = (2 * math.pi * idx) / (total or 1)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
            elif node_id in subsidiaries:
                # Middle Circle: Subsidiaries
                idx = subsidiaries.index(node_id)
                total = len(subsidiaries)
                radius = 450
                angle = (2 * math.pi * idx) / (total or 1) + (math.pi/4)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
            else:
                # Outer Circle: Associates & Others
                group = associates + others
                idx = group.index(node_id)
                total = len(group)
                radius = 650
                angle = (2 * math.pi * idx) / (total or 1) + (math.pi/2)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
            
            nodes.append({
                "id": node_id,
                "type": "custom", 
                "data": { 
                    "label": data.get('label', node_id),
                    "type": data.get('type', 'default'),
                    "risk_score": data.get('risk_score', 0),
                    "position": data.get('position', '')
                },
                "position": { "x": x, "y": y }
            })
            
        for u, v, data in G.edges(data=True):
            edges.append({
                "id": f"e-{u}-{v}",
                "source": u,
                "target": v,
                "animated": True,
                "label": data.get('relation', ''),
                "style": { 
                    "stroke": "#ef4444" if data.get('is_suspicious') else "#94a3b8",
                    "strokeWidth": 3 if data.get('is_suspicious') else 1.5,
                    "strokeDasharray": "5,5" if data.get('is_suspicious') else "0"
                },
                "data": {
                    "is_suspicious": data.get('is_suspicious', False)
                }
            })
            
        return {
            "nodes": nodes,
            "edges": edges
        }
