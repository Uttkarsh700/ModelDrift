"""
Retraining service layer.

Handles retraining business logic:
- Checking if retraining should be triggered
- Creating retraining run records
- Sending Celery tasks
- Querying run history
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional

from app.models.retraining_run import RetrainingRun
from app.models.drift_metric import DriftMetric
from app.tasks.retraining_tasks import run_retraining_task


class RetrainingService:
    """Service for managing retraining jobs."""

    @staticmethod
    def check_and_trigger_if_needed(db: Session, model_name: str = "credit_risk", model_version: str = "v1") -> dict:
        """
        Check latest drift metrics and trigger retraining if needed.

        Triggers if:
        - overall_drift_level == "high"
        OR
        - accuracy_drop >= 0.10 (10%)

        Args:
            db: Database session
            model_name: Model name (default: credit_risk)
            model_version: Model version (default: v1)

        Returns:
            {
                "status": "triggered" | "skipped",
                "run_id": UUID (if triggered),
                "reason": str
            }
        """
        # Get latest drift summary
        drift_metrics = (
            db.query(DriftMetric)
            .filter(
                DriftMetric.model_name == model_name,
                DriftMetric.model_version == model_version,
            )
            .order_by(desc(DriftMetric.created_at))
            .first()
        )

        should_trigger = False
        trigger_reason = None

        # Check drift conditions
        if drift_metrics:
            # Check overall drift level
            if drift_metrics.overall_drift_level == "high":
                should_trigger = True
                trigger_reason = "high_drift"

            # Check accuracy drop
            elif (
                drift_metrics.accuracy_drop is not None
                and drift_metrics.accuracy_drop >= 0.10
            ):
                should_trigger = True
                trigger_reason = "accuracy_drop"

        if not should_trigger:
            return {
                "status": "skipped",
                "run_id": None,
                "reason": "Drift below threshold",
            }

        # Trigger retraining
        return RetrainingService.manual_trigger(db, model_name, model_version, trigger_reason)

    @staticmethod
    def manual_trigger(
        db: Session,
        model_name: str = "credit_risk",
        model_version: str = "v1",
        trigger_reason: str = "manual",
    ) -> dict:
        """
        Manually trigger retraining.

        Args:
            db: Database session
            model_name: Model name
            model_version: Model version
            trigger_reason: Reason for triggering (manual, high_drift, accuracy_drop)

        Returns:
            {
                "status": "triggered",
                "run_id": UUID,
                "reason": str
            }
        """
        # Create retraining run record
        run = RetrainingRun(
            model_name=model_name,
            model_version=model_version,
            trigger_reason=trigger_reason,
            status="pending",
            started_at=datetime.utcnow(),
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        # Send Celery task
        run_retraining_task.delay(str(run.id))

        return {
            "status": "triggered",
            "run_id": str(run.id),
            "reason": f"Retraining triggered ({trigger_reason})",
        }

    @staticmethod
    def get_latest_runs(db: Session, limit: int = 20) -> tuple[list[RetrainingRun], int]:
        """
        Get latest retraining runs.

        Args:
            db: Database session
            limit: Number of runs to return (default: 20)

        Returns:
            (list of runs, total count)
        """
        total_count = db.query(RetrainingRun).count()
        runs = (
            db.query(RetrainingRun)
            .order_by(desc(RetrainingRun.started_at))
            .limit(limit)
            .all()
        )
        return runs, total_count

    @staticmethod
    def get_latest_run(db: Session) -> Optional[RetrainingRun]:
        """
        Get the most recent retraining run.

        Args:
            db: Database session

        Returns:
            Latest run or None
        """
        return (
            db.query(RetrainingRun)
            .order_by(desc(RetrainingRun.started_at))
            .first()
        )
