"""Service for drift detection calculations."""
import numpy as np
from datetime import datetime
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from scipy.stats import ks_2samp
from app.models.drift_metric import DriftMetric
from app.models.prediction import Prediction
from app.models.ground_truth import GroundTruthLabel
from app.schemas.drift import DriftFeatureDetail, DriftRunResponse


FEATURES_TO_CHECK = [
    "credit_utilization",
    "debt_to_income",
    "num_recent_inquiries",
    "avg_account_age_months",
    "num_open_accounts"
]

PSI_THRESHOLD_HIGH = 0.25
PSI_THRESHOLD_MEDIUM = 0.10


def split_baseline_current(db: Session, model_name: str, model_version: str) -> Tuple[List[Prediction], List[Prediction]]:
    """
    Split predictions into baseline and current groups.
    
    - Baseline: First 300 predictions ordered by created_at
    - Current: Latest 200 predictions ordered by created_at
    """
    # Get all predictions for this model, ordered by time
    all_predictions = db.query(Prediction).filter(
        Prediction.model_name == model_name,
        Prediction.model_version == model_version
    ).order_by(Prediction.created_at).all()
    
    # Split: baseline is first 300, current is last 200
    baseline = all_predictions[:300]
    current = all_predictions[-200:] if len(all_predictions) >= 500 else []
    
    return baseline, current


def calculate_psi(baseline_values: np.ndarray, current_values: np.ndarray, bins: int = 10) -> float:
    """
    Calculate Population Stability Index (PSI).
    
    PSI measures how much a distribution has shifted from baseline to current.
    
    Simple explanation:
    - For each bin, compare the percentage of baseline data vs current data
    - If distributions are different, PSI will be higher
    - PSI < 0.10 = little change (low drift)
    - PSI >= 0.25 = significant change (high drift)
    """
    # Create bins based on baseline data
    try:
        baseline_counts, bin_edges = np.histogram(baseline_values, bins=bins)
        current_counts, _ = np.histogram(current_values, bins=bin_edges)
        
        # Convert to proportions
        baseline_props = baseline_counts / baseline_counts.sum()
        current_props = current_counts / current_counts.sum()
        
        # Calculate PSI: sum of (current_prop - baseline_prop) * log(current_prop / baseline_prop)
        # Add small epsilon to avoid log(0)
        epsilon = 1e-10
        baseline_props = np.clip(baseline_props, epsilon, 1)
        current_props = np.clip(current_props, epsilon, 1)
        
        psi = np.sum((current_props - baseline_props) * np.log(current_props / baseline_props))
        
        return float(psi)
    except Exception as e:
        print(f"Error calculating PSI: {e}")
        return 0.0


def get_drift_level(psi_score: float) -> str:
    """Determine drift level based on PSI score."""
    if psi_score < PSI_THRESHOLD_MEDIUM:
        return "low"
    elif psi_score < PSI_THRESHOLD_HIGH:
        return "medium"
    else:
        return "high"


def calculate_accuracy(db: Session, predictions: List[Prediction]) -> float:
    """
    Calculate accuracy for a set of predictions.
    
    Accuracy = correct predictions / total predictions with labels
    
    Prediction mapping:
    - "low_risk" or "medium_risk" → predicted "no_default"
    - "high_risk" → predicted "default"
    """
    if not predictions:
        return 0.0
    
    prediction_ids = [p.prediction_id for p in predictions]
    
    # Get labels for these predictions
    labels = db.query(GroundTruthLabel).filter(
        GroundTruthLabel.prediction_id.in_(prediction_ids)
    ).all()
    
    if not labels:
        return 0.0
    
    # Create a mapping of prediction_id to label
    label_map = {label.prediction_id: label.actual_label for label in labels}
    
    # Map predictions to expected labels
    correct = 0
    total = 0
    
    for pred in predictions:
        if pred.prediction_id in label_map:
            actual_label = label_map[pred.prediction_id]
            
            # Map prediction to expected label
            if pred.prediction in ["low_risk", "medium_risk"]:
                predicted_label = "no_default"
            else:  # high_risk
                predicted_label = "default"
            
            if predicted_label == actual_label:
                correct += 1
            
            total += 1
    
    if total == 0:
        return 0.0
    
    return correct / total


def calculate_drift(db: Session, model_name: str, model_version: str) -> DriftRunResponse:
    """
    Calculate drift metrics comparing baseline vs current data.
    
    Returns drift analysis including PSI, KS-test, and accuracy metrics.
    """
    # Split data into baseline and current
    baseline_preds, current_preds = split_baseline_current(db, model_name, model_version)
    
    if not baseline_preds or not current_preds:
        raise ValueError(f"Insufficient data: baseline={len(baseline_preds)}, current={len(current_preds)}")
    
    # Calculate accuracy for each period
    baseline_accuracy = calculate_accuracy(db, baseline_preds)
    current_accuracy = calculate_accuracy(db, current_preds)
    accuracy_drop = baseline_accuracy - current_accuracy
    
    # Calculate drift metrics for each feature
    features_drift = []
    drift_levels = []
    
    for feature_name in FEATURES_TO_CHECK:
        # Extract feature values from baseline and current
        baseline_values = []
        current_values = []
        
        for pred in baseline_preds:
            if feature_name in pred.input_features:
                baseline_values.append(float(pred.input_features[feature_name]))
        
        for pred in current_preds:
            if feature_name in pred.input_features:
                current_values.append(float(pred.input_features[feature_name]))
        
        if not baseline_values or not current_values:
            continue
        
        # Convert to numpy arrays
        baseline_array = np.array(baseline_values)
        current_array = np.array(current_values)
        
        # Calculate PSI
        psi_score = calculate_psi(baseline_array, current_array, bins=10)
        
        # Calculate KS-test
        ks_stat, ks_pval = ks_2samp(baseline_array, current_array)
        
        # Determine drift level
        drift_level = get_drift_level(psi_score)
        drift_levels.append(drift_level)
        
        # Store in database
        drift_metric = DriftMetric(
            model_name=model_name,
            model_version=model_version,
            feature_name=feature_name,
            psi_score=psi_score,
            ks_statistic=float(ks_stat),
            ks_p_value=float(ks_pval),
            drift_level=drift_level
        )
        db.add(drift_metric)
        
        # Create response object
        features_drift.append(DriftFeatureDetail(
            feature_name=feature_name,
            psi_score=psi_score,
            ks_statistic=float(ks_stat),
            ks_p_value=float(ks_pval),
            drift_level=drift_level
        ))
    
    db.commit()
    
    # Determine overall drift level
    if "high" in drift_levels:
        overall_drift_level = "high"
    elif "medium" in drift_levels:
        overall_drift_level = "medium"
    else:
        overall_drift_level = "low"
    
    return DriftRunResponse(
        status="success",
        model_name=model_name,
        model_version=model_version,
        overall_drift_level=overall_drift_level,
        baseline_accuracy=baseline_accuracy,
        current_accuracy=current_accuracy,
        accuracy_drop=accuracy_drop,
        baseline_sample_size=len(baseline_preds),
        current_sample_size=len(current_preds),
        features=features_drift,
        calculated_at=datetime.utcnow()
    )


def get_latest_drift_metrics(db: Session, model_name: str, model_version: str) -> List[DriftMetric]:
    """Get latest drift calculations for each feature."""
    # Get the latest calculation timestamp
    latest = db.query(DriftMetric).filter(
        DriftMetric.model_name == model_name,
        DriftMetric.model_version == model_version
    ).order_by(desc(DriftMetric.calculated_at)).first()
    
    if not latest:
        return []
    
    # Get all metrics from latest calculation
    latest_metrics = db.query(DriftMetric).filter(
        DriftMetric.model_name == model_name,
        DriftMetric.model_version == model_version,
        DriftMetric.calculated_at == latest.calculated_at
    ).all()
    
    return latest_metrics


def get_drift_summary(db: Session, model_name: str, model_version: str) -> dict:
    """Get summary statistics of latest drift calculation."""
    latest_metrics = get_latest_drift_metrics(db, model_name, model_version)
    
    if not latest_metrics:
        raise ValueError("No drift metrics found")
    
    psi_scores = [m.psi_score for m in latest_metrics]
    drift_levels = [m.drift_level for m in latest_metrics]
    
    # Count drift levels
    high_count = sum(1 for d in drift_levels if d == "high")
    medium_count = sum(1 for d in drift_levels if d == "medium")
    low_count = sum(1 for d in drift_levels if d == "low")
    
    # Determine overall drift level
    if high_count > 0:
        overall_drift_level = "high"
    elif medium_count > 0:
        overall_drift_level = "medium"
    else:
        overall_drift_level = "low"
    
    # Calculate accuracy from latest baseline/current split
    baseline_preds, current_preds = split_baseline_current(db, model_name, model_version)
    baseline_accuracy = calculate_accuracy(db, baseline_preds)
    current_accuracy = calculate_accuracy(db, current_preds)
    accuracy_drop = baseline_accuracy - current_accuracy
    
    return {
        "model_name": model_name,
        "model_version": model_version,
        "overall_drift_level": overall_drift_level,
        "avg_psi": float(np.mean(psi_scores)),
        "max_psi": float(np.max(psi_scores)),
        "min_psi": float(np.min(psi_scores)),
        "baseline_accuracy": baseline_accuracy,
        "current_accuracy": current_accuracy,
        "accuracy_drop": accuracy_drop,
        "high_drift_features": high_count,
        "medium_drift_features": medium_count,
        "low_drift_features": low_count,
        "calculated_at": latest_metrics[0].calculated_at if latest_metrics else datetime.utcnow()
    }
