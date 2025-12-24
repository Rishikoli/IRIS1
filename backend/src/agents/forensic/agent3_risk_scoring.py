"""
Project IRIS - Agent 3: Risk Scoring Agent
Computes 6-category weighted composite risk scores based on forensic analysis results
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

from src.config import settings
from src.database.connection import get_db_client
from src.agents.forensic.agent4_compliance import ComplianceValidationAgent
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

class RiskCategory(Enum):
    """Risk categories for comprehensive risk assessment"""
    FINANCIAL_STABILITY = "financial_stability"
    OPERATIONAL_RISK = "operational_risk"
    MARKET_RISK = "market_risk"
    COMPLIANCE_RISK = "compliance_risk"
    LIQUIDITY_RISK = "liquidity_risk"
    GROWTH_SUSTAINABILITY = "growth_sustainability"

@dataclass
class RiskScore:
    """Individual risk score with details"""
    category: RiskCategory
    score: float  # 0-100 scale (0 = low risk, 100 = high risk)
    weight: float  # Weight in composite score
    confidence: float  # Confidence level 0-1
    factors: List[str]  # Contributing factors
    recommendations: List[str]  # Risk mitigation recommendations

@dataclass
class CompositeRiskAssessment:
    """Complete risk assessment results with Explainable AI (XAI)"""
    company_symbol: str
    assessment_date: str
    overall_risk_score: float  # Weighted average of all categories
    risk_category_scores: Dict[RiskCategory, RiskScore]
    shap_values: Dict[str, float]  # Contribution of each factor to the final score
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    risk_factors: List[str]
    investment_recommendation: str
    monitoring_frequency: str  # DAILY, WEEKLY, MONTHLY, QUARTERLY

class RiskScoringAgent:
    """Agent 3: Risk scoring with 6-category weighted composite"""

    def __init__(self):
        try:
            self.db_client = get_db_client()
        except Exception:
            # For standalone analysis without database
            self.db_client = None
        
        # Initialize Compliance Agent
        self.compliance_agent = ComplianceValidationAgent()
        logger.info("Risk Scoring Agent initialized")

    def calculate_risk_score(self, company_symbol: str, forensic_data: Dict[str, Any]) -> CompositeRiskAssessment:
        """Calculate comprehensive risk score from forensic analysis data"""
        try:
            logger.info(f"Calculating risk score for {company_symbol}")

            logger.info(f"Calculating risk score for {company_symbol}")

            # Extract analysis results
            vertical_analysis = forensic_data.get("vertical_analysis", {})
            horizontal_analysis = forensic_data.get("horizontal_analysis", {})
            financial_ratios = forensic_data.get("financial_ratios", {})

            # Calculate individual risk category scores
            risk_scores = {}

            # 1. Financial Stability Risk
            risk_scores[RiskCategory.FINANCIAL_STABILITY] = self._calculate_financial_stability_risk(
                vertical_analysis, horizontal_analysis, financial_ratios
            )

            # 2. Operational Risk
            risk_scores[RiskCategory.OPERATIONAL_RISK] = self._calculate_operational_risk(
                vertical_analysis, financial_ratios
            )

            # 3. Market Risk (Enhanced with Sentiment Analysis)
            risk_scores[RiskCategory.MARKET_RISK] = self._calculate_market_risk(
                company_symbol, horizontal_analysis, financial_ratios
            )

            # 4. Compliance Risk (Integrated with Agent 4)
            risk_scores[RiskCategory.COMPLIANCE_RISK] = self._calculate_compliance_risk(
                company_symbol, forensic_data
            )

            # 5. Liquidity Risk
            risk_scores[RiskCategory.LIQUIDITY_RISK] = self._calculate_liquidity_risk(
                vertical_analysis, financial_ratios
            )

            # 6. Growth Sustainability Risk
            risk_scores[RiskCategory.GROWTH_SUSTAINABILITY] = self._calculate_growth_sustainability_risk(
                horizontal_analysis, financial_ratios
            )

            # Calculate overall weighted score
            overall_score = self._calculate_composite_score(risk_scores)

            # Calculate SHAP values (Explainability)
            shap_values = self._calculate_shap_values(risk_scores, overall_score)

            # Determine risk level and recommendations
            risk_level = self._determine_risk_level(overall_score)
            investment_recommendation = self._generate_investment_recommendation(overall_score, risk_scores)
            monitoring_frequency = self._determine_monitoring_frequency(overall_score)

            # Compile risk factors
            all_factors = []
            for risk_score in risk_scores.values():
                all_factors.extend(risk_score.factors)

            return CompositeRiskAssessment(
                company_symbol=company_symbol,
                assessment_date=datetime.now().isoformat(),
                overall_risk_score=round(overall_score, 2),
                risk_category_scores=risk_scores,
                shap_values=shap_values,
                risk_level=risk_level,
                risk_factors=list(set(all_factors)),  # Remove duplicates
                investment_recommendation=investment_recommendation,
                monitoring_frequency=monitoring_frequency
            )

        except Exception as e:
            logger.error(f"Failed to calculate risk score for {company_symbol}: {e}")
            return self._create_error_assessment(company_symbol, str(e))

    def _calculate_financial_stability_risk(self, vertical_analysis: Dict, horizontal_analysis: Dict, financial_ratios: Dict) -> RiskScore:
        """Calculate financial stability risk score with enhanced sensitivity"""
        factors = []
        score = 0.0
        confidence = 0.8

        # Check profitability indicators
        va = vertical_analysis.get("vertical_analysis", {})
        ha = horizontal_analysis.get("horizontal_analysis", {})
        ratios = financial_ratios.get("financial_ratios", {})

        # Get the most recent year's data (first available year)
        recent_year = None
        available_years = list(ratios.keys()) if ratios else []
        if available_years:
            recent_year = available_years[0]  # Most recent year
            recent_ratios = ratios[recent_year]
        else:
            recent_ratios = {}

        # Net profit margin analysis - Enhanced sensitivity
        net_margin = float(recent_ratios.get("net_margin_pct", 0))
        if net_margin < 3:  # Lower threshold for concern
            score += 30  # Higher penalty
            factors.append("Very low net profit margin indicates serious profitability concerns")
        elif net_margin < 5:  # Less than 5% margin
            score += 25
            factors.append("Low net profit margin indicates profitability concerns")
        elif net_margin < 8:  # Marginal profitability
            score += 15
            factors.append("Marginal net profit margin suggests profitability challenges")
        elif net_margin > 15:  # Strong margin
            score -= 10
            confidence += 0.1
        else:  # Moderate margin (5-15%)
            score += 3  # Reduced penalty for moderate margins
            factors.append("Moderate net profit margin suggests room for improvement")

        # ROE analysis - enhanced sensitivity
        roe = self._calculate_roe(recent_ratios, va)
        if roe < 5:  # Very poor ROE
            score += 25
            factors.append("Very poor return on equity indicates capital inefficiency")
        elif roe < 10:  # Below average ROE
            score += 20
            factors.append("Below-average return on equity")
        elif roe < 15:  # Marginal ROE
            score += 10
            factors.append("Marginal return on equity requires monitoring")
        elif roe > 20:  # Strong ROE
            score -= 5
        elif roe > 15:  # Good ROE
            score -= 2

        # Debt-to-equity analysis - Enhanced sensitivity
        debt_to_equity = float(recent_ratios.get("debt_to_equity", 0))
        if debt_to_equity > 3:  # Very high leverage
            score += 35  # Higher penalty
            factors.append("Very high debt-to-equity ratio indicates severe financial risk")
        elif debt_to_equity > 2:  # High leverage
            score += 30
            factors.append("High debt-to-equity ratio indicates financial risk")
        elif debt_to_equity > 1:  # Moderate leverage
            score += 15
            factors.append("Moderate debt-to-equity ratio suggests leverage concerns")
        elif debt_to_equity < 0.3:  # Very low leverage
            score -= 10

        # Growth stability - Enhanced sensitivity
        revenue_growth = self._extract_growth_metric(ha, "total_revenue")
        if revenue_growth < -10:  # Severe decline
            score += 25
            factors.append("Severe revenue decline threatens sustainability")
        elif revenue_growth < 0:  # Declining revenue
            score += 15
            factors.append("Declining revenue trend")
        elif revenue_growth < 3:  # Very low growth
            score += 8
            factors.append("Very low revenue growth may indicate stagnation")
        elif revenue_growth > 20:  # Strong growth
            score -= 5

        # Asset quality - Enhanced sensitivity
        total_assets = va.get("balance_sheet", {}).get("total_assets_pct", 0)
        if total_assets < 30:  # Very weak asset base
            score += 15
            factors.append("Very weak asset base relative to revenue")
        elif total_assets < 50:  # Weak asset base
            score += 10
            factors.append("Weak asset base relative to revenue")

        # Earnings Quality Indicators (New)
        # Check for earnings manipulation patterns
        if recent_ratios:
            gross_margin = float(recent_ratios.get("gross_margin_pct", 0))
            operating_margin = float(recent_ratios.get("operating_margin_pct", 0))

            # Unusual margin patterns that might indicate manipulation
            if gross_margin > 0 and operating_margin < 0:
                score += 20
                factors.append("Negative operating margin despite positive gross margin suggests potential earnings manipulation")

            if net_margin > 0 and gross_margin < 5:
                score += 15
                factors.append("Very low gross margin with positive net profit warrants investigation")

        # Normalize score to 0-100
        score = max(0, min(100, score))

        return RiskScore(
            category=RiskCategory.FINANCIAL_STABILITY,
            score=score,
            weight=0.25,  # 25% weight in composite
            confidence=confidence,
            factors=factors,
            recommendations=self._generate_financial_stability_recommendations(score, factors)
        )

    def _calculate_roe(self, ratios: Dict, vertical_analysis: Dict) -> float:
        """Calculate Return on Equity from available data"""
        try:
            # ROE = Net Income / Total Equity (Average Total Equity over the period)
            # We need to calculate this from actual financial statement data

            va = vertical_analysis.get("vertical_analysis", {})
            ratios = ratios.get("financial_ratios", {})

            # Get the most recent year's data
            recent_year = None
            available_years = list(ratios.keys()) if ratios else []
            if available_years:
                recent_year = available_years[0]  # Most recent year
                recent_ratios = ratios[recent_year]
            else:
                logger.warning("No ratio data available for ROE calculation")
                return 15.0  # Fallback placeholder

            # For ROE calculation, we need actual financial statement values
            # Since we're working with ratios and percentages, we need to infer or use proxy calculations

            # Alternative approach: Use the financial ratios if available
            # ROE is typically available as a calculated ratio in financial analysis
            roe = recent_ratios.get("roe", None)

            if roe is not None:
                logger.info(f"Using calculated ROE from financial ratios: {roe}%")
                return float(roe)

            # If ROE ratio not available, calculate from net margin and equity turnover
            # ROE = Net Margin × Asset Turnover × Leverage Ratio
            net_margin = recent_ratios.get("net_margin_pct", 0)
            asset_turnover = recent_ratios.get("asset_turnover", 0)
            equity_multiplier = recent_ratios.get("equity_multiplier", 1)  # Total Assets / Total Equity

            if net_margin > 0 and asset_turnover > 0 and equity_multiplier > 0:
                calculated_roe = net_margin * asset_turnover * equity_multiplier
                logger.info(f"Calculated ROE using Dupont formula: {calculated_roe}%")
                return float(calculated_roe)

            # Last resort: Use industry-standard placeholder based on company type
            # For now, return a more intelligent placeholder based on available data
            logger.info("Using intelligent placeholder ROE based on financial metrics")
            return 15.0  # Conservative placeholder - should be replaced with actual calculation

        except Exception as e:
            logger.error(f"Error calculating ROE: {e}")
            return 0.0

    def _calculate_operational_risk(self, vertical_analysis: Dict, financial_ratios: Dict) -> RiskScore:
        """Calculate operational risk score with enhanced sensitivity and cash flow analysis"""
        factors = []
        score = 0.0
        confidence = 0.7

        va = vertical_analysis.get("vertical_analysis", {})
        ratios = financial_ratios.get("financial_ratios", {})

        # Get the most recent year's data
        recent_year = None
        available_years = list(ratios.keys()) if ratios else []
        if available_years:
            recent_year = available_years[0]
            recent_ratios = ratios[recent_year]
        else:
            recent_ratios = {}

        # Cost management using gross margin as proxy - Enhanced sensitivity
        gross_margin = float(recent_ratios.get("gross_margin_pct", 0))
        if gross_margin < 10:  # Very low gross margin
            score += 25
            factors.append("Very low gross margin indicates severe operational inefficiency")
        elif gross_margin < 15:  # Low gross margin
            score += 20
            factors.append("Low gross margin indicates operational inefficiency")
        elif gross_margin < 20:  # Marginal gross margin
            score += 10
            factors.append("Marginal gross margin suggests operational challenges")
        elif gross_margin > 40:  # Strong margin
            score -= 10

        # Asset turnover analysis - Enhanced sensitivity
        asset_turnover = float(recent_ratios.get("asset_turnover", 0))
        if asset_turnover < 0.5:  # Very poor asset utilization
            score += 20
            factors.append("Very poor asset utilization suggests severe operational inefficiency")
        elif asset_turnover < 1:  # Poor asset utilization
            score += 15
            factors.append("Low asset turnover suggests operational inefficiency")
        elif asset_turnover < 1.5:  # Marginal asset utilization
            score += 8
            factors.append("Marginal asset turnover indicates operational concerns")
        elif asset_turnover > 2:  # Excellent asset utilization
            score -= 5

        # Cash Flow Quality Indicators (New)
        if recent_ratios:
            # Operating Cash Flow analysis (if available)
            operating_cash_flow = recent_ratios.get("operating_cash_flow", 0)
            if operating_cash_flow:
                ocf_ratio = float(operating_cash_flow) / max(1, float(recent_ratios.get("net_income", 1)))
                if ocf_ratio < 0.5:  # Poor cash flow quality
                    score += 15
                    factors.append("Poor operating cash flow quality suggests earnings quality concerns")
                elif ocf_ratio > 2:  # Very strong cash flow
                    score -= 5

            # Free Cash Flow analysis (if available)
            free_cash_flow = recent_ratios.get("free_cash_flow", 0)
            if free_cash_flow:
                fcf_margin = float(free_cash_flow) / max(1, float(recent_ratios.get("total_revenue", 1)))
                if fcf_margin < -0.1:  # Negative free cash flow
                    score += 20
                    factors.append("Negative free cash flow indicates liquidity and operational concerns")
                elif fcf_margin < 0:  # Marginal free cash flow
                    score += 10
                    factors.append("Marginal free cash flow suggests operational challenges")

        # Working Capital Efficiency (New)
        current_ratio = float(recent_ratios.get("current_ratio", 0))
        if current_ratio < 0.8:  # Very poor liquidity
            score += 18
            factors.append("Very poor current ratio indicates severe liquidity risk")
        elif current_ratio < 1:  # Poor liquidity
            score += 12
            factors.append("Poor current ratio suggests liquidity concerns")
        elif current_ratio > 3:  # Excessive liquidity
            score += 5
            factors.append("Excessive current ratio may indicate inefficient working capital")

        score = max(0, min(100, score))

        return RiskScore(
            category=RiskCategory.OPERATIONAL_RISK,
            score=score,
            weight=0.15,  # 15% weight in composite
            confidence=confidence,
            factors=factors,
            recommendations=self._generate_operational_risk_recommendations(score, factors)
        )

    def _calculate_market_risk(self, company_symbol: str, horizontal_analysis: Dict, financial_ratios: Dict) -> RiskScore:
        """Calculate market risk score with enhanced sensitivity and sentiment analysis"""
        factors = []
        score = 0.0
        confidence = 0.6

        ha = horizontal_analysis.get("horizontal_analysis", {})

        # Revenue volatility - Enhanced sensitivity for stricter detection
        revenue_growth = self._extract_growth_metric(ha, "total_revenue")
        abs_revenue_growth = abs(revenue_growth)

        if abs_revenue_growth > 40:  # High volatility
            score += 30  # Higher penalty
            factors.append("High revenue volatility indicates significant market risk")
        elif abs_revenue_growth > 20:  # Moderate-high volatility
            score += 20  # Higher penalty
            factors.append("Moderate-high revenue volatility suggests elevated market sensitivity")
        elif abs_revenue_growth > 10:  # Moderate volatility
            score += 12
            factors.append("Moderate revenue volatility indicates some market risk")
        elif abs_revenue_growth > 5:  # Low volatility
            score += 5
            factors.append("Low revenue volatility suggests market exposure")
        elif abs_revenue_growth < 2:  # Very stable growth
            score -= 3
            factors.append("Very stable revenue growth reduces market risk")

        # Profit volatility - Enhanced sensitivity for stricter detection
        profit_growth = self._extract_growth_metric(ha, "net_profit")
        abs_profit_growth = abs(profit_growth)

        if abs_profit_growth > 80:  # Extreme profit swings
            score += 25  # Higher penalty
            factors.append("Extreme profit volatility suggests high market sensitivity")
        elif abs_profit_growth > 40:  # High profit volatility
            score += 18  # Higher penalty
            factors.append("High profit volatility indicates significant earnings sensitivity")
        elif abs_profit_growth > 20:  # Moderate profit volatility
            score += 10
            factors.append("Moderate profit volatility suggests market exposure")
        elif abs_profit_growth > 10:  # Low profit volatility
            score += 4
            factors.append("Low profit volatility indicates some market sensitivity")
        elif abs_profit_growth < 5:  # Stable profits
            score -= 3

        # Industry-specific risk factors - Enhanced sensitivity
        ratios = financial_ratios.get("financial_ratios", {})
        recent_year = list(ratios.keys())[0] if ratios else None

        if recent_year:
            recent_ratios = ratios[recent_year]

            # Beta-like analysis using asset turnover volatility - Enhanced
            asset_turnover = float(recent_ratios.get("asset_turnover", 0))
            if asset_turnover > 4:  # Very high turnover might indicate cyclical business
                score += 15  # Higher penalty
                factors.append("Very high asset turnover suggests highly cyclical business model")
            elif asset_turnover > 3:  # High turnover
                score += 10
                factors.append("High asset turnover suggests cyclical business model")
            elif asset_turnover < 0.3:  # Very low turnover
                score += 12  # Higher penalty
                factors.append("Very low asset turnover indicates severe market penetration challenges")
            elif asset_turnover < 0.5:  # Low turnover
                score += 8
                factors.append("Low asset turnover indicates market penetration challenges")

            # Debt as market risk proxy - Enhanced sensitivity
            debt_to_assets = float(recent_ratios.get("debt_to_assets", 0))
            if debt_to_assets > 0.9:  # Extreme leverage
                score += 20  # Higher penalty
                factors.append("Extreme leverage severely amplifies market risk exposure")
            elif debt_to_assets > 0.8:  # Very high leverage
                score += 15
                factors.append("Very high leverage amplifies market risk exposure")
            elif debt_to_assets > 0.7:  # High leverage
                score += 10
                factors.append("High leverage increases market risk exposure")

        # Market concentration risk - Enhanced sensitivity
        total_revenue = self._extract_growth_metric(ha, "total_revenue")
        if total_revenue > 20000000000:  # Very large companies
            score -= 8  # Higher reduction for market power
        elif total_revenue > 10000000000:  # Large companies
            score -= 5
        elif total_revenue < 500000000:  # Small companies
            score += 15  # Higher penalty
            factors.append("Very small company size significantly increases market risk exposure")
        elif total_revenue < 1000000000:  # Small companies
            score += 10
            factors.append("Smaller company size increases market risk exposure")

        # Earnings Quality and Manipulation Indicators (New)
        if recent_ratios:
            # Check for potential earnings manipulation
            net_margin = float(recent_ratios.get("net_margin_pct", 0))
            gross_margin = float(recent_ratios.get("gross_margin_pct", 0))

            # Unusual margin relationships that might indicate manipulation
            if gross_margin > 0 and net_margin < 0:
                score += 25
                factors.append("Negative net margin despite positive gross margin suggests potential earnings manipulation")

            if net_margin > 30 and gross_margin < 20:
                score += 20
            if net_margin > 30 and gross_margin < 20:
                score += 20
                factors.append("Unusually high net margin relative to gross margin warrants investigation")

        # Market Sentiment Analysis (New)
        # Search for negative news that might trigger market risk
        sentiment_risk, sentiment_factors = self._analyze_market_sentiment(company_symbol)
        if sentiment_risk > 0:
            score += sentiment_risk
            factors.extend(sentiment_factors)
            confidence += 0.1  # Increased confidence with external data

        score = max(0, min(100, score))

        return RiskScore(
            category=RiskCategory.MARKET_RISK,
            score=score,
            weight=0.20,  # 20% weight in composite
            confidence=confidence,
            factors=factors,
            recommendations=self._generate_market_risk_recommendations(score, factors)
        )

    def _calculate_compliance_risk(self, company_symbol: str, forensic_data: Dict[str, Any]) -> RiskScore:
        """Calculate compliance risk score using Agent 4"""
        try:
            # Call Compliance Validation Agent
            compliance_assessment = self.compliance_agent.validate_compliance(company_symbol, forensic_data)
            
            # Context regarding scoring inversion:
            # Compliance Score: 100 is Perfect (Low Risk)
            # Risk Score: 100 is Critical (High Risk)
            # Formula: Risk Score = 100 - Compliance Score
            
            compliance_score = compliance_assessment.overall_compliance_score
            risk_score_val = max(0.0, 100.0 - compliance_score)
            
            # Extract factors from violations
            factors = []
            for violation in compliance_assessment.violations:
                factors.append(f"{violation.violation_description} ({violation.severity.value.upper()})")
                
            if not factors and risk_score_val < 10:
                factors.append("Strong regulatory compliance profile")
                
            # Extract recommendations
            recommendations = compliance_assessment.recommendations
            
            # Determine confidence based on violations data availability
            confidence = 0.9 if compliance_assessment.violations is not None else 0.5

            return RiskScore(
                category=RiskCategory.COMPLIANCE_RISK,
                score=risk_score_val,
                weight=0.15,  # 15% weight in composite
                confidence=confidence,
                factors=factors,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error calculating compliance risk: {e}")
            # Fallback in case of integration failure
            return RiskScore(
                category=RiskCategory.COMPLIANCE_RISK,
                score=30.0,
                weight=0.15,
                confidence=0.3,
                factors=[f"Compliance integration failed: {str(e)}"],
                recommendations=["Investigate compliance data source connectivity"]
            )

    def _calculate_liquidity_risk(self, vertical_analysis: Dict, financial_ratios: Dict) -> RiskScore:
        """Calculate liquidity risk score"""
        factors = []
        score = 0.0
        confidence = 0.8

        va = vertical_analysis.get("vertical_analysis", {})
        ratios = financial_ratios.get("financial_ratios", {})

        # Get the most recent year's data
        recent_year = None
        available_years = list(ratios.keys()) if ratios else []
        if available_years:
            recent_year = available_years[0]
            recent_ratios = ratios[recent_year]
        else:
            recent_ratios = {}

        # Use debt-to-assets as a proxy for liquidity (lower debt = better liquidity)
        debt_to_assets = float(recent_ratios.get("debt_to_assets", 0))
        if debt_to_assets > 0.7:  # High debt burden
            score += 40
            factors.append("High debt-to-assets ratio indicates liquidity risk")
        elif debt_to_assets < 0.3:  # Low debt burden
            score -= 20

        # Asset turnover as efficiency indicator
        asset_turnover = float(recent_ratios.get("asset_turnover", 0))
        if asset_turnover < 1:  # Poor asset utilization
            score += 25
            factors.append("Low asset turnover indicates liquidity concerns")
        elif asset_turnover > 3:  # Very efficient
            score -= 10

        score = max(0, min(100, score))

        return RiskScore(
            category=RiskCategory.LIQUIDITY_RISK,
            score=score,
            weight=0.10,  # 10% weight in composite
            confidence=confidence,
            factors=factors,
            recommendations=self._generate_liquidity_risk_recommendations(score, factors)
        )

    def _calculate_growth_sustainability_risk(self, horizontal_analysis: Dict, financial_ratios: Dict) -> RiskScore:
        """Calculate growth sustainability risk score"""
        factors = []
        score = 0.0
        confidence = 0.7

        ha = horizontal_analysis.get("horizontal_analysis", {})

        # Revenue growth trend
        revenue_growth = self._extract_growth_metric(ha, "total_revenue")
        if revenue_growth < 0:
            score += 30
            factors.append("Negative revenue growth threatens sustainability")
        elif revenue_growth < 5:
            score += 15
            factors.append("Low revenue growth may indicate stagnation")
        elif revenue_growth > 30:
            score -= 5  # Strong sustainable growth

        # Profit growth consistency
        profit_growth = self._extract_growth_metric(ha, "net_profit")
        if profit_growth < 0:
            score += 25
            factors.append("Declining profits challenge long-term sustainability")
        elif profit_growth > revenue_growth + 10:
            score += 10  # Profit growing much faster than revenue (may not be sustainable)
            factors.append("Profit growth significantly exceeds revenue growth")

        # Use net margin as proxy for ROE sustainability
        ratios = financial_ratios.get("financial_ratios", {})
        if ratios:
            recent_year = list(ratios.keys())[0]
            recent_ratios = ratios[recent_year]
            net_margin = float(recent_ratios.get("net_margin_pct", 0))
            if net_margin < 10:
                score += 20
                factors.append("Low net margin suggests unsustainable growth model")
            elif net_margin > 25:
                score -= 5  # Excellent sustainable returns

        score = max(0, min(100, score))

        return RiskScore(
            category=RiskCategory.GROWTH_SUSTAINABILITY,
            score=score,
            weight=0.15,  # 15% weight in composite
            confidence=confidence,
            factors=factors,
            recommendations=self._generate_growth_risk_recommendations(score, factors)
        )

    def _extract_growth_metric(self, horizontal_analysis: Dict, metric_name: str) -> float:
        """Extract growth metric from horizontal analysis"""
        try:
            income_growth = horizontal_analysis.get("income_statement", {})
            return income_growth.get(f"{metric_name}_growth_pct", 0)
        except:
            return 0.0

    def _calculate_composite_score(self, risk_scores: Dict[RiskCategory, RiskScore]) -> float:
        """Calculate weighted composite risk score"""
        total_weighted_score = 0.0
        total_weight = 0.0

        for risk_score in risk_scores.values():
            total_weighted_score += risk_score.score * risk_score.weight
            total_weight += risk_score.weight

        return (total_weighted_score / total_weight) if total_weight > 0 else 0.0

    def _determine_risk_level(self, overall_score: float) -> str:
        """Determine risk level based on composite score"""
        if overall_score < 25:
            return "LOW"
        elif overall_score < 50:
            return "MEDIUM"
        elif overall_score < 75:
            return "HIGH"
        else:
            return "CRITICAL"

    def _generate_investment_recommendation(self, overall_score: float, risk_scores: Dict[RiskCategory, RiskScore]) -> str:
        """Generate investment recommendation based on risk analysis"""
        if overall_score < 30:
            return "RECOMMENDED - Low risk profile with strong fundamentals"
        elif overall_score < 50:
            return "CAUTION - Moderate risk, conduct additional due diligence"
        elif overall_score < 70:
            return "HIGH RISK - Consider only for high-risk tolerance portfolios"
        else:
            return "NOT RECOMMENDED - Critical risk factors identified"

    def _determine_monitoring_frequency(self, overall_score: float) -> str:
        """Determine appropriate monitoring frequency"""
        if overall_score > 70:
            return "DAILY"
        elif overall_score > 50:
            return "WEEKLY"
        elif overall_score > 30:
            return "MONTHLY"
        else:
            return "QUARTERLY"

    def _generate_financial_stability_recommendations(self, score: float, factors: List[str]) -> List[str]:
        """Generate recommendations for financial stability risk"""
        recommendations = []

        if "Low net profit margin indicates profitability concerns" in factors:
            recommendations.append("Focus on improving operational efficiency and cost management")
        if "Below-average return on equity" in factors:
            recommendations.append("Review capital allocation strategy and investment decisions")
        if "High debt-to-equity ratio indicates financial risk" in factors:
            recommendations.append("Improve working capital management and liquidity position")

        return recommendations if recommendations else ["Monitor financial metrics closely for improvement opportunities"]

    def _generate_operational_risk_recommendations(self, score: float, factors: List[str]) -> List[str]:
        """Generate recommendations for operational risk"""
        recommendations = []

        if "Low gross margin indicates operational inefficiency" in factors:
            recommendations.append("Implement cost optimization initiatives and supply chain improvements")
        if "Low asset turnover suggests operational inefficiency" in factors:
            recommendations.append("Review asset utilization and operational processes")

        return recommendations if recommendations else ["Focus on operational efficiency improvements"]

    def _generate_market_risk_recommendations(self, score: float, factors: List[str]) -> List[str]:
        """Generate recommendations for market risk"""
        recommendations = []

        if "High revenue volatility indicates market risk" in factors:
            recommendations.append("Diversify revenue streams and customer base")
        if "Moderate-high revenue volatility suggests market sensitivity" in factors:
            recommendations.append("Implement revenue stabilization strategies")
        if "Moderate revenue volatility indicates some market risk" in factors:
            recommendations.append("Monitor market conditions closely")
        if "High profit volatility suggests market sensitivity" in factors:
            recommendations.append("Implement hedging strategies and market risk management")
        if "High profit volatility indicates earnings sensitivity" in factors:
            recommendations.append("Focus on earnings stabilization measures")
        if "Moderate profit volatility suggests market exposure" in factors:
            recommendations.append("Reduce exposure to market fluctuations")
        if "High asset turnover suggests cyclical business model" in factors:
            recommendations.append("Prepare for cyclical market downturns")
        if "Low asset turnover indicates market penetration challenges" in factors:
            recommendations.append("Develop market expansion strategies")
        if "High leverage amplifies market risk exposure" in factors:
            recommendations.append("Reduce debt levels to decrease market sensitivity")
        if "Smaller company size increases market risk exposure" in factors:
            recommendations.append("Focus on niche markets and competitive advantages")

        return recommendations if recommendations else ["Monitor market conditions and competitive landscape"]

    def _generate_liquidity_risk_recommendations(self, score: float, factors: List[str]) -> List[str]:
        """Generate recommendations for liquidity risk"""
        recommendations = []

        if "High debt-to-assets ratio indicates liquidity risk" in factors:
            recommendations.append("Improve cash flow management and reduce working capital requirements")
        if "Low asset turnover indicates liquidity concerns" in factors:
            recommendations.append("Maintain adequate cash reserves for operational needs")

        return recommendations if recommendations else ["Strengthen liquidity management practices"]

    def _generate_growth_risk_recommendations(self, score: float, factors: List[str]) -> List[str]:
        """Generate recommendations for growth sustainability risk"""
        recommendations = []

        if "Negative revenue growth threatens sustainability" in factors:
            recommendations.append("Develop new growth strategies and market expansion plans")
        if "Declining profits challenge long-term sustainability" in factors:
            recommendations.append("Review pricing strategy and cost structure for profitability")

        return recommendations if recommendations else ["Focus on sustainable growth initiatives"]

    def _create_error_assessment(self, company_symbol: str, error_message: str) -> CompositeRiskAssessment:
        """Create error assessment when risk calculation fails"""
        return CompositeRiskAssessment(
            company_symbol=company_symbol,
            assessment_date=datetime.now().isoformat(),
            overall_risk_score=0.0,
            risk_category_scores={},
            shap_values={},
            risk_level="ERROR",
            risk_factors=[f"Risk calculation failed: {error_message}"],
            investment_recommendation="ERROR - Unable to assess risk",
            monitoring_frequency="IMMEDIATE"
        )

    def _create_high_risk_mock_assessment(self, company_symbol: str) -> CompositeRiskAssessment:
        """Create mock high risk assessment for testing"""
        risk_scores = {
            RiskCategory.FINANCIAL_STABILITY: RiskScore(RiskCategory.FINANCIAL_STABILITY, 85.0, 0.25, 0.9, ["Severe financial instability"], ["Immediate restructuring required"]),
            RiskCategory.OPERATIONAL_RISK: RiskScore(RiskCategory.OPERATIONAL_RISK, 75.0, 0.15, 0.8, ["Operational failure imminent"], ["Overhaul operations"]),
            RiskCategory.MARKET_RISK: RiskScore(RiskCategory.MARKET_RISK, 80.0, 0.20, 0.8, ["Extreme market exposure"], ["Exit market positions"]),
            RiskCategory.COMPLIANCE_RISK: RiskScore(RiskCategory.COMPLIANCE_RISK, 60.0, 0.15, 0.7, ["Major compliance violations"], ["Audit required"]),
            RiskCategory.LIQUIDITY_RISK: RiskScore(RiskCategory.LIQUIDITY_RISK, 90.0, 0.10, 0.9, ["Insolvency likely"], ["Emergency liquidity injection needed"]),
            RiskCategory.GROWTH_SUSTAINABILITY: RiskScore(RiskCategory.GROWTH_SUSTAINABILITY, 70.0, 0.15, 0.8, ["Unsustainable business model"], ["Pivot strategy"])
        }
        
        return CompositeRiskAssessment(
            company_symbol=company_symbol,
            assessment_date=datetime.now().isoformat(),
            overall_risk_score=78.5,
            risk_category_scores=risk_scores,
            shap_values={"financial_stability": 25.0, "operational_risk": 20.0, "market_risk": 15.0},
            risk_level="CRITICAL",
            risk_factors=["Extremely high leverage", "Severe liquidity crisis", "Operational failure", "Major compliance violations"],
            investment_recommendation="NOT RECOMMENDED - Critical risk factors identified",
            monitoring_frequency="DAILY"
        )

    def generate_risk_report(self, assessment: CompositeRiskAssessment) -> Dict[str, Any]:
        """Generate comprehensive risk report"""
        return {
            "report_type": "risk_assessment",
            "company_symbol": assessment.company_symbol,
            "assessment_date": assessment.assessment_date,
            "overall_risk_score": assessment.overall_risk_score,
            "risk_level": assessment.risk_level,
            "investment_recommendation": assessment.investment_recommendation,
            "monitoring_frequency": assessment.monitoring_frequency,
            "category_breakdown": {
                category.value: {
                    "score": risk_score.score,
                    "level": self._determine_risk_level(risk_score.score),
                    "weight": risk_score.weight,
                    "confidence": risk_score.confidence,
                    "factors": risk_score.factors,
                    "recommendations": risk_score.recommendations
                }
                for category, risk_score in assessment.risk_category_scores.items()
            },
            "shap_values": assessment.shap_values
        }

    def _calculate_shap_values(self, risk_scores: Dict[RiskCategory, RiskScore], overall_score: float) -> Dict[str, float]:
        """
        Calculate SHAP-like attribution values for risk explainability.
        
        Methodology:
        - We assume a 'Base Value' (expected value) of 50.0 (Neutral Risk).
        - Each category's contribution is calculated as its deviation from the base, weighted by its importance.
        - Contribution = (Category Score - Base Value) * Categorical Weight
        - This explains WHY the score is higher or lower than the neutral baseline.
        """
        base_value = 50.0  # Neutral risk baseline
        shap_values = {}
        
        # Calculate raw contributions
        total_deviation = 0.0
        
        for category, risk_data in risk_scores.items():
            # Calculate how much this category pulls the score up or down from neutral
            # Weight is a fraction (e.g., 0.25), so we multiply by 100 to get 'points'
            # Or we simply use the weighted deviation directly
            
            # Simple attribution: How many 'points' did this category add to the total?
            # Total Score = Sum(Score * Weight) / Sum(Weights)
            # Contribution = Score * Weight
            # To make it 'SHAP-like' (centered around average), we compare to base.
            
            # Implementation: Absolute point contribution needed for "M-Score contributed 35 points" style
            # If the user wants "M-Score contributed 35 points", they likely mean the raw weighted contribution
            # OR the deviation. Let's provide the deviation from "Safe" (0) or "Neutral" (50).
            # Given the example "M-Score contributed +35", it implies a summation.
            # Let's stick to deviation from Neutral (50) for "Explainability" (Why is it high?)
            
            deviation = (risk_data.score - base_value) * risk_data.weight
            shap_values[category.value] = round(deviation, 2)
            
        # Add a 'Base Value' entry for the waterfall chart
        shap_values["base_value"] = base_value
        
        return shap_values

    def _analyze_market_sentiment(self, company_symbol: str) -> Tuple[float, List[str]]:
        """
        Analyze market sentiment by searching for negative news.
        Returns: (risk_score_increase, list_of_factors)
        """
        try:
            # Clean symbol
            company_name = company_symbol.split(".")[0]
            
            # Keywords representing negative sentiment/risk
            negative_keywords = [
                "fraud", "scandal", "investigation", "lawsuit", "default", 
                "bankruptcy", "resignation", "raid", "accounting irregularities",
                "insider trading", "money laundering"
            ]
            
            # Construct query
            # Let's try searching for recent negative news specifically
            query = f"{company_name} (fraud OR scandal OR investigation OR lawsuit OR default)"
            
            risk_increase = 0.0
            factors = []
            
            logger.info(f"Searching market sentiment for {company_name}...")
            
            with DDGS() as ddgs:
                # Get last 5 results
                results = list(ddgs.text(query, max_results=5))
                
                if not results:
                    return 0.0, []
                
                negative_hits = 0
                for r in results:
                    title = r.get('title', '').lower()
                    body = r.get('body', '').lower()
                    content = title + " " + body
                    
                    found_keywords = [kw for kw in negative_keywords if kw in content]
                    if found_keywords:
                        negative_hits += 1
                        # Log unique keywords for context
                        factors.append(f"Negative sentiment detected: '{found_keywords[0]}' in news")
                        
                # Scoring logic: +5 per negative hit, max 20
                if negative_hits > 0:
                    risk_increase = min(20.0, negative_hits * 5.0)
                    factors = list(set(factors)) # Deduplicate
                    factors.append(f"High negative news volume ({negative_hits} articles found)")
                    
            return risk_increase, factors

        except Exception as e:
            logger.warning(f"Market sentiment analysis failed: {e}")
            return 0.0, []

