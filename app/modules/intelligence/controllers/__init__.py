"""
Intelligence controllers.
"""

from app.modules.intelligence.controllers.intelligence_controller import (
    router,
    behavior_router,
    risk_router,
)

__all__ = ["router", "behavior_router", "risk_router"]

