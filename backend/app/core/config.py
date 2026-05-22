"""Application configuration."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # API Settings
    API_TITLE: str = "ModelDrift API"
    API_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/modeldrift"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # MLflow
    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    
    # GitHub Actions (optional - for triggering workflows)
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_OWNER: str = os.getenv("GITHUB_OWNER", "")
    GITHUB_REPO: str = os.getenv("GITHUB_REPO", "")
    GITHUB_WORKFLOW_FILE: str = os.getenv("GITHUB_WORKFLOW_FILE", "retrain-model.yml")
    GITHUB_REF: str = os.getenv("GITHUB_REF", "main")
    
    class Config:
        env_file = ".env"


settings = Settings()
