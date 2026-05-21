"""Pydantic schemas for ground truth labels."""
from datetime import datetime
from pydantic import BaseModel, Field


class GroundTruthCreate(BaseModel):
    """Schema for creating a ground truth label."""
    prediction_id: str = Field(..., description="Unique prediction identifier")
    actual_label: str = Field(..., description="Actual label or value")


class GroundTruthResponse(BaseModel):
    """Response for ground truth label creation."""
    status: str = Field(..., description="Status of the operation")
    prediction_id: str = Field(..., description="Unique prediction identifier")


class GroundTruthDetail(BaseModel):
    """Detailed ground truth label information."""
    id: str = Field(..., description="Internal UUID")
    prediction_id: str
    actual_label: str
    received_at: datetime
    
    class Config:
        from_attributes = True
