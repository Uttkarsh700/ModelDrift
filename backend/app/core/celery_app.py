"""
Celery app configuration.

Celery is a distributed task queue that runs long-running tasks in background.
Uses Redis as message broker (where tasks are queued).
"""

from celery import Celery
import os

# Get Redis URL from environment or use default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app instance
celery_app = Celery(
    "modeldrift",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,  # Track when task starts
)
