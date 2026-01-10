"""
Haggl Agent Server

Main FastAPI server that exposes all agents as HTTP endpoints.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Calling Agent imports
from calling_agent import get_agent
from calling_agent.schemas import (
    AgentRequest,
    AgentState,
    OrderContext,
    VendorInfo,
)

# Message Agent imports
from message_agent import get_message_agent
from message_agent.schemas import IncomingSMS

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Haggl Agent server...")
    yield
    logger.info("Shutting down Haggl Agent server...")


app = FastAPI(
    title="Haggl Agent Server",
    description="Multi-agent server for voice calling and SMS messaging",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        os.getenv("NEXT_PUBLIC_APP_URL", "http://localhost:3000"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Shared Models
# =============================================================================

class PlaceOrderRequest(BaseModel):
    """Request to place an order via the calling agent."""
    order_id: str
    business_name: str
    business_type: str
    quantity: int
    vendor_id: str
    vendor_name: str
    vendor_phone: str
    price_per_unit: float


class OrderStatusResponse(BaseModel):
    """Response with order status."""
    order_id: str
    status: str
    call_id: Optional[str] = None
    confirmed: Optional[bool] = None
    price: Optional[float] = None
    total_price: Optional[float] = None
    eta: Optional[str] = None
    transcript: Optional[str] = None
    error: Optional[str] = None


# =============================================================================
# Health Check
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Haggl Agent Server",
        "version": "0.1.0",
        "agents": ["calling_agent", "message_agent"],
    }


# =============================================================================
# Calling Agent Routes
# =============================================================================

@app.post("/calling/order", response_model=OrderStatusResponse)
async def place_order(request: PlaceOrderRequest):
    """
    Place an order using the calling agent.
    
    This endpoint orchestrates:
    1. Initiating the Vapi call
    2. Waiting for completion
    3. Parsing the outcome
    4. Returning structured results
    """
    logger.info(f"Received order request: {request.order_id}")
    
    # Build the agent request
    agent_request = AgentRequest(
        order_id=request.order_id,
        order_context=OrderContext(
            business_name=request.business_name,
            business_type=request.business_type,
            product="eggs",
            quantity=request.quantity,
            unit="dozen",
        ),
        vendor=VendorInfo(
            id=request.vendor_id,
            name=request.vendor_name,
            phone=request.vendor_phone,
            product="eggs",
            price_per_unit=request.price_per_unit,
            unit="dozen",
        ),
    )
    
    # Get the agent and process the order
    agent = get_agent()
    
    try:
        response = await agent.process_order(agent_request)
        
        # Calculate total price if we have outcome with price
        total_price = None
        if response.outcome and response.outcome.price:
            total_price = response.outcome.price * request.quantity
        elif response.status == AgentState.PLACED:
            # Use vendor's price if no negotiated price
            total_price = request.price_per_unit * request.quantity
        
        return OrderStatusResponse(
            order_id=response.order_id,
            status=response.status.value,
            call_id=response.call_id,
            confirmed=response.outcome.confirmed if response.outcome else False,
            price=response.outcome.price if response.outcome else None,
            total_price=total_price,
            eta=response.outcome.eta if response.outcome else None,
            transcript=response.outcome.transcript if response.outcome else None,
            error=response.error,
        )
        
    except Exception as e:
        logger.exception(f"Error processing order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/calling/status/{order_id}", response_model=OrderStatusResponse)
async def get_order_status(order_id: str):
    """Get the status of an order."""
    agent = get_agent()
    
    # Check if we have this order in history
    if order_id in agent._call_history:
        cached = agent._call_history[order_id]
        outcome = cached.get("outcome")
        
        return OrderStatusResponse(
            order_id=order_id,
            status=cached["status"].value if isinstance(cached["status"], AgentState) else cached["status"],
            call_id=cached.get("call_id"),
            confirmed=outcome.confirmed if outcome else False,
            price=outcome.price if outcome else None,
            eta=outcome.eta if outcome else None,
            transcript=outcome.transcript if outcome else None,
            error=cached.get("error"),
        )
    
    raise HTTPException(status_code=404, detail=f"Order {order_id} not found")


@app.post("/calling/reset")
async def reset_calling_agent():
    """Reset the calling agent state (for testing)."""
    agent = get_agent()
    agent.clear_history()
    return {"status": "reset", "message": "Calling agent history cleared"}


# =============================================================================
# Message Agent Routes (Vonage SMS)
# =============================================================================

@app.post("/webhooks/vonage/inbound")
async def vonage_inbound_webhook(request: Request):
    """
    Vonage inbound SMS webhook endpoint.
    
    Receives incoming SMS messages, processes them with the message agent,
    and sends a response via Vonage API.
    
    Configure this URL in your Vonage dashboard:
    https://your-domain.com/webhooks/vonage/inbound
    
    Vonage sends JSON with fields:
    - msisdn: sender phone number
    - to: your Vonage number
    - text: message content
    - messageId: unique message ID
    """
    try:
        data = await request.json()
    except Exception:
        # Vonage may also send form data in some configurations
        form = await request.form()
        data = dict(form)
    
    # Extract fields from Vonage webhook
    from_number = data.get("msisdn") or data.get("from")
    to_number = data.get("to")
    body = data.get("text") or data.get("body", "")
    message_id = data.get("messageId") or data.get("message-id")
    
    if not from_number or not body:
        logger.warning(f"Invalid Vonage webhook data: {data}")
        return JSONResponse(content={"status": "error", "message": "Missing required fields"}, status_code=400)
    
    # Add + prefix if not present (Vonage sends numbers without +)
    if not from_number.startswith("+"):
        from_number = f"+{from_number}"
    if to_number and not to_number.startswith("+"):
        to_number = f"+{to_number}"
    
    logger.info(f"Received SMS from {from_number}: {body[:50]}...")
    
    # Build incoming message
    incoming = IncomingSMS(
        from_number=from_number,
        to_number=to_number or "",
        body=body,
        message_sid=message_id,
    )
    
    # Process with message agent
    message_agent = get_message_agent()
    
    try:
        response_text = await message_agent.process_message(incoming)
        
        # Send response via Vonage
        await message_agent.send_response(from_number, response_text)
        
        # Return 200 OK to acknowledge receipt
        return JSONResponse(content={"status": "ok"})
        
    except Exception as e:
        logger.exception(f"Error processing SMS: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


@app.post("/webhooks/vonage/status")
async def vonage_status_webhook(request: Request):
    """
    Vonage delivery receipt webhook.
    
    Receives delivery status updates for sent messages.
    Configure this URL in your Vonage dashboard for delivery receipts.
    """
    try:
        data = await request.json()
    except Exception:
        form = await request.form()
        data = dict(form)
    
    message_id = data.get("messageId") or data.get("message-id")
    status = data.get("status")
    
    logger.info(f"Vonage delivery status: {message_id} -> {status}")
    
    # Could store/update message status here if needed
    return JSONResponse(content={"status": "ok"})


@app.get("/messaging/history/{phone_number}")
async def get_message_history(phone_number: str):
    """Get conversation history for a phone number."""
    message_agent = get_message_agent()
    conversation = message_agent.get_conversation_history(phone_number)
    
    if not conversation:
        raise HTTPException(status_code=404, detail=f"No conversation found for {phone_number}")
    
    return {
        "phone_number": conversation.phone_number,
        "message_count": len(conversation.messages),
        "messages": [
            {"role": msg.role.value, "content": msg.content, "timestamp": msg.timestamp}
            for msg in conversation.messages
            if msg.role.value != "system"  # Don't expose system prompt
        ],
    }


@app.post("/messaging/reset/{phone_number}")
async def reset_conversation(phone_number: str):
    """Reset conversation history for a phone number."""
    message_agent = get_message_agent()
    cleared = message_agent.clear_conversation(phone_number)
    
    if cleared:
        return {"status": "reset", "message": f"Conversation cleared for {phone_number}"}
    return {"status": "not_found", "message": f"No conversation found for {phone_number}"}


@app.post("/messaging/reset")
async def reset_all_conversations():
    """Reset all conversation histories (for testing)."""
    message_agent = get_message_agent()
    message_agent.clear_all_conversations()
    return {"status": "reset", "message": "All conversations cleared"}


# =============================================================================
# Server Entry Point
# =============================================================================

def start_server(host: str = "0.0.0.0", port: int = 8001):
    """Start the FastAPI server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
