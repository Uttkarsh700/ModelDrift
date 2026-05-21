"""Service for prediction operations."""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.prediction import Prediction
from app.schemas.prediction import PredictionCreate, PredictionDetail


def create_prediction(db: Session, prediction_data: PredictionCreate) -> Prediction:
    """
    Create a new prediction record.
    
    Args:
        db: Database session
        prediction_data: Prediction data from request
        
    Returns:
        Created prediction record
    """
    db_prediction = Prediction(
        model_name=prediction_data.model_name,
        model_version=prediction_data.model_version,
        prediction_id=prediction_data.prediction_id,
        input_features=prediction_data.input_features,
        prediction=prediction_data.prediction,
        confidence=prediction_data.confidence
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction


def get_prediction_by_id(db: Session, prediction_id: str) -> Prediction | None:
    """
    Retrieve a prediction by prediction_id.
    
    Args:
        db: Database session
        prediction_id: Prediction identifier
        
    Returns:
        Prediction record or None if not found
    """
    return db.query(Prediction).filter(
        Prediction.prediction_id == prediction_id
    ).first()


def get_recent_predictions(db: Session, limit: int = 20) -> list[Prediction]:
    """
    Retrieve recent predictions.
    
    Args:
        db: Database session
        limit: Number of predictions to return
        
    Returns:
        List of prediction records, ordered by creation date descending
    """
    return db.query(Prediction).order_by(
        desc(Prediction.created_at)
    ).limit(limit).all()


def get_predictions_by_model(db: Session, model_name: str, limit: int = 20) -> list[Prediction]:
    """
    Retrieve predictions for a specific model.
    
    Args:
        db: Database session
        model_name: Model name filter
        limit: Number of predictions to return
        
    Returns:
        List of prediction records for the model
    """
    return db.query(Prediction).filter(
        Prediction.model_name == model_name
    ).order_by(desc(Prediction.created_at)).limit(limit).all()
