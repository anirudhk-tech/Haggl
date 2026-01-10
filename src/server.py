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

# Sourcing Agent imports
from sourcing_agent import get_sourcing_agent, SourcingRequest, SourcingResponse
from sourcing_agent.tools.storage import get_vendors_by_ingredient, clear_storage

# Evaluation Agent imports
from evaluation_agent import get_evaluation_agent
from evaluation_agent.schemas import (
    EvaluationParameter,
    FeedbackDirection,
    FeedbackRequest,
    EvaluationRequest,
    EvaluationResponse,
    PreferenceWeights,
)

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
        "agents": ["calling_agent", "message_agent", "sourcing_agent", "evaluation_agent"],
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
# Sourcing Agent Routes
# =============================================================================

@app.post("/sourcing/search", response_model=SourcingResponse)
async def search_vendors(request: SourcingRequest):
    """
    Search for vendors for given ingredients.

    This endpoint:
    1. Searches Exa.ai for each ingredient using multiple query strategies
    2. Extracts structured vendor data using Claude
    3. Estimates shipping distance
    4. Saves results to local storage
    5. Returns ranked results
    """
    logger.info(f"Received sourcing request: {request.request_id} for {len(request.ingredients)} ingredients")

    agent = get_sourcing_agent()

    try:
        response = await agent.source_vendors(request)
        logger.info(f"Sourcing complete: found {response.total_vendors_found} vendors")
        return response
    except Exception as e:
        logger.exception(f"Error in sourcing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sourcing/results/{ingredient}")
async def get_vendor_results(ingredient: str):
    """Get cached vendor results for an ingredient."""
    vendors = get_vendors_by_ingredient(ingredient)

    if not vendors:
        return {
            "ingredient": ingredient,
            "vendors": [],
            "message": f"No cached vendors found for '{ingredient}'. Run a search first.",
        }

    return {
        "ingredient": ingredient,
        "vendor_count": len(vendors),
        "vendors": vendors,
    }


@app.get("/sourcing/status")
async def get_sourcing_status():
    """Get current sourcing agent status."""
    agent = get_sourcing_agent()
    return {
        "state": agent.get_state().value,
        "error": agent.error,
    }


@app.post("/sourcing/reset")
async def reset_sourcing():
    """Clear sourcing agent cache and storage (for testing)."""
    agent = get_sourcing_agent()
    agent.clear_cache()
    clear_storage()
    return {"status": "reset", "message": "Sourcing agent cache and storage cleared"}


# =============================================================================
# Evaluation Agent Routes
# =============================================================================

class EvaluationRequestModel(BaseModel):
    """Request model for vendor evaluation."""
    business_id: str
    ingredients: list[str] = []
    budget: float = 1000.0


class FeedbackRequestModel(BaseModel):
    """Request model for preference feedback."""
    business_id: str
    parameter: str  # quality, affordability, shipping, reliability
    direction: str  # up, down


@app.post("/evaluation/vendors")
async def evaluate_vendors(request: EvaluationRequestModel):
    """
    Evaluate and rank vendors for a business based on learned preferences.

    This endpoint:
    1. Gets the business's current preference weights
    2. Scores vendors using Voyage AI embeddings + preference vectors
    3. Returns ranked vendors within budget
    """
    logger.info(f"Received evaluation request for business: {request.business_id}")

    eval_agent = get_evaluation_agent()

    try:
        eval_request = EvaluationRequest(
            business_id=request.business_id,
            ingredients=request.ingredients,
            budget=request.budget,
        )

        response = eval_agent.evaluate_vendors(eval_request)

        return {
            "business_id": request.business_id,
            "selected_vendors": [
                {
                    "vendor_id": v.vendor_id,
                    "vendor_name": v.vendor_name,
                    "scores": {
                        "quality": v.scores.quality,
                        "affordability": v.scores.affordability,
                        "shipping": v.scores.shipping,
                        "reliability": v.scores.reliability,
                    },
                    "embedding_score": v.embedding_score,
                    "parameter_score": v.parameter_score,
                    "final_score": v.final_score,
                    "rank": v.rank,
                }
                for v in response.selected_vendors
            ],
            "total_cost": response.total_cost,
            "budget": response.budget,
            "savings": response.savings,
            "weights_used": response.weights_used.model_dump(),
        }

    except Exception as e:
        logger.exception(f"Error evaluating vendors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluation/feedback")
async def process_feedback(request: FeedbackRequestModel):
    """
    Process user feedback to adjust preference weights.

    When user clicks UP: increase weight for that parameter
    When user clicks DOWN: decrease weight for that parameter

    Weights are normalized to sum to 1.0.
    """
    logger.info(f"Received feedback: {request.business_id} - {request.parameter} {request.direction}")

    eval_agent = get_evaluation_agent()

    try:
        # Validate parameter
        try:
            param = EvaluationParameter(request.parameter)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid parameter '{request.parameter}'. Must be one of: quality, affordability, shipping, reliability"
            )

        # Validate direction
        try:
            direction = FeedbackDirection(request.direction)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid direction '{request.direction}'. Must be 'up' or 'down'"
            )

        feedback = FeedbackRequest(
            parameter=param,
            direction=direction,
        )

        new_weights = eval_agent.process_feedback(request.business_id, feedback)

        return {
            "business_id": request.business_id,
            "parameter_updated": request.parameter,
            "direction": request.direction,
            "new_weights": new_weights.model_dump(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error processing feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/evaluation/preferences/{business_id}")
async def get_preferences(business_id: str):
    """
    Get current preference weights for a business.

    Returns the 4 parameter weights that sum to 1.0:
    - quality: Weight for product quality
    - affordability: Weight for price/value
    - shipping: Weight for proximity/shipping distance
    - reliability: Weight for delivery reliability
    """
    eval_agent = get_evaluation_agent()
    prefs = eval_agent.get_preferences(business_id)

    return {
        "business_id": prefs.business_id,
        "weights": prefs.weights.model_dump(),
        "total_feedback_count": prefs.total_feedback_count,
    }


@app.get("/evaluation/radar/{business_id}/{vendor_id}")
async def get_radar_data(business_id: str, vendor_id: str):
    """
    Get radar chart data for a specific vendor.

    Returns scores formatted for Recharts radar visualization:
    - parameter: Quality/Affordability/Shipping/Reliability
    - value: Score 0-100
    - fullMark: 100
    """
    eval_agent = get_evaluation_agent()

    # Re-evaluate to get vendor scores
    eval_request = EvaluationRequest(
        business_id=business_id,
        ingredients=[],
        budget=10000,  # High budget to include all vendors
    )

    response = eval_agent.evaluate_vendors(eval_request)

    # Find the requested vendor
    vendor = next(
        (v for v in response.selected_vendors if v.vendor_id == vendor_id),
        None
    )

    if not vendor:
        raise HTTPException(status_code=404, detail=f"Vendor {vendor_id} not found")

    return {
        "vendor_id": vendor.vendor_id,
        "vendor_name": vendor.vendor_name,
        "radar_data": eval_agent.get_radar_chart_data(vendor),
    }


@app.post("/evaluation/reset/{business_id}")
async def reset_evaluation_preferences(business_id: str):
    """Reset preference weights to default for a business."""
    eval_agent = get_evaluation_agent()

    # Reset by setting new default preferences
    eval_agent._preferences[business_id] = eval_agent.get_preferences(business_id)
    eval_agent._preferences[business_id].weights = PreferenceWeights()
    eval_agent._preferences[business_id].total_feedback_count = 0

    return {
        "status": "reset",
        "business_id": business_id,
        "message": "Preference weights reset to defaults",
        "weights": eval_agent._preferences[business_id].weights.model_dump(),
    }


# =============================================================================
# Server Entry Point
# =============================================================================

def start_server(host: str = "0.0.0.0", port: int = 8001):
    """Start the FastAPI server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
