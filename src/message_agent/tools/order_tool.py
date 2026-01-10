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
    on_status_update: Optional[StatusCallback] = None,
) -> dict:
    """
    Call a single vendor and track the call through completion.
    
    Returns dict with vendor info and call outcome.
    """
    order_id = f"order-{uuid.uuid4().hex[:8]}"
    
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
                "vendor_name": vendor.name,
                "vendor_index": vendor_index,
                "success": False,
                "error": call_result["error"],
                "outcome": None,
            }
        
        call_id = call_result["call_id"]
        logger.info(f"[Vendor {vendor_index + 1}] Call initiated: {call_id}")
        
        # Wait for call completion
        elapsed = 0
        timeout = 300
        poll_interval = 3
        
        while elapsed < timeout:
            status = await get_call_status(call_id)
            
            if status.get("error"):
                return {
                    "vendor_name": vendor.name,
                    "vendor_index": vendor_index,
                    "success": False,
                    "call_id": call_id,
                    "error": status["error"],
                    "outcome": None,
                }
            
            if status.get("status") == "ended":
                break
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        if elapsed >= timeout:
            return {
                "vendor_name": vendor.name,
                "vendor_index": vendor_index,
                "success": False,
                "call_id": call_id,
                "error": "Call timed out",
                "outcome": None,
            }
        
        # Parse outcome
        final_status = await get_call_status(call_id)
        transcript = final_status.get("transcript", "")
        ended_reason = final_status.get("ended_reason")
        
        logger.info(f"[Vendor {vendor_index + 1}] Call ended. Reason: {ended_reason}")
        logger.info(f"[Vendor {vendor_index + 1}] Transcript: {transcript[:300] if transcript else 'NO TRANSCRIPT'}")
        
        outcome = parse_call_outcome(transcript, ended_reason)
        logger.info(f"[Vendor {vendor_index + 1}] Outcome: confirmed={outcome.confirmed}, price={outcome.price}")
        
        return {
            "vendor_name": vendor.name,
            "vendor_index": vendor_index,
            "success": outcome.confirmed,
            "call_id": call_id,
            "price": outcome.price,
            "eta": outcome.eta,
            "outcome": outcome.model_dump(),
            "error": None,
        }
        
    except Exception as e:
        logger.exception(f"[Vendor {vendor_index + 1}] Error: {e}")
        return {
            "vendor_name": vendor.name,
            "vendor_index": vendor_index,
            "success": False,
            "error": str(e),
            "outcome": None,
        }


async def place_orders_parallel(
    product: str,
    quantity: int,
    unit: str = "dozen",
    business_name: str = "Acme Bakery",
    vendors: Optional[list[dict]] = None,
    on_status_update: Optional[StatusCallback] = None,
) -> dict:
    """
    Call up to 3 vendors in parallel and return all results.
    
    Uses hardcoded test phone numbers for all vendors.
    Each vendor gets a unique name/context for different conversations.
    
    Args:
        product: What to order
        quantity: How many units
        unit: Unit of measurement
        business_name: Business placing the order
        vendors: Optional list of vendor dicts from sourcing (names used for context)
        on_status_update: Callback for status messages
        
    Returns:
        dict with results from all vendor calls
    """
    async def send_update(message: str):
        if on_status_update:
            try:
                await on_status_update(message)
            except Exception as e:
                logger.error(f"Failed to send status update: {e}")
    
    # Build vendor list from sourcing results
    call_vendors = []
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
    
    vendor_names = [v.name for v in call_vendors]
    await send_update(f"📞 Calling {len(call_vendors)} vendors in parallel: {', '.join(vendor_names)}")
    
    logger.info(f"Starting parallel calls to {len(call_vendors)} vendors for {quantity} {unit} of {product}")
    
    # Create tasks for parallel execution
    tasks = [
        call_single_vendor(
            vendor=vendor,
            product=product,
            quantity=quantity,
            unit=unit,
            business_name=business_name,
            vendor_index=i,
            on_status_update=None,  # Don't spam updates during calls
        )
        for i, vendor in enumerate(call_vendors)
    ]
    
    # Run all calls in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    successful = []
    failed = []
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            failed.append({
                "vendor_name": call_vendors[i].name,
                "error": str(result),
            })
        elif result.get("success"):
            successful.append(result)
        else:
            failed.append(result)
    
    # Sort successful by price (lowest first)
    successful.sort(key=lambda x: x.get("price") or 999)
    
    # Build summary message
    if successful:
        best = successful[0]
        price_str = f"${best['price']}/{unit}" if best.get('price') else "price TBD"
        await send_update(
            f"✅ Got {len(successful)} confirmed! Best: {best['vendor_name']} at {price_str}"
        )
        if len(successful) > 1:
            others = ", ".join([s['vendor_name'] for s in successful[1:]])
            await send_update(f"Also confirmed: {others}")
    else:
        await send_update(f"❌ No vendors confirmed. {len(failed)} calls failed.")
    
    if failed:
        failed_names = ", ".join([f.get("vendor_name", "Unknown") for f in failed])
        logger.info(f"Failed calls: {failed_names}")
    
    return {
        "success": len(successful) > 0,
        "total_called": len(call_vendors),
        "confirmed_count": len(successful),
        "failed_count": len(failed),
        "best_vendor": successful[0] if successful else None,
        "all_confirmed": successful,
        "all_failed": failed,
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
