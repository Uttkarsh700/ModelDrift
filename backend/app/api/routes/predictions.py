"""API routes for predictions."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.prediction import PredictionCreate, PredictionResponse, PredictionDetail
from app.services import prediction_service

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])


@router.post("", response_model=PredictionResponse)
def create_prediction(
    prediction: PredictionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new prediction record.
    
    Request body:
    {
      "model_name": "credit_risk",
      "model_version": "v1",
      "prediction_id": "pred_001",
      "input_features": {
        "credit_utilization": 0.72,
        "debt_to_income": 0.43,
        "num_recent_inquiries": 3
      },
      "prediction": "high_risk",
      "confidence": 0.91
    }
    """
    # Check if prediction_id already exists
    existing = prediction_service.get_prediction_by_id(db, prediction.prediction_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Prediction with id {prediction.prediction_id} already exists"
        )
    
    db_prediction = prediction_service.create_prediction(db, prediction)
    
    return PredictionResponse(
        status="success",
        prediction_id=db_prediction.prediction_id
    )


@router.get("/recent", response_model=list[PredictionDetail])
def get_recent_predictions(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get the most recent predictions (default: 20).
    
    Query parameters:
    - limit: Number of predictions to return (default: 20)
    """
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 1
    
    predictions = prediction_service.get_recent_predictions(db, limit)
    return predictions


@router.get("/{prediction_id}", response_model=PredictionDetail)
def get_prediction(
    prediction_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific prediction by prediction_id."""
    prediction = prediction_service.get_prediction_by_id(db, prediction_id)
    if not prediction:
        raise HTTPException(
            status_code=404,
            detail=f"Prediction with id {prediction_id} not found"
        )
    return prediction
