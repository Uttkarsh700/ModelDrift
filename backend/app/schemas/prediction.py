"""Pydantic schemas for predictions."""
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field


class PredictionCreate(BaseModel):
    """Schema for creating a prediction."""
    model_name: str = Field(..., description="Name of the model")
    model_version: str = Field(..., description="Version of the model")
    prediction_id: str = Field(..., description="Unique prediction identifier")
    input_features: Dict[str, Any] = Field(..., description="Input features as JSON")
    prediction: str = Field(..., description="Predicted label or value")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")


class PredictionResponse(BaseModel):
    """Response for prediction creation."""
    status: str = Field(..., description="Status of the operation")
    prediction_id: str = Field(..., description="Unique prediction identifier")


class PredictionDetail(BaseModel):
    """Detailed prediction information."""
    id: str = Field(..., description="Internal UUID")
    model_name: str
    model_version: str
    prediction_id: str
    input_features: Dict[str, Any]
    prediction: str
    confidence: float
    created_at: datetime
    
    class Config:
        from_attributes = True
