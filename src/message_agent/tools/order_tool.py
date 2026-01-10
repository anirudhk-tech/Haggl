"""Order tool - triggers the Calling Agent to place vendor orders."""

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

logger = logging.getLogger(__name__)

# Default vendor for testing
DEFAULT_TEST_VENDOR = VendorInfo(
    id="test-vendor-1",
    name="Local Farm Supply",
    phone="+15633965540",
    product="eggs",
    price_per_unit=4.50,
    unit="dozen",
)

# Type for status callback
StatusCallback = Callable[[str], Awaitable[None]]


async def place_order_with_updates(
    product: str,
    quantity: int,
    unit: str = "dozen",
    business_name: str = "My Business",
    vendor_phone: Optional[str] = None,
    on_status_update: Optional[StatusCallback] = None,
) -> dict:
    """
    Place an order with status updates at each stage.
    
    Sends updates via callback:
    1. "Calling vendor..." - when call initiates
    2. "Connected!" - when call connects
    3. "Call ended - result" - when call completes
    
    Args:
        product: What to order
        quantity: How many units
        unit: Unit of measurement
        business_name: Business placing the order
        vendor_phone: Override vendor phone for testing
        on_status_update: Async callback to send status messages
        
    Returns:
        dict with final order status
    """
    order_id = f"order-{uuid.uuid4().hex[:8]}"
    
    # Use test vendor, optionally override phone
    vendor = DEFAULT_TEST_VENDOR.model_copy()
    if vendor_phone:
        vendor.phone = vendor_phone
    vendor.product = product
    
    async def send_update(message: str):
        if on_status_update:
            try:
                await on_status_update(message)
            except Exception as e:
                logger.error(f"Failed to send status update: {e}")
    
    try:
        # Step 1: Initiate the call
        await send_update(f"📞 Calling vendor for {quantity} {unit} of {product}...")
        
        call_input = CallVendorInput(
            phone_number=vendor.phone,
            vendor_name=vendor.name,
            business_name=business_name,
            product=product,
            quantity=quantity,
            unit=unit,
        )
        
        call_result = await call_vendor(call_input)
        
        if call_result.get("error"):
            await send_update(f"❌ Couldn't reach vendor: {call_result['error']}")
            return {
                "success": False,
                "order_id": order_id,
                "status": "failed",
                "error": call_result["error"],
            }
        
        call_id = call_result["call_id"]
        logger.info(f"Call initiated: {call_id}")
        
        # Step 2: Wait for call to connect/progress
        connected_notified = False
        elapsed = 0
        timeout = 300
        poll_interval = 3
        
        while elapsed < timeout:
            status = await get_call_status(call_id)
            
            if status.get("error"):
                await send_update(f"❌ Call error: {status['error']}")
                return {
                    "success": False,
                    "order_id": order_id,
                    "call_id": call_id,
                    "status": "failed",
                    "error": status["error"],
                }
            
            call_status = status.get("status")
            
            # Notify when connected (only once)
            if call_status in ("in-progress", "ringing") and not connected_notified:
                await send_update("🔗 Connected! Negotiating with vendor...")
                connected_notified = True
            
            # Call ended
            if call_status == "ended":
                break
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        if elapsed >= timeout:
            await send_update("⏱️ Call timed out")
            return {
                "success": False,
                "order_id": order_id,
                "call_id": call_id,
                "status": "timeout",
                "error": "Call timed out",
            }
        
        # Step 3: Parse outcome and send final update
        final_status = await get_call_status(call_id)
        transcript = final_status.get("transcript", "")
        ended_reason = final_status.get("ended_reason")
        
        logger.info(f"Call ended. Reason: {ended_reason}")
        logger.info(f"Transcript: {transcript[:500] if transcript else 'NO TRANSCRIPT'}")
        
        outcome = parse_call_outcome(transcript, ended_reason)
        logger.info(f"Parsed outcome: confirmed={outcome.confirmed}, price={outcome.price}, notes={outcome.notes}")
        
        if outcome.confirmed:
            price_info = f" at ${outcome.price}/{unit}" if outcome.price else ""
            eta_info = f" - {outcome.eta}" if outcome.eta else ""
            await send_update(f"✅ Order confirmed! {quantity} {unit} of {product}{price_info}{eta_info}")
        else:
            await send_update(f"❌ Order not confirmed. {outcome.notes or 'Vendor unavailable.'}")
        
        return {
            "success": outcome.confirmed,
            "order_id": order_id,
            "call_id": call_id,
            "status": "confirmed" if outcome.confirmed else "failed",
            "outcome": outcome.model_dump(),
            "error": None if outcome.confirmed else "Order not confirmed",
        }
        
    except Exception as e:
        logger.exception(f"Failed to place order: {e}")
        await send_update(f"❌ Something went wrong: {str(e)}")
        return {
            "success": False,
            "order_id": order_id,
            "status": "failed",
            "error": str(e),
        }


# Simple version for OpenAI function calling (no callbacks)
async def place_order(
    product: str,
    quantity: int,
    unit: str = "dozen",
    business_name: str = "My Business",
    vendor_phone: Optional[str] = None,
) -> dict:
    """Simple place_order without status callbacks (for backward compat)."""
    return await place_order_with_updates(
        product=product,
        quantity=quantity,
        unit=unit,
        business_name=business_name,
        vendor_phone=vendor_phone,
        on_status_update=None,
    )


# OpenAI function schema for place_order
PLACE_ORDER_FUNCTION = {
    "type": "function",
    "function": {
        "name": "place_order",
        "description": "Place an order for ingredients by calling a vendor. Use this when the user wants to order something like eggs, flour, produce, etc.",
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
