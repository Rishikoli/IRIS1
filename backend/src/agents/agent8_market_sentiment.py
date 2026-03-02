import logging
import pandas as pd
from pytrends.request import TrendReq
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
# import google.generativeai as genai # REMOVED
from transformers import pipeline
import asyncio
from src.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketSentimentAgent:
    """Agent 8: Market Sentiment Analysis using Google Trends and News Scraping"""

    def __init__(self):
        self.pytrends = None  # Lazy-initialized on first use to avoid blocking startup
        # self._initialize_gemini() # REMOVED
        self._initialize_finbert()

    def _initialize_finbert(self):
        """Initialize FinBERT pipeline"""
        try:
            self.finbert = pipeline("sentiment-analysis", model="ProsusAI/finbert")
            logger.info("FinBERT model initialized for sentiment analysis")
        except Exception as e:
            logger.error(f"Failed to initialize FinBERT: {str(e)}")
            self.finbert = None

    # def _initialize_gemini(self):
    #     """Initialize Google Gemini API (DEPRECATED)"""
    #     pass

    async def get_sentiment_analysis(self, company_symbol: str) -> Dict[str, Any]:
        """
        Perform comprehensive market sentiment analysis with robustness
        """
        try:
            # 1. Get Google Trends Data (with fallback & timeout)
            try:
                # Run sync pytrends in thread with timeout
                trends_data = await asyncio.wait_for(
                    asyncio.to_thread(self._get_google_trends, company_symbol),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                logger.warning(f"Google Trends timed out for {company_symbol}")
                trends_data = {"status": "error", "message": "Google Trends timed out", "data": []}
            except Exception as e:
                logger.error(f"Google Trends failed: {e}")
                trends_data = {"status": "error", "message": str(e), "data": []}

            # 2. Get News Sentiment (with fallback)
            try:
                # _get_news_sentiment is already async, just ensure it doesn't hang indefinitely
                news_data = await asyncio.wait_for(
                    self._get_news_sentiment(company_symbol),
                    timeout=45.0
                )
            except asyncio.TimeoutError:
                logger.warning(f"News sentiment timed out for {company_symbol}")
                news_data = {"status": "error", "message": "News analysis timed out", "sentiment": "neutral"}
            except Exception as e:
                logger.error(f"News sentiment failed: {e}")
                news_data = {"status": "error", "message": str(e), "sentiment": "neutral"}
            
            return {
                "company": company_symbol,
                "trends": trends_data,
                "news_sentiment": news_data,
                "overall_sentiment": self._calculate_overall_sentiment(trends_data, news_data)
            }
        except Exception as e:
            logger.error(f"Critical error in sentiment analysis: {str(e)}")
            return {
                "error": str(e),
                "company": company_symbol,
                "trends": {"status": "error", "data": []},
                "news_sentiment": {"status": "error", "sentiment": "neutral"},
                "overall_sentiment": "Neutral"
            }

    def _get_google_trends(self, keyword: str) -> Dict[str, Any]:
        """Fetch Google Trends interest over time"""
        try:
            # Clean keyword (remove .NS, .BO suffix for better trends results)
            search_term = keyword.split('.')[0]

            # Lazy-init pytrends on first actual use
            if self.pytrends is None:
                try:
                    self.pytrends = TrendReq(hl='en-US', tz=360)
                except Exception as init_err:
                    logger.warning(f"PyTrends init failed: {init_err}")
                    return {"status": "error", "message": "Google Trends unavailable", "data": []}

            # Using try-except block specifically for PyTrends as it's prone to 429 errors
            try:
                self.pytrends.build_payload([search_term], cat=0, timeframe='today 1-m', geo='IN', gprop='')
                interest_over_time_df = self.pytrends.interest_over_time()
            except Exception as e:
                logger.warning(f"Google Trends API failed (likely rate limit): {e}")
                return {"status": "error", "message": "Google Trends rate limit exceeded", "data": []}
            
            if interest_over_time_df.empty:
                return {"status": "no_data", "data": []}

            # Convert to list of dicts for frontend
            data = []
            for date, row in interest_over_time_df.iterrows():
                try:
                    val = int(row[search_term])
                except:
                    val = 0
                data.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "interest": val
                })
            
            # Calculate trend direction
            if len(data) >= 2:
                trend_direction = "up" if data[-1]["interest"] > data[0]["interest"] else "down"
            else:
                trend_direction = "neutral"

            return {
                "status": "success",
                "data": data,
                "average_interest": int(interest_over_time_df[search_term].mean()),
                "trend_direction": trend_direction
            }
        except Exception as e:
            logger.error(f"Google Trends general error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _get_news_sentiment(self, keyword: str) -> Dict[str, Any]:
        """Scrape news and analyze sentiment"""
        try:
            search_term = keyword.split('.')[0]
            # Use Google News RSS
            url = f"https://news.google.com/rss/search?q={search_term}+finance+india&hl=en-IN&gl=IN&ceid=IN:en"
            logger.info(f"Fetching news from: {url}")
            
            # Use run_in_executor for blocking requests call
            import asyncio
            try:
                # Add timeout to prevent hanging
                response = await asyncio.to_thread(requests.get, url, timeout=10)
                response.raise_for_status()
            except Exception as req_err:
                logger.error(f"Failed to fetch news RSS: {req_err}")
                return {"status": "error", "message": f"News fetch failed: {str(req_err)}", "sentiment": "neutral"}

            soup = BeautifulSoup(response.content, features="xml")
            
            items = soup.findAll('item')[:10] # Top 10 news items
            headlines = []
            
            for item in items:
                try:
                    headlines.append({
                        "title": item.title.text,
                        "link": item.link.text,
                        "pubDate": item.pubDate.text if item.pubDate else ""
                    })
                except Exception as parse_err:
                    logger.warning(f"Error parsing news item: {parse_err}")
                    continue
            
            if not headlines:
                return {"status": "no_news", "sentiment": "neutral"}

            logger.info(f"Analying {len(headlines)} headlines for {keyword}")

            # Analyze sentiment using Gemini
            try:
                sentiment_result = await self._analyze_headlines_with_gemini(headlines)
            except Exception as e:
                logger.error(f"Gemini analysis validation failed: {e}")
                sentiment_result = {"score": 0, "label": "Error", "summary": "Analysis failed"}
            
            # Analyze sentiment using FinBERT
            try:
                finbert_result = self._analyze_headlines_with_finbert(headlines)
            except Exception as e:
                 logger.error(f"FinBERT analysis validation failed: {e}")
                 finbert_result = {"score": 0, "label": "Error", "breakdown": {}}

            return {
                "status": "success",
                "headlines": headlines,
                "sentiment_analysis": sentiment_result,
                "finbert_analysis": finbert_result
            }
        except Exception as e:
            logger.error(f"News analysis process error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"status": "error", "message": str(e)}

    async def _analyze_headlines_with_gemini(self, headlines: List[Dict]) -> Dict[str, Any]:
        """Use Gemini to analyze sentiment of headlines with caching"""
        from src.utils.gemini_client import GeminiClient
        import json
        
        try:
            headlines_text = "\n".join([f"- {h['title']}" for h in headlines])
            prompt = f"""
        Analyze the market sentiment for the following financial news headlines.
        Provide a sentiment score from -100 (Extremely Negative) to 100 (Extremely Positive).
        Also provide a brief 1-sentence summary of the prevailing sentiment.
        
        Headlines:
        {headlines_text}
        
        Output JSON format:
        {{
            "score": <int>,
            "label": "<string>",
            "summary": "<string>"
        }}
        """
            
            # Use centralized client
            client = GeminiClient()
            text = await client.generate_content(prompt)
            
            # Clean up response to ensure valid JSON
            if text.startswith("```json"):
                text = text[7:-3]
            elif text.startswith("```"):
                text = text[3:-3]
            
            result = json.loads(text)
            
            # Handle case where LLM returns a list instead of a dict
            if isinstance(result, list):
                if result:
                    return result[0]
                return {"score": 0, "label": "Neutral", "summary": "No sentiment data"}
                
            return result
            
        except Exception as e:
            logger.error(f"Gemini sentiment analysis failed: {e}")
            return {"score": 0, "label": "Error", "summary": f"AI Error: {str(e)}"}

    def _analyze_headlines_with_finbert(self, headlines: List[Dict]) -> Dict[str, Any]:
        """Use FinBERT to analyze sentiment of headlines"""
        if not self.finbert:
            logger.info("FinBERT not initialized, attempting lazy initialization...")
            self._initialize_finbert()
            
        if not self.finbert:
            return {"score": 0, "label": "Unknown (Model unavailable)"}

        try:
            total_score = 0
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for headline in headlines:
                # Truncate to 512 tokens approx (chars) to be safe, though pipeline handles it usually
                result = self.finbert(headline['title'][:512])[0]
                score = result['score']
                label = result['label']
                
                if label == 'positive':
                    total_score += score
                    positive_count += 1
                elif label == 'negative':
                    total_score -= score
                    negative_count += 1
                else:
                    neutral_count += 1
            
            # Normalize score to -100 to 100 range
            count = len(headlines)
            if count > 0:
                avg_score = (total_score / count) * 100
            else:
                avg_score = 0
                
            # Determine overall label
            if avg_score > 15:
                overall_label = "Positive"
            elif avg_score < -15:
                overall_label = "Negative"
            else:
                overall_label = "Neutral"
                
            return {
                "score": round(avg_score, 2),
                "label": overall_label,
                "breakdown": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count
                }
            }
        except Exception as e:
            logger.error(f"FinBERT sentiment analysis error: {str(e)}")
            return {"score": 0, "label": "Error", "breakdown": {}}

    def _calculate_overall_sentiment(self, trends: Dict, news: Dict) -> str:
        """Combine trends and news for an overall verdict"""
        # Simple logic for now
        sentiment_analysis = news.get("sentiment_analysis", {})
        finbert_analysis = news.get("finbert_analysis", {})
        
        # Safe access in case sentiment_analysis is not a dict
        if isinstance(sentiment_analysis, dict):
            gemini_score = sentiment_analysis.get("score", 0)
        else:
            gemini_score = 0
            
        if isinstance(finbert_analysis, dict):
            finbert_score = finbert_analysis.get("score", 0)
        else:
            finbert_score = 0
        
        # Weighted average: 60% FinBERT, 40% Gemini (since FinBERT is specialized)
        # If Gemini failed (score 0 and label Error/Neutral), rely 100% on FinBERT
        if sentiment_analysis.get("label") in ["Error", "Neutral"] and gemini_score == 0 and finbert_score != 0:
             combined_score = finbert_score
        else:
             combined_score = (finbert_score * 0.6) + (gemini_score * 0.4)
        
        if combined_score > 20:
            return "Bullish"
        elif combined_score < -20:
            return "Bearish"
        else:
            return "Neutral"

# Global instance
market_sentiment_agent = MarketSentimentAgent()
