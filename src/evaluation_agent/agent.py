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
    ContactMethod,
    VendorContactRequest,
    VendorContactResponse,
)
from .tools.voyage_tool import score_vendors_with_voyage
from .tools.exa_tool import get_sample_vendors
from .tools.email_tool import send_invoice_request_email

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

    async def contact_best_vendor(
        self,
        request: VendorContactRequest,
    ) -> VendorContactResponse:
        """
        Contact the best vendor to request invoice and payment directions.

        Supports email, call, or SMS based on available contact info and preference.
        """
        method = request.preferred_method
        error = None

        # Try preferred method first, fall back to alternatives
        if method == ContactMethod.EMAIL and request.vendor_email:
            result = await self._send_invoice_email(request)
            if result.success:
                return result
            error = result.error

        if method == ContactMethod.CALL and request.vendor_phone:
            result = await self._call_vendor_for_invoice(request)
            if result.success:
                return result
            error = result.error

        if method == ContactMethod.SMS and request.vendor_phone:
            result = await self._send_invoice_sms(request)
            if result.success:
                return result
            error = result.error

        # Fallback: try available methods
        if request.vendor_email and method != ContactMethod.EMAIL:
            result = await self._send_invoice_email(request)
            if result.success:
                return result

        if request.vendor_phone and method != ContactMethod.CALL:
            result = await self._call_vendor_for_invoice(request)
            if result.success:
                return result

        # No successful contact
        return VendorContactResponse(
            success=False,
            method_used=method,
            vendor_id=request.vendor_id,
            vendor_name=request.vendor_name,
            error=error or "No valid contact method available",
        )

    async def _send_invoice_email(
        self,
        request: VendorContactRequest,
    ) -> VendorContactResponse:
        """Send invoice request via email."""
        if not request.vendor_email:
            return VendorContactResponse(
                success=False,
                method_used=ContactMethod.EMAIL,
                vendor_id=request.vendor_id,
                vendor_name=request.vendor_name,
                error="No email address available",
            )

        result = await send_invoice_request_email(
            to_email=request.vendor_email,
            vendor_name=request.vendor_name,
            business_name=request.business_name,
            product=request.product,
            quantity=request.quantity,
            unit=request.unit,
            agreed_price=request.agreed_price,
            reply_to=request.reply_to_email,
        )

        if result.get("error"):
            return VendorContactResponse(
                success=False,
                method_used=ContactMethod.EMAIL,
                vendor_id=request.vendor_id,
                vendor_name=request.vendor_name,
                error=result["error"],
            )

        logger.info(f"Invoice email sent to {request.vendor_name} ({request.vendor_email})")

        return VendorContactResponse(
            success=True,
            method_used=ContactMethod.EMAIL,
            vendor_id=request.vendor_id,
            vendor_name=request.vendor_name,
            message_id=result.get("email_id"),
        )

    async def _call_vendor_for_invoice(
        self,
        request: VendorContactRequest,
    ) -> VendorContactResponse:
        """Call vendor to request invoice and payment directions."""
        if not request.vendor_phone:
            return VendorContactResponse(
                success=False,
                method_used=ContactMethod.CALL,
                vendor_id=request.vendor_id,
                vendor_name=request.vendor_name,
                error="No phone number available",
            )

        try:
            # Import here to avoid circular imports
            from ..calling_agent.tools.vapi_tool import call_vendor_and_wait
            from ..calling_agent.schemas import CallVendorInput

            # Create call input with invoice-specific prompt context
            call_input = CallVendorInput(
                phone_number=request.vendor_phone,
                vendor_name=request.vendor_name,
                business_name=request.business_name,
                product=request.product,
                quantity=int(request.quantity),
                unit=request.unit,
            )

            result = await call_vendor_and_wait(call_input)

            if not result.get("success"):
                return VendorContactResponse(
                    success=False,
                    method_used=ContactMethod.CALL,
                    vendor_id=request.vendor_id,
                    vendor_name=request.vendor_name,
                    error=result.get("error", "Call failed"),
                )

            logger.info(f"Invoice call completed with {request.vendor_name}")

            return VendorContactResponse(
                success=True,
                method_used=ContactMethod.CALL,
                vendor_id=request.vendor_id,
                vendor_name=request.vendor_name,
                message_id=result.get("call_id"),
                call_outcome=result.get("outcome"),
            )

        except Exception as e:
            logger.exception(f"Failed to call vendor {request.vendor_name}: {e}")
            return VendorContactResponse(
                success=False,
                method_used=ContactMethod.CALL,
                vendor_id=request.vendor_id,
                vendor_name=request.vendor_name,
                error=str(e),
            )

    async def _send_invoice_sms(
        self,
        request: VendorContactRequest,
    ) -> VendorContactResponse:
        """Send invoice request via SMS/WhatsApp."""
        if not request.vendor_phone:
            return VendorContactResponse(
                success=False,
                method_used=ContactMethod.SMS,
                vendor_id=request.vendor_id,
                vendor_name=request.vendor_name,
                error="No phone number available",
            )

        try:
            from ..message_agent.tools.vonage_tool import send_sms
            from ..message_agent.schemas import OutgoingSMS

            message_body = (
                f"Hi {request.vendor_name}, this is {request.business_name}. "
                f"Thank you for confirming our order of {request.quantity} {request.unit} of {request.product}. "
                f"Could you please send us an invoice with your payment directions? "
                f"We're ready to process payment. Thank you!"
            )

            sms = OutgoingSMS(
                to_number=request.vendor_phone,
                body=message_body,
            )

            result = await send_sms(sms)

            if result.get("error"):
                return VendorContactResponse(
                    success=False,
                    method_used=ContactMethod.SMS,
                    vendor_id=request.vendor_id,
                    vendor_name=request.vendor_name,
                    error=result["error"],
                )

            logger.info(f"Invoice SMS sent to {request.vendor_name} ({request.vendor_phone})")

            return VendorContactResponse(
                success=True,
                method_used=ContactMethod.SMS,
                vendor_id=request.vendor_id,
                vendor_name=request.vendor_name,
                message_id=result.get("message_id"),
            )

        except Exception as e:
            logger.exception(f"Failed to send SMS to vendor {request.vendor_name}: {e}")
            return VendorContactResponse(
                success=False,
                method_used=ContactMethod.SMS,
                vendor_id=request.vendor_id,
                vendor_name=request.vendor_name,
                error=str(e),
            )


# Global instance
_evaluation_agent: Optional[EvaluationAgent] = None


def get_evaluation_agent() -> EvaluationAgent:
    """Get or create the global evaluation agent instance."""
    global _evaluation_agent
    if _evaluation_agent is None:
        _evaluation_agent = EvaluationAgent()
    return _evaluation_agent
