"""
API routes for retraining management.

Endpoints:
- POST /api/v1/retraining/check-and-trigger: Auto-trigger if drift is high
- POST /api/v1/retraining/manual-trigger: Always trigger retraining
- GET /api/v1/retraining/runs: List latest 20 retraining runs
- GET /api/v1/retraining/runs/latest: Get latest retraining run
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.retraining import (
    CheckAndTriggerResponse,
    ManualTriggerResponse,
    RetrainingRunsListResponse,
    LatestRetrainingRunResponse,
    RetrainingRunResponse,
)
from app.services.retraining_service import RetrainingService

router = APIRouter(
    prefix="/api/v1/retraining",
    tags=["retraining"],
)


@router.post("/check-and-trigger", response_model=CheckAndTriggerResponse)
def check_and_trigger_retraining(db: Session = Depends(get_db)):
    """
    Check latest drift metrics.
    
    Trigger retraining if:
    - overall_drift_level == "high"
    OR
    - accuracy_drop >= 0.10
    
    Returns:
    - status: "triggered" or "skipped"
    - run_id: UUID if triggered
    - reason: explanation string
    """
    result = RetrainingService.check_and_trigger_if_needed(db)
    return CheckAndTriggerResponse(**result)


@router.post("/manual-trigger", response_model=ManualTriggerResponse)
def manual_trigger_retraining(db: Session = Depends(get_db)):
    """
    Manually trigger retraining regardless of drift level.
    
    Always returns:
    - status: "triggered"
    - run_id: UUID of created run
    - reason: "manual"
    """
    result = RetrainingService.manual_trigger(db, trigger_reason="manual")
    return ManualTriggerResponse(**result)


@router.get("/runs", response_model=RetrainingRunsListResponse)
def get_retraining_runs(limit: int = 20, db: Session = Depends(get_db)):
    """
    Get latest retraining runs.
    
    Args:
        limit: Number of runs to return (default: 20, max: 100)
    
    Returns:
    - runs: list of retraining run objects
    - total_count: total number of retraining runs in database
    """
    limit = min(limit, 100)  # Cap at 100
    runs, total_count = RetrainingService.get_latest_runs(db, limit=limit)
    return RetrainingRunsListResponse(
        runs=[RetrainingRunResponse.model_validate(run) for run in runs],
        total_count=total_count,
    )


@router.get("/runs/latest", response_model=LatestRetrainingRunResponse)
def get_latest_retraining_run(db: Session = Depends(get_db)):
    """
    Get the most recent retraining run.
    
    Returns:
    - run: latest retraining run object, or null if no runs exist
    """
    run = RetrainingService.get_latest_run(db)
    if run:
        return LatestRetrainingRunResponse(
            run=RetrainingRunResponse.model_validate(run)
        )
    return LatestRetrainingRunResponse(run=None)
