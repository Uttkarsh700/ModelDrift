"""
Example: Log a single prediction to ModelDrift.

This script demonstrates the basic usage of the ModelDrift SDK.

Usage:
    python log_single_prediction.py
"""
from modeldrift import ModelDriftClient


def main():
    """Log a single prediction."""
    # Initialize client pointing to backend
    client = ModelDriftClient(base_url="http://localhost:8000")
    
    print("🚀 Logging prediction to ModelDrift backend...")
    
    try:
        # Log a prediction
        response = client.log_prediction(
            model_name="credit_risk",
            model_version="v1",
            prediction_id="pred_001",
            input_features={
                "credit_utilization": 0.72,
                "debt_to_income": 0.43,
                "num_recent_inquiries": 3,
                "delinquency_status": 0
            },
            prediction="high_risk",
            confidence=0.91
        )
        
        print(f"✅ Prediction logged successfully!")
        print(f"   Status: {response['status']}")
        print(f"   Prediction ID: {response['prediction_id']}")
        
    except ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("   Make sure the backend is running: python -m uvicorn app.main:app --reload")
    except ValueError as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
