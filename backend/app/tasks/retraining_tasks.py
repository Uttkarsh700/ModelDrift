"""
Celery tasks for retraining.

Long-running tasks that execute in background worker process.
"""

import subprocess
import sys
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.retraining_run import RetrainingRun


@celery_app.task(name="run_retraining_task", bind=True)
def run_retraining_task(self, run_id: str):
    """
    Execute retraining pipeline in background.
    
    Steps:
    1. Mark run as "running"
    2. Execute ml/retrain_model.py via subprocess
    3. Capture stdout/stderr
    4. Mark run as "completed" or "failed"
    5. Save logs to database
    
    Args:
        run_id: UUID of the retraining run record
    """
    db = SessionLocal()
    try:
        # Get run record
        run = db.query(RetrainingRun).filter(RetrainingRun.id == str(run_id)).first()
        if not run:
            raise ValueError(f"Retraining run {run_id} not found")

        # Mark as running
        run.status = "running"
        db.commit()

        # Execute retraining script
        # Note: Change working directory to project root so ml/retrain_model.py can find ml/
        result = subprocess.run(
            [sys.executable, "ml/retrain_model.py"],
            cwd="/app",  # FastAPI container runs from /app
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
        )

        # Combine stdout and stderr
        logs = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"

        # Check if successful
        if result.returncode == 0:
            run.status = "completed"
            run.logs = logs
            run.finished_at = datetime.utcnow()
            db.commit()
        else:
            run.status = "failed"
            run.logs = logs
            run.finished_at = datetime.utcnow()
            db.commit()
            raise subprocess.CalledProcessError(
                result.returncode,
                result.args,
                output=result.stdout,
                stderr=result.stderr,
            )

    except subprocess.TimeoutExpired as e:
        run.status = "failed"
        run.logs = f"Error: Retraining timed out after 600 seconds"
        run.finished_at = datetime.utcnow()
        db.commit()
        raise

    except Exception as e:
        run.status = "failed"
        run.logs = f"Error: {str(e)}"
        run.finished_at = datetime.utcnow()
        db.commit()
        raise

    finally:
        db.close()
