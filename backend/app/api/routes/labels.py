"""API routes for ground truth labels."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.ground_truth import GroundTruthCreate, GroundTruthResponse, GroundTruthDetail
from app.services import ground_truth_service

router = APIRouter(prefix="/api/v1/labels", tags=["labels"])


@router.post("", response_model=GroundTruthResponse)
def create_label(
    label: GroundTruthCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new ground truth label record.
    
    Request body:
    {
      "prediction_id": "pred_001",
      "actual_label": "default"
    }
    """
    # Check if label already exists for this prediction
    existing = ground_truth_service.get_ground_truth_by_prediction_id(db, label.prediction_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ground truth label for prediction_id {label.prediction_id} already exists"
        )
    
    db_label = ground_truth_service.create_ground_truth(db, label)
    
    return GroundTruthResponse(
        status="success",
        prediction_id=db_label.prediction_id
    )


@router.get("/recent", response_model=list[GroundTruthDetail])
def get_recent_labels(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get the most recent ground truth labels (default: 20).
    
    Query parameters:
    - limit: Number of labels to return (default: 20)
    """
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 1
    
    labels = ground_truth_service.get_recent_labels(db, limit)
    return labels


@router.get("/{prediction_id}", response_model=GroundTruthDetail)
def get_label(
    prediction_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific ground truth label by prediction_id."""
    label = ground_truth_service.get_ground_truth_by_prediction_id(db, prediction_id)
    if not label:
        raise HTTPException(
            status_code=404,
            detail=f"Ground truth label for prediction_id {prediction_id} not found"
        )
    return label
