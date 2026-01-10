"""Pydantic schemas for Payment Agent."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class PaymentMethod(str, Enum):
    """Supported payment methods."""
    STRIPE_CARD = "stripe_card"
    STRIPE_ACH = "stripe_ach"
    MOCK_ACH = "mock_ach"
    MOCK_CARD = "mock_card"
    BROWSERBASE_ACH = "browserbase_ach"  # Real browser automation via Browserbase x402


class PaymentStatus(str, Enum):
    """Status of a payment."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REQUIRES_ACTION = "requires_action"
    CANCELED = "canceled"


class MockStripePayment(BaseModel):
    """Mock Stripe payment details (for demo)."""
    payment_intent_id: str = Field(description="Stripe PaymentIntent ID")
    client_secret: Optional[str] = Field(default=None, description="Client secret for frontend")
    amount: int = Field(description="Amount in cents")
    currency: str = Field(default="usd")
    status: str = Field(default="succeeded")
    payment_method_type: str = Field(default="card")


class MockACHPayment(BaseModel):
    """Mock ACH payment details (for demo)."""
    ach_transfer_id: str = Field(description="ACH transfer ID")
    routing_number_last4: str = Field(default="0021", description="Last 4 of routing")
    account_number_last4: str = Field(default="7890", description="Last 4 of account")
    bank_name: str = Field(default="Demo Bank")
    status: str = Field(default="pending")
    estimated_arrival: str = Field(description="Estimated arrival date")


class PaymentRequest(BaseModel):
    """Request to execute a payment."""
    auth_token: str = Field(description="x402 authorization token")
    invoice_id: str = Field(description="Invoice being paid")
    amount_usd: float = Field(description="Amount in USD")
    vendor_name: str = Field(description="Vendor receiving payment")
    payment_method: PaymentMethod = Field(default=PaymentMethod.MOCK_CARD)
    
    # Optional card details (for Stripe mock)
    card_last4: Optional[str] = Field(default="4242", description="Last 4 of card")
    card_brand: Optional[str] = Field(default="visa", description="Card brand")
    
    # Optional ACH details
    use_saved_ach: bool = Field(default=True, description="Use saved ACH credentials")


class PaymentResult(BaseModel):
    """Result of a payment execution."""
    invoice_id: str
    status: PaymentStatus
    payment_method: PaymentMethod
    amount_usd: float
    
    # x402 authorization reference
    auth_token_consumed: bool = Field(default=True)
    x402_tx_hash: Optional[str] = Field(default=None, description="On-chain authorization")
    
    # Payment details (one of these will be populated)
    stripe_payment: Optional[MockStripePayment] = None
    ach_payment: Optional[MockACHPayment] = None
    
    # Confirmation
    confirmation_number: Optional[str] = None
    receipt_url: Optional[str] = None
    
    # Timing
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    processing_time_ms: Optional[int] = None
    
    # Error handling
    error: Optional[str] = None
    retry_eligible: bool = False


class PaymentSummary(BaseModel):
    """Summary of payments for an order."""
    order_id: str
    total_authorized: float
    total_paid: float
    total_pending: float
    payments: list[PaymentResult] = Field(default_factory=list)
    all_succeeded: bool = False
