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

## Current Phase: Alert System & System Health (Phase 12)

This phase adds **database-backed alerts** for monitoring system issues and **system health dashboard**:
- ✅ Alert storage in PostgreSQL with severity and source tracking
- ✅ Automatic alert creation for drift, retraining, GitHub Actions issues
- ✅ Alert resolution with timestamps
- ✅ Active alerts section showing unresolved issues
- ✅ Complete alert history table (last 50 alerts)
- ✅ System health card showing component status
- ✅ Alerts page with KPI cards (total, active, critical, resolved)
- ✅ Demo alert seeding
- ✅ 5 API endpoints for alerts management
- ✅ AlertCard component for display
- ✅ Auto-refresh every 10 seconds

**Key Concepts:**
- **Alert**: Notification of a system issue (drift, retraining failure, config problem)
- **Severity**: info (blue), warning (yellow), critical (red)
- **Source**: Where the alert originated (drift, retraining, github_actions, system)
- **Status**: active (unresolved) or resolved
- **System Health**: Shows status of key components (API, GitHub Actions, PostgreSQL, Redis)

**Alert Creation Rules:**
1. **High drift detected** - If overall_drift_level == "high" → CRITICAL
2. **Accuracy drop detected** - If accuracy_drop >= 0.10 → WARNING
3. **Retraining failed** - If retraining job fails → CRITICAL
4. **GitHub Actions not configured** - If credentials missing → WARNING

**Phase 11 (Completed):**
- Model registry and promotion simulation
- Champion vs challenger comparison
- Automated promotion recommendation
- One-click promotion to production

**Phase 10 (Completed):**
- Retraining automation UI with drift metrics
- 3 ways to trigger retraining (check-and-trigger, manual, GitHub Actions)
- Retraining run history and latest run details
- Auto-refresh and status monitoring

**Phase 9 (Completed):**
- GitHub Actions integration for CI automation
- Manual trigger via GitHub UI
- Trigger endpoint from backend

**Phase 8 (Completed):**
- Background job automation with Celery + Redis
- Auto-trigger retraining when drift detected

**Phase 7 (Completed):**
- Local model retraining with ml/retrain_model.py
- MLflow experiment tracking
- Model comparison and champion selection

**Phase 6 (Completed):**
- React dashboard with dark theme
- Real-time drift metrics visualization
- KPI cards and feature analysis tables

**Earlier Phases (Completed):**
- Phase 5: Drift detection algorithms
- Phase 4: Demo data generation
- Phase 3: Python SDK
- Phase 2: Backend data ingestion
- Phase 1: Project scaffold

**Coming Later (Phase 13+):**
- Model serving & predictions API
- A/B testing and shadow deployment
- Scheduled retraining
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

# Install dependencies (includes Recharts for charts)
npm install

# Start development server (Vite)
npm run dev

# Frontend will be available at:
# http://localhost:5173
```

**Note:** The dashboard requires the backend to be running and demo data to be generated first. See the [Dashboard](#dashboard-phase-6) section for complete setup.

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

## Drift Detection

ModelDrift automatically detects when your model's behavior changes using advanced statistical methods.

### How Drift Detection Works

Drift occurs when the model's input features or output behavior significantly changes from the training data. This can indicate:
- **Data drift**: Input distributions have changed
- **Concept drift**: The relationship between inputs and outputs has changed
- **Accuracy drift**: Model performance is degrading

### Drift Metrics

ModelDrift calculates two key metrics:

**1. PSI (Population Stability Index)**
- Measures how much a feature's distribution has shifted
- Compares baseline (training) data vs current (production) data
- Range: 0 to infinity
- Interpretation:
  - PSI < 0.10: Low drift (similar distributions)
  - 0.10 ≤ PSI < 0.25: Medium drift (some change)
  - PSI ≥ 0.25: High drift (significant change)

**2. KS-Test (Kolmogorov-Smirnov)**
- Statistical test comparing two distributions
- Returns a statistic (0 to 1) and p-value
- P-value < 0.05 indicates statistically significant difference

### Using Drift Detection

**Prerequisites:** Generate demo data first

```bash
# 1. Reset any existing data
python scripts/reset_demo_data.py

# 2. Generate baseline and current predictions
python scripts/generate_demo_data.py
```

**Calculate drift metrics:**

```bash
curl -X POST http://localhost:8000/api/v1/drift/run
```

**Response:**
```json
{
  "status": "success",
  "model_name": "credit_risk",
  "model_version": "v1",
  "overall_drift_level": "high",
  "baseline_accuracy": 0.91,
  "current_accuracy": 0.78,
  "accuracy_drop": 0.13,
  "baseline_sample_size": 300,
  "current_sample_size": 200,
  "features": [
    {
      "feature_name": "credit_utilization",
      "psi_score": 0.31,
      "ks_statistic": 0.42,
      "ks_p_value": 0.001,
      "drift_level": "high"
    },
    {
      "feature_name": "debt_to_income",
      "psi_score": 0.28,
      "ks_statistic": 0.38,
      "ks_p_value": 0.002,
      "drift_level": "high"
    },
    {
      "feature_name": "num_recent_inquiries",
      "psi_score": 0.15,
      "ks_statistic": 0.25,
      "ks_p_value": 0.15,
      "drift_level": "medium"
    }
  ],
  "calculated_at": "2026-05-21T10:45:30.123456"
}
```

### Drift API Endpoints

#### POST /api/v1/drift/run
Calculate drift metrics for a model.

```bash
curl -X POST http://localhost:8000/api/v1/drift/run?model_name=credit_risk&model_version=v1
```

#### GET /api/v1/drift/latest
Get latest drift metrics for each feature.

```bash
curl http://localhost:8000/api/v1/drift/latest?model_name=credit_risk&model_version=v1
```

#### GET /api/v1/drift/summary
Get summary of latest drift calculation.

```bash
curl http://localhost:8000/api/v1/drift/summary?model_name=credit_risk&model_version=v1
```

**Summary Response:**
```json
{
  "model_name": "credit_risk",
  "model_version": "v1",
  "overall_drift_level": "high",
  "avg_psi": 0.25,
  "max_psi": 0.31,
  "min_psi": 0.08,
  "baseline_accuracy": 0.91,
  "current_accuracy": 0.78,
  "accuracy_drop": 0.13,
  "high_drift_features": 2,
  "medium_drift_features": 1,
  "low_drift_features": 2,
  "calculated_at": "2026-05-21T10:45:30.123456"
}
```

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

## Dashboard (Phase 6)

ModelDrift includes a **React-based monitoring dashboard** that displays model health, drift metrics, and recent predictions in real-time.

### Dashboard Features

✅ **Dark Theme UI** - Modern, clean interface
✅ **Real-time Monitoring** - Auto-refreshes every 30 seconds
✅ **KPI Cards** - Model name, drift level, accuracy, PSI, feature counts
✅ **Drift Summary** - Aggregated statistics (min/max PSI, baseline/current accuracy)
✅ **Feature Analysis** - Drift metrics per feature (PSI, KS-test, p-value)
✅ **PSI Chart** - Bar chart visualization of feature drift
✅ **Recent Predictions** - Latest 20 predictions with confidence scores
✅ **Backend Status** - Real-time connection indicator
✅ **Loading/Error States** - Friendly messages and helpful hints
✅ **Responsive Design** - Works on desktop and tablet

### Dashboard Layout

```
┌─ Topbar ──────────────────────────────────────────────────────┐
│ ModelDrift                  [Prototype]  Backend: [Online]    │
├─────────────────────────────────────────────────────────────┤
│ ┌─ Sidebar ────┐ ┌─ Main Content ─────────────────────────┐ │
│ │ Overview  📊 │ │ Overview                                 │ │
│ │ Models    🤖 │ │ Real-time model monitoring...            │ │
│ │ Drift     📈 │ │                                          │ │
│ │ Retraining🔄 │ │ ┌─ Metric Cards (6-column grid) ───────┐ │
│ │ Experiments🧪 │ │ │ Model Name: credit_risk       │        │ │
│ │ Alerts    🔔 │ │ │ Drift Level: HIGH             │        │ │
│ │ Settings  ⚙️  │ │ │ Avg PSI: 0.188                │        │ │
│ │            │ │ │ Current Accuracy: 78.0%       │        │ │
│ │            │ │ │ Accuracy Drop: 13.0%          │        │ │
│ │ Version    │ │ │ High Drift Features: 2        │        │ │
│ │ 0.1.0      │ │ └─────────────────────────────────────────┘ │ │
│ │            │ │                                          │ │
│ │            │ │ ┌─ Drift Summary Statistics ────────────┐ │ │
│ │            │ │ │ Max PSI: 0.310                          │ │
│ │            │ │ │ Min PSI: 0.080                          │ │
│ │            │ │ │ Baseline: 91.0% | Current: 78.0%       │ │
│ │            │ │ └─────────────────────────────────────────┘ │ │
│ │            │ │                                          │ │
│ │            │ │ ┌─ Feature PSI Chart ───────────────────┐ │ │
│ │            │ │ │ [Bar Chart - PSI per feature]        │ │ │
│ │            │ │ │ credit_util | debt_income | inquiries │ │ │
│ │            │ │ └─────────────────────────────────────────┘ │ │
│ │            │ │                                          │ │
│ │            │ │ ┌─ Feature Drift Table ──────────────────┐ │ │
│ │            │ │ │ Feature | PSI | KS | p-value | Level  │ │ │
│ │            │ │ │ credit_util | 0.31 | 0.42 | 0.001 | ▓ │ │
│ │            │ │ └─────────────────────────────────────────┘ │ │
│ │            │ │                                          │ │
│ │            │ │ ┌─ Recent Predictions (20 rows) ───────┐ │ │
│ │            │ │ │ ID | Model | Prediction | Conf | Time │ │ │
│ │            │ │ └─────────────────────────────────────────┘ │ │
│ └────────────┘ └──────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Running the Dashboard

**Prerequisites:**
1. Backend running (`python -m uvicorn app.main:app --reload`)
2. Demo data generated (`python scripts/generate_demo_data.py`)
3. Drift calculation completed (`python scripts/test_drift.py`)

**Install Frontend Dependencies:**

```bash
cd frontend
npm install
```

**Start Dashboard:**

```bash
npm run dev
```

Dashboard will be available at: **http://localhost:5173**

### Dashboard Data Sources

The dashboard fetches data from these backend endpoints:

| Endpoint | Purpose | Used For |
|----------|---------|----------|
| `GET /health` | Backend status | Topbar indicator |
| `GET /api/v1/drift/summary` | Aggregated drift metrics | KPI cards, summary stats |
| `GET /api/v1/drift/latest` | Per-feature drift details | Feature table, PSI chart |
| `GET /api/v1/predictions/recent?limit=20` | Recent predictions | Predictions table |
| `GET /api/v1/labels/recent?limit=20` | Recent ground truth | (Prepared for future use) |

### Dashboard Components

**frontend/src/components:**
- `Sidebar.jsx` - Navigation (7 items, Overview active)
- `Topbar.jsx` - Title, environment badge, backend status
- `MetricCard.jsx` - Reusable KPI card component
- `StatusBadge.jsx` - Color-coded status indicator (low/medium/high)
- `DriftTable.jsx` - Feature-level drift metrics
- `RecentPredictions.jsx` - Prediction history table

**frontend/src/pages:**
- `Overview.jsx` - Main dashboard page (comprehensive implementation)

**frontend/src/api:**
- `client.js` - Axios instance + 6 data-fetching functions

### Customization

**Change Backend URL:**

Create a `.env` file in the frontend root:
```
VITE_API_URL=http://your-backend-url:8000
```

**Modify Dashboard Colors:**

Edit `frontend/src/styles.css` - All colors use CSS variables in dark theme:
- Primary: `#3b82f6` (blue)
- Success: `#10b981` (green)
- Warning: `#f59e0b` (amber)
- Danger: `#ef4444` (red)

**Add New Metrics:**

1. Add function to `frontend/src/api/client.js`
2. Call function in `Overview.jsx` useEffect
3. Render in component with `MetricCard` or custom HTML

### Production Build

```bash
cd frontend
npm run build
```

Output in `frontend/dist/` - ready to deploy to any static host (Vercel, Netlify, S3, etc.)

### Troubleshooting

**"Cannot connect to backend" message:**
- Ensure backend is running: `cd backend && python -m uvicorn app.main:app --reload`
- Check CORS: Backend `app/main.py` allows `http://localhost:5173`
- Verify no port conflicts (backend:8000, frontend:5173)

**"No drift metrics available" message:**
- Generate demo data: `python scripts/generate_demo_data.py`
- Run drift calculation: `python scripts/test_drift.py`
- Refresh dashboard

**Styling issues:**
- Clear browser cache (Ctrl+Shift+Delete)
- Check browser console for CSS errors

## Model Retraining & Experiment Tracking (Phase 7)

This phase adds **local model retraining** with MLflow experiment tracking. When model drift is detected, retrain the model on new labeled data and compare against the current production model.

### Quick Start

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Start MLflow tracking server
mlflow server --host 0.0.0.0 --port 5000

# 3. Retrain model (in new terminal from project root)
python ml/retrain_model.py

# 4. View results (in new terminal)
python ml/compare_models.py

# 5. Explore in MLflow UI
open http://localhost:5000
```

### How It Works

**Retraining Pipeline:**
1. **Fetch Training Data**: `GET /api/v1/training/dataset` retrieves prediction + ground truth records
2. **Feature Extraction**: Extract 5 numeric features from JSON input
3. **Train Model**: RandomForestClassifier with 100 trees
4. **Evaluate**: Calculate accuracy, precision, recall, F1-score on test set (80/20 split)
5. **Log to MLflow**: Store metrics, parameters, and model artifact
6. **Save Locally**: Pickle model to `ml/models/credit_risk_latest.pkl`

**Model Comparison:**
- Query MLflow experiment runs
- Sort by accuracy (best first)
- Display top 5 runs with full metrics
- Highlight champion model

### Files

- [ml/retrain_model.py](ml/retrain_model.py) - Main retraining script (~800 lines)
- [ml/compare_models.py](ml/compare_models.py) - View top MLflow runs (~250 lines)
- [backend/app/api/routes/training.py](backend/app/api/routes/training.py) - Training data endpoint
- [ml/models/](ml/models/) - Saved model artifacts

See [ml/README.md](ml/README.md) for detailed documentation, troubleshooting, and architecture.

## Background Job Automation (Phase 8)

This phase adds **automatic background retraining** triggered when drift is detected. Retraining runs in a background worker process (not blocking the API), with status tracked in the database.

### Why Background Jobs?

**Without background jobs:**
- User calls `/retrain` API endpoint
- API blocks for 5-10 minutes while model trains
- Frontend shows spinning loader
- Timeout if retraining takes too long

**With Celery + background jobs:**
- User calls `/retrain` API endpoint
- API returns immediately with run_id
- Celery worker trains model in background
- Frontend can poll run status without blocking
- Multiple retraining jobs can run in parallel

### Architecture

```
┌─────────────┐                              ┌─────────────┐
│   FastAPI   │                              │   Celery    │
│   Backend   │────────────┐                 │   Worker    │
│   (Port     │            │                 │             │
│    8000)    │            │                 │ Executes    │
└─────────────┘            │                 │ ml/retrain_ │
                           │                 │ model.py    │
                     ┌─────▼─────┐           │             │
                     │   Redis    │◄─────────│ (long task) │
                     │   (Queue)  │           └─────────────┘
                     └────────────┘
                           ▲
                           │
                    Task: run_retraining_task
                    {run_id, model_name, ...}
```

### Quick Start

#### Step 1: Start PostgreSQL & Redis
```bash
docker-compose up postgres redis -d
```

#### Step 2: Start MLflow
```bash
mlflow server --host 0.0.0.0 --port 5000
```

#### Step 3: Start FastAPI Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

#### Step 4: Start Celery Worker (new terminal)
```bash
cd backend
celery -A app.core.celery_app worker --loglevel=info
```

#### Step 5: Trigger Retraining (new terminal)
```bash
# Automatic trigger (only if drift is high)
curl -X POST http://localhost:8000/api/v1/retraining/check-and-trigger

# Manual trigger (always runs)
curl -X POST http://localhost:8000/api/v1/retraining/manual-trigger
```

#### Step 6: Check Run Status
```bash
# Latest run
curl http://localhost:8000/api/v1/retraining/runs/latest

# List last 20 runs
curl http://localhost:8000/api/v1/retraining/runs
```

### API Endpoints

**POST /api/v1/retraining/check-and-trigger**

Auto-triggers retraining if:
- `overall_drift_level == "high"` OR
- `accuracy_drop >= 0.10` (10% drop)

Response:
```json
{
  "status": "triggered",
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "reason": "high drift detected"
}
```

Or (if no trigger needed):
```json
{
  "status": "skipped",
  "run_id": null,
  "reason": "Drift below threshold"
}
```

**POST /api/v1/retraining/manual-trigger**

Always triggers retraining.

Response:
```json
{
  "status": "triggered",
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "reason": "Retraining triggered (manual)"
}
```

**GET /api/v1/retraining/runs/latest**

Get most recent retraining run.

Response:
```json
{
  "run": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "model_name": "credit_risk",
    "model_version": "v1",
    "trigger_reason": "manual",
    "status": "completed",
    "started_at": "2026-05-21T10:30:00",
    "finished_at": "2026-05-21T10:40:00",
    "logs": "Fetched 420 samples...\n✅ Model training complete\nAccuracy: 0.8571\n..."
  }
}
```

**GET /api/v1/retraining/runs?limit=20**

Get latest 20 retraining runs.

Response:
```json
{
  "runs": [
    { "id": "...", "status": "completed", ... },
    { "id": "...", "status": "running", ... },
    ...
  ],
  "total_count": 47
}
```

### Database Schema

**retraining_runs table:**

```
id                 UUID primary key
model_name         String (e.g., "credit_risk")
model_version      String (e.g., "v1")
trigger_reason     String ("high_drift", "accuracy_drop", "manual")
status             String ("pending", "running", "completed", "failed")
started_at         DateTime (when run was created)
finished_at        DateTime (when run completed/failed, nullable)
logs               Text (captured stdout/stderr from ml/retrain_model.py)
```

**Run Status Flow:**

```
pending ──────► running ──────► completed
                    │
                    └──────────► failed
```

### Files

**New files:**
- [backend/app/core/celery_app.py](backend/app/core/celery_app.py) - Celery configuration (Redis broker)
- [backend/app/models/retraining_run.py](backend/app/models/retraining_run.py) - SQLAlchemy model for tracking runs
- [backend/app/schemas/retraining.py](backend/app/schemas/retraining.py) - Pydantic request/response models
- [backend/app/tasks/retraining_tasks.py](backend/app/tasks/retraining_tasks.py) - Celery task (executes ml/retrain_model.py)
- [backend/app/services/retraining_service.py](backend/app/services/retraining_service.py) - Business logic layer
- [backend/app/api/routes/retraining.py](backend/app/api/routes/retraining.py) - API endpoints (4 routes)

**Updated files:**
- `backend/app/main.py` - Registers retraining route + Celery app
- `backend/requirements.txt` - Added celery, redis
- `docker-compose.yml` - Added celery_worker service

### How It Works

**When you call POST /api/v1/retraining/manual-trigger:**

1. API creates a `RetrainingRun` record in database with status="pending"
2. API sends Celery task to Redis: `{run_id, model_name, ...}`
3. API returns immediately with run_id
4. Celery worker picks up task from Redis
5. Worker updates run status to "running"
6. Worker executes: `subprocess.run("python ml/retrain_model.py")`
7. Worker captures stdout/stderr
8. If success: updates status to "completed", saves logs
9. If error: updates status to "failed", saves error logs
10. Frontend can poll `/api/v1/retraining/runs/latest` to see progress

**Example Python flow:**

```python
# In Celery worker process
@celery_app.task(name="run_retraining_task")
def run_retraining_task(run_id: str):
    # 1. Get run from database
    run = db.query(RetrainingRun).filter(RetrainingRun.id == run_id).first()
    
    # 2. Mark as running
    run.status = "running"
    db.commit()
    
    # 3. Execute ml/retrain_model.py
    result = subprocess.run(
        [sys.executable, "ml/retrain_model.py"],
        capture_output=True,
        text=True,
        timeout=600
    )
    
    # 4. Save results
    if result.returncode == 0:
        run.status = "completed"
    else:
        run.status = "failed"
    
    run.logs = result.stdout + result.stderr
    run.finished_at = datetime.utcnow()
    db.commit()
```

### Troubleshooting

**"Cannot connect to Redis"**
```
Error: Error -2 connecting to localhost:6379. Name or service not known.
```

**Solution:**
```bash
# Start Redis
docker-compose up redis -d

# Or check if Redis is running
redis-cli ping  # should print PONG
```

**"Celery worker not picking up tasks"**

Check that worker is running and connected to Redis:
```bash
# In Celery worker terminal, should see:
# Connected to redis://localhost:6379/0
# [*] Ready to accept tasks
```

**"Retraining run status stuck on 'running'"**

Worker might have crashed. Check logs:
```bash
# See worker logs
docker-compose logs celery_worker

# Or restart worker
docker-compose restart celery_worker
```

**"No logs saved to database"**

Check that `/app/ml/retrain_model.py` exists in worker container:
```bash
docker-compose exec celery_worker ls -la /app/ml/retrain_model.py
```

### Using Docker Compose

All-in-one setup with Docker Compose:

```bash
# Start all services (PostgreSQL, Redis, MLflow, Backend, Frontend, Celery Worker)
docker-compose up

# In another terminal, trigger retraining
curl -X POST http://localhost:8000/api/v1/retraining/manual-trigger

# Check status
curl http://localhost:8000/api/v1/retraining/runs/latest
```

### Environment Variables

```bash
# Backend connection (used by Celery worker to update database)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/modeldrift

# Redis connection (Celery broker/backend)
REDIS_URL=redis://localhost:6379

# MLflow tracking (worker logs metrics)
MLFLOW_TRACKING_URI=http://localhost:5000
```

## GitHub Actions Integration (Phase 9)

This phase adds **CI automation** for the retraining pipeline. Workflows run in GitHub's cloud infrastructure (no local resources needed), triggered manually or automatically on code changes.

### Why GitHub Actions for Retraining?

**Complementary to Celery:**
- **Celery** (local): Fast, low-latency, ideal for real-time triggers
- **GitHub Actions** (CI): Cloud-based, auditable, versioned, shareable with team
- **Use Celery** for: Auto-triggers, production background jobs
- **Use GitHub Actions** for: Manual testing, code changes, PR workflows, team collaboration

**Benefits:**
- Runs in GitHub cloud (no local resources)
- Full integration with GitHub UI and PRs
- Automatic triggers on code changes
- Build artifacts stored on GitHub
- Auditable run history
- Team-friendly workflow

### GitHub Actions Workflow

**File:** `.github/workflows/retrain-model.yml`

**Triggers:**

1. **Manual trigger** (workflow_dispatch):
   - Click "Actions" tab → "ModelDrift Retraining Pipeline" → "Run workflow"
   - Provide inputs: model_name, model_version, trigger_reason

2. **Automatic trigger** (push):
   - Trigger on push to main if changes in `ml/**` or `backend/**`

**Workflow steps:**
1. Checkout code
2. Setup Python 3.11
3. Install backend dependencies
4. Run `python ml/retrain_model.py` (generates model + MLflow run)
5. Run `python ml/compare_models.py` (shows champion model)
6. Upload trained model artifact
7. Upload MLflow runs/artifacts

### Quick Start: Manual Trigger from GitHub UI

1. Push code to GitHub:
   ```bash
   git push origin main
   ```

2. Open GitHub repository
3. Click **Actions** tab
4. Click **"ModelDrift Retraining Pipeline"** workflow
5. Click **"Run workflow"** button
6. Provide inputs (or use defaults):
   - model_name: `credit_risk`
   - model_version: `v1`
   - trigger_reason: `manual testing`
7. Click **"Run workflow"**
8. Watch the workflow execute
9. View artifacts in Artifacts section

### Trigger from Backend API

Configure GitHub token and trigger workflow from your backend:

**Step 1: Create GitHub Personal Access Token**
```
https://github.com/settings/tokens
- Name: ModelDrift Retraining
- Scope: workflows
- Copy the token
```

**Step 2: Add to .env**
```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_OWNER=your-github-username-or-org
GITHUB_REPO=ModelDrift
GITHUB_WORKFLOW_FILE=retrain-model.yml
GITHUB_REF=main
```

**Step 3: Check if configured**
```bash
curl http://localhost:8000/api/v1/github-actions/config-status
```

Response (configured):
```json
{
  "configured": true,
  "missing": []
}
```

Response (not configured):
```json
{
  "configured": false,
  "missing": ["GITHUB_TOKEN", "GITHUB_OWNER", "GITHUB_REPO"]
}
```

**Step 4: Trigger retraining from backend**
```bash
curl -X POST http://localhost:8000/api/v1/github-actions/trigger-retraining \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "credit_risk",
    "model_version": "v1",
    "trigger_reason": "high drift detected"
  }'
```

Response:
```json
{
  "status": "triggered",
  "workflow_file": "retrain-model.yml",
  "ref": "main",
  "message": "Retraining workflow triggered on main"
}
```

### API Endpoints

**GET /api/v1/github-actions/config-status**

Check if GitHub Actions is configured.

Response:
```json
{
  "configured": true,
  "missing": []
}
```

**POST /api/v1/github-actions/trigger-retraining**

Trigger retraining via GitHub Actions workflow_dispatch.

Request:
```json
{
  "model_name": "credit_risk",
  "model_version": "v1",
  "trigger_reason": "manual"
}
```

Response:
```json
{
  "status": "triggered",
  "workflow_file": "retrain-model.yml",
  "ref": "main",
  "message": "Retraining workflow triggered on main"
}
```

### Files

**New files:**
- [.github/workflows/retrain-model.yml](.github/workflows/retrain-model.yml) - GitHub Actions workflow
- [backend/app/services/github_actions_service.py](backend/app/services/github_actions_service.py) - Service to call GitHub API
- [backend/app/api/routes/github_actions.py](backend/app/api/routes/github_actions.py) - API endpoints

**Updated files:**
- `backend/app/core/config.py` - Added GitHub environment variables
- `backend/app/main.py` - Registered github_actions routes
- `.env.example` - Added GitHub config variables

### Environment Variables

```bash
# GitHub API token (Personal Access Token)
# Create at: https://github.com/settings/tokens
# Scope: workflows
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx

# GitHub organization or username
GITHUB_OWNER=your-username

# Repository name
GITHUB_REPO=ModelDrift

# Workflow filename
GITHUB_WORKFLOW_FILE=retrain-model.yml

# Git reference (branch)
GITHUB_REF=main
```

### How It Works

**Manual trigger from GitHub UI:**
1. User navigates to Actions tab
2. Selects workflow
3. Clicks "Run workflow"
4. GitHub Actions API creates a workflow dispatch event
5. Workflow runs on GitHub's servers
6. Model trained, artifacts uploaded

**Trigger from backend API:**
1. Backend receives POST to `/github-actions/trigger-retraining`
2. Backend calls GitHub API with workflow_dispatch
3. Passes model_name, model_version, trigger_reason as inputs
4. GitHub creates workflow dispatch event
5. Workflow runs, model trained, artifacts uploaded
6. Backend returns success/error status

### Troubleshooting

**"GitHub Actions trigger is not configured"**

Missing environment variables. Set them in .env:
```bash
GITHUB_TOKEN=your-token
GITHUB_OWNER=your-username
GITHUB_REPO=ModelDrift
```

**"GitHub API error (401): Bad credentials"**

Token is invalid or expired:
1. Check token: `https://github.com/settings/tokens`
2. Regenerate if needed
3. Update .env

**"GitHub API error (404)"**

Repository not found or incorrect:
1. Check GITHUB_OWNER and GITHUB_REPO in .env
2. Verify repository exists and is accessible
3. Token needs `workflows` scope

**"Workflow fails in GitHub Actions"**

Check the workflow logs:
1. Go to Actions tab
2. Click the failed run
3. Click the job
4. View full log
5. Common issues:
   - Missing Python dependencies: Check backend/requirements.txt
   - Database not configured: MLflow uses local file storage in CI
   - Timeout: Increase if retraining takes >30 minutes

### Artifacts

After successful workflow:

**1. Trained Model**
- Name: `trained-model`
- File: `ml/models/credit_risk_latest.pkl`
- Download from: Actions → Run → Artifacts

**2. MLflow Runs**
- Name: `mlflow-runs`
- Location: `/tmp/mlflow`
- Contains: All experiment metadata and metrics

## Model Registry & Promotion (Phase 11)

This phase adds **model versioning and promotion capabilities**. You can register model versions, compare champion vs challenger, and promote better models to production.

### Model Registry Concepts

**Champion Model** 👑
- Currently deployed and serving predictions (production stage)
- The baseline for comparison
- Only one champion per model name

**Challenger Model** 🚀
- Candidate model being tested (staging stage)
- Latest version in staging
- Ready to be promoted if it outperforms champion

**Promotion**
- Moving a challenger model to production
- Automatically archives the old champion
- Sets promoted_at timestamp for tracking

**Stages**
- `production`: Currently deployed (champion)
- `staging`: Candidate model (challenger)
- `archived`: Previous versions (no longer used)

### Registry Database Table

```
model_versions
├── id (UUID primary key)
├── model_name (e.g., "credit_risk")
├── model_version (e.g., "v1", "v2")
├── stage (production, staging, archived)
├── accuracy (float, 0-1)
├── precision (float, 0-1)
├── recall (float, 0-1)
├── f1_score (float, 0-1)
├── drift_score (float, 0-1, optional)
├── artifact_path (path to model file)
├── mlflow_run_id (experiment tracking)
├── created_at (timestamp)
└── promoted_at (timestamp when promoted)
```

### API Endpoints

**1. Register Model**
```bash
POST /api/v1/model-registry/register
Content-Type: application/json

{
  "model_name": "credit_risk",
  "model_version": "v2",
  "stage": "staging",
  "accuracy": 0.93,
  "precision": 0.92,
  "recall": 0.91,
  "f1_score": 0.915,
  "drift_score": 0.20,
  "artifact_path": "ml/models/credit_risk_v2.pkl",
  "mlflow_run_id": "demo_run_002"
}
```

Response: `{ status: "registered", model_name, model_version, stage }`

**2. Get All Models**
```bash
GET /api/v1/model-registry/models
```

Response: `{ models: [...], total_count: 3 }`

**3. Get Champion (Production Model)**
```bash
GET /api/v1/model-registry/champion
```

Response: `{ id, model_name, model_version, ..., stage: "production" }`

**4. Get Challenger (Staging Model)**
```bash
GET /api/v1/model-registry/challenger
```

Response: `{ id, model_name, model_version, ..., stage: "staging" }`

**5. Compare Champion vs Challenger**
```bash
GET /api/v1/model-registry/comparison
```

Response:
```json
{
  "champion": {...},
  "challenger": {...},
  "accuracy_delta": 0.02,
  "f1_delta": 0.015,
  "drift_delta": -0.04,
  "recommendation": "promote_challenger",
  "reason": "Challenger has better accuracy and lower drift."
}
```

**Promotion Rule**: Recommend promoting challenger if:
- Challenger accuracy > Champion accuracy
- AND Challenger F1 >= Champion F1
- AND Challenger drift <= Champion drift (if both have drift)

**6. Promote Challenger to Production**
```bash
POST /api/v1/model-registry/promote
```

Behavior:
- Finds current production (champion) and marks it archived
- Finds latest staging (challenger) and marks it production
- Sets promoted_at timestamp
- Returns success response

Response:
```json
{
  "status": "promoted",
  "promoted_model": {..., stage: "production"},
  "archived_model": {..., stage: "archived"},
  "message": "Model v2 promoted to production"
}
```

**7. Seed Demo Registry**
```bash
POST /api/v1/model-registry/seed-demo
```

Only creates demo data if registry is empty. Creates:
- credit_risk v1 (production)
- credit_risk v2 (staging)
- credit_risk v0 (archived)

Response: `{ status: "seeded", created: 3, models: [...] }`

### Experiments Page

The Experiments page displays:

**1. Champion vs Challenger Comparison Card**
- Side-by-side model metrics
- Accuracy, F1 score, drift comparison
- Color-coded: green (champion), blue (challenger)
- Shows metric deltas

**2. Recommendation Card**
- "Ready to Promote" (if challenger better)
- "Keep Current Champion" (if champion better)
- Shows the reason

**3. Promotion Action Button**
- "Promote Challenger to Production"
- Only appears if recommendation is promote_challenger
- Shows loading state while processing
- Displays success/error message

**4. Demo Setup Button**
- "Seed Demo Registry"
- Creates demo models if registry is empty
- Shows skip message if already seeded

**5. Model Registry Table**
- All models with metrics and stage
- Columns: Model, Version, Stage, Accuracy, F1, Drift, Created, Promoted
- Color-coded stage badges
- Sortable by created_at (newest first)

### How to Use

**Step 1: Seed Demo Registry**
```bash
# Go to Experiments page and click "Seed Demo Registry"
# Or via API:
curl -X POST http://localhost:8000/api/v1/model-registry/seed-demo
```

**Step 2: View Champion vs Challenger**
- Go to Experiments page
- See comparison card with v1 (champion) vs v2 (challenger)
- See recommendation (in demo: should promote v2)

**Step 3: Promote Challenger**
- Click "Promote Challenger to Production"
- Wait 1-2 seconds
- See success message
- v2 moves to production, v1 moves to archived

**Step 4: Verify Changes**
- Model registry table updates
- v2 now shows "production" stage
- v1 now shows "archived" stage
- promoted_at timestamp set for v2

### Files

**Backend (New):**
- [backend/app/models/model_version.py](backend/app/models/model_version.py) - SQLAlchemy ORM model
- [backend/app/schemas/model_registry.py](backend/app/schemas/model_registry.py) - Pydantic schemas
- [backend/app/services/model_registry_service.py](backend/app/services/model_registry_service.py) - Business logic
- [backend/app/api/routes/model_registry.py](backend/app/api/routes/model_registry.py) - API endpoints

**Frontend (New):**
- [frontend/src/pages/Experiments.jsx](frontend/src/pages/Experiments.jsx) - Experiments page (~300 lines)
- [frontend/src/components/ModelRegistryTable.jsx](frontend/src/components/ModelRegistryTable.jsx) - Registry table (~50 lines)

**Updated:**
- [backend/app/main.py](backend/app/main.py) - Registered model_registry routes
- [frontend/src/App.jsx](frontend/src/App.jsx) - Added Experiments page routing
- [frontend/src/api/client.js](frontend/src/api/client.js) - Added 7 API functions
- [frontend/src/components/Sidebar.jsx](frontend/src/components/Sidebar.jsx) - Enabled Experiments nav item
- [frontend/src/styles.css](frontend/src/styles.css) - Added 150+ lines styling

### Testing Checklist

- [x] Backend ORM model created and migrations run
- [x] API endpoints return correct responses
- [x] Frontend can fetch champion/challenger
- [x] Comparison logic works correctly
- [x] Promotion archives old champion
- [x] New champion marked as production
- [x] Promoted_at timestamp set
- [x] Demo seed endpoint works
- [x] Demo seed skips if data exists
- [x] UI renders correctly
- [x] Recommendation shows correct message
- [x] Promotion button disabled if no challenger
- [x] Table updates after promotion
- [x] Auto-refresh works every 10 seconds

### Quick Commands

```bash
# View current models
curl http://localhost:8000/api/v1/model-registry/models

# View champion
curl http://localhost:8000/api/v1/model-registry/champion

# View challenger
curl http://localhost:8000/api/v1/model-registry/challenger

# Get comparison
curl http://localhost:8000/api/v1/model-registry/comparison

# Seed demo
curl -X POST http://localhost:8000/api/v1/model-registry/seed-demo

# Promote (after seeding)
curl -X POST http://localhost:8000/api/v1/model-registry/promote
```

## Retraining Automation UI (Phase 10)

This phase adds a **clean frontend page** for managing retraining automation. Users can view drift metrics, trigger retraining with one click, and monitor run history.

### Retraining Page Features

**View Drift Status:**
- Overall drift level (low/medium/high)
- Accuracy drop percentage
- Automation decision (should retrain?)

**Trigger Retraining (3 ways):**

1. **Check & Trigger** - Auto-checks drift, only retrains if needed
2. **Manual Local Retraining** - Always starts Celery job (fastest)
3. **Trigger GitHub Actions** - Starts cloud workflow (auditable)

**Monitor Runs:**
- Latest retraining run details (status, timestamps, logs)
- Run history table (20 most recent)
- Status colors: pending (gray), running (blue), completed (green), failed (red)

**GitHub Actions Integration:**
- See if GitHub Actions is configured
- Disable trigger button if not configured
- Click to start cloud workflow

### UI Layout

```
Retraining & Automation
├─ 4 KPI Cards
│  ├─ Overall Drift Level
│  ├─ Accuracy Drop %
│  ├─ Latest Retraining Status
│  └─ GitHub Actions Config
├─ Automation Decision Card
│  ├─ Shows current metrics
│  ├─ Shows retrain rule
│  └─ Shows recommendation
├─ Action Buttons (3)
│  ├─ Check & Trigger
│  ├─ Manual Local
│  └─ GitHub Actions
├─ Latest Run Card
│  └─ Details of most recent run
└─ Run History Table
   └─ Last 20 runs with status
```

### Quick Start

1. **Start all services:**
   ```bash
   docker-compose up postgres redis mlflow -d
   ```

2. **Start backend:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

3. **Start Celery worker (new terminal):**
   ```bash
   cd backend
   celery -A app.core.celery_app worker --loglevel=info
   ```

4. **Start frontend (new terminal):**
   ```bash
   cd frontend
   npm run dev
   ```

5. **Open browser:**
   ```
   http://localhost:5173
   ```

6. **Click "Retraining" in sidebar to see the new page**

### How to Test

**Test Manual Retraining:**
1. Go to Retraining page
2. Click "Manual Local Retraining"
3. Wait 1-2 seconds
4. See success message and run appears in history
5. Check Celery worker logs for execution

**Test Check & Trigger:**
1. Generate demo data: `python scripts/generate_demo_data.py`
2. Run drift calculation: `python scripts/test_drift.py`
3. Go to Retraining page
4. Click "Check & Trigger Retraining"
5. If drift is high, retraining starts (otherwise "Monitoring only")
6. Verify run appears in history

**Test Run History Updates:**
1. Trigger a retraining job
2. Scroll to "Retraining Run History" table
3. New run appears at top of table (within 10 seconds)
4. Status updates as it progresses: pending → running → completed

**Test GitHub Actions Trigger:**
1. Configure GitHub token (or see "not configured" button state)
2. Click "Trigger GitHub Actions"
3. See success message
4. Go to GitHub Actions tab to monitor workflow

### API Endpoints Used

The Retraining UI uses 7 backend endpoints:

```
GET  /api/v1/drift/summary                    - Get current drift metrics
GET  /api/v1/retraining/runs                  - Get last 20 runs
GET  /api/v1/retraining/runs/latest           - Get most recent run
POST /api/v1/retraining/check-and-trigger     - Auto-trigger if needed
POST /api/v1/retraining/manual-trigger        - Always trigger
GET  /api/v1/github-actions/config-status     - Check if configured
POST /api/v1/github-actions/trigger-retraining - Trigger workflow
```

### Files

**New files:**
- [frontend/src/pages/Retraining.jsx](frontend/src/pages/Retraining.jsx) - Main retraining page (~280 lines)
- [frontend/src/components/RetrainingRunsTable.jsx](frontend/src/components/RetrainingRunsTable.jsx) - Runs table component (~50 lines)

**Updated files:**
- [frontend/src/App.jsx](frontend/src/App.jsx) - Added page switching logic
- [frontend/src/api/client.js](frontend/src/api/client.js) - Added 7 new API functions
- [frontend/src/components/Sidebar.jsx](frontend/src/components/Sidebar.jsx) - Made clickable, disabled items
- [frontend/src/styles.css](frontend/src/styles.css) - Added 400+ lines for retraining UI

### Component Architecture

**Retraining.jsx** (main page):
- Fetches drift summary, runs, GitHub config on mount
- Auto-refreshes every 10 seconds
- Handles 3 trigger button clicks
- Shows success/error messages
- Conditionally renders all UI elements

**RetrainingRunsTable.jsx** (table):
- Maps run data to table rows
- Color-codes status badges
- Formats timestamps
- Shows empty state if no runs

**Sidebar.jsx** (updated):
- Tracks `activePage` state
- Highlights "Retraining" nav item when active
- Disabled items are gray and unclickable
- Click to navigate between pages

**App.jsx** (updated):
- Maintains `activePage` state
- Renders Overview or Retraining based on state
- Passes state and handler to Sidebar

### Styling

- **Dark theme**: #0f172a (bg), #1e293b (cards), #334155 (borders)
- **Status colors**: gray/blue/green/red for pending/running/completed/failed
- **Buttons**: Blue (check), Purple (manual), Indigo (GitHub Actions)
- **Cards**: 20px padding, rounded corners, subtle borders
- **Responsive**: Mobile-first, works on all screen sizes
- **Animations**: Slide-in for message alerts, hover effects on buttons

## Alert System & System Health (Phase 12)

This phase adds **database-backed alerts** for monitoring system anomalies and a **system health dashboard** for component status tracking.

### Alert System Features

**What are Alerts?**
Alerts are notifications of system issues automatically created when problems are detected. Each alert tracks:
- **Title**: Description of the issue
- **Message**: Detailed information
- **Severity**: info (blue) → warning (yellow) → critical (red)
- **Source**: Where it originated (drift, retraining, github_actions, system)
- **Status**: active (unresolved) or resolved (fixed)
- **Timestamps**: When created and resolved

**Automatic Alert Creation:**

1. **High Drift Detected** 
   - Triggered: When overall_drift_level == "high"
   - Severity: CRITICAL (red)
   - Source: drift
   - Message: Shows drift metrics per feature

2. **Accuracy Drop Detected**
   - Triggered: When accuracy_drop >= 10%
   - Severity: WARNING (yellow)
   - Source: drift
   - Message: Shows accuracy drop percentage

3. **Retraining Failed**
   - Triggered: When retraining job fails
   - Severity: CRITICAL (red)
   - Source: retraining
   - Message: Shows error details

4. **GitHub Actions Not Configured**
   - Triggered: When checking GitHub Actions config and credentials missing
   - Severity: WARNING (yellow)
   - Source: github_actions
   - Message: Instructs how to configure

**Alerts Page (/alerts)**

The Alerts page provides comprehensive monitoring with:

1. **KPI Cards**
   - Total Alerts: All alerts in database
   - Active Alerts: Red badge if count > 0
   - Critical Alerts: Shows CRITICAL severity count
   - Resolved Alerts: Shows green badge

2. **Active Alerts Section**
   - Shows up to 20 unresolved alerts
   - Each card displays:
     - Color-coded severity badge (critical=red, warning=yellow, info=blue)
     - Title and full message
     - Source label with icon (📊 Drift, 🔄 Retraining, 🔷 GitHub Actions, ⚙️ System)
     - Created timestamp
     - Resolved timestamp (if resolved)
     - Resolve button (blue, for active alerts)
   - "✅ No Active Alerts" message when none exist

3. **System Health Card**
   - Backend API: Green if /health responds, red if offline
   - GitHub Actions: Green (configured) or yellow (not configured)
   - PostgreSQL: Blue (manual status, always shows)
   - Redis/Celery: Blue (manual status, always shows)
   - Each item shows status with color-coded border

4. **Demo Seed Button**
   - Creates 6 sample alerts for testing
   - Shows success message when complete
   - Skips if alerts already exist (prevents duplicate demo data)
   - Useful for UI testing and demonstrations

5. **All Alerts History Table**
   - Shows last 50 alerts in database
   - Columns: Severity, Title, Source, Status, Created, Resolved
   - Color-coded severity badges
   - Status shows "Active" or "Resolved" with color

**Auto-Refresh & Real-Time Updates**
- Page auto-refreshes every 10 seconds
- Fetches summary, active alerts, and all alerts
- Shows loading state while fetching
- Handles API errors gracefully

### Backend API Endpoints

#### 1. Get All Alerts
```bash
GET /api/v1/alerts?limit=50

# Response
{
  "alerts": [
    {
      "id": "uuid",
      "title": "High drift detected",
      "message": "Overall drift level is HIGH...",
      "severity": "critical",
      "source": "drift",
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z",
      "resolved_at": null
    }
  ],
  "total_count": 42
}
```

#### 2. Get Active Alerts
```bash
GET /api/v1/alerts/active

# Response
{
  "alerts": [
    { ...alert object... }
  ],
  "total_count": 3
}
```

#### 3. Get Alerts Summary
```bash
GET /api/v1/alerts/summary

# Response
{
  "total": 42,
  "active": 3,
  "critical": 2,
  "warning": 5,
  "info": 35,
  "resolved": 39
}
```

#### 4. Resolve Alert
```bash
POST /api/v1/alerts/{alert_id}/resolve

# Response
{
  "status": "success",
  "alert_id": "uuid",
  "message": "Alert resolved successfully"
}
```

#### 5. Seed Demo Alerts
```bash
POST /api/v1/alerts/seed-demo

# Response (if seeded)
{
  "message": "Demo alerts seeded successfully",
  "count": 6
}

# Response (if already exist)
{
  "message": "Alerts table already has data, skipping seed"
}
```

### Backend Implementation Details

**New Files Created:**

- `backend/app/models/alert.py`: SQLAlchemy ORM model for alerts table
- `backend/app/schemas/alert.py`: Pydantic request/response schemas (5 models)
- `backend/app/services/alert_service.py`: Business logic for alert operations (7 methods)
- `backend/app/api/routes/alerts.py`: FastAPI router with 5 endpoints

**Updated Files:**

- `backend/app/main.py`: Imported Alert model and alerts router
- `backend/app/services/drift_service.py`: Create alerts on high drift/accuracy drop
- `backend/app/tasks/retraining_tasks.py`: Create alerts on retraining failure
- `backend/app/api/routes/github_actions.py`: Create alerts on GitHub config missing

**Key Service Methods:**

```python
# Create new alert
AlertService.create_alert(db, request)

# Create alert only if one with same title+source doesn't exist (prevents duplicates)
AlertService.create_alert_if_not_exists(db, title, message, severity, source)

# Get all alerts (paginated)
AlertService.get_all_alerts(db, limit=50)

# Get only active/unresolved alerts
AlertService.get_active_alerts(db)

# Get summary statistics
AlertService.get_alerts_summary(db)

# Mark alert as resolved
AlertService.resolve_alert(db, alert_id)

# Create 6 demo alerts for testing
AlertService.seed_demo_alerts(db)
```

### Frontend Implementation

**New Components:**

- `frontend/src/components/AlertCard.jsx`: Reusable alert display component (130 lines)
  - Props: alert object, onResolve callback, isResolving boolean
  - Severity colors: critical=red, warning=yellow, info=blue
  - Shows title, message, source, timestamps
  - Resolve button for active alerts

- `frontend/src/pages/Alerts.jsx`: Main alerts monitoring page (300+ lines)
  - KPI cards showing totals
  - Active alerts section with AlertCard components
  - System health card with component statuses
  - Demo seed button
  - All alerts history table
  - 10-second auto-refresh polling

**Updated Components:**

- `frontend/src/api/client.js`: Added 8 functions
  - `getAlerts(limit)`: Fetch all alerts
  - `getActiveAlerts()`: Fetch active only
  - `getAlertsSummary()`: Fetch summary stats
  - `resolveAlert(alertId)`: Mark as resolved
  - `seedDemoAlerts()`: Create demo data
  - `getHealth()`: Check backend API status
  - Error handling with sensible defaults

- `frontend/src/App.jsx`: Added routing for Alerts page

- `frontend/src/components/Sidebar.jsx`: Enabled "Alerts" navigation item (was disabled)

**Styling (150+ lines in styles.css):**

- Alert card styling with severity-based border colors
- KPI card styling specific to alerts page
- System health grid layout (4-column)
- Health status indicators
- Active/resolved badges
- Empty state messaging
- Responsive design (1-column on mobile)

### Quick Commands

```bash
# View all alerts
curl http://localhost:8000/api/v1/alerts

# View active alerts
curl http://localhost:8000/api/v1/alerts/active

# Get alerts summary
curl http://localhost:8000/api/v1/alerts/summary

# Seed demo alerts
curl -X POST http://localhost:8000/api/v1/alerts/seed-demo

# Resolve an alert (replace UUID)
curl -X POST http://localhost:8000/api/v1/alerts/{alert_id}/resolve
```

### Testing Phase 12

**1. Seed Demo Alerts**
- Open Alerts page
- Click "Seed Demo Alerts" button
- Verify 6 demo alerts appear in table

**2. Test Active Alerts**
- Go to Alerts page
- Verify active alerts section shows alerts with "Resolve" buttons
- Click Resolve on an alert
- Verify it moves to history with "Resolved" badge

**3. Test Real Drift Alert**
- Go to Overview page
- Click "Calculate Drift"
- Wait for calculation to complete
- Go to Alerts page
- Verify high drift alert appears (if drift is high)

**4. Test GitHub Config Alert**
- Go to Retraining page
- Verify GitHub Actions shows "Not configured"
- Go to Alerts page
- Verify GitHub Actions config alert exists

**5. Test System Health**
- Go to Alerts page
- Verify Backend API status shows green (if backend running)
- Verify other statuses appear with proper colors

## Next Steps

1. ✅ Phase 1: Project scaffold (completed)
2. ✅ Phase 2: Backend data ingestion (completed)
3. ✅ Phase 3: Python SDK Logger (completed)
4. ✅ Phase 4: Demo Data Generation (completed)
5. ✅ Phase 5: Drift Detection Engine (completed)
6. ✅ Phase 6: Dashboard & Monitoring (completed)
7. ✅ Phase 7: Model Retraining & Experiment Tracking (completed)
8. ✅ Phase 8: Background Job Automation (completed)
9. ✅ Phase 9: GitHub Actions Integration (completed)
10. ✅ Phase 10: Retraining Automation UI (completed)
11. ✅ Phase 11: Model Registry & Promotion (completed)
12. ✅ Phase 12: Alert System & System Health (completed)
13. 🔲 Phase 13: Production deployment & monitoring

## Installation

### Backend Dependencies (With Drift Detection, Retraining & Background Jobs)

After pulling the latest code, update backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Dependencies:
- `fastapi==0.104.1` - Web framework
- `sqlalchemy==2.0.23` - ORM
- `psycopg2-binary==2.9.9` - PostgreSQL driver
- `numpy>=1.24.0` - Numerical computing
- `scipy>=1.10.0` - Statistical tests (KS-test)
- `scikit-learn>=1.3.0` - Machine learning (for RandomForest)
- `pandas>=2.0.0` - Data manipulation (for feature extraction)
- `mlflow>=2.10.0` - Experiment tracking (for model logging)
- `celery>=5.3.0` - Background job queue (NEW - for async tasks)
- `redis>=5.0.0` - Redis client (NEW - for Celery broker)
- `requests>=2.28.0` - HTTP client

### Running Backend with Background Jobs

Start all services:

```bash
# 1. Start PostgreSQL, Redis, MLflow (Docker Compose)
docker-compose up postgres redis mlflow -d

# 2. Start FastAPI backend
cd backend
python -m uvicorn app.main:app --reload

# 3. Start Celery worker (new terminal)
cd backend
celery -A app.core.celery_app worker --loglevel=info

# 4. Trigger retraining (new terminal)
curl -X POST http://localhost:8000/api/v1/retraining/manual-trigger
```

### ML Module Dependencies (For Retraining)

ML module scripts use the same backend requirements plus:

```bash
# All dependencies already in backend/requirements.txt
# Just ensure backend packages are installed
```

To run retraining:

```bash
cd backend
pip install -r requirements.txt

cd ../ml
python retrain_model.py
```

### Frontend Dependencies (With Dashboard)

After pulling the latest code, update frontend dependencies:

```bash
cd frontend
npm install
```

Dependencies:
- `react@^18.2.0` - UI library
- `react-dom@^18.2.0` - DOM rendering
- `axios@^1.6.0` - HTTP client
- `recharts@^2.10.0` - Charting library (for PSI chart visualization)

## License

MIT
