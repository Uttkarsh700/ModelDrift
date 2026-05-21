# ModelDrift

> ML Model Monitoring & Auto-Retraining Prototype

## Overview

ModelDrift is a monorepo prototype for monitoring machine learning models in production and triggering automatic retraining when drift is detected. This is a **scaffold-only phase** with minimal business logic.

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **Frontend**: React 18, Vite, Axios
- **Database**: PostgreSQL
- **Cache**: Redis
- **ML Tracking**: MLflow
- **Containerization**: Docker & Docker Compose

## Project Structure

```
modeldrift/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── core/           # Configuration
│   │   ├── api/            # Route handlers
│   │   ├── db/             # Database setup
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # React + Vite application
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── api/            # API client
│   │   ├── components/     # React components
│   │   └── pages/          # Page components
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── sdk/                     # Python SDK for ML apps
│   ├── modeldrift/         # SDK package
│   │   ├── __init__.py
│   │   └── client.py       # ModelDriftClient
│   ├── examples/           # Example scripts
│   │   ├── log_single_prediction.py
│   │   ├── log_batch_predictions.py
│   │   └── log_ground_truth.py
│   ├── pyproject.toml
│   └── README.md
├── ml/                      # ML modules (placeholder)
│   ├── train.py
│   ├── evaluate.py
│   └── sample_data/
├── scripts/                 # Utility scripts
│   └── seed_demo_data.py
├── docker-compose.yml       # Container orchestration
├── .env.example             # Environment variables template
├── .gitignore
└── README.md
```

## Current Phase: Python SDK Logger (Phase 3)

This phase provides a **Python SDK for ML applications** to log predictions and labels:
- ✅ ModelDriftClient class for easy integration
- ✅ `log_prediction()` method for inference logging
- ✅ `log_ground_truth()` method for outcome tracking
- ✅ Clear error handling for common issues
- ✅ Three example scripts for different use cases
- ✅ No authentication required (development phase)

**Phase 2 (Completed):**
- Backend FastAPI data ingestion system
- Database models for predictions and labels
- RESTful API endpoints for predictions and labels

**Phase 1 (Completed):**
- Project structure and folder hierarchy
- Backend FastAPI setup with health check endpoint
- Frontend React setup with basic pages
- Docker Compose configuration for all services

**Coming Later (Phase 4+):**
- Drift detection algorithms
- Model training and evaluation
- Auto-retraining triggers
- Performance monitoring dashboards
- Training history and metrics
- Real-time alerts

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend)

### Run Locally with Docker Compose

```bash
# Clone and navigate to project
cd modeldrift

# Build and start all services
docker-compose up --build

# Services will be available at:
# - Backend: http://localhost:8000
# - Frontend: http://localhost:5173
# - MLflow: http://localhost:5000
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

### Run Backend Locally (without Docker)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Ensure PostgreSQL and Redis are running
# Then start backend:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Run Frontend Locally (without Docker)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Using the Python SDK

The SDK allows any ML application to easily log predictions and outcomes to ModelDrift.

### Install SDK

```bash
cd sdk

# Install in development mode
pip install -e .
```

### Quick Example

```python
from modeldrift import ModelDriftClient

# Initialize client
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

client.close()
```

### Run Examples

```bash
cd sdk

# Log single prediction
python examples/log_single_prediction.py

# Log 20 sample predictions
python examples/log_batch_predictions.py

# Log ground truth labels
python examples/log_ground_truth.py
```

### SDK Documentation

See [sdk/README.md](sdk/README.md) for:
- Complete API reference
- Error handling examples
- Architecture overview
- More examples

## Demo Data Generation

ModelDrift includes scripts to generate realistic demo data for testing drift detection and building dashboards.

### Why Demo Data?

The demo data creates two time periods:

1. **Baseline Data (300 predictions)**: Healthier credit profiles
   - Lower credit utilization (15-50%)
   - Lower debt-to-income (10-40%)
   - Older accounts (60-180 months)
   - Fewer recent inquiries (0-2)
   - More accurate predictions

2. **Current Data (200 predictions)**: Riskier profiles showing drift
   - Higher credit utilization (50-95%)
   - Higher debt-to-income (40-85%)
   - Newer accounts (12-60 months)
   - More recent inquiries (2-8)
   - Less accurate predictions (showing degradation)

This allows testing drift detection, accuracy drop detection, and dashboard visualizations.

### Generate Demo Data

**Prerequisites:** Backend must be running

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Then in another terminal:

```bash
cd scripts
python generate_demo_data.py
```

**Output:**
```
🚀 ModelDrift Demo Data Generator

✅ Connected to ModelDrift backend

📊 Generating baseline data (healthier profiles)...
  ✅ Baseline: 50/300 predictions
  ✅ Baseline: 100/300 predictions
  ...
  ✅ Baseline complete: 300 predictions, 240 labels

📊 Generating current data (riskier profiles - showing drift)...
  ✅ Current: 50/200 predictions
  ...
  ✅ Current complete: 200 predictions, 180 labels

📈 Demo Data Summary:
  Baseline predictions:  300
  Baseline labels:       240
  Current predictions:   200
  Current labels:        180
  Total predictions:     500
  Total labels:          420

✅ Demo data generation complete!
```

### Reset Demo Data

Clear all predictions and labels from the database:

```bash
python scripts/reset_demo_data.py
```

**Prompt:**
```
🗑️  ModelDrift Demo Data Reset

📊 Current data in database:
  Predictions:       500
  Ground truth labels: 420

⚠️  Are you sure you want to delete all predictions and labels? (yes/no): yes

✅ Reset Complete!
  Deleted 420 ground truth labels
  Deleted 500 predictions
  Total records removed: 920
```

### Verify Demo Data

After generating demo data, verify it's in the database:

```bash
# Recent predictions
curl http://localhost:8000/api/v1/predictions/recent?limit=20

# Recent labels
curl http://localhost:8000/api/v1/labels/recent?limit=20

# Or use Swagger UI: http://localhost:8000/docs
```

Sample response:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "model_name": "credit_risk",
    "model_version": "v1",
    "prediction_id": "baseline_0001",
    "input_features": {
      "credit_utilization": 0.35,
      "debt_to_income": 0.25,
      "num_recent_inquiries": 1,
      "avg_account_age_months": 120,
      "num_open_accounts": 4
    },
    "prediction": "low_risk",
    "confidence": 0.92,
    "created_at": "2026-05-21T10:30:45.123456"
  }
]
```

## API Endpoints

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "ok",
  "service": "modeldrift-backend"
}
```

### Root

```bash
GET /
```

Response:
```json
{
  "message": "Welcome to ModelDrift API",
  "docs": "/docs"
}
```

### Predictions

#### Create Prediction

```bash
POST /api/v1/predictions
Content-Type: application/json

{
  "model_name": "credit_risk",
  "model_version": "v1",
  "prediction_id": "pred_001",
  "input_features": {
    "credit_utilization": 0.72,
    "debt_to_income": 0.43,
    "num_recent_inquiries": 3
  },
  "prediction": "high_risk",
  "confidence": 0.91
}
```

Response (201):
```json
{
  "status": "success",
  "prediction_id": "pred_001"
}
```

#### Get Recent Predictions

```bash
GET /api/v1/predictions/recent?limit=20
```

Response (200):
```json
[
  {
    "id": "uuid-string",
    "model_name": "credit_risk",
    "model_version": "v1",
    "prediction_id": "pred_001",
    "input_features": {...},
    "prediction": "high_risk",
    "confidence": 0.91,
    "created_at": "2026-05-21T10:30:00"
  }
]
```

#### Get Specific Prediction

```bash
GET /api/v1/predictions/{prediction_id}
```

Response (200): Single prediction object

### Ground Truth Labels

#### Create Label

```bash
POST /api/v1/labels
Content-Type: application/json

{
  "prediction_id": "pred_001",
  "actual_label": "default"
}
```

Response (201):
```json
{
  "status": "success",
  "prediction_id": "pred_001"
}
```

#### Get Recent Labels

```bash
GET /api/v1/labels/recent?limit=20
```

Response (200):
```json
[
  {
    "id": "uuid-string",
    "prediction_id": "pred_001",
    "actual_label": "default",
    "received_at": "2026-05-21T11:00:00"
  }
]
```

#### Get Specific Label

```bash
GET /api/v1/labels/{prediction_id}
```

Response (200): Single label object

## Testing the API with curl

### Create a Prediction

```bash
curl -X POST http://localhost:8000/api/v1/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "credit_risk",
    "model_version": "v1",
    "prediction_id": "pred_001",
    "input_features": {
      "credit_utilization": 0.72,
      "debt_to_income": 0.43,
      "num_recent_inquiries": 3
    },
    "prediction": "high_risk",
    "confidence": 0.91
  }'
```

### Get Recent Predictions

```bash
curl http://localhost:8000/api/v1/predictions/recent?limit=20
```

### Get Specific Prediction

```bash
curl http://localhost:8000/api/v1/predictions/pred_001
```

### Create a Ground Truth Label

```bash
curl -X POST http://localhost:8000/api/v1/labels \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_id": "pred_001",
    "actual_label": "default"
  }'
```

### Get Recent Labels

```bash
curl http://localhost:8000/api/v1/labels/recent?limit=20
```

### Get Specific Label

```bash
curl http://localhost:8000/api/v1/labels/pred_001
```

## Database Schema

### Predictions Table

```sql
CREATE TABLE predictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  model_name VARCHAR(255) NOT NULL,
  model_version VARCHAR(255) NOT NULL,
  prediction_id VARCHAR(255) NOT NULL UNIQUE,
  input_features JSONB NOT NULL,
  prediction VARCHAR(255) NOT NULL,
  confidence FLOAT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_predictions_model_name ON predictions(model_name);
CREATE INDEX idx_predictions_prediction_id ON predictions(prediction_id);
CREATE INDEX idx_predictions_created_at ON predictions(created_at);
```

### Ground Truth Labels Table

```sql
CREATE TABLE ground_truth_labels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prediction_id VARCHAR(255) NOT NULL UNIQUE,
  actual_label VARCHAR(255) NOT NULL,
  received_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_ground_truth_labels_prediction_id ON ground_truth_labels(prediction_id);
CREATE INDEX idx_ground_truth_labels_received_at ON ground_truth_labels(received_at);
```

**Note:** Tables are created automatically on app startup using SQLAlchemy ORM.

### Interactive API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Frontend Pages

### Overview

Main dashboard showing:
- ModelDrift title and subtitle
- Backend health status
- Placeholder for next features

## Environment Variables

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `MLFLOW_TRACKING_URI`: MLflow server URL
- `VITE_API_URL`: Backend API URL (frontend)

## Verification

### Backend Health Check

```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "ok",
  "service": "modeldrift-backend"
}
```

### Frontend Status

Open browser to http://localhost:5173

Should display:
- Title: "ModelDrift"
- Subtitle: "ML Monitoring & Auto-Retraining Prototype"
- Green status indicator for backend health

### Database Connection

```bash
# Connect to PostgreSQL
psql -h localhost -U postgres -d modeldrift

# Should connect successfully
```

### Redis Connection

```bash
# Connect to Redis
redis-cli

# Should connect successfully
```

### SDK Testing

Test the Python SDK with example scripts:

```bash
cd sdk

# Run single prediction example
python examples/log_single_prediction.py
# Expected: ✅ Prediction logged successfully!

# Run batch predictions example
python examples/log_batch_predictions.py
# Expected: ✅ All predictions logged successfully!

# Run ground truth example
python examples/log_ground_truth.py
# Expected: ✅ All labels logged successfully!
```

Verify data in backend:

```bash
# Check recent predictions
curl http://localhost:8000/api/v1/predictions/recent?limit=5

# Check recent labels
curl http://localhost:8000/api/v1/labels/recent?limit=5
```

Or view in Swagger UI: http://localhost:8000/docs

### Demo Data Generation

Generate realistic test data for drift detection and dashboard testing:

```bash
# Generate 500 predictions (300 baseline + 200 current)
python scripts/generate_demo_data.py

# Verify data was created
curl http://localhost:8000/api/v1/predictions/recent?limit=10

# Reset and regenerate
python scripts/reset_demo_data.py  # Clear old data
python scripts/generate_demo_data.py  # Create new data
```

## Development Notes

- Backend uses FastAPI with auto-reloading
- Frontend uses Vite for fast HMR
- Docker Compose volumes enable live code changes
- All services are containerized for consistency

## Next Steps

1. ✅ Phase 1: Project scaffold (completed)
2. ✅ Phase 2: Backend data ingestion (completed)
3. ✅ Phase 3: Python SDK Logger (completed)
4. ✅ Phase 4: Demo Data Generation (completed)
5. 🔲 Phase 5: Drift detection algorithms
6. 🔲 Phase 6: Model training pipeline
7. 🔲 Phase 7: Auto-retraining triggers
8. 🔲 Phase 8: Monitoring dashboard
9. 🔲 Phase 9: Real-time alerts

## License

MIT
