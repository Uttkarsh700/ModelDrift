"""SQLAlchemy model for drift metrics."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base


class DriftMetric(Base):
    """Drift metric model for storing feature drift calculations."""
    __tablename__ = "drift_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(255), nullable=False, index=True)
    model_version = Column(String(255), nullable=False)
    feature_name = Column(String(255), nullable=False, index=True)
    psi_score = Column(Float, nullable=False)
    ks_statistic = Column(Float, nullable=False)
    ks_p_value = Column(Float, nullable=False)
    drift_level = Column(String(50), nullable=False)  # low, medium, high
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<DriftMetric(model={self.model_name}, feature={self.feature_name}, drift_level={self.drift_level})>"
