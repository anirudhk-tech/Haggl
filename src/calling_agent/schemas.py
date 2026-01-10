"""Pydantic schemas for the Calling Agent."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
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
    product: str = Field(description="Product being ordered (e.g., 'eggs')")
    quantity: int = Field(description="Quantity needed")
    unit: str = Field(default="dozen", description="Unit of measurement")


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


# =============================================================================
# Message Agent Schemas
# =============================================================================

class MessageRole(str, Enum):
    """Role in a conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationMessage(BaseModel):
    """A single message in a conversation."""
    role: MessageRole
    content: str
    timestamp: Optional[str] = None


class IncomingSMS(BaseModel):
    """Incoming SMS from Twilio webhook."""
    from_number: str = Field(description="Sender phone number in E.164 format")
    to_number: str = Field(description="Recipient phone number (our Twilio number)")
    body: str = Field(description="Message content")
    message_sid: Optional[str] = Field(default=None, description="Twilio message SID")


class OutgoingSMS(BaseModel):
    """Outgoing SMS to send via Twilio."""
    to_number: str = Field(description="Recipient phone number in E.164 format")
    body: str = Field(description="Message content")


class ConversationState(BaseModel):
    """State of a conversation with a user."""
    phone_number: str = Field(description="User's phone number")
    messages: list[ConversationMessage] = Field(default_factory=list)
    context: dict = Field(default_factory=dict, description="Additional context for the conversation")
