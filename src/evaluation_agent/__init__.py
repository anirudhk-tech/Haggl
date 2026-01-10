"""Haggl Evaluation Agent - Personalized Vendor Selection with Voyage AI"""

__version__ = "0.1.0"

from .agent import EvaluationAgent, get_evaluation_agent
from .schemas import EvaluationRequest, EvaluationResponse, PreferenceWeights

__all__ = [
    "EvaluationAgent",
    "get_evaluation_agent",
    "EvaluationRequest",
    "EvaluationResponse",
    "PreferenceWeights",
]
