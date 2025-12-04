#!/usr/bin/env python3
"""
Forensic Analysis Service - Database Operations
Handles persistence of forensic analysis results and anomalies
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.database.connection import get_db_session
from src.models.forensic_analysis import (
    ForensicAnalysis, FinancialAnomaly, AnalysisJob,
    AnomalyType, SeverityLevel, AnalysisStatus
)
from src.models.company import Company

logger = logging.getLogger(__name__)


class ForensicAnalysisService:
    """Service for persisting forensic analysis results to database"""

    def __init__(self):
        self.db_session = get_db_session()

    def save_forensic_analysis(self, company_symbol: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Save comprehensive forensic analysis results to database"""
        try:
            with self.db_session() as session:
                # Get or create company
                company = self._get_or_create_company(session, company_symbol)

                # Create analysis job
                job = self._create_analysis_job(session, company.id, analysis_results)

                # Create forensic analysis record
                forensic_analysis = self._create_forensic_analysis(
                    session, job.id, company.id, analysis_results
                )

                # Save individual anomalies
                anomalies_saved = self._save_anomalies(
                    session, forensic_analysis.id, company.id, analysis_results
                )

                # Update job status
                job.status = AnalysisStatus.COMPLETED
                job.completed_at = datetime.utcnow()
                job.result_summary = {
                    "anomalies_detected": anomalies_saved,
                    "analysis_types": list(analysis_results.keys()),
                    "overall_risk_score": analysis_results.get("overall_risk_score", 0)
                }

                session.commit()

                logger.info(f"Forensic analysis saved for {company_symbol}: {anomalies_saved} anomalies")

                return {
                    "success": True,
                    "job_id": job.job_id,
                    "forensic_analysis_id": forensic_analysis.id,
                    "anomalies_saved": anomalies_saved
                }

        except SQLAlchemyError as e:
            logger.error(f"Database error saving forensic analysis: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Error saving forensic analysis: {e}")
            return {"success": False, "error": str(e)}

    def _get_or_create_company(self, session: Session, symbol: str) -> Company:
        """Get existing company or create new one"""
        company = session.query(Company).filter_by(symbol=symbol).first()

        if not company:
            company = Company(
                symbol=symbol,
                name=f"Company {symbol}",  # Placeholder name
                sector="Unknown",
                industry="Unknown",
                created_at=datetime.utcnow()
            )
            session.add(company)
            session.flush()  # Get the ID

        return company

    def _create_analysis_job(self, session: Session, company_id: int, results: Dict[str, Any]) -> AnalysisJob:
        """Create analysis job record"""
        job = AnalysisJob(
            job_id=str(uuid.uuid4()),
            job_type="FORENSIC",
            company_id=company_id,
            period_start=datetime.utcnow(),  # Could be extracted from results
            period_end=datetime.utcnow(),
            analysis_type="comprehensive",
            status=AnalysisStatus.ANALYZING,
            started_at=datetime.utcnow(),
            progress_percentage=100
        )
        session.add(job)
        session.flush()
        return job

    def _create_forensic_analysis(self, session: Session, job_id: int, company_id: int,
                                results: Dict[str, Any]) -> ForensicAnalysis:
        """Create forensic analysis record"""
        forensic_analysis = ForensicAnalysis(
            job_id=job_id,
            company_id=company_id,
            analysis_start_date=datetime.utcnow(),
            analysis_end_date=datetime.utcnow(),

            # Extract key metrics from results
            benford_chi_square=results.get("benford_analysis", {}).get("benford_analysis", {}).get("chi_square_statistic"),
            benford_passes_test=not results.get("benford_analysis", {}).get("benford_analysis", {}).get("is_anomalous", True),

            z_score=results.get("altman_z_score", {}).get("altman_z_score", {}).get("z_score"),
            z_score_category=results.get("altman_z_score", {}).get("altman_z_score", {}).get("classification"),

            m_score=results.get("beneish_m_score", {}).get("beneish_m_score", {}).get("m_score"),
            m_score_probability=results.get("beneish_m_score", {}).get("beneish_m_score", {}).get("is_likely_manipulator", False),

            overall_risk_score=results.get("overall_risk_score", 0),

            # Store complete results as JSON
            key_findings=self._extract_key_findings(results),
            red_flags=self._extract_red_flags(results)
        )

        session.add(forensic_analysis)
        session.flush()
        return forensic_analysis

    def _save_anomalies(self, session: Session, forensic_analysis_id: int, company_id: int,
                       results: Dict[str, Any]) -> int:
        """Save individual anomalies to database"""
        anomalies_data = results.get("anomaly_detection", {}).get("anomalies", [])
        saved_count = 0

        for anomaly_data in anomalies_data:
            try:
                # Map anomaly type and severity
                anomaly_type = self._map_anomaly_type(anomaly_data.get("type", ""))
                severity = self._map_severity_level(anomaly_data.get("severity", "MEDIUM"))

                if not anomaly_type:
                    logger.warning(f"Unknown anomaly type: {anomaly_data.get('type')}")
                    continue

                anomaly = FinancialAnomaly(
                    forensic_analysis_id=forensic_analysis_id,
                    company_id=company_id,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    confidence_score=0.8,  # Default confidence

                    title=anomaly_data.get("description", ""),
                    description=anomaly_data.get("description", ""),
                    evidence=anomaly_data.get("evidence", {}),
                    affected_periods=[anomaly_data.get("period")],

                    detection_method="rule_based",
                    detection_date=datetime.utcnow()
                )

                session.add(anomaly)
                saved_count += 1

            except Exception as e:
                logger.error(f"Error saving anomaly {anomaly_data.get('type')}: {e}")
                continue

        return saved_count

    def _map_anomaly_type(self, anomaly_type_str: str) -> Optional[AnomalyType]:
        """Map string anomaly type to enum"""
        type_mapping = {
            "REVENUE_DECLINE": AnomalyType.REVENUE_RECOGNITION,
            "PROFIT_CASH_DIVERGENCE": AnomalyType.CASH_FLOW_DIVERGENCE,
            "RECEIVABLES_BUILDUP": AnomalyType.ASSET_OVERSTATEMENT,
            "BENFORD_LAW_VIOLATION": AnomalyType.BENFORD_LAW_VIOLATION,
        }

        return type_mapping.get(anomaly_type_str)

    def _map_severity_level(self, severity_str: str) -> SeverityLevel:
        """Map string severity to enum"""
        severity_mapping = {
            "LOW": SeverityLevel.LOW,
            "MEDIUM": SeverityLevel.MEDIUM,
            "HIGH": SeverityLevel.HIGH,
            "CRITICAL": SeverityLevel.CRITICAL
        }

        return severity_mapping.get(severity_str, SeverityLevel.MEDIUM)

    def _extract_key_findings(self, results: Dict[str, Any]) -> str:
        """Extract key findings from analysis results"""
        findings = []

        # Check for anomalies
        anomalies = results.get("anomaly_detection", {}).get("anomalies", [])
        if anomalies:
            findings.append(f"Detected {len(anomalies)} financial anomalies")

        # Check Benford's Law
        benford = results.get("benford_analysis", {}).get("benford_analysis", {})
        if benford.get("is_anomalous"):
            findings.append("Benford's Law analysis indicates potential data manipulation")

        # Check Z-Score
        z_score = results.get("altman_z_score", {}).get("altman_z_score", {})
        if z_score.get("classification") == "DISTRESS":
            findings.append("Altman Z-Score indicates high bankruptcy risk")

        # Check M-Score
        m_score = results.get("beneish_m_score", {}).get("beneish_m_score", {})
        if m_score.get("is_likely_manipulator"):
            findings.append("Beneish M-Score suggests potential earnings manipulation")

        return "; ".join(findings) if findings else "No significant findings"

    def _extract_red_flags(self, results: Dict[str, Any]) -> List[str]:
        """Extract red flags from analysis results"""
        red_flags = []

        # Anomaly-based red flags
        anomalies = results.get("anomaly_detection", {}).get("anomalies", [])
        for anomaly in anomalies:
            if anomaly.get("severity") in ["HIGH", "CRITICAL"]:
                red_flags.append(f"{anomaly['type']}: {anomaly['description']}")

        # Benford's Law red flag
        benford = results.get("benford_analysis", {}).get("benford_analysis", {})
        if benford.get("is_anomalous"):
            red_flags.append("Benford's Law violation detected")

        # Z-Score red flag
        z_score = results.get("altman_z_score", {}).get("altman_z_score", {})
        if z_score.get("classification") == "DISTRESS":
            red_flags.append("High bankruptcy risk (Altman Z-Score)")

        return red_flags

    def get_company_anomalies(self, company_symbol: str, limit: int = 50) -> Dict[str, Any]:
        """Retrieve recent anomalies for a company"""
        try:
            with self.db_session() as session:
                anomalies = session.query(FinancialAnomaly)\
                    .join(Company)\
                    .filter(Company.symbol == company_symbol)\
                    .order_by(FinancialAnomaly.detection_date.desc())\
                    .limit(limit)\
                    .all()

                return {
                    "success": True,
                    "anomalies": [
                        {
                            "id": a.id,
                            "type": a.anomaly_type.value,
                            "severity": a.severity.value,
                            "title": a.title,
                            "description": a.description,
                            "evidence": a.evidence,
                            "detection_date": a.detection_date.isoformat(),
                            "confidence_score": a.confidence_score
                        }
                        for a in anomalies
                    ]
                }

        except Exception as e:
            logger.error(f"Error retrieving anomalies for {company_symbol}: {e}")
            return {"success": False, "error": str(e)}
