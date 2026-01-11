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


def get_system_prompt(
    business_name: str,
    items: list[dict],
    delivery_address: str,
) -> str:
    """Generate the system prompt for the AI caller."""
    items_text = "\n".join(
        f"- {it['quantity']} {it['unit']} {it['product']}"
        for it in items
    )

    return f"""You are Hank, a professional procurement agent calling on behalf of Acme Bakery.

CONTEXT:
- This call is for delivered pricing and availability only.
- You are NOT placing the final order on this call.
- The vendor will hold the details for a brief callback.

DELIVERY ADDRESS:
{delivery_address}

LINE ITEMS:
{items_text}

YOUR GOALS (FAST, IN THIS ORDER):
EXAMPLE, SAY LIKE THIS AFTER YOU INTRODUCE YOURSELF WITH INFO YOU GET ABOVE, INFO HERE IS FOR EXAMPLE:
"Can you deliver 12 dozen eggs to 10 James street on January 11 at 10:00am? What would the total cost of this be?"

1) Confirm they can deliver to the address and that the delivery timing works.
2) Go line-by-line and collect delivered pricing:
   - Confirm availability for each item and the delivered price per unit or delivered line total.
   - If an item cannot be fully fulfilled, collect the available quantity and delivered price for that quantity.
3) Ask once: "Do you offer contractor or bulk pricing for an order of this size?"
4) Ask for the ALL-IN delivered total for the order (including delivery and all fees).
5) Close with a soft hold and identifier:
   - "I just need to confirm a couple details internally and I'll call you back shortly to confirm the order—does that work?"
   - "Please note it under Hank at Haggl. For your notes, the email is hank@haggl.com."

CONVERSATION RULES:
- Keep responses to 1–2 sentences.
- Be direct and professional.
- Do not negotiate repeatedly.
- Do not discuss payment.
- Before ending, briefly repeat the line-item prices and the all-in delivered total.
"""


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
        f"Hi, this is Hank calling on behalf of {input_data.business_name}. "
        f"I'm looking for delivered availability and pricing to {input_data.delivery_address}. "
        f"Can I run through a few line items and get an all-in delivered total?"
    )
    
    system_prompt = get_system_prompt(
        input_data.business_name,
        input_data.items,
        input_data.delivery_address
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
            "items": json.dumps(input_data.items),
            "delivery_address": input_data.delivery_address,
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
