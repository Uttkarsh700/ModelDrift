"""
Alerts API Routes

Endpoints for managing alerts and viewing alert history.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.alert import (
    AlertResponse,
    AlertsListResponse,
    AlertsSummaryResponse,
    ResolveAlertResponse,
)
from app.services.alert_service import AlertService

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


@router.get("", response_model=AlertsListResponse)
async def get_alerts(limit: int = 50, db: Session = Depends(get_db)):
    """
    Get all alerts (last 50 by default) ordered by creation date (newest first).
    """
    alerts = AlertService.get_all_alerts(db, limit)
    responses = [AlertResponse.from_orm(a) for a in alerts]
    return AlertsListResponse(alerts=responses, total_count=len(responses))


@router.get("/active", response_model=AlertsListResponse)
async def get_active_alerts(db: Session = Depends(get_db)):
    """
    Get all active (unresolved) alerts.
    """
    alerts = AlertService.get_active_alerts(db)
    responses = [AlertResponse.from_orm(a) for a in alerts]
    return AlertsListResponse(alerts=responses, total_count=len(responses))


@router.get("/summary", response_model=AlertsSummaryResponse)
async def get_alerts_summary(db: Session = Depends(get_db)):
    """
    Get alert statistics and summary.
    
    Returns counts of total, active, critical, warning, resolved alerts.
    """
    summary = AlertService.get_alerts_summary(db)
    return AlertsSummaryResponse(**summary)


@router.post("/{alert_id}/resolve", response_model=ResolveAlertResponse)
async def resolve_alert(alert_id: str, db: Session = Depends(get_db)):
    """
    Mark an alert as resolved and set the resolved_at timestamp.
    """
    try:
        alert = AlertService.resolve_alert(db, alert_id)
        return ResolveAlertResponse(
            status="resolved",
            alert_id=str(alert.id),
            message="Alert marked as resolved"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/seed-demo", response_model=dict)
async def seed_demo_alerts(db: Session = Depends(get_db)):
    """
    Seed the alerts table with demo data.
    
    Only creates demo alerts if the table is empty.
    Creates alerts for different sources and severities.
    """
    return AlertService.seed_demo_alerts(db)
