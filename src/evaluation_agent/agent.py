"""
Evaluation Agent - Personalized Vendor Selection with Voyage AI

Scores and selects vendors based on business owner's learned preferences
across four dimensions: Quality, Affordability, Shipping, Reliability.
"""

import os
import logging
from typing import Optional
from datetime import datetime

from .schemas import (
    EvaluationParameter,
    FeedbackDirection,
    PreferenceWeights,
    VendorScores,
    VendorEvaluation,
    FeedbackRequest,
    BusinessPreferences,
    EvaluationRequest,
    EvaluationResponse,
)
from .tools.voyage_tool import score_vendors_with_voyage
from .tools.exa_tool import get_sample_vendors

logger = logging.getLogger(__name__)

# Configuration
LEARNING_RATE = float(os.getenv("EVAL_LEARNING_RATE", "0.05"))
MIN_WEIGHT = float(os.getenv("EVAL_MIN_WEIGHT", "0.05"))
MAX_WEIGHT = float(os.getenv("EVAL_MAX_WEIGHT", "0.60"))


class EvaluationAgent:
    """
    Personalized vendor evaluation agent.

    Uses Voyage AI embeddings to learn business owner preferences
    and score vendors accordingly.
    """

    def __init__(self):
        self._preferences: dict[str, BusinessPreferences] = {}
        self._voyage_model_id: Optional[str] = None

    def get_preferences(self, business_id: str) -> BusinessPreferences:
        """Get or create preferences for a business."""
        if business_id not in self._preferences:
            self._preferences[business_id] = BusinessPreferences(
                business_id=business_id,
                weights=PreferenceWeights(),
            )
        return self._preferences[business_id]

    def process_feedback(
        self,
        business_id: str,
        feedback: FeedbackRequest
    ) -> PreferenceWeights:
        """
        Process user feedback and update preference weights.

        When user clicks UP: increase weight for that parameter
        When user clicks DOWN: decrease weight for that parameter
        """
        prefs = self.get_preferences(business_id)

        # Calculate adjustment
        adjustment = LEARNING_RATE if feedback.direction == FeedbackDirection.UP else -LEARNING_RATE

        # Get current weights as dict
        weights_dict = prefs.weights.model_dump()
        param_key = feedback.parameter.value

        # Apply adjustment
        new_value = weights_dict[param_key] + adjustment
        new_value = max(MIN_WEIGHT, min(MAX_WEIGHT, new_value))
        weight_change = new_value - weights_dict[param_key]

        # Redistribute to other parameters
        other_params = [p for p in weights_dict.keys() if p != param_key]
        redistribution = -weight_change / len(other_params)

        weights_dict[param_key] = new_value
        for p in other_params:
            weights_dict[p] = max(MIN_WEIGHT, min(MAX_WEIGHT, weights_dict[p] + redistribution))

        # Normalize and update
        new_weights = PreferenceWeights(**weights_dict).normalize()
        prefs.weights = new_weights
        prefs.total_feedback_count += 1

        logger.info(f"Updated weights for {business_id}: {param_key} {feedback.direction.value}")

        return new_weights

    def evaluate_vendors(
        self,
        request: EvaluationRequest,
        vendors: Optional[list[dict]] = None,
    ) -> EvaluationResponse:
        """
        Evaluate and select vendors based on personalized preferences.
        """
        prefs = self.get_preferences(request.business_id)

        # Use provided vendors or get sample vendors
        if vendors is None:
            vendors = get_sample_vendors()

        # Filter by requested ingredients
        filtered_vendors = [
            v for v in vendors
            if v.get("product") in request.ingredients or not request.ingredients
        ]

        if not filtered_vendors:
            filtered_vendors = vendors

        # Score using Voyage AI
        weights_dict = prefs.weights.model_dump()
        scored = score_vendors_with_voyage(
            vendors=filtered_vendors,
            weights=weights_dict,
            model_id=self._voyage_model_id,
        )

        # Select within budget
        selected = []
        total_cost = 0.0

        for vendor in scored:
            price = vendor.get("price_per_unit", 0)
            if total_cost + price <= request.budget:
                selected.append(VendorEvaluation(
                    vendor_id=vendor["vendor_id"],
                    vendor_name=vendor["vendor_name"],
                    scores=VendorScores(**vendor["scores"]),
                    embedding_score=vendor["embedding_score"],
                    parameter_score=vendor["parameter_score"],
                    final_score=vendor["final_score"],
                    rank=len(selected) + 1,
                ))
                total_cost += price

        return EvaluationResponse(
            selected_vendors=selected,
            total_cost=total_cost,
            budget=request.budget,
            savings=request.budget - total_cost,
            weights_used=prefs.weights,
        )

    def get_radar_chart_data(self, evaluation: VendorEvaluation) -> list[dict]:
        """Format vendor scores for radar chart."""
        return [
            {"parameter": "Quality", "value": evaluation.scores.quality, "fullMark": 100},
            {"parameter": "Affordability", "value": evaluation.scores.affordability, "fullMark": 100},
            {"parameter": "Shipping", "value": evaluation.scores.shipping, "fullMark": 100},
            {"parameter": "Reliability", "value": evaluation.scores.reliability, "fullMark": 100},
        ]

    def set_voyage_model(self, model_id: str):
        """Set the Voyage AI model to use for scoring."""
        self._voyage_model_id = model_id
        logger.info(f"Using Voyage model: {model_id}")


# Global instance
_evaluation_agent: Optional[EvaluationAgent] = None


def get_evaluation_agent() -> EvaluationAgent:
    """Get or create the global evaluation agent instance."""
    global _evaluation_agent
    if _evaluation_agent is None:
        _evaluation_agent = EvaluationAgent()
    return _evaluation_agent
