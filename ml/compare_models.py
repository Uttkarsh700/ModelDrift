"""
ModelDrift Model Comparison

Simple script to compare MLflow experiment runs and show champion model.

Usage:
    python ml/compare_models.py
"""
import os
import sys
from mlflow.tracking import MlflowClient
import mlflow

# Configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
EXPERIMENT_NAME = "ModelDrift-CreditRisk"


def get_mlflow_runs(tracking_uri=MLFLOW_TRACKING_URI, experiment_name=EXPERIMENT_NAME):
    """
    Fetch all runs from MLflow experiment, sorted by accuracy.
    
    Args:
        tracking_uri: MLflow tracking server URI
        experiment_name: Experiment name
        
    Returns:
        tuple: (client, experiment_id, runs_list)
    """
    # Set tracking URI
    mlflow.set_tracking_uri(tracking_uri)
    
    client = MlflowClient(tracking_uri)
    
    print(f"📡 Connecting to MLflow: {tracking_uri}")
    
    try:
        # Get experiment
        experiment = client.get_experiment_by_name(experiment_name)
        
        if not experiment:
            print(f"❌ Experiment '{experiment_name}' not found in MLflow")
            print(f"   Have you run retraining yet?")
            print(f"   python ml/retrain_model.py")
            return None, None, []
        
        experiment_id = experiment.experiment_id
        print(f"✅ Found experiment: {experiment_name} (ID: {experiment_id})")
        
        # Get all runs
        runs = client.search_runs(experiment_ids=[experiment_id])
        
        if not runs:
            print(f"❌ No runs found in experiment '{experiment_name}'")
            return client, experiment_id, []
        
        print(f"✅ Found {len(runs)} runs")
        return client, experiment_id, runs
        
    except Exception as e:
        print(f"❌ Error connecting to MLflow: {e}")
        print(f"   Is MLflow running? Start it with:")
        print(f"   mlflow server --host 0.0.0.0 --port 5000")
        return None, None, []


def sort_runs_by_metric(runs, metric_name="accuracy"):
    """
    Sort runs by metric (descending).
    
    Args:
        runs: List of MLflow runs
        metric_name: Metric to sort by
        
    Returns:
        list: Sorted runs
    """
    def get_metric(run):
        # MLflow stores metrics in run.data.metrics
        if run.data.metrics and metric_name in run.data.metrics:
            return run.data.metrics[metric_name]
        return -1  # Runs without the metric go to the end
    
    return sorted(runs, key=get_metric, reverse=True)


def display_run_details(run, rank=1):
    """
    Print details of a single run in a readable format.
    
    Args:
        run: MLflow run object
        rank: Rank number (1st, 2nd, etc.)
    """
    run_id = run.info.run_id[:8]  # Short run ID
    status = run.info.status
    
    # Get metrics
    metrics = run.data.metrics or {}
    accuracy = metrics.get("accuracy", 0)
    precision = metrics.get("precision", 0)
    recall = metrics.get("recall", 0)
    f1_score = metrics.get("f1_score", 0)
    
    # Get params
    params = run.data.params or {}
    n_estimators = params.get("n_estimators", "?")
    max_depth = params.get("max_depth", "?")
    
    # Determine medal
    if rank == 1:
        medal = "🥇"
        champion_label = " (CHAMPION)"
    elif rank == 2:
        medal = "🥈"
        champion_label = ""
    elif rank == 3:
        medal = "🥉"
        champion_label = ""
    else:
        medal = "  "
        champion_label = ""
    
    print(f"\n{medal} Rank {rank}{champion_label}")
    print(f"  Run ID:      {run_id}")
    print(f"  Status:      {status}")
    print(f"  Accuracy:    {accuracy:.4f}")
    print(f"  Precision:   {precision:.4f}")
    print(f"  Recall:      {recall:.4f}")
    print(f"  F1-Score:    {f1_score:.4f}")
    print(f"  Hyperparams: n_estimators={n_estimators}, max_depth={max_depth}")


def main():
    """Main model comparison."""
    print("=" * 70)
    print("📊 ModelDrift Model Comparison")
    print("=" * 70)
    
    # Fetch runs
    client, experiment_id, runs = get_mlflow_runs()
    
    if not runs:
        print("\n⚠️  No runs to compare.")
        sys.exit(1)
    
    # Sort by accuracy
    sorted_runs = sort_runs_by_metric(runs, "accuracy")
    
    print(f"\n📈 Top {min(len(sorted_runs), 5)} Runs (sorted by accuracy):")
    print("-" * 70)
    
    for i, run in enumerate(sorted_runs[:5], 1):
        display_run_details(run, rank=i)
    
    # Champion details
    champion_run = sorted_runs[0]
    champion_metrics = champion_run.data.metrics or {}
    
    print("\n" + "=" * 70)
    print("🏆 Champion Model")
    print("=" * 70)
    print(f"Run ID:          {champion_run.info.run_id[:8]}")
    print(f"Accuracy:        {champion_metrics.get('accuracy', 0):.4f}")
    print(f"Precision:       {champion_metrics.get('precision', 0):.4f}")
    print(f"Recall:          {champion_metrics.get('recall', 0):.4f}")
    print(f"F1-Score:        {champion_metrics.get('f1_score', 0):.4f}")
    print(f"\nExperiment:      {EXPERIMENT_NAME}")
    print(f"MLflow UI:       {MLFLOW_TRACKING_URI}")
    print("=" * 70)


if __name__ == "__main__":
    main()
