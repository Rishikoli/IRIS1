"""
Project IRIS - Agent 4: Compliance Validation Agent
Validates compliance with Ind AS, SEBI regulations, and Companies Act requirements
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

from src.config import settings

logger = logging.getLogger(__name__)

class ComplianceFramework(Enum):
    """Compliance frameworks for validation"""
    IND_AS = "ind_as"
    SEBI = "sebi"
    COMPANIES_ACT = "companies_act"
    RBI = "rbi"
    IFRS = "ifrs"

class ComplianceSeverity(Enum):
    """Compliance violation severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class ComplianceViolation:
    """Individual compliance violation"""
    framework: ComplianceFramework
    rule_id: str
    rule_description: str
    severity: ComplianceSeverity
    violation_description: str
    evidence: Dict[str, Any]
    remediation_steps: List[str]
    regulatory_reference: str
    financial_impact: Optional[float] = None

@dataclass
class ComplianceAssessment:
    """Complete compliance assessment results"""
    company_symbol: str
    assessment_date: str
    overall_compliance_score: float  # 0-100 scale
    compliance_status: str  # COMPLIANT, NON_COMPLIANT, PARTIAL_COMPLIANCE
    violations: List[ComplianceViolation]
    framework_scores: Dict[ComplianceFramework, float]
    recommendations: List[str]
    next_review_date: str

class ComplianceValidationAgent:
    """Agent 4: Compliance validation with regulatory frameworks"""

    def __init__(self):
        try:
            from database.connection import get_db_client
            self.db_client = get_db_client()
        except Exception:
            # For standalone analysis without database
            self.db_client = None
        
        # Initialize compliance rules
        self._initialize_compliance_rules()
        logger.info("Compliance Validation Agent initialized")

    def _initialize_compliance_rules(self):
        """Initialize compliance validation rules"""
        self.compliance_rules = {
            ComplianceFramework.IND_AS: self._get_ind_as_rules(),
            ComplianceFramework.SEBI: self._get_sebi_rules(),
            ComplianceFramework.COMPANIES_ACT: self._get_companies_act_rules(),
            ComplianceFramework.RBI: self._get_rbi_rules()
        }

    def validate_compliance(self, company_symbol: str, financial_data: Dict[str, Any]) -> ComplianceAssessment:
        """Validate compliance across all regulatory frameworks"""
        try:
            logger.info(f"Starting compliance validation for {company_symbol}")
            
            violations = []
            framework_scores = {}
            
            # Validate against each framework
            for framework in ComplianceFramework:
                if framework in self.compliance_rules:
                    framework_violations = self._validate_framework(framework, financial_data)
                    violations.extend(framework_violations)
                    
                    # Calculate framework score (100 - penalty points)
                    penalty_points = sum(self._get_penalty_points(v.severity) for v in framework_violations)
                    framework_scores[framework] = max(0, 100 - penalty_points)
            
            # Calculate overall compliance score
            overall_score = sum(framework_scores.values()) / len(framework_scores) if framework_scores else 0
            
            # Determine compliance status
            compliance_status = self._determine_compliance_status(overall_score, violations)
            
            # Generate recommendations
            recommendations = self._generate_compliance_recommendations(violations)
            
            # Set next review date
            next_review_date = self._calculate_next_review_date(compliance_status)
            
            return ComplianceAssessment(
                company_symbol=company_symbol,
                assessment_date=datetime.now().isoformat(),
                overall_compliance_score=round(overall_score, 2),
                compliance_status=compliance_status,
                violations=violations,
                framework_scores=framework_scores,
                recommendations=recommendations,
                next_review_date=next_review_date
            )
            
        except Exception as e:
            logger.error(f"Compliance validation failed for {company_symbol}: {e}")
            return self._create_error_assessment(company_symbol, str(e))

    def _validate_framework(self, framework: ComplianceFramework, financial_data: Dict[str, Any]) -> List[ComplianceViolation]:
        """Validate compliance for a specific framework"""
        violations = []
        rules = self.compliance_rules.get(framework, {})
        
        for rule_id, rule_config in rules.items():
            try:
                violation = self._check_rule(framework, rule_id, rule_config, financial_data)
                if violation:
                    violations.append(violation)
            except Exception as e:
                logger.warning(f"Failed to check rule {rule_id}: {e}")
        
        return violations

    def _check_rule(self, framework: ComplianceFramework, rule_id: str, rule_config: Dict, financial_data: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Check a specific compliance rule"""
        rule_type = rule_config.get("type")
        
        if rule_type == "ratio_check":
            return self._check_ratio_rule(framework, rule_id, rule_config, financial_data)
        elif rule_type == "disclosure_check":
            return self._check_disclosure_rule(framework, rule_id, rule_config, financial_data)
        elif rule_type == "threshold_check":
            return self._check_threshold_rule(framework, rule_id, rule_config, financial_data)
        elif rule_type == "trend_check":
            return self._check_trend_rule(framework, rule_id, rule_config, financial_data)
        
        return None

    def _check_ratio_rule(self, framework: ComplianceFramework, rule_id: str, rule_config: Dict, financial_data: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Check ratio-based compliance rules"""
        try:
            # Extract financial ratios
            ratios = financial_data.get("financial_ratios", {}).get("financial_ratios", {})
            if not ratios:
                return None
            
            # Get the most recent period's ratios
            latest_period = max(ratios.keys()) if ratios else None
            if not latest_period:
                return None
            
            period_ratios = ratios[latest_period]
            
            ratio_name = rule_config.get("ratio")
            min_value = rule_config.get("min_value")
            max_value = rule_config.get("max_value")
            
            actual_value = period_ratios.get(ratio_name)
            if actual_value is None:
                return None
            
            # Check violations
            violation_found = False
            violation_desc = ""
            
            if min_value is not None and actual_value < min_value:
                violation_found = True
                violation_desc = f"{ratio_name} ({actual_value:.2f}) is below minimum required ({min_value})"
            
            if max_value is not None and actual_value > max_value:
                violation_found = True
                violation_desc = f"{ratio_name} ({actual_value:.2f}) exceeds maximum allowed ({max_value})"
            
            if violation_found:
                return ComplianceViolation(
                    framework=framework,
                    rule_id=rule_id,
                    rule_description=rule_config.get("description", ""),
                    severity=ComplianceSeverity(rule_config.get("severity", "medium")),
                    violation_description=violation_desc,
                    evidence={"actual_value": actual_value, "period": latest_period},
                    remediation_steps=rule_config.get("remediation", []),
                    regulatory_reference=rule_config.get("reference", "")
                )
            
        except Exception as e:
            logger.warning(f"Error checking ratio rule {rule_id}: {e}")
        
        return None

    def _check_disclosure_rule(self, framework: ComplianceFramework, rule_id: str, rule_config: Dict, financial_data: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Check disclosure-related compliance rules"""
        try:
            required_fields = rule_config.get("required_fields", [])
            missing_fields = []
            
            # Check vertical analysis disclosures
            vertical_analysis = financial_data.get("vertical_analysis", {}).get("vertical_analysis", {})
            
            for field in required_fields:
                if field not in vertical_analysis.get("income_statement", {}) and field not in vertical_analysis.get("balance_sheet", {}):
                    missing_fields.append(field)
            
            if missing_fields:
                return ComplianceViolation(
                    framework=framework,
                    rule_id=rule_id,
                    rule_description=rule_config.get("description", ""),
                    severity=ComplianceSeverity(rule_config.get("severity", "medium")),
                    violation_description=f"Missing required disclosures: {', '.join(missing_fields)}",
                    evidence={"missing_fields": missing_fields},
                    remediation_steps=rule_config.get("remediation", []),
                    regulatory_reference=rule_config.get("reference", "")
                )
            
        except Exception as e:
            logger.warning(f"Error checking disclosure rule {rule_id}: {e}")
        
        return None

    def _check_threshold_rule(self, framework: ComplianceFramework, rule_id: str, rule_config: Dict, financial_data: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Check threshold-based compliance rules"""
        try:
            # Check Altman Z-Score thresholds
            if "altman_z_score" in financial_data:
                altman_data = financial_data["altman_z_score"]
                if altman_data.get("success"):
                    z_score = altman_data.get("altman_z_score", {}).get("z_score", 0)
                    threshold = rule_config.get("threshold", 1.8)
                    
                    if z_score < threshold:
                        return ComplianceViolation(
                            framework=framework,
                            rule_id=rule_id,
                            rule_description=rule_config.get("description", ""),
                            severity=ComplianceSeverity(rule_config.get("severity", "high")),
                            violation_description=f"Altman Z-Score ({z_score:.2f}) below regulatory threshold ({threshold})",
                            evidence={"z_score": z_score, "threshold": threshold},
                            remediation_steps=rule_config.get("remediation", []),
                            regulatory_reference=rule_config.get("reference", "")
                        )
            
        except Exception as e:
            logger.warning(f"Error checking threshold rule {rule_id}: {e}")
        
        return None

    def _check_trend_rule(self, framework: ComplianceFramework, rule_id: str, rule_config: Dict, financial_data: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Check trend-based compliance rules"""
        try:
            # Check horizontal analysis trends
            horizontal_analysis = financial_data.get("horizontal_analysis", {}).get("horizontal_analysis", {})
            
            if horizontal_analysis:
                # Look for concerning trends
                for period_key, metrics in horizontal_analysis.items():
                    revenue_growth = metrics.get("total_revenue_growth_pct")
                    profit_growth = metrics.get("net_profit_growth_pct")
                    
                    # Check for significant revenue decline
                    if revenue_growth is not None and revenue_growth < -20:
                        return ComplianceViolation(
                            framework=framework,
                            rule_id=rule_id,
                            rule_description=rule_config.get("description", ""),
                            severity=ComplianceSeverity(rule_config.get("severity", "medium")),
                            violation_description=f"Significant revenue decline ({revenue_growth:.1f}%) requires disclosure",
                            evidence={"revenue_growth": revenue_growth, "period": period_key},
                            remediation_steps=rule_config.get("remediation", []),
                            regulatory_reference=rule_config.get("reference", "")
                        )
            
        except Exception as e:
            logger.warning(f"Error checking trend rule {rule_id}: {e}")
        
        return None

    def _get_ind_as_rules(self) -> Dict[str, Dict]:
        """Get Indian Accounting Standards compliance rules"""
        return {
            "ind_as_1_presentation": {
                "type": "disclosure_check",
                "description": "Financial statement presentation requirements",
                "required_fields": ["total_revenue", "net_profit", "total_assets", "total_equity"],
                "severity": "high",
                "reference": "Ind AS 1 - Presentation of Financial Statements",
                "remediation": ["Ensure all required line items are disclosed", "Review financial statement format"]
            },
            "ind_as_7_cash_flows": {
                "type": "ratio_check",
                "description": "Cash flow adequacy requirements",
                "ratio": "current_ratio",
                "min_value": 1.0,
                "severity": "medium",
                "reference": "Ind AS 7 - Statement of Cash Flows",
                "remediation": ["Improve working capital management", "Enhance cash flow forecasting"]
            }
        }

    def _get_sebi_rules(self) -> Dict[str, Dict]:
        """Get SEBI compliance rules"""
        return {
            "sebi_lodr_financial_results": {
                "type": "disclosure_check",
                "description": "SEBI LODR financial results disclosure",
                "required_fields": ["total_revenue", "net_profit", "total_assets"],
                "severity": "critical",
                "reference": "SEBI LODR Regulation 33",
                "remediation": ["File quarterly results within prescribed timeline", "Ensure all mandatory disclosures"]
            },
            "sebi_debt_equity_ratio": {
                "type": "ratio_check",
                "description": "Debt-equity ratio monitoring",
                "ratio": "debt_to_equity",
                "max_value": 2.0,
                "severity": "medium",
                "reference": "SEBI Guidelines on Corporate Governance",
                "remediation": ["Reduce debt levels", "Improve equity base", "Review capital structure"]
            },
            "sebi_financial_distress": {
                "type": "threshold_check",
                "description": "Financial distress monitoring",
                "threshold": 1.8,
                "severity": "high",
                "reference": "SEBI Circular on Financial Distress",
                "remediation": ["Implement turnaround strategy", "Engage with lenders", "Consider restructuring"]
            }
        }

    def _get_companies_act_rules(self) -> Dict[str, Dict]:
        """Get Companies Act compliance rules"""
        return {
            "companies_act_financial_statements": {
                "type": "disclosure_check",
                "description": "Companies Act financial statement requirements",
                "required_fields": ["total_revenue", "net_profit", "total_assets", "total_equity"],
                "severity": "critical",
                "reference": "Companies Act 2013 - Section 129",
                "remediation": ["Prepare financial statements as per prescribed format", "Ensure board approval"]
            },
            "companies_act_liquidity": {
                "type": "ratio_check",
                "description": "Minimum liquidity requirements",
                "ratio": "current_ratio",
                "min_value": 0.75,
                "severity": "high",
                "reference": "Companies Act 2013 - Section 186",
                "remediation": ["Improve liquidity position", "Review working capital management"]
            },
            "companies_act_trends": {
                "type": "trend_check",
                "description": "Material adverse changes disclosure",
                "severity": "medium",
                "reference": "Companies Act 2013 - Section 134",
                "remediation": ["Disclose material changes in annual report", "Provide management commentary"]
            }
        }

    def _get_rbi_rules(self) -> Dict[str, Dict]:
        """Get RBI compliance rules (for financial companies)"""
        return {
            "rbi_capital_adequacy": {
                "type": "ratio_check",
                "description": "Capital adequacy requirements",
                "ratio": "debt_to_equity",
                "max_value": 1.5,
                "severity": "critical",
                "reference": "RBI Master Circular on Capital Adequacy",
                "remediation": ["Increase capital base", "Reduce risk-weighted assets"]
            }
        }

    def _get_penalty_points(self, severity: ComplianceSeverity) -> int:
        """Get penalty points for violation severity"""
        penalty_map = {
            ComplianceSeverity.CRITICAL: 25,
            ComplianceSeverity.HIGH: 15,
            ComplianceSeverity.MEDIUM: 10,
            ComplianceSeverity.LOW: 5,
            ComplianceSeverity.INFO: 1
        }
        return penalty_map.get(severity, 10)

    def _determine_compliance_status(self, overall_score: float, violations: List[ComplianceViolation]) -> str:
        """Determine overall compliance status"""
        critical_violations = [v for v in violations if v.severity == ComplianceSeverity.CRITICAL]
        
        if critical_violations:
            return "NON_COMPLIANT"
        elif overall_score >= 80:
            return "COMPLIANT"
        else:
            return "PARTIAL_COMPLIANCE"

    def _generate_compliance_recommendations(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        # Priority recommendations for critical violations
        critical_violations = [v for v in violations if v.severity == ComplianceSeverity.CRITICAL]
        if critical_violations:
            recommendations.append("Address critical compliance violations immediately")
            recommendations.append("Engage with regulatory authorities if necessary")
        
        # Framework-specific recommendations
        frameworks_with_violations = set(v.framework for v in violations)
        for framework in frameworks_with_violations:
            if framework == ComplianceFramework.SEBI:
                recommendations.append("Review SEBI LODR compliance requirements")
            elif framework == ComplianceFramework.IND_AS:
                recommendations.append("Ensure Ind AS compliance in financial reporting")
            elif framework == ComplianceFramework.COMPANIES_ACT:
                recommendations.append("Review Companies Act 2013 compliance obligations")
        
        # General recommendations
        if violations:
            recommendations.append("Implement compliance monitoring system")
            recommendations.append("Conduct regular compliance audits")
            recommendations.append("Provide compliance training to management")
        
        return list(set(recommendations))  # Remove duplicates

    def _calculate_next_review_date(self, compliance_status: str) -> str:
        """Calculate next compliance review date"""
        if compliance_status == "NON_COMPLIANT":
            next_review = datetime.now() + timedelta(days=30)  # Monthly review
        elif compliance_status == "PARTIAL_COMPLIANCE":
            next_review = datetime.now() + timedelta(days=90)  # Quarterly review
        else:
            next_review = datetime.now() + timedelta(days=180)  # Semi-annual review
        
        return next_review.isoformat()

    def _create_error_assessment(self, company_symbol: str, error_message: str) -> ComplianceAssessment:
        """Create error assessment when compliance validation fails"""
        return ComplianceAssessment(
            company_symbol=company_symbol,
            assessment_date=datetime.now().isoformat(),
            overall_compliance_score=0.0,
            compliance_status="ERROR",
            violations=[],
            framework_scores={},
            recommendations=[f"Compliance validation failed: {error_message}"],
            next_review_date=datetime.now().isoformat()
        )

    def generate_compliance_report(self, assessment: ComplianceAssessment) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        return {
            "report_type": "compliance_assessment",
            "company_symbol": assessment.company_symbol,
            "assessment_date": assessment.assessment_date,
            "overall_compliance_score": assessment.overall_compliance_score,
            "compliance_status": assessment.compliance_status,
            "next_review_date": assessment.next_review_date,
            "framework_scores": {
                framework.value: score 
                for framework, score in assessment.framework_scores.items()
            },
            "violations_summary": {
                "total_violations": len(assessment.violations),
                "critical": len([v for v in assessment.violations if v.severity == ComplianceSeverity.CRITICAL]),
                "high": len([v for v in assessment.violations if v.severity == ComplianceSeverity.HIGH]),
                "medium": len([v for v in assessment.violations if v.severity == ComplianceSeverity.MEDIUM]),
                "low": len([v for v in assessment.violations if v.severity == ComplianceSeverity.LOW])
            },
            "violations": [
                {
                    "framework": violation.framework.value,
                    "rule_id": violation.rule_id,
                    "severity": violation.severity.value,
                    "description": violation.violation_description,
                    "reference": violation.regulatory_reference,
                    "remediation": violation.remediation_steps
                }
                for violation in assessment.violations
            ],
            "recommendations": assessment.recommendations,
            "generated_at": datetime.now().isoformat(),
            "agent_version": "4.0.0"
        }
