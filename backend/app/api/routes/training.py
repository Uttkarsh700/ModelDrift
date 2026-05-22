"""API routes for model training."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import join
from app.db.database import get_db
from app.models.prediction import Prediction
from app.models.ground_truth import GroundTruthLabel

router = APIRouter(prefix="/api/v1/training", tags=["training"])


@router.get("/dataset")
def get_training_dataset(
    model_name: str = "credit_risk",
    model_version: str = "v1",
    db: Session = Depends(get_db)
):
    """
    Get training dataset: predictions joined with ground truth labels.
    
    Only returns rows where both prediction and ground truth label exist.
    
    Query parameters:
    - model_name: Model name (default: credit_risk)
    - model_version: Model version (default: v1)
    
    Response: List of training samples with:
    - prediction_id
    - input_features (dict of feature columns)
    - prediction (model prediction)
    - actual_label (ground truth)
    - created_at (prediction timestamp)
    """
    try:
        # Query predictions with joined ground truth labels
        training_data = db.query(
            Prediction.prediction_id,
            Prediction.input_features,
            Prediction.prediction,
            GroundTruthLabel.actual_label,
            Prediction.created_at
        ).join(
            GroundTruthLabel,
            Prediction.prediction_id == GroundTruthLabel.prediction_id
        ).filter(
            Prediction.model_name == model_name,
            Prediction.model_version == model_version
        ).all()

        # Convert to list of dicts
        result = []
        for row in training_data:
            result.append({
                "prediction_id": row.prediction_id,
                "input_features": row.input_features,
                "prediction": row.prediction,
                "actual_label": row.actual_label,
                "created_at": row.created_at.isoformat() if row.created_at else None
            })

        return {
            "status": "success",
            "model_name": model_name,
            "model_version": model_version,
            "total_samples": len(result),
            "data": result
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": []
        }
