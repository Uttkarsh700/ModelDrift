"""SQLAlchemy model for ground truth labels."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base


class GroundTruthLabel(Base):
    """Ground truth label model for storing actual outcomes."""
    __tablename__ = "ground_truth_labels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_id = Column(String(255), nullable=False, unique=True, index=True)
    actual_label = Column(String(255), nullable=False)
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<GroundTruthLabel(id={self.id}, prediction_id={self.prediction_id}, actual_label={self.actual_label})>"
