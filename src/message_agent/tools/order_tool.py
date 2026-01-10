"""Order tool - triggers the Calling Agent to place vendor orders."""

import os
import logging
import uuid
import asyncio
from typing import Optional, Callable, Awaitable

from calling_agent.schemas import (
    AgentRequest,
    OrderContext,
    VendorInfo,
    CallVendorInput,
)
from calling_agent.tools.vapi_tool import (
    call_vendor,
    get_call_status,
    parse_call_outcome,
)

# Storage imports
try:
    from storage.orders import create_order, update_order_status, add_vendor_to_order
    from storage.calls import create_call, update_call_status
    from storage.schemas import OrderStatus, CallStatus, CallOutcomeDocument
    STORAGE_ENABLED = True
except ImportError:
    STORAGE_ENABLED = False

# Evaluation imports
try:
    from .evaluation_tool import evaluate_vendor_calls
    EVAL_ENABLED = True
except ImportError:
    EVAL_ENABLED = False

# Event streaming imports
try:
    from events import (
        emit_stage_change,
        emit_log,
        emit_call_update,
        emit_evaluation_update,
        emit_approval_required,
        AgentStage,
    )
    EVENTS_ENABLED = True
except ImportError:
    EVENTS_ENABLED = False

logger = logging.getLogger(__name__)

# Configuration
CALL_ONE_VENDOR = os.getenv("CALL_ONE_VENDOR", "false").lower() == "true"
PRIMARY_TEST_PHONE = "+15633965540"

# Hardcoded test phone numbers for parallel vendor calls
TEST_VENDOR_PHONES = [
    "+15633965540",  # Vendor 1
    "+17203154946",  # Vendor 2
    "+15128508061",  # Vendor 3
]

# Fallback vendor names if sourcing returns nothing (unlikely)
FALLBACK_VENDOR_NAMES = ["Vendor A", "Vendor B", "Vendor C"]

# Type for status callback
StatusCallback = Callable[[str], Awaitable[None]]


async def call_single_vendor(
    vendor: VendorInfo,
    product: str,
    quantity: int,
    unit: str,
    business_name: str,
    vendor_index: int,
    order_id: str,
    vendor_metadata: Optional[dict] = None,
    on_status_update: Optional[StatusCallback] = None,
) -> dict:
    """
    Call a single vendor and track the call through completion.
    
    Args:
        vendor: VendorInfo with contact details
        product: Product to order
        quantity: Quantity needed
        unit: Unit of measurement
        business_name: Ordering business
        vendor_index: Index for logging
        order_id: Order ID for tracking
        vendor_metadata: Additional vendor data (quality_score, reliability_score, etc.)
        on_status_update: Optional callback for status updates
    
    Returns dict with vendor info, call outcome, and metadata for evaluation.
    """
    metadata = vendor_metadata or {}
    
    async def send_update(message: str):
        if on_status_update:
            try:
                await on_status_update(message)
            except Exception as e:
                logger.error(f"Failed to send status update: {e}")
    
    try:
        call_input = CallVendorInput(
            phone_number=vendor.phone,
            vendor_name=vendor.name,
            business_name=business_name,
            product=product,
            quantity=quantity,
            unit=unit,
        )
        
        logger.info(f"[Vendor {vendor_index + 1}] Calling {vendor.name} at {vendor.phone}")
        call_result = await call_vendor(call_input)
        
        if call_result.get("error"):
            logger.error(f"[Vendor {vendor_index + 1}] Failed to initiate: {call_result['error']}")
            return {
                "vendor_id": vendor.id,
                "vendor_name": vendor.name,
                "vendor_index": vendor_index,
                "success": False,
                "error": call_result["error"],
                "outcome": None,
                # Include metadata for evaluation even on failure
                "quality_score": metadata.get("quality_score", 50.0),
                "reliability_score": metadata.get("reliability_score", 50.0),
                "distance_miles": metadata.get("distance_miles", 0.0),
                "certifications": metadata.get("certifications", []),
            }
        
        call_id = call_result["call_id"]
        logger.info(f"[Vendor {vendor_index + 1}] Call initiated: {call_id}")
        
        # Save call to MongoDB
        if STORAGE_ENABLED:
            try:
                create_call(
                    call_id=call_id,
                    order_id=order_id,
                    vendor_id=vendor.id,
                    vendor_name=vendor.name,
                    vendor_phone=vendor.phone
                )
            except Exception as e:
                logger.warning(f"Failed to save call to MongoDB: {e}")
        
        # Wait for call completion
        elapsed = 0
        timeout = 300
        poll_interval = 3
        
        while elapsed < timeout:
            status = await get_call_status(call_id)
            
            if status.get("error"):
                # Update call status in MongoDB
                if STORAGE_ENABLED:
                    try:
                        update_call_status(call_id, CallStatus.FAILED)
                    except Exception:
                        pass
                return {
                    "vendor_id": vendor.id,
                    "vendor_name": vendor.name,
                    "vendor_index": vendor_index,
                    "success": False,
                    "call_id": call_id,
                    "error": status["error"],
                    "outcome": None,
                    "quality_score": metadata.get("quality_score", 50.0),
                    "reliability_score": metadata.get("reliability_score", 50.0),
                    "distance_miles": metadata.get("distance_miles", 0.0),
                    "certifications": metadata.get("certifications", []),
                }
            
            if status.get("status") == "ended":
                break
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        if elapsed >= timeout:
            if STORAGE_ENABLED:
                try:
                    update_call_status(call_id, CallStatus.FAILED, ended_reason="timeout")
                except Exception:
                    pass
            return {
                "vendor_id": vendor.id,
                "vendor_name": vendor.name,
                "vendor_index": vendor_index,
                "success": False,
                "call_id": call_id,
                "error": "Call timed out",
                "outcome": None,
                "quality_score": metadata.get("quality_score", 50.0),
                "reliability_score": metadata.get("reliability_score", 50.0),
                "distance_miles": metadata.get("distance_miles", 0.0),
                "certifications": metadata.get("certifications", []),
            }
        
        # Parse outcome
        final_status = await get_call_status(call_id)
        transcript = final_status.get("transcript", "")
        ended_reason = final_status.get("ended_reason")
        duration = final_status.get("duration")
        
        logger.info(f"[Vendor {vendor_index + 1}] Call ended. Reason: {ended_reason}")
        logger.info(f"[Vendor {vendor_index + 1}] Transcript: {transcript[:300] if transcript else 'NO TRANSCRIPT'}")
        
        outcome = parse_call_outcome(transcript, ended_reason)
        logger.info(f"[Vendor {vendor_index + 1}] Outcome: confirmed={outcome.confirmed}, price={outcome.price}")
        
        # Update call in MongoDB with outcome
        if STORAGE_ENABLED:
            try:
                update_call_status(
                    call_id=call_id,
                    status=CallStatus.ENDED,
                    ended_reason=ended_reason,
                    duration_seconds=duration,
                    outcome=CallOutcomeDocument(
                        confirmed=outcome.confirmed,
                        price=outcome.price,
                        eta=outcome.eta,
                        notes=outcome.notes,
                        transcript=transcript[:1000] if transcript else None,  # Limit transcript size
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to update call in MongoDB: {e}")
        
        return {
            "vendor_id": vendor.id,
            "vendor_name": vendor.name,
            "vendor_index": vendor_index,
            "success": outcome.confirmed,
            "call_id": call_id,
            "price": outcome.price,
            "eta": outcome.eta,
            "outcome": outcome.model_dump(),
            "error": None,
            # Include metadata for evaluation
            "quality_score": metadata.get("quality_score", 50.0),
            "reliability_score": metadata.get("reliability_score", 50.0),
            "distance_miles": metadata.get("distance_miles", 0.0),
            "price_per_unit": outcome.price or metadata.get("price_per_unit"),
            "unit": unit,
            "certifications": metadata.get("certifications", []),
        }
        
    except Exception as e:
        logger.exception(f"[Vendor {vendor_index + 1}] Error: {e}")
        return {
            "vendor_id": vendor.id,
            "vendor_name": vendor.name,
            "vendor_index": vendor_index,
            "success": False,
            "error": str(e),
            "outcome": None,
            "quality_score": metadata.get("quality_score", 50.0),
            "reliability_score": metadata.get("reliability_score", 50.0),
            "distance_miles": metadata.get("distance_miles", 0.0),
            "certifications": metadata.get("certifications", []),
        }


async def place_orders_parallel(
    product: str,
    quantity: int,
    unit: str = "dozen",
    business_name: str = "Acme Bakery",
    vendors: Optional[list[dict]] = None,
    phone_number: Optional[str] = None,
    on_status_update: Optional[StatusCallback] = None,
) -> dict:
    """
    Call up to 3 vendors in parallel, then evaluate to pick best vendor.
    
    Uses hardcoded test phone numbers for all vendors.
    Each vendor gets a unique name/context for different conversations.
    After all calls complete, uses the Evaluation Agent to pick the best vendor.
    
    Args:
        product: What to order
        quantity: How many units
        unit: Unit of measurement
        business_name: Business placing the order
        vendors: Optional list of vendor dicts from sourcing (names used for context)
        phone_number: Customer phone number (for order tracking)
        on_status_update: Callback for status messages
        
    Returns:
        dict with evaluation result including selected vendor
    """
    # Generate order ID
    order_id = f"order-{uuid.uuid4().hex[:8]}"
    
    # Emit: Order created
    if EVENTS_ENABLED:
        await emit_stage_change(
            AgentStage.MESSAGE_RECEIVED,
            f"New order received: {quantity} {unit} of {product}",
            order_id=order_id,
            product=product,
            quantity=quantity,
            unit=unit,
        )
    
    # Create order in MongoDB
    if STORAGE_ENABLED and phone_number:
        try:
            create_order(
                order_id=order_id,
                phone_number=phone_number,
                product=product,
                quantity=quantity,
                unit=unit
            )
            update_order_status(order_id, OrderStatus.CALLING)
            logger.info(f"Created order in MongoDB: {order_id}")
        except Exception as e:
            logger.warning(f"Failed to create order in MongoDB: {e}")
    
    async def send_update(message: str):
        if on_status_update:
            try:
                await on_status_update(message)
            except Exception as e:
                logger.error(f"Failed to send status update: {e}")
    
    # Build vendor list from sourcing results with metadata for evaluation
    call_vendors = []
    vendor_metadata_list = []
    
    if vendors and len(vendors) > 0:
        # Use vendors from sourcing (already have test phone numbers assigned)
        for i, v in enumerate(vendors[:3]):  # Max 3 vendors
            call_vendors.append(VendorInfo(
                id=f"vendor-{i+1}",
                name=v.get("name", f"Vendor {i+1}"),
                phone=v.get("phone", TEST_VENDOR_PHONES[i]),  # Use phone from sourcing (already test number)
                product=product,
                price_per_unit=v.get("price_per_unit") or 4.00,
                unit=unit,
            ))
            # Store metadata for evaluation
            vendor_metadata_list.append({
                "quality_score": v.get("quality_score", 50.0),
                "reliability_score": v.get("reliability_score", 50.0),
                "distance_miles": v.get("distance_miles", 0.0),
                "price_per_unit": v.get("price_per_unit"),
                "certifications": v.get("certifications", []),
                "rating": v.get("rating"),
            })
    else:
        # Fallback: create generic vendors if sourcing returned nothing
        for i, name in enumerate(FALLBACK_VENDOR_NAMES):
            call_vendors.append(VendorInfo(
                id=f"vendor-{i+1}",
                name=name,
                phone=TEST_VENDOR_PHONES[i],
                product=product,
                price_per_unit=4.00,
                unit=unit,
            ))
            vendor_metadata_list.append({
                "quality_score": 50.0,
                "reliability_score": 50.0,
                "distance_miles": 0.0,
                "certifications": [],
            })
    
    # CALL_ONE_VENDOR mode: only call first vendor with primary test phone
    if CALL_ONE_VENDOR:
        logger.info("CALL_ONE_VENDOR=true - limiting to single vendor call")
        call_vendors = [call_vendors[0]]
        vendor_metadata_list = [vendor_metadata_list[0]]
        call_vendors[0].phone = PRIMARY_TEST_PHONE
    
    vendor_names = [v.name for v in call_vendors]
    num_vendors = len(call_vendors)
    
    if num_vendors == 1:
        await send_update(f"📞 Calling vendor: {vendor_names[0]}")
    else:
        await send_update(f"📞 Calling {num_vendors} vendors in parallel: {', '.join(vendor_names)}")
    
    logger.info(f"Starting parallel calls to {len(call_vendors)} vendors for {quantity} {unit} of {product}")
    
    # Emit: Calling/Negotiating stage
    if EVENTS_ENABLED:
        await emit_stage_change(
            AgentStage.CALLING,
            f"Calling {num_vendors} vendors: {', '.join(vendor_names)}",
            order_id=order_id,
            vendors=vendor_names,
        )
        for v in call_vendors:
            await emit_call_update(
                AgentStage.NEGOTIATING,
                f"Dialing {v.name}...",
                order_id=order_id,
                vendor_name=v.name,
                call_status="dialing",
            )
    
    # Create tasks for parallel execution with metadata
    tasks = [
        call_single_vendor(
            vendor=vendor,
            product=product,
            quantity=quantity,
            unit=unit,
            business_name=business_name,
            vendor_index=i,
            order_id=order_id,
            vendor_metadata=vendor_metadata_list[i],
            on_status_update=None,  # Don't spam updates during calls
        )
        for i, vendor in enumerate(call_vendors)
    ]
    
    # Run all calls in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    all_results = []
    successful = []
    failed = []
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            failed_result = {
                "vendor_id": call_vendors[i].id,
                "vendor_name": call_vendors[i].name,
                "success": False,
                "error": str(result),
                **vendor_metadata_list[i],
            }
            failed.append(failed_result)
            all_results.append(failed_result)
        elif result.get("success"):
            successful.append(result)
            all_results.append(result)
        else:
            failed.append(result)
            all_results.append(result)
    
    logger.info(f"Calls complete: {len(successful)} confirmed, {len(failed)} failed")
    
    # Emit: Calls complete updates
    if EVENTS_ENABLED:
        for r in successful:
            await emit_call_update(
                AgentStage.NEGOTIATING,
                f"✓ {r.get('vendor_name')} confirmed at ${r.get('price', 'TBD')}/{unit}",
                order_id=order_id,
                vendor_name=r.get("vendor_name", "Unknown"),
                call_status="confirmed",
                price=r.get("price"),
            )
        for r in failed:
            await emit_call_update(
                AgentStage.NEGOTIATING,
                f"✗ {r.get('vendor_name')} - {r.get('error', 'no answer')}",
                order_id=order_id,
                vendor_name=r.get("vendor_name", "Unknown"),
                call_status="failed",
            )
    
    # === EVALUATION STEP ===
    # Don't send confirmation yet - first evaluate to pick best vendor
    
    if not successful:
        await send_update(f"❌ No vendors confirmed. {len(failed)} calls failed.")
        
        # Update order status in MongoDB
        if STORAGE_ENABLED:
            try:
                update_order_status(order_id, OrderStatus.FAILED)
            except Exception as e:
                logger.warning(f"Failed to update order status: {e}")
        
        return {
            "success": False,
            "order_id": order_id,
            "total_called": len(call_vendors),
            "confirmed_count": 0,
            "failed_count": len(failed),
            "selected_vendor": None,
            "evaluation": None,
            "all_results": all_results,
            "product": product,
            "quantity": quantity,
            "unit": unit,
        }
    
    # Notify user that we're evaluating
    await send_update(f"🔍 Got {len(successful)} confirmed! Evaluating best option...")
    
    # Emit: Evaluating stage
    if EVENTS_ENABLED:
        await emit_stage_change(
            AgentStage.EVALUATING,
            f"Evaluating {len(successful)} confirmed vendors...",
            order_id=order_id,
            confirmed_count=len(successful),
        )
    
    # Run evaluation to pick best vendor
    if EVAL_ENABLED and len(successful) > 0:
        logger.info(f"Running evaluation on {len(successful)} confirmed vendors")
        
        eval_result = await evaluate_vendor_calls(
            order_id=order_id,
            call_results=all_results,
            product=product,
            business_id=business_name.lower().replace(" ", "_"),
        )
        
        if eval_result.get("success") and eval_result.get("selected_vendor"):
            selected = eval_result["selected_vendor"]
            
            # Send final confirmation with evaluation result
            price_str = f"${selected.get('price')}/{unit}" if selected.get('price') else "price TBD"
            eta_str = f" (ETA: {selected.get('eta')})" if selected.get('eta') else ""
            
            await send_update(
                f"✅ CONFIRMED: {selected['vendor_name']} at {price_str}{eta_str}"
            )
            
            if len(successful) > 1:
                reason = eval_result.get("reason", "Best overall score")
                await send_update(f"📊 Selected based on: {reason[:100]}")
            
            # Emit: Evaluation complete + Approval pending
            if EVENTS_ENABLED:
                await emit_evaluation_update(
                    AgentStage.EVALUATING,
                    f"Selected: {selected['vendor_name']} (score: {selected.get('final_score', 0):.1f})",
                    order_id=order_id,
                    selected_vendor=selected['vendor_name'],
                    scores=selected.get('scores'),
                )
                await emit_approval_required(
                    order_id=order_id,
                    vendor_name=selected['vendor_name'],
                    price=selected.get('price') or 0,
                    product=product,
                    quantity=quantity,
                    unit=unit,
                )
            
            # Update order status in MongoDB with evaluated selection
            if STORAGE_ENABLED:
                try:
                    update_order_status(
                        order_id,
                        OrderStatus.CONFIRMED,
                        vendor_confirmed=selected.get("vendor_name"),
                        confirmed_price=selected.get("price"),
                        confirmed_eta=selected.get("eta"),
                    )
                except Exception as e:
                    logger.warning(f"Failed to update order status: {e}")
            
            return {
                "success": True,
                "order_id": order_id,
                "total_called": len(call_vendors),
                "confirmed_count": len(successful),
                "failed_count": len(failed),
                "selected_vendor": selected,
                "evaluation": eval_result,
                "all_confirmed": successful,
                "all_failed": failed,
                "all_results": all_results,
                "product": product,
                "quantity": quantity,
                "unit": unit,
            }
    
    # Fallback: if evaluation not available or failed, pick by lowest price
    logger.warning("Evaluation not available, falling back to price-based selection")
    successful.sort(key=lambda x: x.get("price") or 999)
    best = successful[0]
    
    price_str = f"${best['price']}/{unit}" if best.get('price') else "price TBD"
    await send_update(
        f"✅ CONFIRMED: {best['vendor_name']} at {price_str} (lowest price)"
    )
    
    # Update order status in MongoDB
    if STORAGE_ENABLED:
        try:
            update_order_status(
                order_id,
                OrderStatus.CONFIRMED,
                vendor_confirmed=best.get("vendor_name"),
                confirmed_price=best.get("price"),
                confirmed_eta=best.get("eta"),
            )
        except Exception as e:
            logger.warning(f"Failed to update order status: {e}")
    
    return {
        "success": True,
        "order_id": order_id,
        "total_called": len(call_vendors),
        "confirmed_count": len(successful),
        "failed_count": len(failed),
        "selected_vendor": {
            "vendor_name": best.get("vendor_name"),
            "price": best.get("price"),
            "eta": best.get("eta"),
            "call_id": best.get("call_id"),
        },
        "evaluation": {"reason": "Fallback: lowest price"},
        "all_confirmed": successful,
        "all_failed": failed,
        "all_results": all_results,
        "product": product,
        "quantity": quantity,
        "unit": unit,
    }


# Legacy single-vendor function (for backward compat)
async def place_order_with_updates(
    product: str,
    quantity: int,
    unit: str = "dozen",
    business_name: str = "My Business",
    vendor_phone: Optional[str] = None,
    on_status_update: Optional[StatusCallback] = None,
) -> dict:
    """Place order with single vendor (legacy)."""
    # Use the new parallel function with just the first vendor
    return await place_orders_parallel(
        product=product,
        quantity=quantity,
        unit=unit,
        business_name=business_name,
        vendors=None,  # Use defaults
        on_status_update=on_status_update,
    )


# Simple version for OpenAI function calling (no callbacks)
async def place_order(
    product: str,
    quantity: int,
    unit: str = "dozen",
    business_name: str = "My Business",
    vendor_phone: Optional[str] = None,
) -> dict:
    """Simple place_order without status callbacks."""
    return await place_orders_parallel(
        product=product,
        quantity=quantity,
        unit=unit,
        business_name=business_name,
        vendors=None,
        on_status_update=None,
    )


# OpenAI function schema for place_order
PLACE_ORDER_FUNCTION = {
    "type": "function",
    "function": {
        "name": "place_order",
        "description": "Place an order for ingredients by calling multiple vendors in parallel. Calls up to 3 vendors simultaneously to get the best price. Use this when the user confirms they want to order.",
        "parameters": {
            "type": "object",
            "properties": {
                "product": {
                    "type": "string",
                    "description": "The product to order (e.g., 'eggs', 'flour', 'milk')",
                },
                "quantity": {
                    "type": "integer",
                    "description": "How many units to order",
                },
                "unit": {
                    "type": "string",
                    "description": "Unit of measurement (e.g., 'dozen', 'pounds', 'gallons')",
                    "default": "dozen",
                },
            },
            "required": ["product", "quantity"],
        },
    },
}
