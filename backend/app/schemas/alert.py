from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class CreateAlertRequest(BaseModel):
    """Request to create a new alert."""
    title: str = Field(..., example="High drift detected")
    message: str = Field(..., example="Overall drift level is high (>0.5)")
    severity: Literal["info", "warning", "critical"] = Field(..., example="critical")
    source: Literal["drift", "retraining", "github_actions", "system"] = Field(..., example="drift")


class AlertResponse(BaseModel):
    """Response containing alert information."""
    id: str
    title: str
    message: str
    severity: str
    source: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


class AlertsListResponse(BaseModel):
    """List of alerts."""
    alerts: list[AlertResponse]
    total_count: int


class AlertsSummaryResponse(BaseModel):
    """Summary statistics of alerts."""
    total_alerts: int
    active_alerts: int
    critical_alerts: int
    warning_alerts: int
    info_alerts: int
    resolved_alerts: int


class ResolveAlertResponse(BaseModel):
    """Response after resolving an alert."""
    status: str = Field(example="resolved")
    alert_id: str
    message: str = Field(example="Alert marked as resolved")
