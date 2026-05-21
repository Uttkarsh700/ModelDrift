"""Service for ground truth label operations."""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.ground_truth import GroundTruthLabel
from app.schemas.ground_truth import GroundTruthCreate, GroundTruthDetail


def create_ground_truth(db: Session, label_data: GroundTruthCreate) -> GroundTruthLabel:
    """
    Create a new ground truth label record.
    
    Args:
        db: Database session
        label_data: Ground truth label data from request
        
    Returns:
        Created ground truth label record
    """
    db_label = GroundTruthLabel(
        prediction_id=label_data.prediction_id,
        actual_label=label_data.actual_label
    )
    db.add(db_label)
    db.commit()
    db.refresh(db_label)
    return db_label


def get_ground_truth_by_prediction_id(db: Session, prediction_id: str) -> GroundTruthLabel | None:
    """
    Retrieve a ground truth label by prediction_id.
    
    Args:
        db: Database session
        prediction_id: Prediction identifier
        
    Returns:
        Ground truth label record or None if not found
    """
    return db.query(GroundTruthLabel).filter(
        GroundTruthLabel.prediction_id == prediction_id
    ).first()


def get_recent_labels(db: Session, limit: int = 20) -> list[GroundTruthLabel]:
    """
    Retrieve recent ground truth labels.
    
    Args:
        db: Database session
        limit: Number of labels to return
        
    Returns:
        List of ground truth label records, ordered by received_at descending
    """
    return db.query(GroundTruthLabel).order_by(
        desc(GroundTruthLabel.received_at)
    ).limit(limit).all()
