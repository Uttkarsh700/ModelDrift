"""SQLAlchemy model for predictions."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.database import Base


class Prediction(Base):
    """Prediction model for storing model predictions."""
    __tablename__ = "predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(255), nullable=False, index=True)
    model_version = Column(String(255), nullable=False)
    prediction_id = Column(String(255), nullable=False, unique=True, index=True)
    input_features = Column(JSONB, nullable=False)
    prediction = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, prediction_id={self.prediction_id}, model_name={self.model_name})>"
