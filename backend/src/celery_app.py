"""
Project IRIS - Celery Configuration
Background task processing for forensic analysis
"""

from celery import Celery
from config import settings

# Create Celery app
celery_app = Celery(
    'iris-forensic',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=['src.tasks']
)

# Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_time_limit=settings.celery_task_time_limit,
    task_soft_time_limit=settings.celery_task_time_limit - 60,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Task routing
celery_app.conf.task_routes = {
    'src.tasks.forensic_analysis': {'queue': 'forensic_analysis'},
    'src.tasks.sentiment_analysis': {'queue': 'sentiment_analysis'},
    'src.tasks.regulatory_monitoring': {'queue': 'regulatory_monitoring'},
    'src.tasks.peer_benchmarking': {'queue': 'peer_benchmarking'},
}

# Import tasks after app creation to avoid circular imports
if __name__ == '__main__':
    celery_app.start()
