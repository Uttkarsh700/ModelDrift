# ModelDrift Python SDK

Python SDK for logging ML model predictions and ground truth labels to the ModelDrift backend.

## Overview

ModelDrift SDK simplifies integration of your ML applications with the ModelDrift monitoring system. Instead of manually making HTTP requests, you can use simple function calls to log predictions and outcomes.

```python
from modeldrift import ModelDriftClient

client = ModelDriftClient(base_url="http://localhost:8000")

# Log a prediction
client.log_prediction(
    model_name="credit_risk",
    model_version="v1",
    prediction_id="pred_001",
    input_features={
        "credit_utilization": 0.72,
        "debt_to_income": 0.43,
        "num_recent_inquiries": 3
    },
    prediction="high_risk",
    confidence=0.91
)

# Later, when ground truth is available
client.log_ground_truth(
    prediction_id="pred_001",
    actual_label="default"
)
```

## Installation

### Local Development Installation

```bash
# Navigate to sdk directory
cd sdk

# Install SDK in development mode
pip install -e .

# Or install with the full pyproject.toml
pip install -e . --no-deps
```

### Direct Usage (Without Installation)

You can also use the SDK directly from source without installing:

```bash
# Add the sdk/modeldrift directory to your Python path
# Then: from modeldrift import ModelDriftClient
```

## Quick Start

### 1. Make sure backend is running

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Backend will start at `http://localhost:8000`

### 2. Use the SDK in your ML app

```python
from modeldrift import ModelDriftClient

# Initialize client
client = ModelDriftClient(base_url="http://localhost:8000")

# Log prediction after model inference
prediction_result = model.predict(input_data)
response = client.log_prediction(
    model_name="my_model",
    model_version="v1.0",
    prediction_id=str(uuid.uuid4()),
    input_features=input_data,
    prediction=prediction_result,
    confidence=0.95
)

# When outcome is known (hours/days later)
client.log_ground_truth(
    prediction_id=prediction_id,
    actual_label=true_outcome
)

# Close connection when done
client.close()
```

## API Reference

### ModelDriftClient

#### `__init__(base_url="http://localhost:8000", timeout=10)`

Initialize the client.

**Parameters:**
- `base_url` (str): Base URL of the ModelDrift API. Default: `http://localhost:8000`
- `timeout` (int): Request timeout in seconds. Default: `10`

#### `log_prediction(model_name, model_version, prediction_id, input_features, prediction, confidence)`

Log a model prediction.

**Parameters:**
- `model_name` (str): Name of the model (e.g., "credit_risk", "fraud_detector")
- `model_version` (str): Version of the model (e.g., "v1", "v1.2.3")
- `prediction_id` (str): Unique identifier for this prediction (must be unique across all predictions)
- `input_features` (dict): Input features used for prediction. Supports nested dictionaries and lists.
- `prediction` (str): Predicted label or value
- `confidence` (float): Confidence score between 0.0 and 1.0

**Returns:**
- `dict`: Response with keys: `{"status": "success", "prediction_id": "..."}`

**Raises:**
- `ConnectionError`: If backend is unavailable
- `TimeoutError`: If request times out
- `ValueError`: If API returns error (e.g., duplicate prediction_id)

#### `log_ground_truth(prediction_id, actual_label)`

Log ground truth label for a prediction.

**Parameters:**
- `prediction_id` (str): ID of the prediction (must match a previously logged prediction)
- `actual_label` (str): Actual label or outcome

**Returns:**
- `dict`: Response with keys: `{"status": "success", "prediction_id": "..."}`

**Raises:**
- `ConnectionError`: If backend is unavailable
- `TimeoutError`: If request times out
- `ValueError`: If API returns error (e.g., prediction_id not found, duplicate label)

#### `close()`

Close the underlying HTTP session.

## Examples

Three example scripts are provided in `examples/`:

### 1. Log Single Prediction

```bash
cd sdk
python examples/log_single_prediction.py
```

Logs one sample credit risk prediction. Use this to verify your backend setup.

### 2. Log Batch Predictions

```bash
cd sdk
python examples/log_batch_predictions.py
```

Generates and logs 20 sample credit risk predictions with random features. Demonstrates batch operations.

### 3. Log Ground Truth Labels

```bash
cd sdk
python examples/log_ground_truth.py
```

Logs ground truth labels for sample predictions. Run this after logging predictions to demonstrate outcome tracking.

## Architecture

```
Your ML Application
        ↓
        ├─→ model.predict(data) → inference
        ├─→ client.log_prediction() → [SDK]
        └─→ ModelDrift Backend (FastAPI)
                ↓
        PostgreSQL Database
```

The SDK:
- Accepts predictions in your ML code
- Converts to JSON and HTTP POST
- Communicates with FastAPI backend
- Stores in PostgreSQL database

Later, when ground truth is available:
- `client.log_ground_truth()` updates the database
- Backend can calculate drift metrics
- Dashboard displays results

## Error Handling

SDK provides clear error messages:

```python
from modeldrift import ModelDriftClient

client = ModelDriftClient(base_url="http://localhost:8000")

try:
    client.log_prediction(
        model_name="credit_risk",
        model_version="v1",
        prediction_id="pred_001",
        input_features={"feature1": 0.5},
        prediction="high_risk",
        confidence=0.91
    )
except ConnectionError as e:
    print(f"Backend not available: {e}")
    print("Make sure: docker-compose up or uvicorn app.main:app --reload")
except ValueError as e:
    print(f"API validation error: {e}")
except TimeoutError as e:
    print(f"Request timed out: {e}")
```

## Verification

### Check if predictions reached backend

```bash
# Retrieve recent predictions
curl http://localhost:8000/api/v1/predictions/recent?limit=10

# Retrieve recent labels
curl http://localhost:8000/api/v1/labels/recent?limit=10
```

### View in Swagger UI

Visit http://localhost:8000/docs

- Go to **Predictions** section
- Try the **GET /api/v1/predictions/recent** endpoint
- See your logged predictions

## Development Notes

- SDK uses the `requests` library (synchronous HTTP client)
- No external ML libraries required
- Pure Python, runs anywhere
- No authentication needed (development phase)
- Thread-safe (uses session with connection pooling)

## Limitations (Intentional)

- ✗ No async/await support (use for simple scripts and batch jobs)
- ✗ No authentication (development phase)
- ✗ No retry logic (use on reliable networks)
- ✗ No local caching (all requests go directly to backend)

These can be added in future versions if needed.

## Next Steps

1. ✅ Phase 2: Backend data ingestion (done)
2. ✅ Phase 3: Python SDK Logger (done)
3. 🔲 Phase 4: Drift detection algorithms
4. 🔲 Phase 5: Monitoring dashboard
5. 🔲 Phase 6: Auto-retraining triggers

## License

MIT
