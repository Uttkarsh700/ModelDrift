"""
Pydantic schemas for retraining API requests/responses.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid


class RetrainingRunResponse(BaseModel):
    """Response model for a retraining run."""
    id: uuid.UUID
    model_name: str
    model_version: str
    trigger_reason: str
    status: str  # pending, running, completed, failed
    started_at: datetime
    finished_at: Optional[datetime] = None
    logs: Optional[str] = None

    class Config:
        from_attributes = True


class CheckAndTriggerResponse(BaseModel):
    """Response for check-and-trigger endpoint."""
    status: str  # "triggered" or "skipped"
    run_id: Optional[uuid.UUID] = None
    reason: str


class ManualTriggerResponse(BaseModel):
    """Response for manual trigger endpoint."""
    status: str  # "triggered"
    run_id: uuid.UUID
    reason: str


class RetrainingRunsListResponse(BaseModel):
    """Response for listing retraining runs."""
    runs: list[RetrainingRunResponse]
    total_count: int


class LatestRetrainingRunResponse(BaseModel):
    """Response for getting latest retraining run."""
    run: Optional[RetrainingRunResponse] = None
