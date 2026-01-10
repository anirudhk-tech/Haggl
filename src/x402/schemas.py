"""Pydantic schemas for x402 Authorization Layer."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class AuthorizationStatus(str, Enum):
    """Status of an authorization request."""
    PENDING = "pending"
    AUTHORIZED = "authorized"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXECUTED = "executed"


class Invoice(BaseModel):
    """Invoice to be authorized for payment."""
    invoice_id: str = Field(description="Unique invoice identifier")
    vendor_name: str = Field(description="Name of the vendor")
    vendor_id: Optional[str] = Field(default=None, description="Vendor ID if known")
    amount_usd: float = Field(description="Amount in USD")
    currency: str = Field(default="USD", description="Currency code")
    due_date: Optional[str] = Field(default=None, description="Due date YYYY-MM-DD")
    payment_url: Optional[str] = Field(default=None, description="URL to pay online")
    description: Optional[str] = Field(default=None, description="Invoice description")
    line_items: list[dict] = Field(default_factory=list, description="Line items")


class SpendingPolicy(BaseModel):
    """Spending policy configuration for budget enforcement."""
    per_transaction_max: float = Field(default=500.0, description="Max per transaction")
    daily_limit: float = Field(default=2000.0, description="Daily spending limit")
    weekly_limit: float = Field(default=5000.0, description="Weekly spending limit")
    require_memo: bool = Field(default=True, description="Require invoice ID in memo")
    min_confirmation_delay_seconds: int = Field(default=0, description="Delay before auth")


class AuthorizationRequest(BaseModel):
    """Request to authorize a payment via x402."""
    invoice: Invoice
    budget_total: float = Field(description="Total budget available")
    budget_remaining: float = Field(description="Remaining budget")
    request_id: Optional[str] = Field(default=None, description="Idempotency key")


class AuthorizationResponse(BaseModel):
    """Response from x402 authorization."""
    request_id: str
    invoice_id: str
    status: AuthorizationStatus
    auth_token: Optional[str] = Field(default=None, description="Single-use auth token")
    tx_hash: Optional[str] = Field(default=None, description="On-chain transaction hash")
    explorer_url: Optional[str] = Field(default=None, description="Block explorer URL")
    amount_authorized: Optional[float] = Field(default=None, description="Amount in USD")
    escrow_address: Optional[str] = Field(default=None, description="Escrow wallet address")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    error: Optional[str] = Field(default=None, description="Error message if rejected")
    policy_checks: dict = Field(default_factory=dict, description="Policy check results")


class BudgetContext(BaseModel):
    """Budget context for a procurement session."""
    session_id: str
    total_budget: float
    spent_amount: float = 0.0
    pending_amount: float = 0.0
    
    @property
    def remaining(self) -> float:
        return self.total_budget - self.spent_amount - self.pending_amount
    
    @property
    def available(self) -> float:
        return self.total_budget - self.spent_amount


class WalletInfo(BaseModel):
    """Information about a CDP wallet."""
    address: str
    network: str
    balance_usdc: float = 0.0
    balance_eth: float = 0.0
