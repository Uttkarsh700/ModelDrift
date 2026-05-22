"""
Model Registry API Routes

Endpoints for model registration, comparison, and promotion.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.model_registry import (
    RegisterModelRequest,
    RegisterResponse,
    ModelVersionResponse,
    ModelsListResponse,
    ChampionChallengerResponse,
    PromotionResponse,
)
from app.services.model_registry_service import ModelRegistryService

router = APIRouter(prefix="/api/v1/model-registry", tags=["model-registry"])


@router.post("/register", response_model=RegisterResponse)
async def register_model(request: RegisterModelRequest, db: Session = Depends(get_db)):
    """
    Register a new model version in the registry.
    
    This endpoint allows you to register a trained model with its metrics.
    Models start in 'staging' or 'production' stage.
    """
    model = ModelRegistryService.register_model(db, request)
    return RegisterResponse(
        status="registered",
        model_name=model.model_name,
        model_version=model.model_version,
        stage=model.stage
    )


@router.get("/models", response_model=ModelsListResponse)
async def get_all_models(db: Session = Depends(get_db)):
    """
    Get all model versions ordered by creation date (newest first).
    """
    models = ModelRegistryService.get_all_models(db)
    responses = [ModelVersionResponse.from_orm(m) for m in models]
    return ModelsListResponse(models=responses, total_count=len(responses))


@router.get("/champion", response_model=ModelVersionResponse)
async def get_champion(db: Session = Depends(get_db)):
    """
    Get the current production (champion) model.
    
    The champion is the model currently deployed and serving predictions.
    """
    model = ModelRegistryService.get_champion(db)
    if not model:
        raise HTTPException(status_code=404, detail="No champion model found")
    return ModelVersionResponse.from_orm(model)


@router.get("/challenger", response_model=ModelVersionResponse)
async def get_challenger(db: Session = Depends(get_db)):
    """
    Get the latest staging (challenger) model.
    
    The challenger is the candidate model waiting to be promoted to production.
    """
    model = ModelRegistryService.get_challenger(db)
    if not model:
        raise HTTPException(status_code=404, detail="No challenger model found")
    return ModelVersionResponse.from_orm(model)


@router.get("/comparison", response_model=ChampionChallengerResponse)
async def get_comparison(db: Session = Depends(get_db)):
    """
    Compare champion and challenger models with promotion recommendation.
    
    Response includes:
    - Both models' metrics
    - Deltas (differences)
    - Recommendation: "promote_challenger" or "keep_champion"
    - Reason for the recommendation
    """
    return ModelRegistryService.compare_models(db)


@router.post("/promote", response_model=PromotionResponse)
async def promote_challenger(db: Session = Depends(get_db)):
    """
    Promote the challenger model to production.
    
    This endpoint:
    1. Archives the current champion
    2. Promotes challenger to production
    3. Sets promoted_at timestamp
    """
    try:
        promoted, archived = ModelRegistryService.promote_challenger(db)
        
        return PromotionResponse(
            status="promoted",
            promoted_model=ModelVersionResponse.from_orm(promoted),
            archived_model=ModelVersionResponse.from_orm(archived) if archived else None,
            message=f"Model {promoted.model_version} promoted to production"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/seed-demo", response_model=dict)
async def seed_demo_registry(db: Session = Depends(get_db)):
    """
    Seed the model registry with demo data.
    
    Only creates demo models if the registry is empty.
    
    Creates:
    - credit_risk v1 (production)
    - credit_risk v2 (staging)
    - credit_risk v0 (archived)
    """
    return ModelRegistryService.seed_demo_registry(db)
