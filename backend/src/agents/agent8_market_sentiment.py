import logging
import pandas as pd
from pytrends.request import TrendReq
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import google.generativeai as genai
from transformers import pipeline
from src.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketSentimentAgent:
    """Agent 8: Market Sentiment Analysis using Google Trends and News Scraping"""

    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
        self._initialize_gemini()
        self._initialize_finbert()

    def _initialize_finbert(self):
        """Initialize FinBERT pipeline"""
        try:
            self.finbert = pipeline("sentiment-analysis", model="ProsusAI/finbert")
            logger.info("FinBERT model initialized for sentiment analysis")
        except Exception as e:
            logger.error(f"Failed to initialize FinBERT: {str(e)}")
            self.finbert = None

    def _initialize_gemini(self):
        """Initialize Google Gemini API"""
        try:
            if not settings.gemini_api_key:
                logger.warning("GEMINI_API_KEY not found in settings")
                return

            genai.configure(api_key=settings.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("Gemini model initialized for sentiment analysis")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")
            self.gemini_model = None

    def get_sentiment_analysis(self, company_symbol: str) -> Dict[str, Any]:
        """
        Perform comprehensive market sentiment analysis
        """
        try:
            # 1. Get Google Trends Data
            trends_data = self._get_google_trends(company_symbol)
            
            # 2. Get News Sentiment
            news_data = self._get_news_sentiment(company_symbol)
            
            return {
                "company": company_symbol,
                "trends": trends_data,
                "news_sentiment": news_data,
                "overall_sentiment": self._calculate_overall_sentiment(trends_data, news_data)
            }
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return {
                "error": str(e),
                "company": company_symbol
            }

    def _get_google_trends(self, keyword: str) -> Dict[str, Any]:
        """Fetch Google Trends interest over time"""
        try:
            # Clean keyword (remove .NS, .BO suffix for better trends results)
            search_term = keyword.split('.')[0]
            
            self.pytrends.build_payload([search_term], cat=0, timeframe='today 1-m', geo='IN', gprop='')
            interest_over_time_df = self.pytrends.interest_over_time()
            
            if interest_over_time_df.empty:
                return {"status": "no_data", "data": []}

            # Convert to list of dicts for frontend
            data = []
            for date, row in interest_over_time_df.iterrows():
                data.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "interest": int(row[search_term])
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
            logger.error(f"Google Trends error: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _get_news_sentiment(self, keyword: str) -> Dict[str, Any]:
        """Scrape news and analyze sentiment"""
        try:
            search_term = keyword.split('.')[0]
            # Use Google News RSS
            url = f"https://news.google.com/rss/search?q={search_term}+finance+india&hl=en-IN&gl=IN&ceid=IN:en"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, features="xml")
            
            items = soup.findAll('item')[:10] # Top 10 news items
            headlines = []
            
            for item in items:
                headlines.append({
                    "title": item.title.text,
                    "link": item.link.text,
                    "pubDate": item.pubDate.text
                })
            
            if not headlines:
                return {"status": "no_news", "sentiment": "neutral"}

            # Analyze sentiment using Gemini
            sentiment_result = self._analyze_headlines_with_gemini(headlines)
            
            # Analyze sentiment using FinBERT
            finbert_result = self._analyze_headlines_with_finbert(headlines)

            return {
                "status": "success",
                "headlines": headlines,
                "sentiment_analysis": sentiment_result,
                "finbert_analysis": finbert_result
            }
        except Exception as e:
            logger.error(f"News scraping error: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _analyze_headlines_with_gemini(self, headlines: List[Dict]) -> Dict[str, Any]:
        """Use Gemini to analyze sentiment of headlines"""
        if not self.gemini_model:
            return {"score": 0, "label": "Unknown (Model unavailable)"}

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
            
            response = self.gemini_model.generate_content(prompt)
            # Clean up response to ensure valid JSON
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3]
            
            import json
            result = json.loads(text)
            
            # Handle case where LLM returns a list instead of a dict
            if isinstance(result, list):
                if result:
                    return result[0]
                return {"score": 0, "label": "Neutral", "summary": "No sentiment data"}
                
            return result
        except Exception as e:
            logger.error(f"Gemini sentiment analysis error: {str(e)}")
            return {"score": 0, "label": "Error", "summary": "Could not analyze sentiment."}

    def _analyze_headlines_with_finbert(self, headlines: List[Dict]) -> Dict[str, Any]:
        """Use FinBERT to analyze sentiment of headlines"""
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
        combined_score = (finbert_score * 0.6) + (gemini_score * 0.4)
        
        if combined_score > 20:
            return "Bullish"
        elif combined_score < -20:
            return "Bearish"
        else:
            return "Neutral"

# Global instance
market_sentiment_agent = MarketSentimentAgent()
