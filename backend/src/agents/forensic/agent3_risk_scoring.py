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

from models import Company, FinancialStatement, StatementType, ReportingPeriod
from database.connection import get_db_client
from config import settings

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
    """Complete risk assessment results"""
    company_symbol: str
    assessment_date: str
    overall_risk_score: float  # Weighted average of all categories
    risk_category_scores: Dict[RiskCategory, RiskScore]
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    risk_factors: List[str]
    investment_recommendation: str
    monitoring_frequency: str  # DAILY, WEEKLY, MONTHLY, QUARTERLY

class RiskScoringAgent:
    """Agent 3: Risk scoring with 6-category weighted composite"""

    def __init__(self):
        self.db_client = get_db_client()
        logger.info("Risk Scoring Agent initialized")

    def calculate_risk_score(self, company_symbol: str, forensic_data: Dict[str, Any]) -> CompositeRiskAssessment:
        """Calculate comprehensive risk score from forensic analysis data"""
        try:
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

            # 3. Market Risk
            risk_scores[RiskCategory.MARKET_RISK] = self._calculate_market_risk(
                horizontal_analysis, financial_ratios
            )

            # 4. Compliance Risk (placeholder - would integrate with Agent 4)
            risk_scores[RiskCategory.COMPLIANCE_RISK] = self._calculate_compliance_risk()

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
                risk_level=risk_level,
                risk_factors=list(set(all_factors)),  # Remove duplicates
                investment_recommendation=investment_recommendation,
                monitoring_frequency=monitoring_frequency
            )

        except Exception as e:
            logger.error(f"Failed to calculate risk score for {company_symbol}: {e}")
            return self._create_error_assessment(company_symbol, str(e))

    def _calculate_financial_stability_risk(self, vertical_analysis: Dict, horizontal_analysis: Dict, financial_ratios: Dict) -> RiskScore:
        """Calculate financial stability risk score"""
        factors = []
        score = 0.0
        confidence = 0.8

        # Check profitability indicators
        va = vertical_analysis.get("vertical_analysis", {})
        ha = horizontal_analysis.get("horizontal_analysis", {})
        ratios = financial_ratios.get("financial_ratios", {})

        # Net profit margin analysis
        net_margin = ratios.get("net_profit_margin_pct", 0)
        if net_margin < 5:  # Less than 5% margin
            score += 25
            factors.append("Low net profit margin indicates profitability concerns")
        elif net_margin > 15:  # Strong margin
            score -= 10
            confidence += 0.1

        # ROE analysis
        roe = ratios.get("return_on_equity_pct", 0)
        if roe < 10:  # Below average ROE
            score += 20
            factors.append("Below-average return on equity")
        elif roe > 20:  # Strong ROE
            score -= 5

        # Debt-to-equity analysis
        current_ratio = ratios.get("current_ratio", 0)
        if current_ratio < 1:  # Inadequate liquidity
            score += 30
            factors.append("Current ratio below 1 indicates liquidity risk")
        elif current_ratio > 2:  # Very strong liquidity
            score -= 10

        # Growth stability
        revenue_growth = self._extract_growth_metric(ha, "total_revenue")
        if revenue_growth < 0:  # Declining revenue
            score += 15
            factors.append("Declining revenue trend")
        elif revenue_growth > 20:  # Strong growth
            score -= 5

        # Asset quality
        total_assets = va.get("balance_sheet", {}).get("total_assets_pct", 0)
        if total_assets < 50:  # Weak asset base
            score += 10
            factors.append("Weak asset base relative to revenue")

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

    def _calculate_operational_risk(self, vertical_analysis: Dict, financial_ratios: Dict) -> RiskScore:
        """Calculate operational risk score"""
        factors = []
        score = 0.0
        confidence = 0.7

        va = vertical_analysis.get("vertical_analysis", {})
        ratios = financial_ratios.get("financial_ratios", {})

        # Cost management
        cost_revenue_pct = va.get("income_statement", {}).get("cost_of_revenue_pct", 0)
        if cost_revenue_pct > 80:  # High cost ratio
            score += 20
            factors.append("High cost of revenue ratio indicates operational inefficiency")
        elif cost_revenue_pct < 60:  # Efficient operations
            score -= 10

        # Asset turnover (simplified)
        roa = ratios.get("return_on_assets_pct", 0)
        if roa < 5:  # Poor asset utilization
            score += 15
            factors.append("Low return on assets suggests operational inefficiency")
        elif roa > 15:  # Excellent asset utilization
            score -= 5

        # Inventory management (if available)
        # This would be enhanced with actual inventory data

        score = max(0, min(100, score))

        return RiskScore(
            category=RiskCategory.OPERATIONAL_RISK,
            score=score,
            weight=0.15,  # 15% weight in composite
            confidence=confidence,
            factors=factors,
            recommendations=self._generate_operational_risk_recommendations(score, factors)
        )

    def _calculate_market_risk(self, horizontal_analysis: Dict, financial_ratios: Dict) -> RiskScore:
        """Calculate market risk score"""
        factors = []
        score = 0.0
        confidence = 0.6

        ha = horizontal_analysis.get("horizontal_analysis", {})

        # Revenue volatility
        revenue_growth = self._extract_growth_metric(ha, "total_revenue")
        if abs(revenue_growth) > 50:  # High volatility
            score += 25
            factors.append("High revenue volatility indicates market risk")
        elif abs(revenue_growth) < 10:  # Stable growth
            score -= 5

        # Profit volatility
        profit_growth = self._extract_growth_metric(ha, "net_profit")
        if abs(profit_growth) > 100:  # Extreme profit swings
            score += 20
            factors.append("High profit volatility suggests market sensitivity")
        elif abs(profit_growth) < 20:  # Stable profits
            score -= 5

        # Market position (simplified)
        # This would be enhanced with market share data

        score = max(0, min(100, score))

        return RiskScore(
            category=RiskCategory.MARKET_RISK,
            score=score,
            weight=0.20,  # 20% weight in composite
            confidence=confidence,
            factors=factors,
            recommendations=self._generate_market_risk_recommendations(score, factors)
        )

    def _calculate_compliance_risk(self) -> RiskScore:
        """Calculate compliance risk score (placeholder)"""
        # This would be enhanced with actual compliance data from Agent 4

        return RiskScore(
            category=RiskCategory.COMPLIANCE_RISK,
            score=30.0,  # Placeholder - would be calculated based on actual compliance data
            weight=0.15,  # 15% weight in composite
            confidence=0.5,  # Lower confidence until Agent 4 is integrated
            factors=["Compliance assessment requires integration with regulatory data sources"],
            recommendations=["Integrate with SEBI compliance monitoring systems", "Implement automated compliance checking"]
        )

    def _calculate_liquidity_risk(self, vertical_analysis: Dict, financial_ratios: Dict) -> RiskScore:
        """Calculate liquidity risk score"""
        factors = []
        score = 0.0
        confidence = 0.8

        va = vertical_analysis.get("vertical_analysis", {})
        ratios = financial_ratios.get("financial_ratios", {})

        # Current ratio analysis
        current_ratio = ratios.get("current_ratio", 0)
        if current_ratio < 1.0:
            score += 40
            factors.append("Current ratio below 1.0 indicates severe liquidity risk")
        elif current_ratio < 1.5:
            score += 20
            factors.append("Current ratio below 1.5 suggests moderate liquidity concerns")
        elif current_ratio > 3.0:
            score += 10
            factors.append("Very high current ratio may indicate inefficient asset utilization")

        # Quick ratio analysis
        quick_ratio = ratios.get("quick_ratio", 0)
        if quick_ratio < 0.8:
            score += 25
            factors.append("Quick ratio below 0.8 indicates immediate liquidity risk")
        elif quick_ratio > 2.0:
            score -= 5

        # Cash position (simplified)
        # This would be enhanced with actual cash flow data

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

        # ROE sustainability
        roe = financial_ratios.get("financial_ratios", {}).get("return_on_equity_pct", 0)
        if roe < 8:
            score += 20
            factors.append("Low ROE suggests unsustainable growth model")
        elif roe > 25:
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

        if "Low net profit margin" in " ".join(factors):
            recommendations.append("Focus on improving operational efficiency and cost management")
        if "Below-average return on equity" in " ".join(factors):
            recommendations.append("Review capital allocation strategy and investment decisions")
        if "Current ratio below" in " ".join(factors):
            recommendations.append("Improve working capital management and liquidity position")

        return recommendations if recommendations else ["Monitor financial metrics closely for improvement opportunities"]

    def _generate_operational_risk_recommendations(self, score: float, factors: List[str]) -> List[str]:
        """Generate recommendations for operational risk"""
        recommendations = []

        if "High cost of revenue" in " ".join(factors):
            recommendations.append("Implement cost optimization initiatives and supply chain improvements")
        if "Low return on assets" in " ".join(factors):
            recommendations.append("Review asset utilization and operational processes")

        return recommendations if recommendations else ["Focus on operational efficiency improvements"]

    def _generate_market_risk_recommendations(self, score: float, factors: List[str]) -> List[str]:
        """Generate recommendations for market risk"""
        recommendations = []

        if "High revenue volatility" in " ".join(factors):
            recommendations.append("Diversify revenue streams and customer base")
        if "High profit volatility" in " ".join(factors):
            recommendations.append("Implement hedging strategies and market risk management")

        return recommendations if recommendations else ["Monitor market conditions and competitive landscape"]

    def _generate_liquidity_risk_recommendations(self, score: float, factors: List[str]) -> List[str]:
        """Generate recommendations for liquidity risk"""
        recommendations = []

        if "Current ratio below" in " ".join(factors):
            recommendations.append("Improve cash flow management and reduce working capital requirements")
        if "Quick ratio below" in " ".join(factors):
            recommendations.append("Maintain adequate cash reserves for operational needs")

        return recommendations if recommendations else ["Strengthen liquidity management practices"]

    def _generate_growth_risk_recommendations(self, score: float, factors: List[str]) -> List[str]:
        """Generate recommendations for growth sustainability risk"""
        recommendations = []

        if "Negative revenue growth" in " ".join(factors):
            recommendations.append("Develop new growth strategies and market expansion plans")
        if "Declining profits" in " ".join(factors):
            recommendations.append("Review pricing strategy and cost structure for profitability")

        return recommendations if recommendations else ["Focus on sustainable growth initiatives"]

    def _create_error_assessment(self, company_symbol: str, error_message: str) -> CompositeRiskAssessment:
        """Create error assessment when risk calculation fails"""
        return CompositeRiskAssessment(
            company_symbol=company_symbol,
            assessment_date=datetime.now().isoformat(),
            overall_risk_score=0.0,
            risk_category_scores={},
            risk_level="ERROR",
            risk_factors=[f"Risk calculation failed: {error_message}"],
            investment_recommendation="ERROR - Unable to assess risk",
            monitoring_frequency="IMMEDIATE"
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
                    "weight": risk_score.weight,
                    "confidence": risk_score.confidence,
                    "factors": risk_score.factors,
                    "recommendations": risk_score.recommendations
                }
                for category, risk_score in assessment.risk_category_scores.items()
            },
            "key_risk_factors": assessment.risk_factors,
            "generated_at": datetime.now().isoformat(),
            "agent_version": "3.0.0"
        }
