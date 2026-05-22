"""
API routes for GitHub Actions integration.

Endpoints:
- GET /api/v1/github-actions/config-status: Check if GitHub Actions is configured
- POST /api/v1/github-actions/trigger-retraining: Trigger retraining via GitHub Actions
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.github_actions_service import GitHubActionsService
from app.services.alert_service import AlertService

router = APIRouter(
    prefix="/api/v1/github-actions",
    tags=["github-actions"],
)


class GitHubActionsConfigResponse(BaseModel):
    """Response for config status check."""
    configured: bool
    missing: list[str] = []


class TriggerRetrainingRequest(BaseModel):
    """Request to trigger retraining via GitHub Actions."""
    model_name: str = "credit_risk"
    model_version: str = "v1"
    trigger_reason: str = "manual"


class TriggerRetrainingResponse(BaseModel):
    """Response from trigger retraining endpoint."""
    status: str  # "triggered" or "error"
    workflow_file: str | None = None
    ref: str | None = None
    message: str


@router.get("/config-status", response_model=GitHubActionsConfigResponse)
def check_github_actions_config(db: Session = Depends(get_db)):
    """
    Check if GitHub Actions is properly configured.

    Returns:
    - configured: boolean indicating if all required env vars are set
    - missing: list of missing environment variables (if not configured)
    """
    is_configured, missing_vars = GitHubActionsService.is_configured()
    
    # Create alert if not configured
    if not is_configured:
        AlertService.create_alert_if_not_exists(
            db,
            title="GitHub Actions not configured",
            message="GitHub Actions credentials are not set. CI/CD automation is disabled.",
            severity="warning",
            source="github_actions"
        )
    
    return GitHubActionsConfigResponse(
        configured=is_configured,
        missing=missing_vars,
    )


@router.post("/trigger-retraining", response_model=TriggerRetrainingResponse)
def trigger_github_actions_retraining(request: TriggerRetrainingRequest):
    """
    Trigger retraining via GitHub Actions workflow_dispatch.

    This endpoint triggers the GitHub Actions workflow defined in
    .github/workflows/retrain-model.yml.

    Request body:
    - model_name: Name of model (default: "credit_risk")
    - model_version: Version of model (default: "v1")
    - trigger_reason: Reason for triggering (e.g., "high drift detected")

    Returns:
    - status: "triggered" if successful, "error" otherwise
    - workflow_file: Name of the workflow file
    - ref: Git reference (branch) where workflow was triggered
    - message: Descriptive message
    """
    result = GitHubActionsService.trigger_retraining(
        model_name=request.model_name,
        model_version=request.model_version,
        trigger_reason=request.trigger_reason,
    )

    return TriggerRetrainingResponse(**result)
