# ModelDrift ML Module

Local model retraining and experiment tracking for ModelDrift.

## Overview

This module handles:
- **Retraining**: Fetch data from backend, train RandomForestClassifier, log to MLflow
- **Comparison**: View top runs from MLflow experiments
- **Model Storage**: Save trained models locally for later serving

## What is Retraining?

**Model drift** occurs when the data distribution changes, causing model performance to degrade. **Retraining** is the process of:

1. Collecting new labeled data from production
2. Training a fresh model on that data
3. Comparing the new model to the current one
4. If better, deploying the new model
5. If worse, keeping the current one

ModelDrift automates steps 1-4 locally. Step 5 (deployment) is manual for now.

## MLflow Integration

**MLflow** is an experiment tracking platform that logs:
- Model parameters (hyperparameters)
- Model metrics (accuracy, precision, recall, F1)
- Model artifacts (saved model files)
- Run metadata (timestamps, status)

This lets you:
- Compare model runs side-by-side
- Track performance over time
- Reproduce experiments
- Share results with team

## File Structure

```
ml/
├── retrain_model.py      # Main retraining script
├── compare_models.py     # View MLflow experiment runs
├── models/
│   ├── .gitkeep
│   └── credit_risk_latest.pkl  # Saved trained model
└── README.md
```

## Quick Start

### 1. Prerequisites

Generate demo data first (in project root):

```bash
# Generate training data
python scripts/generate_demo_data.py

# (Optional) Calculate drift to verify data loaded
python scripts/test_drift.py
```

### 2. Start MLflow Tracking Server

```bash
# Option A: Local MLflow (no Docker)
mlflow server --host 0.0.0.0 --port 5000

# Option B: Docker Compose (starts MLflow automatically)
cd /path/to/ModelDrift
docker-compose up mlflow
```

MLflow UI will be at: **http://localhost:5000**

### 3. Retrain Model

```bash
# Install dependencies (if not done)
cd backend
pip install -r requirements.txt
cd ../ml

# Run retraining
python retrain_model.py
```

**What happens:**
1. Fetches training data from backend (`GET /api/v1/training/dataset`)
2. Extracts features from `input_features` JSON
3. Converts labels to binary (no_default=0, default=1)
4. Splits data: 80% train, 20% test
5. Trains RandomForestClassifier (100 trees, depth 10)
6. Calculates metrics: accuracy, precision, recall, F1-score
7. Logs everything to MLflow
8. Saves model as `ml/models/credit_risk_latest.pkl`

**Example output:**
```
======================================================================
🔄 ModelDrift Retraining Pipeline
======================================================================
📡 Fetching training data from http://localhost:8000...
✅ Fetched 420 training samples
✅ Prepared DataFrame with 420 samples and 5 features

📊 Dataset split:
  Total samples: 420
  Train samples: 336 (80.0%)
  Test samples:  84 (20.0%)

🤖 Training RandomForestClassifier (n_estimators=100, max_depth=10)...
✅ Model training complete

📊 Evaluating model on test set...
  Accuracy:  0.8571
  Precision: 0.8571
  Recall:    0.8000
  F1-Score:  0.8276

📝 Logging to MLflow (experiment: ModelDrift-CreditRisk)...
✅ MLflow run created: a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6

💾 Model saved to ml/models/credit_risk_latest.pkl

======================================================================
✅ Retraining Complete!
======================================================================
Metrics:
  Accuracy:        0.8571
  Precision:       0.8571
  Recall:          0.8000
  F1-Score:        0.8276

Artifacts:
  Model File:      ml/models/credit_risk_latest.pkl
  MLflow Run ID:    a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
  View in UI:      http://localhost:5000
======================================================================
```

### 4. Compare Models

After training multiple times, view experiment results:

```bash
python compare_models.py
```

**Output:**
```
======================================================================
📊 ModelDrift Model Comparison
======================================================================
📡 Connecting to MLflow: http://localhost:5000
✅ Found experiment: ModelDrift-CreditRisk (ID: 1)
✅ Found 5 runs

📈 Top 5 Runs (sorted by accuracy):
----------------------------------------------------------------------

🥇 Rank 1 (CHAMPION)
  Run ID:      a1b2c3d4
  Status:      FINISHED
  Accuracy:    0.8571
  Precision:   0.8571
  Recall:      0.8000
  F1-Score:    0.8276
  Hyperparams: n_estimators=100, max_depth=10

🥈 Rank 2
  Run ID:      b2c3d4e5
  Status:      FINISHED
  Accuracy:    0.8333
  Precision:   0.8500
  Recall:      0.7600
  F1-Score:    0.8036
  Hyperparams: n_estimators=100, max_depth=10

...

======================================================================
🏆 Champion Model
======================================================================
Run ID:          a1b2c3d4
Accuracy:        0.8571
Precision:       0.8571
Recall:          0.8000
F1-Score:        0.8276

Experiment:      ModelDrift-CreditRisk
MLflow UI:       http://localhost:5000
======================================================================
```

## Features Tracked

### Features (5 total)
- `credit_utilization` - Credit line usage percentage
- `debt_to_income` - Debt to income ratio
- `num_recent_inquiries` - Recent credit inquiries
- `avg_account_age_months` - Average account age
- `num_open_accounts` - Number of open accounts

### Labels (Binary)
- `no_default` → 0
- `default` → 1

### Training Details
- **Algorithm**: RandomForestClassifier
- **Train/Test Split**: 80%/20%
- **Hyperparameters**: n_estimators=100, max_depth=10
- **Metrics**: Accuracy, Precision, Recall, F1-Score

## MLflow UI

Access MLflow to explore experiments, runs, and model artifacts:

```bash
# View in browser
open http://localhost:5000
```

**What you can do in MLflow:**
- Compare metrics side-by-side
- View model parameters
- Download model artifacts
- Search/filter runs
- View run history timeline

## Environment Variables

Control behavior with environment variables:

```bash
# Backend URL (where to fetch data from)
export BACKEND_URL=http://localhost:8000

# MLflow tracking server
export MLFLOW_TRACKING_URI=http://localhost:5000
```

## Troubleshooting

### "Cannot connect to backend"
```
❌ Cannot connect to backend. Is it running on http://localhost:8000?
```

**Solution:**
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### "No training samples available"
```
❌ No training data available. Generate demo data first:
   python scripts/generate_demo_data.py
```

### "Error connecting to MLflow"
```
❌ Error connecting to MLflow: ...
   Is MLflow running? Start it with:
   mlflow server --host 0.0.0.0 --port 5000
```

**Solution:**
```bash
mlflow server --host 0.0.0.0 --port 5000
```

Or use Docker Compose:
```bash
docker-compose up mlflow
```

## Architecture

```
┌────────────────────────────────────────────────┐
│ retrain_model.py                               │
│ ┌──────────────────────────────────────────┐  │
│ │ 1. fetch_training_data()                 │  │
│ │    → GET /api/v1/training/dataset        │  │
│ │    → Returns: prediction + label rows    │  │
│ └──────────────────────────────────────────┘  │
│ ┌──────────────────────────────────────────┐  │
│ │ 2. prepare_dataframe()                   │  │
│ │    → Extract features from JSON          │  │
│ │    → Convert labels to 0/1               │  │
│ │    → Returns: DataFrame ready for ML     │  │
│ └──────────────────────────────────────────┘  │
│ ┌──────────────────────────────────────────┐  │
│ │ 3. train_model()                         │  │
│ │    → RandomForestClassifier              │  │
│ │    → 80/20 train/test split              │  │
│ │    → Returns: fitted model               │  │
│ └──────────────────────────────────────────┘  │
│ ┌──────────────────────────────────────────┐  │
│ │ 4. evaluate_model()                      │  │
│ │    → Calculate metrics on test set       │  │
│ │    → Returns: accuracy, precision, etc.  │  │
│ └──────────────────────────────────────────┘  │
│ ┌──────────────────────────────────────────┐  │
│ │ 5. log_to_mlflow()                       │  │
│ │    → Create MLflow run                   │  │
│ │    → Log params, metrics, model          │  │
│ │    → Returns: run_id                     │  │
│ └──────────────────────────────────────────┘  │
│ ┌──────────────────────────────────────────┐  │
│ │ 6. save_model()                          │  │
│ │    → Pickle model to disk                │  │
│ │    → Saved to: ml/models/credit_risk...  │  │
│ └──────────────────────────────────────────┘  │
└────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────┐
│ MLflow Tracking Server (http://localhost:5000) │
│ - Stores run metadata, params, metrics         │
│ - Provides web UI for exploration              │
│ - Persists data to backend storage             │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ compare_models.py                              │
│ ┌──────────────────────────────────────────┐  │
│ │ Query MLflow experiment runs             │  │
│ │ Sort by accuracy (descending)            │  │
│ │ Display top 5 + champion                 │  │
│ └──────────────────────────────────────────┘  │
└────────────────────────────────────────────────┘
```

## Next Steps (Phase 8+)

- **Auto-retraining triggers**: Automatically retrain when drift is detected
- **Model serving**: Use saved model for predictions
- **A/B testing**: Deploy new model to subset of traffic
- **Retraining schedules**: Scheduled retraining (hourly, daily, etc.)
- **Hyperparameter tuning**: GridSearch/RandomSearch for best params
- **Feature engineering**: Auto-detect important features
- **Model registry**: MLflow Model Registry for versioning

## References

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [scikit-learn RandomForest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
