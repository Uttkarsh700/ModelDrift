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
│   │   ├── models/         # SQLAlchemy models (placeholder)
│   │   ├── schemas/        # Pydantic schemas (placeholder)
│   │   └── services/       # Business logic (placeholder)
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

## Current Phase: Data Ingestion (Phase 2)

This phase implements **backend data ingestion** for model predictions and ground truth labels:
- ✅ Database models for predictions and labels
- ✅ Pydantic schemas for request/response validation
- ✅ SQLAlchemy services for data operations
- ✅ RESTful API endpoints for predictions and labels
- ✅ Automatic table creation on app startup
- ✅ JSONB support for flexible feature storage

**Phase 1 (Completed):**
- Project structure and folder hierarchy
- Backend FastAPI setup with health check endpoint
- Frontend React setup with basic pages
- Docker Compose configuration for all services
- Database and cache connections (configured)

**Coming Later (Phase 3+):**
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

## Development Notes

- Backend uses FastAPI with auto-reloading
- Frontend uses Vite for fast HMR
- Docker Compose volumes enable live code changes
- All services are containerized for consistency

## Next Steps

1. Add drift detection algorithms to `ml/`
2. Implement model training with scikit-learn
3. Add MLflow integration
4. Create database models for tracking metrics
5. Build monitoring dashboard in React
6. Implement auto-retraining logic
7. Add authentication and authorization
8. Create data pipeline for ingesting predictions

## License

MIT
