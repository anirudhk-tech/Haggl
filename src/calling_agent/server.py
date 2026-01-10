"""
FastAPI server for the IngredientAI Calling Agent.

Exposes the agent as HTTP endpoints for the Next.js frontend to consume.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from .schemas import (
    AgentRequest,
    AgentResponse,
    AgentState,
    OrderContext,
    VendorInfo,
)
from .agent import get_agent, CallingAgent

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
    logger.info("Starting IngredientAI Calling Agent server...")
    yield
    logger.info("Shutting down IngredientAI Calling Agent server...")


app = FastAPI(
    title="IngredientAI Calling Agent",
    description="Phase 2: NeMo-orchestrated vendor calling agent",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for Next.js frontend
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


# Request/Response models for the API
class PlaceOrderRequest(BaseModel):
    """Request to place an order via the agent."""
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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "IngredientAI Calling Agent",
        "version": "0.1.0",
    }


@app.post("/agent/order", response_model=OrderStatusResponse)
async def place_order(request: PlaceOrderRequest):
    """
    Place an order using the calling agent.
    
    This is the main endpoint that orchestrates:
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


@app.get("/agent/status/{order_id}", response_model=OrderStatusResponse)
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


@app.post("/agent/reset")
async def reset_agent():
    """Reset the agent state (for testing)."""
    agent = get_agent()
    agent.clear_history()
    return {"status": "reset", "message": "Agent history cleared"}


def start_server(host: str = "0.0.0.0", port: int = 8001):
    """Start the FastAPI server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
