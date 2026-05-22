from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class RegisterModelRequest(BaseModel):
    """Request to register a new model version in the registry."""
    model_name: str = Field(..., example="credit_risk")
    model_version: str = Field(..., example="v2")
    stage: Literal["production", "staging", "archived"] = Field(..., example="staging")
    accuracy: float = Field(..., ge=0, le=1, example=0.93)
    precision: float = Field(..., ge=0, le=1, example=0.91)
    recall: float = Field(..., ge=0, le=1, example=0.90)
    f1_score: float = Field(..., ge=0, le=1, example=0.905)
    drift_score: Optional[float] = Field(None, ge=0, le=1, example=0.31)
    artifact_path: Optional[str] = Field(None, example="ml/models/credit_risk_latest.pkl")
    mlflow_run_id: Optional[str] = Field(None, example="demo_run_001")


class ModelVersionResponse(BaseModel):
    """Response containing model version information."""
    id: str
    model_name: str
    model_version: str
    stage: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    drift_score: Optional[float]
    artifact_path: Optional[str]
    mlflow_run_id: Optional[str]
    created_at: datetime
    promoted_at: Optional[datetime]

    class Config:
        from_attributes = True


class RegisterResponse(BaseModel):
    """Response after registering a model."""
    status: str = Field(example="registered")
    model_name: str
    model_version: str
    stage: str


class ChampionChallengerResponse(BaseModel):
    """Champion and Challenger models with comparison metrics."""
    champion: Optional[ModelVersionResponse]
    challenger: Optional[ModelVersionResponse]
    accuracy_delta: Optional[float] = Field(None, description="Challenger accuracy - Champion accuracy")
    f1_delta: Optional[float] = Field(None, description="Challenger F1 - Champion F1")
    drift_delta: Optional[float] = Field(None, description="Challenger drift - Champion drift")
    recommendation: Literal["promote_challenger", "keep_champion"] = Field(example="promote_challenger")
    reason: str = Field(example="Challenger has better accuracy and lower drift.")


class ModelsListResponse(BaseModel):
    """List of all model versions."""
    models: list[ModelVersionResponse]
    total_count: int


class PromotionResponse(BaseModel):
    """Response after promoting a model."""
    status: str = Field(example="promoted")
    promoted_model: ModelVersionResponse
    archived_model: Optional[ModelVersionResponse]
    message: str
