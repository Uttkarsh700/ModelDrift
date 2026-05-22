"""
Retraining run model for tracking automated/manual retraining jobs.

Stores metadata about each retraining execution:
- When it started/finished
- What triggered it (drift/accuracy drop/manual)
- Current status (pending/running/completed/failed)
- Captured logs from ml/retrain_model.py
"""

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.core.database import Base


class RetrainingRun(Base):
    """
    Tracks each retraining execution.
    
    Statuses:
    - pending: Created, waiting for Celery to pick up
    - running: Currently executing ml/retrain_model.py
    - completed: Finished successfully
    - failed: Encountered error
    """
    __tablename__ = "retraining_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(255), nullable=False, index=True)
    model_version = Column(String(255), nullable=False)
    trigger_reason = Column(String(255), nullable=False)  # "high_drift", "accuracy_drop", "manual"
    status = Column(String(50), nullable=False, default="pending", index=True)  # pending, running, completed, failed
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    logs = Column(Text, nullable=True)  # stdout/stderr captured during execution

    def __repr__(self):
        return f"<RetrainingRun {self.id} {self.model_name} {self.status}>"
