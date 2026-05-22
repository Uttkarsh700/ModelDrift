from sqlalchemy import Column, String, Float, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base


class ModelVersion(Base):
    """
    Model Registry Table.
    
    Tracks different versions of trained models with their metrics and deployment stage.
    
    Stages:
    - production: Currently deployed model (champion)
    - staging: Candidate model waiting for promotion (challenger)
    - archived: Previous production model (no longer used)
    """
    __tablename__ = "model_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Model identification
    model_name = Column(String, nullable=False)  # e.g., "credit_risk"
    model_version = Column(String, nullable=False)  # e.g., "v1", "v2"
    
    # Deployment stage
    stage = Column(String, nullable=False)  # production, staging, archived
    
    # Performance metrics
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    drift_score = Column(Float, nullable=True)  # Optional: only if drift detected
    
    # Artifact tracking
    artifact_path = Column(String, nullable=True)  # Path to model file (e.g., ml/models/credit_risk_latest.pkl)
    mlflow_run_id = Column(String, nullable=True)  # MLflow experiment run ID
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    promoted_at = Column(DateTime, nullable=True)  # When promoted to production

    def __repr__(self):
        return f"<ModelVersion {self.model_name} {self.model_version} ({self.stage})>"
