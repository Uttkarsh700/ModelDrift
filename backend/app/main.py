"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import health, predictions, labels
from app.db.database import Base, engine

# Import models to register them with Base metadata
from app.models.prediction import Prediction  # noqa: F401
from app.models.ground_truth import GroundTruthLabel  # noqa: F401

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
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health.router)
app.include_router(predictions.router)
app.include_router(labels.router)


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
