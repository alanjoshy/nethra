"""
Intelligence schemas.
"""

from app.modules.intelligence.schemas.intelligence_schemas import (
    # Phase 1 schemas
    RelatedCaseResult,
    RelatedCasesResponse,
    RepeatOffenderResult,
    RepeatOffendersResponse,
    TagCorrelation,
    SuspectPattern,
    PatternCorrelationResponse,
    BehaviorSimilarityResult,
    BehaviorSimilarityResponse,
    RiskBreakdown,
    RiskScoreResponse,
    # Legacy schemas
    RelatedCaseResponse,
    SuspectedPersonResponse,
    IntelligenceResponse,
)

__all__ = [
    # Phase 1
    "RelatedCaseResult",
    "RelatedCasesResponse",
    "RepeatOffenderResult",
    "RepeatOffendersResponse",
    "TagCorrelation",
    "SuspectPattern",
    "PatternCorrelationResponse",
    "BehaviorSimilarityResult",
    "BehaviorSimilarityResponse",
    "RiskBreakdown",
    "RiskScoreResponse",
    # Legacy
    "RelatedCaseResponse",
    "SuspectedPersonResponse",
    "IntelligenceResponse",
]

