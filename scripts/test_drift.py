"""
Quick test script for drift detection.

This script:
1. Resets demo data
2. Generates fresh demo data
3. Runs drift detection
4. Displays results

Usage:
    python scripts/test_drift.py
"""
import subprocess
import sys
import json
import time
import requests
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report status."""
    print(f"\n{'=' * 60}")
    print(f"📝 {description}")
    print('=' * 60)
    result = subprocess.run(cmd, shell=True, capture_output=False)
    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        return False
    return True


def test_drift_api():
    """Test drift detection API endpoints."""
    print(f"\n{'=' * 60}")
    print("🔍 Testing Drift Detection API")
    print('=' * 60)
    
    base_url = "http://localhost:8000/api/v1/drift"
    
    # Test 1: Run drift calculation
    print("\n1️⃣  Running drift calculation...")
    try:
        response = requests.post(f"{base_url}/run?model_name=credit_risk&model_version=v1")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Drift calculation complete")
            print(f"   Overall drift level: {data['overall_drift_level'].upper()}")
            print(f"   Baseline accuracy: {data['baseline_accuracy']:.2%}")
            print(f"   Current accuracy: {data['current_accuracy']:.2%}")
            print(f"   Accuracy drop: {data['accuracy_drop']:.2%}")
            print(f"   Features analyzed: {len(data['features'])}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 2: Get latest metrics
    print("\n2️⃣  Fetching latest drift metrics...")
    try:
        response = requests.get(f"{base_url}/latest?model_name=credit_risk&model_version=v1")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Latest metrics retrieved")
            print(f"   Features with metrics: {len(data['features'])}")
            for feature in data['features'][:3]:  # Show first 3
                print(f"   - {feature['feature_name']:30s} PSI: {feature['psi_score']:6.3f} Level: {feature['drift_level']}")
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 3: Get summary
    print("\n3️⃣  Fetching drift summary...")
    try:
        response = requests.get(f"{base_url}/summary?model_name=credit_risk&model_version=v1")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Summary retrieved")
            print(f"   Overall drift level: {data['overall_drift_level'].upper()}")
            print(f"   Average PSI: {data['avg_psi']:.3f}")
            print(f"   Max PSI: {data['max_psi']:.3f}")
            print(f"   High drift features: {data['high_drift_features']}")
            print(f"   Medium drift features: {data['medium_drift_features']}")
            print(f"   Low drift features: {data['low_drift_features']}")
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    return True


def main():
    """Run full drift detection test."""
    print("🚀 ModelDrift Drift Detection Test\n")
    
    # Check if backend is running
    print("📌 Checking backend connectivity...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code != 200:
            print("❌ Backend is not responding to health check")
            print("   Start backend: cd backend && python -m uvicorn app.main:app --reload")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("   Start backend: cd backend && python -m uvicorn app.main:app --reload")
        return
    
    print("✅ Backend is running\n")
    
    # Step 1: Reset data
    if not run_command(
        "python scripts/reset_demo_data.py",
        "Step 1: Resetting demo data"
    ):
        return
    
    # Wait for user to confirm
    print("\n⏸️  Waiting for reset to complete...")
    time.sleep(2)
    
    # Step 2: Generate demo data
    if not run_command(
        "python scripts/generate_demo_data.py",
        "Step 2: Generating fresh demo data"
    ):
        return
    
    # Wait for data to be inserted
    print("\n⏸️  Waiting for data insertion...")
    time.sleep(2)
    
    # Step 3: Test drift API
    if not test_drift_api():
        return
    
    print(f"\n{'=' * 60}")
    print("✅ All drift detection tests passed!")
    print('=' * 60)
    print("\n💡 Next steps:")
    print("   View in Swagger: http://localhost:8000/docs")
    print("   Check specific endpoints:")
    print("   - POST /api/v1/drift/run")
    print("   - GET /api/v1/drift/latest")
    print("   - GET /api/v1/drift/summary\n")


if __name__ == "__main__":
    main()
