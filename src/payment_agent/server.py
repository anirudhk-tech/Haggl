"""
FastAPI server for the x402 Authorization + Payment Agent.

Endpoints:
- POST /x402/authorize - Request payment authorization
- POST /x402/pay - Execute authorized payment
- GET /x402/status/{invoice_id} - Get payment status
- GET /x402/spending - Get spending summary
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..x402 import (
    X402Authorizer,
    get_authorizer,
    AuthorizationRequest,
    AuthorizationResponse,
    Invoice,
    SpendingPolicy,
)
from .executor import PaymentExecutor, get_executor
from .schemas import (
    PaymentMethod,
    PaymentRequest,
    PaymentResult,
    PaymentStatus,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("🚀 Starting x402 Authorization + Payment Agent server...")
    logger.info("   Mode: Demo/Mock (no real payments)")
    yield
    logger.info("Shutting down x402 server...")


app = FastAPI(
    title="Haggl x402 Payment Agent",
    description="x402 Authorization Layer + Mock Payment Execution for demos",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
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


# ============================================================================
# Request/Response Models
# ============================================================================

class AuthorizeRequest(BaseModel):
    """Request to authorize a payment."""
    invoice_id: str = Field(description="Unique invoice ID")
    vendor_name: str = Field(description="Vendor name")
    amount_usd: float = Field(description="Amount in USD")
    budget_total: float = Field(description="Total budget for this session")
    budget_remaining: float = Field(description="Remaining budget")
    description: Optional[str] = Field(default=None, description="Invoice description")


class PayRequest(BaseModel):
    """Request to execute an authorized payment."""
    auth_token: str = Field(description="x402 authorization token")
    invoice_id: str = Field(description="Invoice ID to pay")
    amount_usd: float = Field(description="Amount in USD")
    vendor_name: str = Field(description="Vendor receiving payment")
    payment_method: PaymentMethod = Field(
        default=PaymentMethod.MOCK_CARD,
        description="Payment method to use"
    )


class FullPaymentRequest(BaseModel):
    """Combined authorize + pay request for convenience."""
    invoice_id: str
    vendor_name: str
    amount_usd: float
    budget_total: float
    budget_remaining: float
    payment_method: PaymentMethod = PaymentMethod.MOCK_CARD
    description: Optional[str] = None


class FullPaymentResponse(BaseModel):
    """Combined response showing both authorization and payment."""
    authorization: AuthorizationResponse
    payment: Optional[PaymentResult] = None
    success: bool = False
    message: str = ""


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Haggl x402 Payment Agent",
        "version": "0.1.0",
        "mode": "demo"
    }


@app.post("/x402/authorize", response_model=AuthorizationResponse)
async def authorize_payment(request: AuthorizeRequest):
    """
    Step 1: Authorize a payment via x402.
    
    This checks spending policies and creates an on-chain authorization
    (USDC transfer to escrow). Returns an auth token needed for execution.
    """
    logger.info(f"📋 Authorization request for invoice {request.invoice_id}")
    
    # Build invoice
    invoice = Invoice(
        invoice_id=request.invoice_id,
        vendor_name=request.vendor_name,
        amount_usd=request.amount_usd,
        description=request.description
    )
    
    # Build authorization request
    auth_request = AuthorizationRequest(
        invoice=invoice,
        budget_total=request.budget_total,
        budget_remaining=request.budget_remaining
    )
    
    # Get authorizer and process
    authorizer = get_authorizer()
    response = await authorizer.authorize(auth_request)
    
    return response


@app.post("/x402/pay", response_model=PaymentResult)
async def execute_payment(request: PayRequest):
    """
    Step 2: Execute an authorized payment.
    
    Requires a valid auth token from the /authorize endpoint.
    Supports mock card and ACH payment methods.
    """
    logger.info(f"💳 Payment execution request for invoice {request.invoice_id}")
    
    # Verify auth token
    authorizer = get_authorizer()
    invoice_id = authorizer.consume_auth_token(request.auth_token)
    
    if invoice_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authorization token"
        )
    
    if invoice_id != request.invoice_id:
        raise HTTPException(
            status_code=400,
            detail=f"Auth token is for invoice {invoice_id}, not {request.invoice_id}"
        )
    
    # Get the original authorization for the tx_hash
    # (In production, we'd look this up by auth_token)
    x402_tx_hash = None
    for auth in authorizer._authorizations.values():
        if auth.invoice_id == invoice_id:
            x402_tx_hash = auth.tx_hash
            break
    
    # Execute payment
    executor = get_executor()
    payment_request = PaymentRequest(
        auth_token=request.auth_token,
        invoice_id=request.invoice_id,
        amount_usd=request.amount_usd,
        vendor_name=request.vendor_name,
        payment_method=request.payment_method
    )
    
    result = await executor.execute_payment(payment_request, x402_tx_hash=x402_tx_hash)
    
    return result


@app.post("/x402/authorize-and-pay", response_model=FullPaymentResponse)
async def authorize_and_pay(request: FullPaymentRequest):
    """
    Combined endpoint: Authorize and execute in one call.
    
    Convenience endpoint that does both steps:
    1. x402 authorization (on-chain)
    2. Payment execution (mock Stripe/ACH)
    """
    logger.info(f"🔄 Full payment flow for invoice {request.invoice_id}")
    
    # Step 1: Authorize
    invoice = Invoice(
        invoice_id=request.invoice_id,
        vendor_name=request.vendor_name,
        amount_usd=request.amount_usd,
        description=request.description
    )
    
    auth_request = AuthorizationRequest(
        invoice=invoice,
        budget_total=request.budget_total,
        budget_remaining=request.budget_remaining
    )
    
    authorizer = get_authorizer()
    auth_response = await authorizer.authorize(auth_request)
    
    if auth_response.status.value != "authorized":
        return FullPaymentResponse(
            authorization=auth_response,
            payment=None,
            success=False,
            message=f"Authorization failed: {auth_response.error}"
        )
    
    # Step 2: Execute payment
    executor = get_executor()
    payment_request = PaymentRequest(
        auth_token=auth_response.auth_token,
        invoice_id=request.invoice_id,
        amount_usd=request.amount_usd,
        vendor_name=request.vendor_name,
        payment_method=request.payment_method
    )
    
    # Consume the token
    authorizer.consume_auth_token(auth_response.auth_token)
    
    payment_result = await executor.execute_payment(
        payment_request,
        x402_tx_hash=auth_response.tx_hash
    )
    
    success = payment_result.status in (PaymentStatus.SUCCEEDED, PaymentStatus.PROCESSING)
    
    return FullPaymentResponse(
        authorization=auth_response,
        payment=payment_result,
        success=success,
        message="Payment authorized and executed successfully" if success else f"Payment failed: {payment_result.error}"
    )


@app.get("/x402/status/{invoice_id}")
async def get_payment_status(invoice_id: str):
    """Get the status of a payment by invoice ID."""
    
    authorizer = get_authorizer()
    executor = get_executor()
    
    # Look up authorization
    auth = None
    for a in authorizer._authorizations.values():
        if a.invoice_id == invoice_id:
            auth = a
            break
    
    # Look up payment
    payment = executor.get_payment_status(invoice_id)
    
    if not auth and not payment:
        raise HTTPException(
            status_code=404,
            detail=f"No authorization or payment found for invoice {invoice_id}"
        )
    
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
    from ..x402.wallet import get_wallet
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
async def reset_state():
    """Reset all state (for testing/demos)."""
    authorizer = get_authorizer()
    executor = get_executor()
    
    authorizer.reset()
    executor.reset()
    
    return {"status": "reset", "message": "All state cleared"}


# ============================================================================
# Server runner
# ============================================================================

def start_server(host: str = "0.0.0.0", port: int = 8002):
    """Start the FastAPI server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
