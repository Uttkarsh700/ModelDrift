"""
Alert Service Layer

Handles all alert creation, retrieval, and management.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from app.models.alert import Alert
from app.schemas.alert import CreateAlertRequest, AlertResponse


class AlertService:
    """Business logic for alert management."""

    @staticmethod
    def create_alert(db: Session, request: CreateAlertRequest) -> Alert:
        """
        Create a new alert.
        
        Args:
            db: Database session
            request: Alert data
            
        Returns:
            Created Alert instance
        """
        alert = Alert(
            title=request.title,
            message=request.message,
            severity=request.severity,
            source=request.source,
            status="active"
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def create_alert_if_not_exists(db: Session, title: str, message: str, severity: str, source: str) -> Alert:
        """
        Create alert only if no active alert with same title and source exists.
        
        Prevents duplicate alerts for same issue.
        
        Args:
            db: Database session
            title: Alert title
            message: Alert message
            severity: Alert severity
            source: Alert source
            
        Returns:
            Existing active alert or newly created alert
        """
        # Check if active alert with same title and source exists
        existing = db.query(Alert).filter(
            Alert.title == title,
            Alert.source == source,
            Alert.status == "active"
        ).first()

        if existing:
            return existing

        # Create new alert
        alert = Alert(
            title=title,
            message=message,
            severity=severity,
            source=source,
            status="active"
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def get_all_alerts(db: Session, limit: int = 50) -> list[Alert]:
        """
        Get all alerts ordered by creation date (newest first).
        
        Args:
            db: Database session
            limit: Maximum alerts to return
            
        Returns:
            List of Alert instances
        """
        return db.query(Alert)\
            .order_by(desc(Alert.created_at))\
            .limit(limit)\
            .all()

    @staticmethod
    def get_active_alerts(db: Session) -> list[Alert]:
        """
        Get all active (unresolved) alerts.
        
        Args:
            db: Database session
            
        Returns:
            List of active Alert instances
        """
        return db.query(Alert)\
            .filter(Alert.status == "active")\
            .order_by(desc(Alert.created_at))\
            .all()

    @staticmethod
    def get_alerts_summary(db: Session) -> dict:
        """
        Get alert statistics.
        
        Args:
            db: Database session
            
        Returns:
            Dict with counts of total, active, critical, warning, resolved alerts
        """
        total = db.query(Alert).count()
        active = db.query(Alert).filter(Alert.status == "active").count()
        critical = db.query(Alert).filter(Alert.severity == "critical", Alert.status == "active").count()
        warning = db.query(Alert).filter(Alert.severity == "warning", Alert.status == "active").count()
        info = db.query(Alert).filter(Alert.severity == "info", Alert.status == "active").count()
        resolved = db.query(Alert).filter(Alert.status == "resolved").count()

        return {
            "total_alerts": total,
            "active_alerts": active,
            "critical_alerts": critical,
            "warning_alerts": warning,
            "info_alerts": info,
            "resolved_alerts": resolved
        }

    @staticmethod
    def resolve_alert(db: Session, alert_id: str) -> Alert:
        """
        Mark an alert as resolved.
        
        Args:
            db: Database session
            alert_id: Alert UUID to resolve
            
        Returns:
            Updated Alert instance
        """
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")

        alert.status = "resolved"
        alert.resolved_at = datetime.utcnow()
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def seed_demo_alerts(db: Session) -> dict:
        """
        Seed the alerts table with demo data (only if empty).
        
        Creates sample alerts for different sources and severities.
        
        Args:
            db: Database session
            
        Returns:
            Dict with status and count of alerts created
        """
        existing_count = db.query(Alert).count()
        if existing_count > 0:
            return {"status": "skipped", "reason": "Alerts table already has data", "created": 0}

        alerts_data = [
            ("High drift detected", "Overall drift level is HIGH (0.65). Model performance degradation detected.", "critical", "drift", "active"),
            ("Accuracy drop detected", "Accuracy dropped by 12.5% from baseline. Performance declining.", "warning", "drift", "active"),
            ("Retraining failed", "Last retraining run failed with error: Insufficient training samples.", "critical", "retraining", "resolved"),
            ("GitHub Actions not configured", "GitHub Actions credentials not set. CI/CD automation disabled.", "warning", "github_actions", "active"),
            ("Model drift detected", "Drift score increased to 0.48. Consider running model diagnostics.", "warning", "drift", "resolved"),
            ("System performance warning", "CPU usage above 80%. Monitor system resources.", "info", "system", "active"),
        ]

        created_alerts = []
        for title, message, severity, source, status in alerts_data:
            alert = Alert(
                title=title,
                message=message,
                severity=severity,
                source=source,
                status=status,
                resolved_at=datetime.utcnow() if status == "resolved" else None
            )
            created_alerts.append(alert)
            db.add(alert)

        db.commit()

        return {
            "status": "seeded",
            "created": len(created_alerts),
            "alerts": [
                {
                    "title": a.title,
                    "severity": a.severity,
                    "source": a.source,
                    "status": a.status
                }
                for a in created_alerts
            ]
        }  
