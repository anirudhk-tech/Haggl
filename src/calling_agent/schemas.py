"""Pydantic schemas for the Calling Agent."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class AgentState(str, Enum):
    """Agent state machine states."""
    READY_TO_CALL = "ready_to_call"
    CALL_IN_PROGRESS = "call_in_progress"
    PROCESSING = "processing"
    CONFIRMED = "confirmed"
    PLACED = "placed"
    FAILED = "failed"


class OrderContext(BaseModel):
    """Context for placing an order."""
    business_name: str = Field(description="Name of the business placing the order")
    business_type: str = Field(description="Type of business (bakery, restaurant, etc.)")
    product: str = Field(default="eggs", description="Product being ordered")
    quantity: int = Field(description="Quantity in dozens")
    unit: str = Field(default="dozen", description="Unit of measurement")
    delivery_address: Optional[str] = Field(default=None, description="Delivery address for the order")


class VendorInfo(BaseModel):
    """Information about a vendor."""
    id: str
    name: str
    phone: str
    product: str
    price_per_unit: float
    unit: str


class CallVendorInput(BaseModel):
    """Input schema for the call_vendor tool."""
    phone_number: str = Field(description="Vendor phone number in E.164 format")
    vendor_name: str = Field(description="Name of the vendor being called")
    business_name: str = Field(description="Name of the business placing the order")
    items: list[dict] = Field(description="List of items to order, each with 'product', 'quantity', and 'unit' keys")
    delivery_address: str = Field(description="Delivery address for the order")


class CallOutcome(BaseModel):
    """Structured outcome from a vendor call."""
    confirmed: bool = Field(description="Whether the order was confirmed")
    price: Optional[float] = Field(default=None, description="Negotiated price per unit")
    eta: Optional[str] = Field(default=None, description="Estimated delivery/pickup time")
    notes: Optional[str] = Field(default=None, description="Additional notes from the call")
    transcript: Optional[str] = Field(default=None, description="Full call transcript")


class AgentRequest(BaseModel):
    """Request to the calling agent."""
    order_id: str = Field(description="Unique order ID")
    order_context: OrderContext
    vendor: VendorInfo


class AgentResponse(BaseModel):
    """Response from the calling agent."""
    order_id: str
    status: AgentState
    call_id: Optional[str] = None
    outcome: Optional[CallOutcome] = None
    error: Optional[str] = None
