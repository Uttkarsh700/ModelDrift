"""
Example: Log ground truth labels to ModelDrift.

This script demonstrates how to send actual outcomes (ground truth labels)
for previously logged predictions.

Usage:
    python log_ground_truth.py
"""
from modeldrift import ModelDriftClient


def main():
    """Log ground truth labels for sample predictions."""
    client = ModelDriftClient(base_url="http://localhost:8000")
    
    # Sample data: prediction_id -> actual_label
    ground_truths = [
        ("pred_001", "default"),
        ("pred_002", "no_default"),
        ("pred_003", "default"),
        ("batch_demo_001", "no_default"),
        ("batch_demo_002", "default"),
        ("batch_demo_005", "default"),
    ]
    
    total_labels = len(ground_truths)
    failed = 0
    
    print(f"🚀 Logging {total_labels} ground truth labels to ModelDrift...")
    print()
    
    try:
        for i, (prediction_id, actual_label) in enumerate(ground_truths, 1):
            try:
                response = client.log_ground_truth(
                    prediction_id=prediction_id,
                    actual_label=actual_label
                )
                
                status_icon = "✅" if response['status'] == "success" else "⚠️"
                print(f"{status_icon} [{i}/{total_labels}] {prediction_id}: {actual_label}")
                
            except Exception as e:
                failed += 1
                print(f"❌ [{i}/{total_labels}] {prediction_id}: Error - {e}")
        
        print()
        print(f"📊 Summary:")
        print(f"   Total sent: {total_labels}")
        print(f"   Successful: {total_labels - failed}")
        print(f"   Failed: {failed}")
        
        if failed == 0:
            print(f"   ✅ All labels logged successfully!")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
"""
Example: Log batch predictions to ModelDrift.

This script generates and logs 20 sample credit risk predictions
to demonstrate batch logging.

Usage:
    python log_batch_predictions.py
"""
import random
from modeldrift import ModelDriftClient


def generate_sample_features():
    """Generate random credit risk features."""
    return {
        "credit_utilization": round(random.uniform(0, 1), 2),
        "debt_to_income": round(random.uniform(0, 1), 2),
        "num_recent_inquiries": random.randint(0, 10),
        "delinquency_status": random.randint(0, 3),
        "average_account_age": random.randint(1, 30),
        "num_credit_accounts": random.randint(1, 20),
        "payment_history_score": random.randint(300, 850)
    }


def main():
    """Log batch predictions."""
    # Initialize client
    client = ModelDriftClient(base_url="http://localhost:8000")
    
    risk_levels = ["low_risk", "medium_risk", "high_risk"]
    total_predictions = 20
    failed = 0
    
    print(f"🚀 Logging {total_predictions} sample predictions to ModelDrift...")
    print()
    
    try:
        for i in range(1, total_predictions + 1):
            prediction_id = f"batch_demo_{i:03d}"
            risk_level = random.choice(risk_levels)
            confidence = round(random.uniform(0.65, 0.99), 2)
            
            try:
                response = client.log_prediction(
                    model_name="credit_risk",
                    model_version="v1",
                    prediction_id=prediction_id,
                    input_features=generate_sample_features(),
                    prediction=risk_level,
                    confidence=confidence
                )
                
                status_icon = "✅" if response['status'] == "success" else "⚠️"
                print(f"{status_icon} [{i:2d}/{total_predictions}] {prediction_id}: {risk_level} (confidence: {confidence})")
                
            except Exception as e:
                failed += 1
                print(f"❌ [{i:2d}/{total_predictions}] {prediction_id}: Error - {e}")
        
        print()
        print(f"📊 Summary:")
        print(f"   Total sent: {total_predictions}")
        print(f"   Successful: {total_predictions - failed}")
        print(f"   Failed: {failed}")
        
        if failed == 0:
            print(f"   ✅ All predictions logged successfully!")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
