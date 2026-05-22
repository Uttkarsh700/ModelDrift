"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import health, predictions, labels, drift, training, retraining, github_actions, model_registry
from app.db.database import Base, engine
from app.core.celery_app import celery_app  # noqa: F401 - needed for workers

# Import models to register them with Base metadata
from app.models.prediction import Prediction  # noqa: F401
from app.models.ground_truth import GroundTruthLabel  # noqa: F401
from app.models.drift_metric import DriftMetric  # noqa: F401
from app.models.retraining_run import RetrainingRun  # noqa: F401
from app.models.model_version import ModelVersion  # noqa: F401

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    debug=settings.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite frontend dev server
        "http://localhost:3000",   # Alternative dev server
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health.router)
app.include_router(predictions.router)
app.include_router(labels.router)
app.include_router(drift.router)
app.include_router(training.router)
app.include_router(retraining.router)
app.include_router(github_actions.router)
app.include_router(model_registry.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to ModelDrift API",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
