"""Application layer services.

Service protocols define contracts for infrastructure implementations.
"""
from src.application.services.ai_service import (
    AIService,
    AIServiceProtocol,
    DemandForecastResult,
    DemandPrediction,
    RecommendationItem,
    RecommendationResult,
    UserPreference,
)
from src.application.services.auth_service import (
    JWTHandlerProtocol,
    PasswordHasherProtocol,
    TokenPair,
    TokenPayload,
)

__all__ = [
    # Auth
    "JWTHandlerProtocol",
    "PasswordHasherProtocol",
    "TokenPair",
    "TokenPayload",
    # AI
    "AIService",
    "AIServiceProtocol",
    "DemandForecastResult",
    "DemandPrediction",
    "RecommendationItem",
    "RecommendationResult",
    "UserPreference",
]
