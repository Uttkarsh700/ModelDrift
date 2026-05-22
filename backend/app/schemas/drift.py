"""Pydantic schemas for drift detection."""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class DriftFeatureDetail(BaseModel):
    """Drift details for a single feature."""
    feature_name: str
    psi_score: float = Field(..., description="Population Stability Index")
    ks_statistic: float = Field(..., description="Kolmogorov-Smirnov test statistic")
    ks_p_value: float = Field(..., description="KS test p-value")
    drift_level: str = Field(..., description="low, medium, or high")


class DriftRunResponse(BaseModel):
    """Response from drift calculation run."""
    status: str = Field(..., description="success or error")
    model_name: str
    model_version: str
    overall_drift_level: str = Field(..., description="low, medium, or high")
    baseline_accuracy: float = Field(..., description="Accuracy on baseline data")
    current_accuracy: float = Field(..., description="Accuracy on current data")
    accuracy_drop: float = Field(..., description="Difference in accuracy")
    baseline_sample_size: int = Field(..., description="Number of baseline predictions")
    current_sample_size: int = Field(..., description="Number of current predictions")
    features: List[DriftFeatureDetail] = Field(..., description="Per-feature drift metrics")
    calculated_at: datetime


class DriftSummaryResponse(BaseModel):
    """Summary of latest drift calculations."""
    model_name: str
    model_version: str
    overall_drift_level: str = Field(..., description="low, medium, or high")
    avg_psi: float = Field(..., description="Average PSI across features")
    max_psi: float = Field(..., description="Maximum PSI score")
    min_psi: float = Field(..., description="Minimum PSI score")
    baseline_accuracy: float
    current_accuracy: float
    accuracy_drop: float
    high_drift_features: int = Field(..., description="Count of high-drift features")
    medium_drift_features: int = Field(..., description="Count of medium-drift features")
    low_drift_features: int = Field(..., description="Count of low-drift features")
    calculated_at: datetime


class DriftLatestResponse(BaseModel):
    """Latest drift metrics grouped by feature."""
    model_name: str
    model_version: str
    features: List[DriftFeatureDetail]
    calculated_at: datetime
