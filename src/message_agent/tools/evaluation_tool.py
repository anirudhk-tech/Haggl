"""Evaluation tool - picks best vendor using the Evaluation Agent."""

import logging
import uuid
from typing import Optional

from evaluation_agent import get_evaluation_agent, EvaluationRequest

# Storage imports
try:
    from storage.evaluations import create_evaluation, update_evaluation_status
    from storage.schemas import EvaluationStatus, VendorCallResult
    STORAGE_ENABLED = True
except ImportError:
    STORAGE_ENABLED = False

logger = logging.getLogger(__name__)


async def evaluate_vendor_calls(
    order_id: str,
    call_results: list[dict],
    product: str,
    business_id: str = "acme_bakery",
    budget: float = 1000.0,
) -> dict:
    """
    Evaluate call results and pick the best vendor.
    
    Uses the Evaluation Agent to score vendors based on:
    - Call outcome (confirmed, price, eta)
    - Quality score
    - Reliability score
    - Affordability (price comparison)
    - Shipping/distance
    
    Args:
        order_id: Order ID for tracking
        call_results: List of call result dicts from parallel calls
        product: Product being ordered
        business_id: Business ID for preference weights
        budget: Maximum budget
        
    Returns:
        dict with selected vendor and reasoning
    """
    evaluation_id = f"eval-{uuid.uuid4().hex[:8]}"
    
    logger.info(f"Evaluating {len(call_results)} vendor calls for order {order_id}")
    
    # Filter to only confirmed vendors
    confirmed_results = [r for r in call_results if r.get("success") or r.get("confirmed")]
    
    if not confirmed_results:
        logger.warning("No confirmed vendors to evaluate")
        return {
            "success": False,
            "evaluation_id": evaluation_id,
            "selected_vendor": None,
            "reason": "No vendors confirmed the order",
            "all_results": call_results,
        }
    
    # Build VendorCallResult objects for storage
    vendor_call_results = []
    for r in call_results:
        vendor_call_results.append(VendorCallResult(
            vendor_id=r.get("vendor_id", f"vendor-{len(vendor_call_results)}"),
            vendor_name=r.get("vendor_name", "Unknown"),
            call_id=r.get("call_id"),
            confirmed=r.get("success", False) or r.get("confirmed", False),
            quoted_price=r.get("price") or r.get("quoted_price"),
            eta=r.get("eta"),
            quality_score=r.get("quality_score", 50.0),
            reliability_score=r.get("reliability_score", 50.0),
            distance_miles=r.get("distance_miles", 0.0),
            price_per_unit=r.get("price") or r.get("price_per_unit"),
            unit=r.get("unit", "dozen"),
            certifications=r.get("certifications", []),
        ))
    
    # Create evaluation record in MongoDB
    if STORAGE_ENABLED:
        try:
            create_evaluation(
                evaluation_id=evaluation_id,
                order_id=order_id,
                vendor_results=vendor_call_results,
            )
            update_evaluation_status(evaluation_id, EvaluationStatus.IN_PROGRESS)
        except Exception as e:
            logger.warning(f"Failed to save evaluation to MongoDB: {e}")
    
    # Build vendor data for evaluation agent
    vendors_for_eval = []
    for r in confirmed_results:
        # Use quoted price from call if available, otherwise sourced price
        price = r.get("price") or r.get("quoted_price") or r.get("price_per_unit") or 5.0
        
        vendors_for_eval.append({
            "vendor_id": r.get("vendor_id", f"vendor-{len(vendors_for_eval)}"),
            "vendor_name": r.get("vendor_name", "Unknown"),
            "product": product,
            "price_per_unit": price,
            "unit": r.get("unit", "dozen"),
            "distance_miles": r.get("distance_miles", 50.0),
            "quality_score": r.get("quality_score", 50.0),
            "reliability_score": r.get("reliability_score", 50.0),
            "certifications": r.get("certifications", []),
            "description": f"Confirmed order at ${price}/unit. ETA: {r.get('eta', 'TBD')}",
            # Extra data from call
            "call_id": r.get("call_id"),
            "eta": r.get("eta"),
            "confirmed": True,
        })
    
    try:
        # Get evaluation agent
        eval_agent = get_evaluation_agent()
        
        # Create evaluation request
        eval_request = EvaluationRequest(
            business_id=business_id,
            budget=budget,
            ingredients=[product],
        )
        
        # Run evaluation
        logger.info(f"Running evaluation with {len(vendors_for_eval)} confirmed vendors")
        eval_response = eval_agent.evaluate_vendors(eval_request, vendors_for_eval)
        
        if eval_response.selected_vendors:
            selected = eval_response.selected_vendors[0]  # Top-ranked vendor
            
            # Find the full result for this vendor
            selected_result = next(
                (r for r in confirmed_results if r.get("vendor_name") == selected.vendor_name),
                confirmed_results[0]
            )
            
            # Build selection reason
            reason = (
                f"Selected {selected.vendor_name} with score {selected.final_score:.2f}. "
                f"Quality: {selected.scores.quality:.0f}/100, "
                f"Affordability: {selected.scores.affordability:.0f}/100, "
                f"Shipping: {selected.scores.shipping:.0f}/100, "
                f"Reliability: {selected.scores.reliability:.0f}/100"
            )
            
            logger.info(f"Evaluation complete: {reason}")
            
            # Update MongoDB with result
            if STORAGE_ENABLED:
                try:
                    update_evaluation_status(
                        evaluation_id,
                        EvaluationStatus.COMPLETED,
                        selected_vendor_id=selected.vendor_id,
                        selected_vendor_name=selected.vendor_name,
                        selection_reason=reason,
                        weights_used=eval_response.weights_used.model_dump() if eval_response.weights_used else None,
                    )
                except Exception as e:
                    logger.warning(f"Failed to update evaluation in MongoDB: {e}")
            
            return {
                "success": True,
                "evaluation_id": evaluation_id,
                "selected_vendor": {
                    "vendor_id": selected.vendor_id,
                    "vendor_name": selected.vendor_name,
                    "price": selected_result.get("price") or selected_result.get("quoted_price"),
                    "eta": selected_result.get("eta"),
                    "call_id": selected_result.get("call_id"),
                    "final_score": selected.final_score,
                    "rank": selected.rank,
                    "scores": {
                        "quality": selected.scores.quality,
                        "affordability": selected.scores.affordability,
                        "shipping": selected.scores.shipping,
                        "reliability": selected.scores.reliability,
                    },
                },
                "reason": reason,
                "all_evaluated": [
                    {
                        "vendor_name": v.vendor_name,
                        "final_score": v.final_score,
                        "rank": v.rank,
                    }
                    for v in eval_response.selected_vendors
                ],
                "weights_used": eval_response.weights_used.model_dump() if eval_response.weights_used else None,
                "total_confirmed": len(confirmed_results),
            }
        else:
            logger.warning("Evaluation returned no vendors")
            
            # Fallback: pick best by price
            best = min(confirmed_results, key=lambda x: x.get("price") or 999)
            
            if STORAGE_ENABLED:
                try:
                    update_evaluation_status(
                        evaluation_id,
                        EvaluationStatus.COMPLETED,
                        selected_vendor_name=best.get("vendor_name"),
                        selection_reason="Fallback selection by lowest price",
                    )
                except Exception:
                    pass
            
            return {
                "success": True,
                "evaluation_id": evaluation_id,
                "selected_vendor": {
                    "vendor_name": best.get("vendor_name"),
                    "price": best.get("price"),
                    "eta": best.get("eta"),
                    "call_id": best.get("call_id"),
                },
                "reason": "Fallback selection by lowest price",
                "total_confirmed": len(confirmed_results),
            }
            
    except Exception as e:
        logger.exception(f"Evaluation failed: {e}")
        
        # Update status to failed
        if STORAGE_ENABLED:
            try:
                update_evaluation_status(evaluation_id, EvaluationStatus.FAILED)
            except Exception:
                pass
        
        # Fallback: pick by lowest price if any confirmed
        if confirmed_results:
            best = min(confirmed_results, key=lambda x: x.get("price") or 999)
            return {
                "success": True,
                "evaluation_id": evaluation_id,
                "selected_vendor": {
                    "vendor_name": best.get("vendor_name"),
                    "price": best.get("price"),
                    "eta": best.get("eta"),
                    "call_id": best.get("call_id"),
                },
                "reason": f"Fallback selection (eval error: {str(e)[:100]})",
                "total_confirmed": len(confirmed_results),
            }
        
        return {
            "success": False,
            "evaluation_id": evaluation_id,
            "selected_vendor": None,
            "reason": f"Evaluation failed: {str(e)}",
            "all_results": call_results,
        }
