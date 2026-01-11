"""
Haggl Agent Server

Main FastAPI server that exposes all agents as HTTP endpoints:
- Calling Agent: Voice calls via Vapi
- Message Agent: SMS via Vonage  
- Sourcing Agent: Vendor discovery via Exa.ai
- Evaluation Agent: Vendor scoring via Voyage AI
- Payment Agent: x402 authorization + payment execution
"""

import os
import logging
import uuid
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Event streaming
from events import (
    get_event_bus,
    emit_stage_change,
    emit_log,
    emit_order_approved,
    AgentStage,
)

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
from sourcing_agent.schemas import IngredientRequest, UserLocation
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

# x402 / Payment Agent imports
from x402 import (
    get_authorizer,
    get_vault,
    get_escrow_manager,
    AuthorizationRequest,
    AuthorizationResponse,
    Invoice,
)
from payment_agent import get_executor
from payment_agent.schemas import PaymentMethod, PaymentRequest, PaymentResult, PaymentStatus
from payment_agent.browserbase import BrowserbaseClient, PaymentPortalAutomator, InvoiceParser

# Business storage imports
from storage.businesses import (
    create_business_from_onboarding,
    get_business_profile,
    get_business_by_phone,
    get_business_context_for_agent,
)

# Load environment variables from project root
import pathlib
project_root = pathlib.Path(__file__).parent.parent
load_dotenv(project_root / ".env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("🚀 Starting Haggl Agent server...")
    logger.info("   Agents: calling, message, sourcing, evaluation, payment")
    
    # Emit startup event
    try:
        await emit_log(
            AgentStage.IDLE,
            "Haggl server started. Ready for orders.",
            level="info",
        )
    except Exception as e:
        logger.warning(f"Failed to emit startup event: {e}")
    
    yield
    logger.info("Shutting down Haggl Agent server...")


app = FastAPI(
    title="Haggl Agent Server",
    description="Multi-agent B2B procurement platform",
    version="0.3.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
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
        "version": "0.3.0",
        "agents": [
            "calling_agent",
            "message_agent", 
            "sourcing_agent",
            "evaluation_agent",
            "payment_agent",
        ],
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
# Message Agent Routes (Vonage WhatsApp/SMS)
# =============================================================================

@app.post("/webhooks/vonage/inbound")
async def vonage_whatsapp_inbound(request: Request):
    """
    Vonage Messages API inbound webhook for WhatsApp/SMS.
    
    Receives incoming WhatsApp/SMS messages, processes them with the message agent,
    and sends a response via Vonage Messages API.
    
    Configure this URL in your Vonage Application settings:
    https://your-domain.com/webhooks/vonage/inbound
    """
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(content={"status": "error"}, status_code=400)
    
    logger.info(f"Vonage webhook received: {data}")
    
    # Extract fields from Messages API webhook
    # Format: {"from": "15633965540", "to": "12193674151", "message": {"content": {"type": "text", "text": "..."}}}
    from_number = data.get("from") or data.get("msisdn")
    to_number = data.get("to")
    
    # Get message content - Messages API nests it
    message_data = data.get("message", {})
    content = message_data.get("content", {})
    body = content.get("text", "")
    
    # Also check for direct text field (varies by webhook format)
    if not body:
        body = data.get("text", "") or data.get("body", "")
    
    message_id = data.get("message_uuid") or data.get("messageId") or data.get("message-id")
    channel = data.get("channel", "whatsapp")
    
    if not from_number or not body:
        logger.warning(f"Invalid webhook data: {data}")
        return JSONResponse(content={"status": "ok"})  # Return 200 to avoid retries
    
    # Add + prefix if not present
    if not from_number.startswith("+"):
        from_number = f"+{from_number}"
    if to_number and not to_number.startswith("+"):
        to_number = f"+{to_number}"
    
    logger.info(f"Received {channel} from {from_number}: {body[:50]}...")
    
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
        logger.info(f"Agent response: {response_text}")
        
        # Send response
        send_result = await message_agent.send_response(from_number, response_text)
        logger.info(f"Send result: {send_result}")
        
        if send_result.get("error"):
            logger.error(f"Failed to send message: {send_result['error']}")
        
        return JSONResponse(content={"status": "ok"})
        
    except Exception as e:
        logger.exception(f"Error processing message: {e}")
        return JSONResponse(content={"status": "ok"})  # Return 200 to avoid retries


@app.post("/webhooks/vonage/status")
async def vonage_status_webhook(request: Request):
    """Vonage delivery receipt webhook."""
    try:
        data = await request.json()
    except Exception:
        form = await request.form()
        data = dict(form)
    
    message_id = data.get("messageId") or data.get("message-id")
    status = data.get("status")
    logger.info(f"Vonage delivery status: {message_id} -> {status}")
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
            if msg.role.value != "system"
        ],
    }


# =============================================================================
# Sourcing Agent Routes
# =============================================================================

class SourcingRequestModel(BaseModel):
    """Request to source vendors for ingredients."""
    ingredients: list[dict] = Field(description="List of ingredients to source")
    location: dict = Field(description="User location (city, state, zip)")
    max_results_per_ingredient: int = Field(default=10)


@app.post("/sourcing/search", response_model=SourcingResponse)
async def search_vendors(request: SourcingRequestModel):
    """
    Search for vendors for given ingredients.
    
    Uses Exa.ai for semantic search and Claude for data extraction.
    """
    logger.info(f"Sourcing request for {len(request.ingredients)} ingredients")
    
    # Convert to internal schema
    ingredients = [
        IngredientRequest(
            name=ing.get("name", ""),
            quantity=ing.get("quantity", 0),
            unit=ing.get("unit", ""),
            quality=ing.get("quality"),
        )
        for ing in request.ingredients
    ]
    
    location = UserLocation(
        city=request.location.get("city", ""),
        state=request.location.get("state", ""),
        zip_code=request.location.get("zip_code", ""),
    )
    
    sourcing_request = SourcingRequest(
        ingredients=ingredients,
        location=location,
        max_results_per_ingredient=request.max_results_per_ingredient,
    )
    
    agent = get_sourcing_agent()
    return await agent.source_vendors(sourcing_request)


@app.get("/sourcing/vendors/{ingredient}")
async def get_vendors(ingredient: str):
    """Get cached vendors for an ingredient."""
    vendors = get_vendors_by_ingredient(ingredient)
    return {"ingredient": ingredient, "vendors": vendors, "count": len(vendors)}


@app.post("/sourcing/reset")
async def reset_sourcing():
    """Clear all cached vendor data."""
    clear_storage()
    return {"status": "reset", "message": "Vendor storage cleared"}


# =============================================================================
# Evaluation Agent Routes
# =============================================================================

class FeedbackRequestModel(BaseModel):
    """Feedback request from UI."""
    business_id: str
    parameter: str  # quality, affordability, shipping, reliability
    direction: str  # up, down


@app.post("/evaluation/evaluate", response_model=EvaluationResponse)
async def evaluate_vendors(request: EvaluationRequest):
    """
    Evaluate and rank vendors using Voyage AI embeddings.
    
    Returns vendors sorted by personalized scores.
    """
    logger.info(f"Evaluation request for {len(request.vendors)} vendors")
    agent = get_evaluation_agent()
    return agent.evaluate_vendors(request)


@app.post("/evaluation/feedback")
async def submit_feedback(request: FeedbackRequestModel):
    """
    Submit preference feedback (UP/DOWN) for a parameter.
    
    Updates the business's preference weights.
    """
    agent = get_evaluation_agent()
    
    feedback = FeedbackRequest(
        parameter=EvaluationParameter(request.parameter),
        direction=FeedbackDirection(request.direction),
    )
    
    new_weights = agent.process_feedback(request.business_id, feedback)
    return {"status": "updated", "weights": new_weights.model_dump()}


@app.get("/evaluation/preferences/{business_id}")
async def get_preferences(business_id: str):
    """Get current preference weights for a business."""
    agent = get_evaluation_agent()
    prefs = agent.get_preferences(business_id)
    return {
        "business_id": business_id,
        "weights": prefs.weights.model_dump(),
        "feedback_count": prefs.total_feedback_count,
    }


# =============================================================================
# x402 Payment Agent Routes
# =============================================================================

class AuthorizeRequest(BaseModel):
    """Request to authorize a payment."""
    invoice_id: str = Field(description="Unique invoice ID")
    vendor_name: str = Field(description="Vendor name")
    vendor_id: Optional[str] = Field(default=None, description="Vendor ID")
    amount_usd: float = Field(description="Amount in USD")
    budget_total: float = Field(description="Total budget for this session")
    budget_remaining: float = Field(description="Remaining budget")
    description: Optional[str] = Field(default=None, description="Invoice description")


class PayRequestModel(BaseModel):
    """Request to execute an authorized payment."""
    auth_token: str = Field(description="x402 authorization token")
    invoice_id: str = Field(description="Invoice ID to pay")
    amount_usd: float = Field(description="Amount in USD")
    vendor_name: str = Field(description="Vendor receiving payment")
    payment_method: str = Field(default="mock_card", description="Payment method")


class StoreCredentialsRequest(BaseModel):
    """Request to store ACH credentials."""
    business_id: str
    routing_number: str
    account_number: str
    account_name: str
    bank_name: Optional[str] = None


class EscrowReleaseRequest(BaseModel):
    """Request to release escrow to vendor."""
    auth_token: str
    vendor_id: str
    ach_confirmation: Optional[str] = None


class PayInvoiceRequest(BaseModel):
    """Request to pay invoice via browser automation."""
    invoice_url: str
    business_id: str
    auth_token: str
    contact_email: str = "orders@haggl.demo"


@app.post("/x402/authorize", response_model=AuthorizationResponse)
async def authorize_payment(request: AuthorizeRequest):
    """Authorize a payment via x402 (USDC to escrow)."""
    logger.info(f"📋 Authorization request for invoice {request.invoice_id}")
    
    invoice = Invoice(
        invoice_id=request.invoice_id,
        vendor_name=request.vendor_name,
        vendor_id=request.vendor_id,
        amount_usd=request.amount_usd,
        description=request.description
    )
    
    auth_request = AuthorizationRequest(
        invoice=invoice,
        budget_total=request.budget_total,
        budget_remaining=request.budget_remaining
    )
    
    authorizer = get_authorizer()
    return await authorizer.authorize(auth_request)


@app.post("/x402/pay", response_model=PaymentResult)
async def execute_payment(request: PayRequestModel):
    """Execute an authorized payment."""
    logger.info(f"💳 Payment execution request for invoice {request.invoice_id}")
    
    authorizer = get_authorizer()
    invoice_id = authorizer.consume_auth_token(request.auth_token)
    
    if invoice_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired authorization token")
    
    if invoice_id != request.invoice_id:
        raise HTTPException(status_code=400, detail=f"Auth token is for invoice {invoice_id}, not {request.invoice_id}")
    
    # Get original authorization tx_hash
    x402_tx_hash = None
    for auth in authorizer._authorizations.values():
        if auth.invoice_id == invoice_id:
            x402_tx_hash = auth.tx_hash
            break
    
    executor = get_executor()
    payment_request = PaymentRequest(
        auth_token=request.auth_token,
        invoice_id=request.invoice_id,
        amount_usd=request.amount_usd,
        vendor_name=request.vendor_name,
        payment_method=PaymentMethod(request.payment_method)
    )
    
    return await executor.execute_payment(payment_request, x402_tx_hash=x402_tx_hash)


@app.get("/x402/status/{invoice_id}")
async def get_payment_status(invoice_id: str):
    """Get the status of a payment by invoice ID."""
    authorizer = get_authorizer()
    executor = get_executor()
    
    auth = None
    for a in authorizer._authorizations.values():
        if a.invoice_id == invoice_id:
            auth = a
            break
    
    payment = executor.get_payment_status(invoice_id)
    
    if not auth and not payment:
        raise HTTPException(status_code=404, detail=f"No authorization or payment found for invoice {invoice_id}")
    
    return {
        "invoice_id": invoice_id,
        "authorization": auth.model_dump() if auth else None,
        "payment": payment.model_dump() if payment else None
    }


@app.get("/x402/spending")
async def get_spending_summary():
    """Get current spending summary and limits."""
    authorizer = get_authorizer()
    return authorizer.get_spending_summary()


@app.get("/x402/wallet")
async def get_wallet_info():
    """Get wallet information."""
    from x402.wallet import get_wallet
    wallet = get_wallet()
    balance = await wallet.get_balance()
    info = await wallet.get_or_create_account()
    
    return {
        "address": info.address,
        "network": info.network,
        "balance": balance,
        "mode": "mock" if wallet.mock_mode else "real"
    }


@app.post("/x402/reset")
async def reset_x402_state():
    """Reset all x402 state (for testing/demos)."""
    authorizer = get_authorizer()
    executor = get_executor()
    authorizer.reset()
    executor.reset()
    return {"status": "reset", "message": "x402 state cleared"}


# Credential Vault Endpoints
@app.post("/vault/credentials")
async def store_credentials(request: StoreCredentialsRequest):
    """Store encrypted ACH credentials for a business."""
    vault = get_vault()
    return vault.store_credentials(
        business_id=request.business_id,
        routing_number=request.routing_number,
        account_number=request.account_number,
        account_name=request.account_name,
        bank_name=request.bank_name
    )


@app.get("/vault/credentials/{business_id}")
async def get_credential_info(business_id: str):
    """Get non-sensitive credential info (masked account numbers)."""
    vault = get_vault()
    info = vault.get_credential_info(business_id)
    if not info:
        raise HTTPException(status_code=404, detail=f"No credentials found for business {business_id}")
    return info


# Escrow Endpoints
@app.post("/escrow/release")
async def release_escrow(request: EscrowReleaseRequest):
    """Release escrowed funds to vendor after successful payment."""
    authorizer = get_authorizer()
    result = authorizer.release_escrow(
        auth_token=request.auth_token,
        vendor_id=request.vendor_id,
        ach_confirmation=request.ach_confirmation
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to release escrow"))
    return result


@app.get("/escrow/stats")
async def get_escrow_stats():
    """Get escrow statistics."""
    authorizer = get_authorizer()
    return authorizer.get_escrow_stats()


# Browser Automation Endpoints
@app.post("/browser/pay-invoice")
async def pay_invoice_via_browser(request: PayInvoiceRequest):
    """Pay an invoice through browser automation."""
    logger.info(f"🌐 Browser payment request for {request.invoice_url}")
    
    browser = BrowserbaseClient(mock_mode=False)
    automator = PaymentPortalAutomator(browser)
    
    result = await automator.pay_invoice(
        invoice_url=request.invoice_url,
        business_id=request.business_id,
        auth_token=request.auth_token,
        contact_email=request.contact_email
    )
    
    # If successful, release escrow
    if result.get("status") == "succeeded":
        authorizer = get_authorizer()
        escrow_result = authorizer.release_escrow(
            auth_token=request.auth_token,
            vendor_id=result.get("parsed_invoice", {}).get("vendor_name", "unknown"),
            ach_confirmation=result.get("confirmation")
        )
        result["escrow_released"] = escrow_result.get("success", False)
    
    return result


@app.post("/browser/parse-invoice")
async def parse_invoice_from_url(invoice_url: str):
    """Navigate to an invoice URL and parse its details."""
    browser = BrowserbaseClient(mock_mode=False)
    parser = InvoiceParser()
    
    try:
        session = await browser.create_session()
        if session.get("error"):
            raise HTTPException(status_code=500, detail=session["error"])
        
        await browser.connect_browser()
        await browser.navigate(invoice_url)
        
        screenshot = await browser.screenshot()
        if screenshot:
            parsed = await parser.parse_from_screenshot(screenshot)
            return {"url": invoice_url, "parsed": parsed}
        
        return {"url": invoice_url, "error": "Could not capture screenshot"}
    finally:
        await browser.close()


# =============================================================================
# Real-time Events (SSE)
# =============================================================================

@app.get("/events/stream")
async def event_stream(request: Request):
    """
    Server-Sent Events endpoint for real-time agent updates.
    
    Connect from frontend with:
    const eventSource = new EventSource('/events/stream');
    eventSource.onmessage = (e) => console.log(JSON.parse(e.data));
    """
    client_id = str(uuid.uuid4())[:8]
    
    async def generate():
        event_bus = get_event_bus()
        try:
            async for event in event_bus.subscribe(client_id):
                # Check if client disconnected
                if await request.is_disconnected():
                    break
                yield event
        except Exception as e:
            logger.error(f"SSE error for client {client_id}: {e}")
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/events/recent")
async def get_recent_events(limit: int = 20):
    """Get recent events (for initial page load)."""
    event_bus = get_event_bus()
    events = event_bus.get_recent_events(limit)
    return {
        "events": [e.model_dump() for e in events],
        "count": len(events),
    }


@app.post("/events/test")
async def emit_test_event():
    """Emit a test event (for debugging SSE connection)."""
    await emit_log(
        AgentStage.IDLE,
        "Test event emitted! SSE is working.",
        level="info",
    )
    return {"status": "ok", "message": "Test event emitted"}


# =============================================================================
# Business Profile / Onboarding
# =============================================================================

class OnboardingRequest(BaseModel):
    """Request to save onboarding data."""
    business_id: str = Field(description="Unique ID (phone number recommended)")
    business_type: str = Field(description="Type: restaurant, bakery, cafe, retail, other")
    products: list[dict] = Field(description="Selected products from onboarding")
    business_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[dict] = None


@app.post("/onboarding/complete")
async def complete_onboarding(request: OnboardingRequest):
    """
    Save onboarding data to MongoDB.
    
    Called by frontend when user completes onboarding flow.
    """
    logger.info(f"Onboarding complete for business: {request.business_id}")
    
    profile = create_business_from_onboarding(
        business_id=request.business_id,
        business_type=request.business_type,
        products=request.products,
        phone=request.phone,
        business_name=request.business_name,
        location=request.location,
    )
    
    if profile:
        return {
            "status": "success",
            "business_id": profile.business_id,
            "products_saved": len(profile.products),
        }
    
    return {"status": "error", "message": "Failed to save onboarding data"}


@app.get("/business/{business_id}")
async def get_business(business_id: str):
    """Get business profile by ID."""
    profile = get_business_profile(business_id)
    if profile:
        return profile.model_dump()
    raise HTTPException(status_code=404, detail=f"Business {business_id} not found")


@app.get("/business/by-phone/{phone}")
async def get_business_by_phone_endpoint(phone: str):
    """Get business profile by phone number."""
    profile = get_business_by_phone(phone)
    if profile:
        return profile.model_dump()
    raise HTTPException(status_code=404, detail=f"Business with phone {phone} not found")


class LinkPhoneRequest(BaseModel):
    """Request to link phone number to business."""
    business_id: str
    phone: str


@app.post("/business/link-phone")
async def link_phone_to_business(request: LinkPhoneRequest):
    """
    Link a phone number to an existing business profile.
    
    This allows WhatsApp users to be associated with their business.
    """
    from storage.businesses import get_business_profile, save_business_profile
    
    profile = get_business_profile(request.business_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Business {request.business_id} not found")
    
    # Update phone
    profile.phone = request.phone
    
    if save_business_profile(profile):
        return {"status": "success", "message": f"Phone {request.phone} linked to {request.business_id}"}
    
    raise HTTPException(status_code=500, detail="Failed to link phone")


# =============================================================================
# Orders Management
# =============================================================================

# In-memory order store (would be MongoDB in production)
_pending_approvals: dict[str, dict] = {}


class ApproveOrderRequest(BaseModel):
    """Request to approve an order."""
    order_id: str


@app.get("/orders/pending")
async def get_pending_approvals():
    """Get orders pending approval."""
    return {
        "orders": list(_pending_approvals.values()),
        "count": len(_pending_approvals),
    }


@app.post("/orders/approve")
async def approve_order(request: ApproveOrderRequest):
    """
    Approve an order for payment.
    
    This will eventually trigger x402 payment flow.
    """
    order_id = request.order_id
    
    if order_id in _pending_approvals:
        order = _pending_approvals.pop(order_id)
        vendor_name = order.get("vendor_name", "Unknown")
        
        # Emit approval event
        await emit_order_approved(order_id, vendor_name)
        
        logger.info(f"✅ Order {order_id} approved!")
        
        return {
            "status": "approved",
            "order_id": order_id,
            "message": f"Order approved! Will process payment to {vendor_name}.",
        }
    
    # Even if not in pending, emit the event for demo purposes
    await emit_order_approved(order_id, "Demo Vendor")
    
    return {
        "status": "approved",
        "order_id": order_id,
        "message": "Order approved!",
    }


def add_pending_approval(
    order_id: str,
    vendor_name: str,
    price: float,
    product: str,
    quantity: int,
    unit: str,
):
    """Add an order to pending approvals (called by agents)."""
    _pending_approvals[order_id] = {
        "order_id": order_id,
        "vendor_name": vendor_name,
        "price": price,
        "product": product,
        "quantity": quantity,
        "unit": unit,
        "created_at": datetime.utcnow().isoformat(),
    }


# =============================================================================
# Server Entry Point
# =============================================================================

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
