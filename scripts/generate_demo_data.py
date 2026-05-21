"""
Generate realistic demo data for ModelDrift testing.

This script creates two time periods:
1. Baseline data: Healthier credit profiles, lower defaults
2. Current data: Riskier profiles showing drift, higher defaults

Usage:
    python scripts/generate_demo_data.py
"""
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path so we can import modeldrift SDK
sys.path.insert(0, str(Path(__file__).parent.parent / "sdk"))

from modeldrift import ModelDriftClient


def generate_baseline_features():
    """Generate healthier credit profile features."""
    return {
        "credit_utilization": round(random.uniform(0.15, 0.50), 2),
        "debt_to_income": round(random.uniform(0.10, 0.40), 2),
        "num_recent_inquiries": random.randint(0, 2),
        "avg_account_age_months": random.randint(60, 180),
        "num_open_accounts": random.randint(2, 8),
    }


def generate_current_features():
    """Generate riskier credit profile features showing drift."""
    return {
        "credit_utilization": round(random.uniform(0.50, 0.95), 2),
        "debt_to_income": round(random.uniform(0.40, 0.85), 2),
        "num_recent_inquiries": random.randint(2, 8),
        "avg_account_age_months": random.randint(12, 60),
        "num_open_accounts": random.randint(8, 15),
    }


def predict_baseline_risk(features):
    """Determine risk level for baseline data (healthier)."""
    score = (
        features["credit_utilization"] * 0.3 +
        features["debt_to_income"] * 0.3 +
        (features["num_recent_inquiries"] / 10) * 0.2 +
        (1 - features["avg_account_age_months"] / 200) * 0.1 +
        (features["num_open_accounts"] / 20) * 0.1
    )
    
    if score < 0.3:
        return "low_risk", round(random.uniform(0.80, 0.98), 2)
    elif score < 0.6:
        return "medium_risk", round(random.uniform(0.70, 0.85), 2)
    else:
        return "high_risk", round(random.uniform(0.60, 0.80), 2)


def predict_current_risk(features):
    """Determine risk level for current data (showing drift)."""
    score = (
        features["credit_utilization"] * 0.3 +
        features["debt_to_income"] * 0.3 +
        (features["num_recent_inquiries"] / 10) * 0.2 +
        (1 - features["avg_account_age_months"] / 200) * 0.1 +
        (features["num_open_accounts"] / 20) * 0.1
    )
    
    if score < 0.4:
        return "low_risk", round(random.uniform(0.75, 0.90), 2)
    elif score < 0.65:
        return "medium_risk", round(random.uniform(0.65, 0.80), 2)
    else:
        return "high_risk", round(random.uniform(0.55, 0.78), 2)


def generate_ground_truth(risk_level, data_type):
    """
    Generate ground truth label based on risk level.
    
    Current data is slightly worse (less accurate), so defaults are more likely.
    """
    if data_type == "baseline":
        # Baseline: mostly accurate predictions
        if risk_level == "low_risk":
            return "no_default" if random.random() > 0.05 else "default"
        elif risk_level == "medium_risk":
            return "no_default" if random.random() > 0.15 else "default"
        else:  # high_risk
            return "default" if random.random() > 0.25 else "no_default"
    else:
        # Current: less accurate, more defaults
        if risk_level == "low_risk":
            return "no_default" if random.random() > 0.15 else "default"
        elif risk_level == "medium_risk":
            return "default" if random.random() > 0.45 else "no_default"
        else:  # high_risk
            return "default" if random.random() > 0.15 else "no_default"


def main():
    """Generate and load demo data."""
    print("🚀 ModelDrift Demo Data Generator\n")
    print("=" * 60)
    
    # Initialize SDK client
    try:
        client = ModelDriftClient(base_url="http://localhost:8000")
        print("✅ Connected to ModelDrift backend\n")
    except Exception as e:
        print(f"❌ Failed to connect to backend: {e}")
        print("   Make sure backend is running: python -m uvicorn app.main:app --reload")
        return
    
    # Generate baseline data (300 predictions)
    print("📊 Generating baseline data (healthier profiles)...")
    baseline_pred_ids = []
    baseline_count = 0
    baseline_label_count = 0
    
    for i in range(1, 301):
        try:
            features = generate_baseline_features()
            risk_level, confidence = predict_baseline_risk(features)
            prediction_id = f"baseline_{i:04d}"
            
            # Log prediction
            response = client.log_prediction(
                model_name="credit_risk",
                model_version="v1",
                prediction_id=prediction_id,
                input_features=features,
                prediction=risk_level,
                confidence=confidence
            )
            
            baseline_pred_ids.append(prediction_id)
            baseline_count += 1
            
            # Log ground truth for 80% of baseline predictions
            if random.random() > 0.20:
                actual_label = generate_ground_truth(risk_level, "baseline")
                try:
                    client.log_ground_truth(
                        prediction_id=prediction_id,
                        actual_label=actual_label
                    )
                    baseline_label_count += 1
                except Exception as e:
                    pass  # Some might fail due to duplicate, that's ok
            
            if i % 50 == 0:
                print(f"  ✅ Baseline: {i}/300 predictions")
                
        except Exception as e:
            print(f"  ⚠️  Error on baseline {i}: {e}")
    
    print(f"  ✅ Baseline complete: {baseline_count} predictions, {baseline_label_count} labels\n")
    
    # Generate current data (200 predictions - riskier)
    print("📊 Generating current data (riskier profiles - showing drift)...")
    current_pred_ids = []
    current_count = 0
    current_label_count = 0
    
    for i in range(1, 201):
        try:
            features = generate_current_features()
            risk_level, confidence = predict_current_risk(features)
            prediction_id = f"current_{i:04d}"
            
            # Log prediction
            response = client.log_prediction(
                model_name="credit_risk",
                model_version="v1",
                prediction_id=prediction_id,
                input_features=features,
                prediction=risk_level,
                confidence=confidence
            )
            
            current_pred_ids.append(prediction_id)
            current_count += 1
            
            # Log ground truth for 90% of current predictions
            if random.random() > 0.10:
                actual_label = generate_ground_truth(risk_level, "current")
                try:
                    client.log_ground_truth(
                        prediction_id=prediction_id,
                        actual_label=actual_label
                    )
                    current_label_count += 1
                except Exception as e:
                    pass  # Some might fail due to duplicate, that's ok
            
            if i % 50 == 0:
                print(f"  ✅ Current: {i}/200 predictions")
                
        except Exception as e:
            print(f"  ⚠️  Error on current {i}: {e}")
    
    print(f"  ✅ Current complete: {current_count} predictions, {current_label_count} labels\n")
    
    # Summary
    print("=" * 60)
    print("📈 Demo Data Summary:\n")
    print(f"  Baseline predictions:  {baseline_count}")
    print(f"  Baseline labels:       {baseline_label_count}")
    print(f"  Current predictions:   {current_count}")
    print(f"  Current labels:        {current_label_count}")
    print(f"  Total predictions:     {baseline_count + current_count}")
    print(f"  Total labels:          {baseline_label_count + current_label_count}")
    print("\n✅ Demo data generation complete!")
    print("\n📝 What was created:")
    print("  • Baseline data: Healthier credit profiles (older accounts, lower utilization)")
    print("  • Current data:  Riskier profiles showing drift (newer accounts, higher utilization)")
    print("  • Ground truth:  Actual outcomes (no_default vs default)")
    print("\n🚀 Ready for drift detection testing!")
    print("\n💡 Verify the data:")
    print("  curl http://localhost:8000/api/v1/predictions/recent?limit=20")
    print("  curl http://localhost:8000/api/v1/labels/recent?limit=20")
    print("  Or visit: http://localhost:8000/docs\n")
    
    client.close()


if __name__ == "__main__":
    main()
