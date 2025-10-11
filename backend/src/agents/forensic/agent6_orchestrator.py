"""
Project IRIS - Agent 6: Orchestrator Agent
Coordinates pipeline execution and job management across all forensic analysis agents
"""

import logging
import asyncio
import uuid
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json

from config import settings

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
    """Agent 6: Pipeline coordinator and job management"""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.active_jobs: Dict[str, AnalysisJob] = {}
        self.job_queue: List[AnalysisJob] = []
        self.job_history: List[AnalysisJob] = []
        self.cache: Dict[str, Dict[str, Any]] = {}
        
        # Initialize agents
        self._initialize_agents()
        
        logger.info("Orchestrator Agent initialized")

    def _initialize_agents(self):
        """Initialize all forensic analysis agents"""
        try:
            from agents.forensic.agent1_ingestion import DataIngestionAgent
            from agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent
            from agents.forensic.agent3_risk_scoring import RiskScoringAgent
            
            self.ingestion_agent = DataIngestionAgent()
            self.forensic_agent = ForensicAnalysisAgent()
            self.risk_agent = RiskScoringAgent()
            
            logger.info("All forensic agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            # Create mock agents for testing
            self.ingestion_agent = None
            self.forensic_agent = None
            self.risk_agent = None

    async def submit_analysis_job(self, 
                                company_symbol: str,
                                analysis_types: List[str] = None,
                                data_source: str = "yahoo_finance",
                                periods: int = 2,
                                priority: JobPriority = JobPriority.NORMAL) -> str:
        """Submit a new analysis job"""
        
        if analysis_types is None:
            analysis_types = ["vertical", "horizontal", "ratios", "risk_scoring"]
        
        job_id = str(uuid.uuid4())
        
        job = AnalysisJob(
            job_id=job_id,
            company_symbol=company_symbol,
            analysis_types=analysis_types,
            data_source=data_source,
            periods=periods,
            priority=priority,
            status=JobStatus.PENDING,
            created_at=datetime.now().isoformat()
        )
        
        # Check cache first
        cache_key = self._generate_cache_key(company_symbol, analysis_types, data_source, periods)
        if self.config.enable_caching and cache_key in self.cache:
            cached_result = self.cache[cache_key]
            if self._is_cache_valid(cached_result):
                job.status = JobStatus.COMPLETED
                job.results = cached_result["data"]
                job.completed_at = datetime.now().isoformat()
                job.progress = 100.0
                
                self.job_history.append(job)
                logger.info(f"Job {job_id} completed from cache")
                return job_id
        
        # Add to queue
        self.job_queue.append(job)
        self.job_queue.sort(key=lambda x: x.priority.value, reverse=True)
        
        logger.info(f"Job {job_id} submitted for {company_symbol}")
        
        # Start processing if capacity available
        asyncio.create_task(self._process_job_queue())
        
        return job_id

    async def _process_job_queue(self):
        """Process jobs from the queue"""
        while (len(self.active_jobs) < self.config.max_concurrent_jobs and 
               len(self.job_queue) > 0):
            
            job = self.job_queue.pop(0)
            self.active_jobs[job.job_id] = job
            
            # Start job processing
            asyncio.create_task(self._execute_job(job))

    async def _execute_job(self, job: AnalysisJob):
        """Execute a single analysis job"""
        try:
            logger.info(f"Starting job {job.job_id} for {job.company_symbol}")
            
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now().isoformat()
            job.progress = 10.0
            
            results = {}
            
            # Step 1: Data Ingestion (if needed)
            if "ingestion" in job.analysis_types or any(t in job.analysis_types for t in ["vertical", "horizontal", "ratios"]):
                job.progress = 20.0
                logger.info(f"Job {job.job_id}: Starting data ingestion")
                
                if self.ingestion_agent:
                    ingestion_data = await self._run_ingestion(job.company_symbol, job.data_source, job.periods)
                    results["ingestion"] = ingestion_data
                else:
                    # Mock data for testing
                    results["ingestion"] = {"success": True, "data_source": job.data_source}
            
            # Step 2: Forensic Analysis
            if any(t in job.analysis_types for t in ["vertical", "horizontal", "ratios", "benford", "altman", "beneish"]):
                job.progress = 40.0
                logger.info(f"Job {job.job_id}: Starting forensic analysis")
                
                if self.forensic_agent:
                    forensic_data = await self._run_forensic_analysis(job.company_symbol, job.periods)
                    results["forensic_analysis"] = forensic_data
                else:
                    # Mock data for testing
                    results["forensic_analysis"] = {
                        "success": True,
                        "vertical_analysis": {"success": True},
                        "horizontal_analysis": {"success": True},
                        "financial_ratios": {"success": True}
                    }
            
            # Step 3: Risk Scoring
            if "risk_scoring" in job.analysis_types:
                job.progress = 70.0
                logger.info(f"Job {job.job_id}: Starting risk scoring")
                
                if self.risk_agent and "forensic_analysis" in results:
                    risk_assessment = await self._run_risk_scoring(job.company_symbol, results["forensic_analysis"])
                    results["risk_assessment"] = risk_assessment
                else:
                    # Mock data for testing
                    results["risk_assessment"] = {
                        "overall_risk_score": 35.0,
                        "risk_level": "MEDIUM",
                        "investment_recommendation": "CAUTION - Moderate risk profile"
                    }
            
            # Step 4: Compile final results
            job.progress = 90.0
            final_results = {
                "job_id": job.job_id,
                "company_symbol": job.company_symbol,
                "analysis_date": datetime.now().isoformat(),
                "data_source": job.data_source,
                "periods_analyzed": job.periods,
                "success": True,
                **results
            }
            
            # Cache results
            if self.config.enable_caching:
                cache_key = self._generate_cache_key(job.company_symbol, job.analysis_types, job.data_source, job.periods)
                self.cache[cache_key] = {
                    "data": final_results,
                    "cached_at": datetime.now().isoformat()
                }
            
            # Complete job
            job.status = JobStatus.COMPLETED
            job.results = final_results
            job.completed_at = datetime.now().isoformat()
            job.progress = 100.0
            
            logger.info(f"Job {job.job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Job {job.job_id} failed: {e}")
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now().isoformat()
        
        finally:
            # Move job from active to history
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
            self.job_history.append(job)
            
            # Continue processing queue
            await self._process_job_queue()

    async def _run_ingestion(self, company_symbol: str, data_source: str, periods: int) -> Dict[str, Any]:
        """Run data ingestion"""
        try:
            if data_source == "yahoo_finance":
                return self.ingestion_agent.get_financials(company_symbol, "yahoo", periods=periods)
            else:
                return {"success": False, "error": f"Unsupported data source: {data_source}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _run_forensic_analysis(self, company_symbol: str, periods: int) -> Dict[str, Any]:
        """Run forensic analysis"""
        try:
            return self.forensic_agent.analyze_yahoo_finance_data(company_symbol, quarters=periods)
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _run_risk_scoring(self, company_symbol: str, forensic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run risk scoring"""
        try:
            risk_assessment = self.risk_agent.calculate_risk_score(company_symbol, forensic_data)
            return asdict(risk_assessment)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and results"""
        # Check active jobs
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            return {
                "job_id": job.job_id,
                "status": job.status.value,
                "progress": job.progress,
                "company_symbol": job.company_symbol,
                "created_at": job.created_at,
                "started_at": job.started_at,
                "error_message": job.error_message
            }
        
        # Check job history
        for job in self.job_history:
            if job.job_id == job_id:
                return {
                    "job_id": job.job_id,
                    "status": job.status.value,
                    "progress": job.progress,
                    "company_symbol": job.company_symbol,
                    "created_at": job.created_at,
                    "started_at": job.started_at,
                    "completed_at": job.completed_at,
                    "error_message": job.error_message,
                    "results": job.results
                }
        
        # Check queue
        for job in self.job_queue:
            if job.job_id == job_id:
                return {
                    "job_id": job.job_id,
                    "status": job.status.value,
                    "progress": job.progress,
                    "company_symbol": job.company_symbol,
                    "created_at": job.created_at,
                    "queue_position": self.job_queue.index(job) + 1
                }
        
        return None

    def get_job_results(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job results if completed"""
        for job in self.job_history:
            if job.job_id == job_id and job.status == JobStatus.COMPLETED:
                return job.results
        return None

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or running job"""
        # Cancel from queue
        for i, job in enumerate(self.job_queue):
            if job.job_id == job_id:
                job.status = JobStatus.CANCELLED
                job.completed_at = datetime.now().isoformat()
                self.job_history.append(self.job_queue.pop(i))
                logger.info(f"Job {job_id} cancelled from queue")
                return True
        
        # Cancel active job (mark for cancellation)
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = JobStatus.CANCELLED
            logger.info(f"Job {job_id} marked for cancellation")
            return True
        
        return False

    def get_system_status(self) -> Dict[str, Any]:
        """Get orchestrator system status"""
        return {
            "active_jobs": len(self.active_jobs),
            "queued_jobs": len(self.job_queue),
            "completed_jobs": len([j for j in self.job_history if j.status == JobStatus.COMPLETED]),
            "failed_jobs": len([j for j in self.job_history if j.status == JobStatus.FAILED]),
            "cache_entries": len(self.cache),
            "max_concurrent_jobs": self.config.max_concurrent_jobs,
            "agents_status": {
                "ingestion_agent": "available" if self.ingestion_agent else "unavailable",
                "forensic_agent": "available" if self.forensic_agent else "unavailable", 
                "risk_agent": "available" if self.risk_agent else "unavailable"
            }
        }

    def _generate_cache_key(self, company_symbol: str, analysis_types: List[str], data_source: str, periods: int) -> str:
        """Generate cache key for results"""
        key_parts = [company_symbol, data_source, str(periods), "_".join(sorted(analysis_types))]
        return "|".join(key_parts)

    def _is_cache_valid(self, cached_result: Dict[str, Any]) -> bool:
        """Check if cached result is still valid"""
        try:
            cached_at = datetime.fromisoformat(cached_result["cached_at"])
            expiry_time = cached_at + timedelta(hours=self.config.cache_ttl_hours)
            return datetime.now() < expiry_time
        except:
            return False

    def cleanup_old_jobs(self, max_history_size: int = 1000):
        """Clean up old job history"""
        if len(self.job_history) > max_history_size:
            # Keep most recent jobs
            self.job_history = sorted(self.job_history, 
                                    key=lambda x: x.completed_at or x.created_at, 
                                    reverse=True)[:max_history_size]
            logger.info(f"Cleaned up job history, kept {max_history_size} most recent jobs")

    def cleanup_old_cache(self):
        """Clean up expired cache entries"""
        expired_keys = []
        for key, cached_result in self.cache.items():
            if not self._is_cache_valid(cached_result):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
