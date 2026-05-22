"""
Model Registry Service Layer

Handles all business logic for model versioning and promotion.
Champion = currently deployed production model
Challenger = latest staging candidate model
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from app.models.model_version import ModelVersion
from app.schemas.model_registry import RegisterModelRequest, ChampionChallengerResponse, ModelVersionResponse


class ModelRegistryService:
    """Business logic for model registry management."""

    @staticmethod
    def register_model(db: Session, request: RegisterModelRequest) -> ModelVersion:
        """
        Register a new model version in the registry.
        
        Args:
            db: Database session
            request: Model registration data
            
        Returns:
            Created ModelVersion instance
        """
        model = ModelVersion(
            model_name=request.model_name,
            model_version=request.model_version,
            stage=request.stage,
            accuracy=request.accuracy,
            precision=request.precision,
            recall=request.recall,
            f1_score=request.f1_score,
            drift_score=request.drift_score,
            artifact_path=request.artifact_path,
            mlflow_run_id=request.mlflow_run_id,
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    @staticmethod
    def get_all_models(db: Session, model_name: str = "credit_risk") -> list[ModelVersion]:
        """
        Get all versions of a model, ordered by creation date (newest first).
        
        Args:
            db: Database session
            model_name: Model name to filter by (default: credit_risk)
            
        Returns:
            List of ModelVersion instances
        """
        return db.query(ModelVersion)\
            .filter(ModelVersion.model_name == model_name)\
            .order_by(desc(ModelVersion.created_at))\
            .all()

    @staticmethod
    def get_champion(db: Session, model_name: str = "credit_risk") -> ModelVersion:
        """
        Get the current production (champion) model.
        
        The champion is the model currently deployed and serving predictions.
        
        Args:
            db: Database session
            model_name: Model name to find champion for
            
        Returns:
            ModelVersion in production stage, or None if no champion exists
        """
        return db.query(ModelVersion)\
            .filter(
                ModelVersion.model_name == model_name,
                ModelVersion.stage == "production"
            )\
            .order_by(desc(ModelVersion.promoted_at))\
            .first()

    @staticmethod
    def get_challenger(db: Session, model_name: str = "credit_risk") -> ModelVersion:
        """
        Get the latest staging (challenger) model.
        
        The challenger is the candidate model waiting to be promoted to production.
        
        Args:
            db: Database session
            model_name: Model name to find challenger for
            
        Returns:
            Latest ModelVersion in staging stage, or None if no challenger exists
        """
        return db.query(ModelVersion)\
            .filter(
                ModelVersion.model_name == model_name,
                ModelVersion.stage == "staging"
            )\
            .order_by(desc(ModelVersion.created_at))\
            .first()

    @staticmethod
    def compare_models(db: Session, model_name: str = "credit_risk") -> ChampionChallengerResponse:
        """
        Compare champion and challenger models with promotion recommendation.
        
        Promotion rule:
        Recommend promoting challenger if ALL conditions are met:
        1. Challenger accuracy > Champion accuracy
        2. Challenger F1 >= Champion F1
        3. Challenger drift <= Champion drift (if both have drift scores)
        
        Args:
            db: Database session
            model_name: Model name to compare
            
        Returns:
            ChampionChallengerResponse with comparison and recommendation
        """
        champion = ModelRegistryService.get_champion(db, model_name)
        challenger = ModelRegistryService.get_challenger(db, model_name)

        # If no champion or challenger, keep champion (default safe behavior)
        if not champion or not challenger:
            return ChampionChallengerResponse(
                champion=ModelVersionResponse.from_orm(champion) if champion else None,
                challenger=ModelVersionResponse.from_orm(challenger) if challenger else None,
                accuracy_delta=None,
                f1_delta=None,
                drift_delta=None,
                recommendation="keep_champion",
                reason="No challenger available for comparison." if not challenger else "No champion available."
            )

        # Calculate deltas
        accuracy_delta = challenger.accuracy - champion.accuracy
        f1_delta = challenger.f1_score - champion.f1_score
        drift_delta = None
        if challenger.drift_score is not None and champion.drift_score is not None:
            drift_delta = challenger.drift_score - champion.drift_score

        # Determine recommendation
        # Promote if: accuracy better AND f1 same/better AND drift same/lower
        accuracy_better = challenger.accuracy > champion.accuracy
        f1_same_or_better = challenger.f1_score >= champion.f1_score
        drift_same_or_better = True
        if challenger.drift_score is not None and champion.drift_score is not None:
            drift_same_or_better = challenger.drift_score <= champion.drift_score

        should_promote = accuracy_better and f1_same_or_better and drift_same_or_better

        if should_promote:
            recommendation = "promote_challenger"
            reason = "Challenger outperforms champion: better accuracy, same/better F1, and same/lower drift."
        else:
            recommendation = "keep_champion"
            if not accuracy_better:
                reason = "Challenger accuracy is not better than champion."
            elif not f1_same_or_better:
                reason = "Challenger F1 score is lower than champion."
            elif not drift_same_or_better:
                reason = "Challenger has higher drift than champion."
            else:
                reason = "Keep champion for stability."

        return ChampionChallengerResponse(
            champion=ModelVersionResponse.from_orm(champion),
            challenger=ModelVersionResponse.from_orm(challenger),
            accuracy_delta=accuracy_delta,
            f1_delta=f1_delta,
            drift_delta=drift_delta,
            recommendation=recommendation,
            reason=reason
        )

    @staticmethod
    def promote_challenger(db: Session, model_name: str = "credit_risk") -> tuple:
        """
        Promote the challenger model to production.
        
        Steps:
        1. Find current production (champion) model
        2. Archive the champion
        3. Promote challenger to production
        4. Set promoted_at timestamp
        
        Args:
            db: Database session
            model_name: Model name to promote
            
        Returns:
            Tuple of (promoted_model, archived_model)
        """
        # Get current champion (to archive)
        champion = ModelRegistryService.get_champion(db, model_name)
        archived = None
        if champion:
            champion.stage = "archived"
            champion.promoted_at = None
            db.add(champion)
            archived = champion

        # Get challenger (to promote)
        challenger = ModelRegistryService.get_challenger(db, model_name)
        if not challenger:
            raise ValueError(f"No challenger model found for {model_name}")

        # Promote challenger
        challenger.stage = "production"
        challenger.promoted_at = datetime.utcnow()
        db.add(challenger)
        db.commit()
        db.refresh(challenger)

        return challenger, archived

    @staticmethod
    def seed_demo_registry(db: Session) -> dict:
        """
        Seed the model registry with demo data (only if table is empty).
        
        Creates:
        - credit_risk v1 (production/champion)
        - credit_risk v2 (staging/challenger)
        - credit_risk v0 (archived)
        
        Args:
            db: Database session
            
        Returns:
            Dict with status and count of models created
        """
        existing_count = db.query(ModelVersion).count()
        if existing_count > 0:
            return {"status": "skipped", "reason": "Registry already has data", "created": 0}

        # v1 - Production (Champion)
        v1 = ModelVersion(
            model_name="credit_risk",
            model_version="v1",
            stage="production",
            accuracy=0.91,
            precision=0.89,
            recall=0.88,
            f1_score=0.885,
            drift_score=0.25,
            artifact_path="ml/models/credit_risk_v1.pkl",
            mlflow_run_id="demo_run_001",
            promoted_at=datetime.utcnow()
        )

        # v2 - Staging (Challenger)
        v2 = ModelVersion(
            model_name="credit_risk",
            model_version="v2",
            stage="staging",
            accuracy=0.93,
            precision=0.92,
            recall=0.91,
            f1_score=0.915,
            drift_score=0.20,
            artifact_path="ml/models/credit_risk_v2.pkl",
            mlflow_run_id="demo_run_002",
        )

        # v0 - Archived
        v0 = ModelVersion(
            model_name="credit_risk",
            model_version="v0",
            stage="archived",
            accuracy=0.88,
            precision=0.85,
            recall=0.84,
            f1_score=0.845,
            drift_score=0.35,
            artifact_path="ml/models/credit_risk_v0.pkl",
            mlflow_run_id="demo_run_000",
        )

        db.add_all([v1, v2, v0])
        db.commit()

        return {
            "status": "seeded",
            "created": 3,
            "models": ["credit_risk v1 (production)", "credit_risk v2 (staging)", "credit_risk v0 (archived)"]
        }
