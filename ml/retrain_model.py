"""
ModelDrift Retraining Pipeline

Fetches training data from the backend, trains a RandomForestClassifier,
and logs metrics/model to MLflow for experiment tracking.

Usage:
    python ml/retrain_model.py
"""
import os
import sys
import json
import pickle
from datetime import datetime
import requests
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import mlflow

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_SAVE_PATH = "ml/models/credit_risk_latest.pkl"
EXPERIMENT_NAME = "ModelDrift-CreditRisk"

# Feature columns in order
FEATURE_COLUMNS = [
    "credit_utilization",
    "debt_to_income",
    "num_recent_inquiries",
    "avg_account_age_months",
    "num_open_accounts"
]

# Label mapping
LABEL_MAP = {
    "no_default": 0,
    "default": 1
}


def fetch_training_data(backend_url=BACKEND_URL, model_name="credit_risk", model_version="v1"):
    """
    Fetch training dataset from backend /api/v1/training/dataset endpoint.
    
    Returns:
        dict: Response with 'data' key containing training samples
    """
    url = f"{backend_url}/api/v1/training/dataset"
    params = {
        "model_name": model_name,
        "model_version": model_version
    }
    
    print(f"📡 Fetching training data from {url}...")
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] != "success":
            print(f"❌ Backend error: {data.get('message', 'Unknown error')}")
            return {"data": []}
        
        print(f"✅ Fetched {data['total_samples']} training samples")
        return data
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running on http://localhost:8000?")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        sys.exit(1)


def prepare_dataframe(training_samples):
    """
    Convert training samples into a pandas DataFrame with features and labels.
    
    Args:
        training_samples: List of dicts with input_features and actual_label
        
    Returns:
        pd.DataFrame: Prepared data with feature columns and 'label' column
    """
    if not training_samples:
        print("❌ No training samples available")
        sys.exit(1)
    
    # Extract features and labels
    rows = []
    for sample in training_samples:
        row = {}
        
        # Extract each feature from input_features dict
        input_features = sample.get("input_features", {})
        for feature_name in FEATURE_COLUMNS:
            row[feature_name] = input_features.get(feature_name, 0.0)
        
        # Convert label to binary (0 = no_default, 1 = default)
        actual_label = sample.get("actual_label", "no_default")
        row["label"] = LABEL_MAP.get(actual_label, 0)
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    print(f"✅ Prepared DataFrame with {len(df)} samples and {len(FEATURE_COLUMNS)} features")
    
    return df


def train_model(X_train, y_train, n_estimators=100, max_depth=10):
    """
    Train a RandomForestClassifier.
    
    Args:
        X_train: Training features
        y_train: Training labels
        n_estimators: Number of trees in the forest
        max_depth: Maximum depth of trees
        
    Returns:
        RandomForestClassifier: Trained model
    """
    print(f"\n🤖 Training RandomForestClassifier (n_estimators={n_estimators}, max_depth={max_depth})...")
    
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42,
        n_jobs=-1  # Use all CPU cores
    )
    model.fit(X_train, y_train)
    
    print("✅ Model training complete")
    return model


def evaluate_model(model, X_test, y_test):
    """
    Evaluate model on test set and calculate metrics.
    
    Args:
        model: Trained model
        X_test: Test features
        y_test: Test labels
        
    Returns:
        dict: Metrics (accuracy, precision, recall, f1_score)
    """
    print("\n📊 Evaluating model on test set...")
    
    y_pred = model.predict(X_test)
    
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1_score": f1_score(y_test, y_pred, zero_division=0)
    }
    
    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f}")
    print(f"  F1-Score:  {metrics['f1_score']:.4f}")
    
    return metrics


def log_to_mlflow(model, model_params, metrics, X_train, X_test, y_train, y_test):
    """
    Log model, parameters, and metrics to MLflow.
    
    Args:
        model: Trained model
        model_params: Model hyperparameters dict
        metrics: Evaluation metrics dict
        X_train, X_test, y_train, y_test: Train/test data for logging
    """
    # Set MLflow tracking URI
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    
    # Set experiment
    mlflow.set_experiment(EXPERIMENT_NAME)
    
    print(f"\n📝 Logging to MLflow (experiment: {EXPERIMENT_NAME})...")
    
    with mlflow.start_run() as run:
        # Log parameters
        mlflow.log_params({
            "model_type": "RandomForestClassifier",
            **model_params
        })
        
        # Log metrics
        mlflow.log_metrics(metrics)
        
        # Log additional info
        mlflow.log_params({
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "features": len(FEATURE_COLUMNS)
        })
        
        # Log model
        mlflow.sklearn.log_model(model, "model")
        
        run_id = run.info.run_id
        print(f"✅ MLflow run created: {run_id}")
        print(f"   Experiment: {EXPERIMENT_NAME}")
        print(f"   Tracking URI: {MLFLOW_TRACKING_URI}")
        
        return run_id


def save_model(model, filepath):
    """
    Save trained model to disk using pickle.
    
    Args:
        model: Trained model
        filepath: Path to save model file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, "wb") as f:
        pickle.dump(model, f)
    
    print(f"\n💾 Model saved to {filepath}")


def main():
    """Main retraining pipeline."""
    print("=" * 70)
    print("🔄 ModelDrift Retraining Pipeline")
    print("=" * 70)
    
    # Step 1: Fetch training data
    response = fetch_training_data()
    training_samples = response.get("data", [])
    
    if not training_samples:
        print("❌ No training data available. Generate demo data first:")
        print("   python scripts/generate_demo_data.py")
        sys.exit(1)
    
    # Step 2: Prepare DataFrame
    df = prepare_dataframe(training_samples)
    
    # Step 3: Split data
    X = df[FEATURE_COLUMNS]
    y = df["label"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n📊 Dataset split:")
    print(f"  Total samples: {len(df)}")
    print(f"  Train samples: {len(X_train)} ({len(X_train)/len(df)*100:.1f}%)")
    print(f"  Test samples:  {len(X_test)} ({len(X_test)/len(df)*100:.1f}%)")
    
    # Step 4: Train model
    model_params = {
        "n_estimators": 100,
        "max_depth": 10
    }
    model = train_model(X_train, y_train, **model_params)
    
    # Step 5: Evaluate model
    metrics = evaluate_model(model, X_test, y_test)
    
    # Step 6: Log to MLflow
    try:
        run_id = log_to_mlflow(model, model_params, metrics, X_train, X_test, y_train, y_test)
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to MLflow: {e}")
        print("   MLflow is optional. Model will still be saved locally.")
        run_id = None
    
    # Step 7: Save model
    save_model(model, MODEL_SAVE_PATH)
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ Retraining Complete!")
    print("=" * 70)
    print(f"Model Type:        RandomForestClassifier")
    print(f"Dataset Size:      {len(df)} samples")
    print(f"Train/Test Split:  80%/20% ({len(X_train)}/{len(X_test)})")
    print(f"Features:          {len(FEATURE_COLUMNS)}")
    print(f"\nMetrics:")
    print(f"  Accuracy:        {metrics['accuracy']:.4f}")
    print(f"  Precision:       {metrics['precision']:.4f}")
    print(f"  Recall:          {metrics['recall']:.4f}")
    print(f"  F1-Score:        {metrics['f1_score']:.4f}")
    print(f"\nArtifacts:")
    print(f"  Model File:      {MODEL_SAVE_PATH}")
    if run_id:
        print(f"  MLflow Run ID:   {run_id}")
        print(f"  View in UI:      {MLFLOW_TRACKING_URI}")
    print("=" * 70)


if __name__ == "__main__":
    main()
