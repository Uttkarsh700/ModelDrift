from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base


class Alert(Base):
    """
    Alert Storage Table.
    
    Tracks system alerts for monitoring: drift, retraining failures, configuration issues.
    
    Severity:
    - info: Informational message
    - warning: Warning condition (accuracy drop, missing config)
    - critical: Critical issue (high drift, failed retraining)
    
    Status:
    - active: Alert is ongoing/unresolved
    - resolved: Alert has been acknowledged/resolved
    
    Source:
    - drift: Drift detection alerts
    - retraining: Retraining task failures
    - github_actions: GitHub Actions configuration issues
    - system: System health issues
    """
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Alert content
    title = Column(String, nullable=False)  # e.g., "High drift detected"
    message = Column(Text, nullable=False)  # Detailed message
    
    # Alert classification
    severity = Column(String, nullable=False)  # info, warning, critical
    source = Column(String, nullable=False)  # drift, retraining, github_actions, system
    
    # Alert status
    status = Column(String, nullable=False, default="active")  # active, resolved
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime, nullable=True)  # When alert was resolved

    def __repr__(self):
        return f"<Alert {self.severity} {self.title} ({self.status})>"
