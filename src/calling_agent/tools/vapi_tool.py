"""Vapi tool for the Calling Agent."""

import os
import json
import httpx
import asyncio
from typing import Optional

from ..schemas import CallVendorInput, CallOutcome

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
VAPI_BASE_URL = "https://api.vapi.ai"


def get_system_prompt(business_name: str, product: str, quantity: int, unit: str) -> str:
    """Generate the system prompt for the AI caller."""
    return f"""You are a professional procurement agent calling on behalf of {business_name}, a local bakery.

YOUR GOALS:
1. Confirm that the vendor has {quantity} {unit} of {product} available
2. Ask for their current price per {unit}
3. If the price seems reasonable, confirm the order
4. Get an estimated delivery or pickup time
5. Thank them and confirm the order details

CONVERSATION GUIDELINES:
- Keep responses concise (1-2 sentences)
- Be professional and friendly
- If they offer a price, you can ask "Is there any bulk discount for an order this size?"
- Accept reasonable prices - don't haggle excessively

BEFORE ENDING, CONFIRM:
- Total quantity: {quantity} {unit}
- Price per {unit}
- Pickup/delivery time

If they cannot fulfill the order, thank them politely and end the call."""


async def call_vendor(input_data: CallVendorInput) -> dict:
    """
    Make an outbound call to a vendor via Vapi.
    
    This is the main tool exposed to the NAT agent.
    """
    if not VAPI_API_KEY:
        return {"error": "VAPI_API_KEY not configured", "call_id": None}
    
    if not VAPI_PHONE_NUMBER_ID:
        return {"error": "VAPI_PHONE_NUMBER_ID not configured", "call_id": None}
    
    first_message = (
        f"Hi, I'm calling on behalf of {input_data.business_name}. "
        f"We're looking to place an order for {input_data.quantity} {input_data.unit} "
        f"of {input_data.product} and wanted to discuss pricing."
    )
    
    system_prompt = get_system_prompt(
        input_data.business_name,
        input_data.product,
        input_data.quantity,
        input_data.unit
    )
    
    payload = {
        "phoneNumberId": VAPI_PHONE_NUMBER_ID,
        "customer": {
            "number": input_data.phone_number,
        },
        "assistant": {
            "firstMessage": first_message,
            "model": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt,
                    }
                ],
            },
            "voice": {
                "provider": "openai",
                "voiceId": "alloy",
            },
        },
        "metadata": {
            "business_name": input_data.business_name,
            "product": input_data.product,
            "quantity": str(input_data.quantity),
        },
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{VAPI_BASE_URL}/call",
                headers={
                    "Authorization": f"Bearer {VAPI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30.0,
            )
            
            if response.status_code != 201:
                return {
                    "error": f"Vapi API error: {response.status_code} - {response.text}",
                    "call_id": None,
                }
            
            call_data = response.json()
            return {
                "call_id": call_data.get("id"),
                "status": "call_initiated",
                "vendor_name": input_data.vendor_name,
                "error": None,
            }
            
        except Exception as e:
            return {"error": str(e), "call_id": None}


async def get_call_status(call_id: str) -> dict:
    """Get the status and transcript of a Vapi call."""
    if not VAPI_API_KEY:
        return {"error": "VAPI_API_KEY not configured"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{VAPI_BASE_URL}/call/{call_id}",
                headers={"Authorization": f"Bearer {VAPI_API_KEY}"},
                timeout=30.0,
            )
            
            if response.status_code != 200:
                return {"error": f"Vapi API error: {response.status_code}"}
            
            call_data = response.json()
            return {
                "call_id": call_id,
                "status": call_data.get("status"),
                "ended_reason": call_data.get("endedReason"),
                "transcript": call_data.get("transcript", ""),
                "duration": call_data.get("duration"),
                "recording_url": call_data.get("recordingUrl"),
            }
            
        except Exception as e:
            return {"error": str(e)}


async def wait_for_call_completion(call_id: str, timeout: int = 300, poll_interval: int = 3) -> dict:
    """Wait for a call to complete and return the final status."""
    elapsed = 0
    
    while elapsed < timeout:
        status = await get_call_status(call_id)
        
        if status.get("error"):
            return status
        
        call_status = status.get("status")
        
        if call_status == "ended":
            return status
        
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval
    
    return {"error": "Call timed out", "call_id": call_id}


def parse_call_outcome(transcript: str, ended_reason: Optional[str] = None) -> CallOutcome:
    """
    Parse the call transcript to extract structured outcome.
    
    Extracts: confirmed, price, eta
    """
    if not transcript:
        return CallOutcome(
            confirmed=False,
            notes=f"No transcript available. Ended reason: {ended_reason or 'unknown'}",
        )
    
    lower_transcript = transcript.lower()
    
    # Check for confirmation keywords
    confirmation_keywords = [
        "confirm", "confirmed", "order placed", "sounds good", "perfect",
        "we can do that", "yes we have", "available", "got it"
    ]
    confirmed = any(kw in lower_transcript for kw in confirmation_keywords)
    
    # Check for rejection keywords
    rejection_keywords = [
        "sorry", "can't", "cannot", "don't have", "out of stock",
        "not available", "unable"
    ]
    if any(kw in lower_transcript for kw in rejection_keywords):
        confirmed = False
    
    # Extract price (patterns like "$X.XX per dozen" or "X dollars")
    price = None
    import re
    
    price_patterns = [
        r'\$(\d+\.?\d*)\s*(?:per|a|each)',
        r'(\d+\.?\d*)\s*(?:dollars?|cents?)\s*(?:per|a|each)',
        r'price\s*(?:is|of)?\s*\$?(\d+\.?\d*)',
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, lower_transcript)
        if match:
            try:
                price = float(match.group(1))
                # If it's cents, convert to dollars
                if 'cent' in lower_transcript[match.start():match.end()+10]:
                    price = price / 100
                break
            except ValueError:
                pass
    
    # Extract ETA/delivery time
    eta = None
    eta_patterns = [
        r'(?:ready|available|deliver|pick\s*up).*?(?:in\s+)?(\d+\s*(?:hour|minute|day)s?)',
        r'(tomorrow|today|this\s+afternoon|this\s+morning)',
        r'(?:by|around|at)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)',
    ]
    
    for pattern in eta_patterns:
        match = re.search(pattern, lower_transcript, re.IGNORECASE)
        if match:
            eta = match.group(1) if match.group(1) else match.group(0)
            break
    
    return CallOutcome(
        confirmed=confirmed,
        price=price,
        eta=eta,
        notes="Order confirmed via phone call" if confirmed else "Order not confirmed",
        transcript=transcript,
    )


async def call_vendor_and_wait(input_data: CallVendorInput) -> dict:
    """
    Complete flow: make call, wait for completion, parse outcome.
    
    This is the main function used by the agent.
    """
    # Step 1: Initiate the call
    call_result = await call_vendor(input_data)
    
    if call_result.get("error"):
        return {
            "success": False,
            "error": call_result["error"],
            "outcome": None,
        }
    
    call_id = call_result["call_id"]
    
    # Step 2: Wait for call to complete
    final_status = await wait_for_call_completion(call_id)
    
    if final_status.get("error"):
        return {
            "success": False,
            "call_id": call_id,
            "error": final_status["error"],
            "outcome": None,
        }
    
    # Step 3: Parse the outcome
    outcome = parse_call_outcome(
        final_status.get("transcript", ""),
        final_status.get("ended_reason"),
    )
    
    return {
        "success": True,
        "call_id": call_id,
        "outcome": outcome.model_dump(),
        "error": None,
    }
