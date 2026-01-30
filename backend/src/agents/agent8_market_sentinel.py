
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketSentinelAgent:
    """
    Agent 8: Market Sentinel - Real-time Pump & Dump Detection
    Analyzes price and volume patterns (SMA, EMA, RSI) to detect anomalies.
    """

    def __init__(self):
        pass

    def analyze_stock(self, symbol: str) -> Dict[str, Any]:
        """
        Perform technical analysis to detect potential manipulation.
        """
        try:
            # 1. Fetch Data
            # Fetch 1 year of daily data for robust MAs, and 5 days of minute data for realtime checks if needed?
            # For now, let's stick to daily/hourly for stability.
            data = self._fetch_data(symbol)
            
            if data is None or data.empty:
                 return {"success": False, "error": f"No data found for {symbol}"}

            # 2. Calculate Indicators
            indicators = self._calculate_indicators(data)
            
            # 3. Detect Anomalies (Pump & Dump Logic)
            analysis = self._detect_pump_and_dump(data, indicators)
            
            return {
                "success": True,
                "symbol": symbol,
                "current_price": indicators['current_price'],
                "indicators": indicators,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in Market Sentinel analysis for {symbol}: {e}")
            return {"success": False, "error": str(e)}
            
    def _fetch_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Fetch historical data from Yahoo Finance"""
        try:
            # Try different suffixes for India if needed
            tickers_to_try = [symbol]
            if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
                 tickers_to_try.extend([f"{symbol}.NS", f"{symbol}.BO"])
            
            for ticker_symbol in tickers_to_try:
                ticker = yf.Ticker(ticker_symbol)
                # Fetch 6 months of data
                data = ticker.history(period="6m")
                if not data.empty:
                    return data
            return None
        except Exception as e:
            logger.error(f"Data fetch failed: {e}")
            return None

    def _calculate_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators (SMA, EMA, RSI, Volume MA)"""
        
        # Ensure we have enough data
        if len(data) < 50:
             return {"note": "Insufficient data for full analysis"}

        close = data['Close']
        volume = data['Volume']
        
        # Simple Moving Averages
        sma_20 = close.rolling(window=20).mean().iloc[-1]
        sma_50 = close.rolling(window=50).mean().iloc[-1]
        
        # Exponential Moving Averages
        ema_12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
        ema_26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
        
        # Moving Average Convergence Divergence (MACD)
        # macd_line = ema_12 - ema_26
        
        # Volume Moving Average (20 days)
        vol_ma_20 = volume.rolling(window=20).mean().iloc[-1]
        
        # RSI (14 days)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi_14 = 100 - (100 / (1 + rs)).iloc[-1]
        
        return {
            "current_price": float(close.iloc[-1]),
            "prev_close": float(close.iloc[-2]),
            "sma_20": float(sma_20),
            "sma_50": float(sma_50),
            "ema_12": float(ema_12),
            "ema_26": float(ema_26),
            "rsi_14": float(rsi_14) if not pd.isna(rsi_14) else 50.0,
            "current_volume": int(volume.iloc[-1]),
            "avg_volume_20": int(vol_ma_20)
        }

    def _detect_pump_and_dump(self, data: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Core logic to detect Pump and Dump signals"""
        
        signals = []
        risk_score = 0
        
        # Checklist for P&D:
        
        # 1. Volume Spike: Current Volume > 3x Average Volume
        vol_ratio = indicators['current_volume'] / indicators['avg_volume_20'] if indicators['avg_volume_20'] > 0 else 0
        if vol_ratio > 3.0:
            signals.append(f"EXTREME Volume Spike ({vol_ratio:.1f}x average)")
            risk_score += 40
        elif vol_ratio > 2.0:
            signals.append(f"High Volume Spike ({vol_ratio:.1f}x average)")
            risk_score += 20
            
        # 2. Price Surge: Price > SMA 20 by large margin (e.g., 20% in short time)
        price_to_sma = (indicators['current_price'] - indicators['sma_20']) / indicators['sma_20']
        if price_to_sma > 0.30: # 30% above 20-day average
             signals.append("Price Parabolic (>30% above 20-day avg)")
             risk_score += 30
        elif price_to_sma > 0.15:
             signals.append("Price Surging (>15% above 20-day avg)")
             risk_score += 15
             
        # 3. RSI Overbought
        if indicators['rsi_14'] > 80:
            signals.append(f"RSI Extremely Overbought ({indicators['rsi_14']:.1f})")
            risk_score += 20
        elif indicators['rsi_14'] > 70:
            signals.append(f"RSI Overbought ({indicators['rsi_14']:.1f})")
            risk_score += 10
            
        # 4. Intra-day Volatility (High - Low) / Open? (Need intra-day data ideally)
        # Using Daily range for now
        daily_range = (data['High'].iloc[-1] - data['Low'].iloc[-1]) / data['Open'].iloc[-1]
        if daily_range > 0.10: # >10% daily swing
             signals.append(f"High Volatility ({daily_range*100:.1f}% daily range)")
             risk_score += 10
             
        # Verdict
        risk_level = "LOW"
        if risk_score >= 70:
            risk_level = "CRITICAL (Potential Pump & Dump)"
        elif risk_score >= 40:
            risk_level = "HIGH"
        elif risk_score >= 20:
            risk_level = "MEDIUM"
            
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "signals": signals,
            "vol_spike_ratio": round(vol_ratio, 2),
            "details": "Price and volume anomalies detected." if signals else "Trading within normal parameters."
        }

# Global Instance
market_sentinel_agent = MarketSentinelAgent()
