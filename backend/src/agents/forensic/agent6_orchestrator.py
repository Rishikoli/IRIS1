"""
Project IRIS - Agent 6: Orchestrator Agent (Kafka-Enabled)
Coordinates pipeline execution and job management across all forensic analysis agents
Now uses Kafka for event-driven communication
"""

import logging
import asyncio
import uuid
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json

from src.config import settings
from src.utils.kafka_utils import (
    kafka_producer, create_event, send_event,
    EventTypes, AgentTypes, KafkaConsumer, create_orchestrator_consumer
)

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    """Job execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobPriority(Enum):
    """Job priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class AnalysisJob:
    """Analysis job definition"""
    job_id: str
    company_symbol: str
    analysis_types: List[str]
    data_source: str
    periods: int
    priority: JobPriority
    status: JobStatus
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    progress: float = 0.0

@dataclass
class PipelineConfig:
    """Pipeline configuration"""
    max_concurrent_jobs: int = 3
    job_timeout_minutes: int = 30
    retry_attempts: int = 2
    enable_caching: bool = True
    cache_ttl_hours: int = 24

class OrchestratorAgent:
    """Agent 6: Pipeline coordinator and job management (Kafka-enabled)"""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.active_jobs: Dict[str, AnalysisJob] = {}
        self.job_queue: List[AnalysisJob] = []
        self.job_history: List[AnalysisJob] = []
        self.cache: Dict[str, Dict[str, Any]] = {}

        # Kafka integration
        self.kafka_consumer = create_orchestrator_consumer()
        self.event_handlers = {
            EventTypes.DATA_INGESTION_COMPLETED: self._handle_data_ingestion_completed,
            EventTypes.FORENSIC_ANALYSIS_COMPLETED: self._handle_forensic_analysis_completed,
            EventTypes.RISK_SCORING_COMPLETED: self._handle_risk_scoring_completed,
        }

        logger.info("Orchestrator Agent (Kafka-enabled) initialized")

    async def start_event_processing(self):
        """Start Kafka event processing"""
        logger.info("Starting Kafka event processing for orchestrator")

        async def event_handler(event):
            """Handle incoming Kafka events"""
            try:
                handler = self.event_handlers.get(event.event_type)
                if handler:
                    await handler(event)
                else:
                    logger.warning(f"No handler for event type: {event.event_type}")
            except Exception as e:
                logger.error(f"Error handling event {event.event_type}: {e}")

        # Start consuming events
        await self.kafka_consumer.consume_events_async(event_handler)

    def _initialize_agents(self):
        """Initialize agent connections (now through Kafka)"""
        logger.info("Agent connections established via Kafka event streaming")

    async def submit_analysis_job(self,
                                company_symbol: str,
                                analysis_types: List[str] = None,
                                data_source: str = "yahoo_finance",
                                periods: int = 2,
                                priority: JobPriority = JobPriority.NORMAL) -> str:
        """Submit a new analysis job"""

        if analysis_types is None:
            analysis_types = ["forensic", "risk", "compliance"]

        job_id = f"job_{company_symbol}_{int(datetime.now().timestamp())}"

        # Create job
        job = AnalysisJob(
            job_id=job_id,
            company_symbol=company_symbol,
            analysis_types=analysis_types,
            data_source=data_source,
            periods=periods,
            priority=priority,
            status=JobStatus.PENDING,
            created_at=datetime.utcnow().isoformat(),
            progress=0.0
        )

        # Store job
        self.active_jobs[job_id] = job

        # Send pipeline started event
        event_data = {
            "job_id": job_id,
            "company_symbol": company_symbol,
            "analysis_types": analysis_types,
            "data_source": data_source,
            "periods": periods,
            "priority": priority.value
        }

        send_event(
            EventTypes.ORCHESTRATOR_PIPELINE_STARTED,
            AgentTypes.AGENT_6_ORCHESTRATOR,
            event_data,
            company_symbol
        )

        # Trigger data ingestion first
        await self._trigger_data_ingestion(job)

        logger.info(f"Submitted analysis job {job_id} for {company_symbol}")
        return job_id

    async def _trigger_data_ingestion(self, job: AnalysisJob):
        """Trigger data ingestion via Kafka event"""
        event_data = {
            "job_id": job.job_id,
            "company_symbol": job.company_symbol,
            "data_source": job.data_source,
            "periods": job.periods
        }

        send_event(
            EventTypes.ORCHESTRATOR_AGENT_TRIGGERED,
            AgentTypes.AGENT_6_ORCHESTRATOR,
            event_data,
            job.company_symbol
        )

        logger.info(f"Triggered data ingestion for job {job.job_id}")

    async def _handle_data_ingestion_completed(self, event):
        """Handle data ingestion completion event"""
        job_id = event.data.get("job_id")
        company_symbol = event.company_symbol

        if job_id and job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = JobStatus.RUNNING
            job.progress = 25.0

            # Trigger forensic analysis
            await self._trigger_forensic_analysis(job)

            logger.info(f"Data ingestion completed for job {job_id}, starting forensic analysis")

    async def _trigger_forensic_analysis(self, job: AnalysisJob):
        """Trigger forensic analysis via Kafka event"""
        event_data = {
            "job_id": job.job_id,
            "company_symbol": job.company_symbol,
            "data_source": job.data_source
        }

        send_event(
            EventTypes.DATA_INGESTION_COMPLETED,
            AgentTypes.AGENT_6_ORCHESTRATOR,
            event_data,
            job.company_symbol
        )

        logger.info(f"Triggered forensic analysis for job {job.job_id}")

    async def _handle_forensic_analysis_completed(self, event):
        """Handle forensic analysis completion event"""
        job_id = event.data.get("job_id")
        company_symbol = event.company_symbol

        if job_id and job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.progress = 75.0

            # Trigger risk scoring
            await self._trigger_risk_scoring(job)

            logger.info(f"Forensic analysis completed for job {job_id}, starting risk scoring")

    async def _trigger_risk_scoring(self, job: AnalysisJob):
        """Trigger risk scoring via Kafka event"""
        event_data = {
            "job_id": job.job_id,
            "company_symbol": job.company_symbol
        }

        send_event(
            EventTypes.FORENSIC_ANALYSIS_COMPLETED,
            AgentTypes.AGENT_6_ORCHESTRATOR,
            event_data,
            job.company_symbol
        )

        logger.info(f"Triggered risk scoring for job {job.job_id}")

    async def _handle_risk_scoring_completed(self, event):
        """Handle risk scoring completion event"""
        job_id = event.data.get("job_id")
        company_symbol = event.company_symbol

        if job_id and job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow().isoformat()
            job.progress = 100.0

            # Move to history
            self.job_history.append(job)
            del self.active_jobs[job_id]

            # Send completion event
            event_data = {
                "job_id": job_id,
                "company_symbol": company_symbol,
                "completed_at": job.completed_at
            }

            send_event(
                EventTypes.ORCHESTRATOR_PIPELINE_COMPLETED,
                AgentTypes.AGENT_6_ORCHESTRATOR,
                event_data,
                company_symbol
            )

            logger.info(f"Analysis pipeline completed for job {job_id}")

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            return asdict(job)
        elif job_id in [job.job_id for job in self.job_history]:
            job = next(job for job in self.job_history if job.job_id == job_id)
            return asdict(job)
        else:
            return None

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.utcnow().isoformat()

            # Send cancellation event
            event_data = {
                "job_id": job_id,
                "cancelled_at": job.completed_at
            }

            send_event(
                "job_cancelled",
                AgentTypes.AGENT_6_ORCHESTRATOR,
                event_data,
                job.company_symbol
            )

            # Move to history
            self.job_history.append(job)
            del self.active_jobs[job_id]

            logger.info(f"Job {job_id} cancelled")
            return True

        return False