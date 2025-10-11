"""
Project IRIS - Background Tasks
Celery task definitions for async processing
"""

from celery import shared_task
from src.config import settings


@shared_task
def forensic_analysis_task(company_id: str, start_date: str, end_date: str, period: str = 'quarter'):
    """
    Background task for complete forensic analysis
    """
    from src.agents.forensic.agent6_orchestrator import ForensicOrchestratorAgent

    orchestrator = ForensicOrchestratorAgent()
    job_id = orchestrator.execute_forensic_analysis(
        company_id,
        (start_date, end_date),
        period=period
    )

    return {
        'job_id': job_id,
        'company_id': company_id,
        'status': 'COMPLETED'
    }


@shared_task
def sentiment_analysis_task(company_id: str):
    """
    Background task for market sentiment analysis
    """
    from src.agents.forensic.agent8_sentiment import MarketSentimentAgent

    agent = MarketSentimentAgent()
    results = agent.analyze_company_sentiment(company_id)

    return {
        'company_id': company_id,
        'sentiment_score': results.get('aggregate_score', 0),
        'status': 'COMPLETED'
    }


@shared_task
def regulatory_monitoring_task(company_id: str):
    """
    Background task for regulatory monitoring
    """
    from src.agents.forensic.agent10_regulatory import RegulatoryMonitoringAgent

    agent = RegulatoryMonitoringAgent()
    results = agent.monitor_company_regulatory_status(company_id)

    return {
        'company_id': company_id,
        'violations_count': len(results.get('violations', [])),
        'status': 'COMPLETED'
    }


@shared_task
def peer_benchmarking_task(company_id: str):
    """
    Background task for peer benchmarking
    """
    from src.agents.forensic.agent9_peer_benchmarking import PeerBenchmarkingAgent

    agent = PeerBenchmarkingAgent()
    results = agent.benchmark_company_peers(company_id)

    return {
        'company_id': company_id,
        'peer_count': len(results.get('peers', [])),
        'status': 'COMPLETED'
    }
