import logging
import numpy as np
from typing import Dict, Any, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimeTravelerAgent:
    """Agent 13: The Time Traveler - Predictive Forensics"""

    def __init__(self):
        pass

    def predict_future_performance(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predicts future financial performance (Revenue, Net Income) for next 3 years.
        
        Args:
            historical_data: Dictionary containing 'financials' with 'revenue' and 'net_income' lists.
                             Expected format: {'revenue': [{'year': 2023, 'value': 100}, ...], ...}
        """
        try:
            predictions = {
                "revenue_forecast": [],
                "net_income_forecast": [],
                "future_risk_score": 0,
                "trend": "Stable"
            }
            
            # Extract data
            revenue_data = historical_data.get('revenue', [])
            net_income_data = historical_data.get('net_income', [])
            
            if not revenue_data or len(revenue_data) < 3:
                logger.warning("Insufficient data for prediction")
                return predictions

            # Sort by year
            revenue_data.sort(key=lambda x: x['year'])
            net_income_data.sort(key=lambda x: x['year'])
            
            # Predict Revenue
            rev_years = np.array([d['year'] for d in revenue_data])
            rev_values = np.array([d['value'] for d in revenue_data])
            
            rev_slope, rev_intercept = np.polyfit(rev_years, rev_values, 1)
            
            last_year = rev_years[-1]
            future_years = [last_year + 1, last_year + 2, last_year + 3]
            
            for year in future_years:
                pred_value = rev_slope * year + rev_intercept
                predictions["revenue_forecast"].append({"year": int(year), "value": round(pred_value, 2)})
                
            # Predict Net Income
            ni_years = np.array([d['year'] for d in net_income_data])
            ni_values = np.array([d['value'] for d in net_income_data])
            
            ni_slope, ni_intercept = np.polyfit(ni_years, ni_values, 1)
            
            for year in future_years:
                pred_value = ni_slope * year + ni_intercept
                predictions["net_income_forecast"].append({"year": int(year), "value": round(pred_value, 2)})
            
            # Calculate Future Risk Score
            # If slope is negative, risk increases
            risk_score = 50 # Base
            
            if rev_slope < 0:
                risk_score += 20
                predictions["trend"] = "Declining"
            elif rev_slope > 0:
                risk_score -= 10
                predictions["trend"] = "Growing"
                
            if ni_slope < 0:
                risk_score += 20
            elif ni_slope > 0:
                risk_score -= 10
                
            predictions["future_risk_score"] = max(0, min(100, risk_score))
            
            return predictions

        except Exception as e:
            logger.error(f"Time Traveler prediction failed: {e}")
            return {}
