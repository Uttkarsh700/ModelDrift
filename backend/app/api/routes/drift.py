"""API routes for drift detection."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.drift import DriftRunResponse, DriftSummaryResponse, DriftLatestResponse, DriftFeatureDetail
from app.services import drift_service

router = APIRouter(prefix="/api/v1/drift", tags=["drift"])


@router.post("/run", response_model=DriftRunResponse)
def run_drift_detection(
    model_name: str = "credit_risk",
    model_version: str = "v1",
    db: Session = Depends(get_db)
):
    """
    Calculate drift metrics for a model.
    
    This endpoint:
    1. Splits predictions into baseline (first 300) and current (last 200)
    2. Calculates PSI (Population Stability Index) for each feature
    3. Performs KS-test on feature distributions
    4. Calculates accuracy for both periods
    5. Stores metrics in database
    6. Returns comprehensive drift report
    
    Query parameters:
    - model_name: Model to analyze (default: "credit_risk")
    - model_version: Model version (default: "v1")
    """
    try:
        result = drift_service.calculate_drift(db, model_name, model_version)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drift calculation error: {str(e)}")


@router.get("/latest", response_model=DriftLatestResponse)
def get_latest_drift(
    model_name: str = "credit_risk",
    model_version: str = "v1",
    db: Session = Depends(get_db)
):
    """
    Get latest drift metrics for each feature.
    
    Returns the most recent drift calculation results grouped by feature.
    """
    try:
        latest_metrics = drift_service.get_latest_drift_metrics(db, model_name, model_version)
        
        if not latest_metrics:
            raise HTTPException(status_code=404, detail="No drift metrics found. Run /drift/run first.")
        
        features = [
            DriftFeatureDetail(
                feature_name=m.feature_name,
                psi_score=m.psi_score,
                ks_statistic=m.ks_statistic,
                ks_p_value=m.ks_p_value,
                drift_level=m.drift_level
            )
            for m in latest_metrics
        ]
        
        return DriftLatestResponse(
            model_name=model_name,
            model_version=model_version,
            features=features,
            calculated_at=latest_metrics[0].calculated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=DriftSummaryResponse)
def get_drift_summary(
    model_name: str = "credit_risk",
    model_version: str = "v1",
    db: Session = Depends(get_db)
):
    """
    Get summary of latest drift calculation.
    
    Returns high-level metrics including:
    - Overall drift level
    - Average/max/min PSI
    - Accuracy comparison
    - Feature drift breakdown
    """
    try:
        summary = drift_service.get_drift_summary(db, model_name, model_version)
        return DriftSummaryResponse(**summary)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
