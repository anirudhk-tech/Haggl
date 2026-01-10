"""Pydantic schemas for MongoDB documents."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# Enums
# =============================================================================

class OrderStatus(str, Enum):
    """Order status states."""
    PENDING = "pending"
    SOURCING = "sourcing"
    CALLING = "calling"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    COMPLETED = "completed"


class CallStatus(str, Enum):
    """Call status states."""
    INITIATED = "initiated"
    RINGING = "ringing"
    IN_PROGRESS = "in_progress"
    ENDED = "ended"
    FAILED = "failed"


# =============================================================================
# Vendor Documents
# =============================================================================

class VendorLocation(BaseModel):
    """Vendor location info."""
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "USA"
    distance_miles: Optional[float] = None


class VendorPricing(BaseModel):
    """Vendor pricing info."""
    price_per_unit: Optional[float] = None
    unit: Optional[str] = None
    currency: str = "USD"
    bulk_discount: bool = False
    moq: Optional[float] = None  # Minimum Order Quantity


class VendorReviews(BaseModel):
    """Vendor review info."""
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    review_count: Optional[int] = None
    source: Optional[str] = None  # Google, Yelp, etc.


class VendorDocument(BaseModel):
    """MongoDB vendor document schema."""
    vendor_id: str = Field(description="Unique vendor ID")
    name: str = Field(description="Vendor name")
    ingredient: str = Field(description="Primary ingredient/product")
    
    # Contact
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    
    # Location
    location: Optional[VendorLocation] = None
    
    # Pricing
    pricing: Optional[VendorPricing] = None
    
    # Reviews
    reviews: Optional[VendorReviews] = None
    
    # Evaluation scores (for Evaluation Agent)
    quality_score: float = Field(default=50.0, ge=0, le=100, description="Quality score 0-100")
    reliability_score: float = Field(default=50.0, ge=0, le=100, description="Reliability score 0-100")
    
    # Metadata
    source_url: Optional[str] = None  # Where we found them
    certifications: list[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class VendorEmbedding(BaseModel):
    """Vendor embedding for vector search."""
    vendor_id: str
    ingredient: str
    embedding: list[float] = Field(description="Vector embedding (e.g., 1536 dims for OpenAI)")
    text: str = Field(description="Text that was embedded")
    model: str = Field(default="text-embedding-3-small")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# Conversation Documents
# =============================================================================

class MessageDocument(BaseModel):
    """Single message in a conversation."""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConversationDocument(BaseModel):
    """MongoDB conversation document schema."""
    phone_number: str = Field(description="User's phone number (unique key)")
    messages: list[MessageDocument] = Field(default_factory=list)
    
    # Context from workflow
    context: dict = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# =============================================================================
# Order Documents
# =============================================================================

class OrderDocument(BaseModel):
    """MongoDB order document schema."""
    order_id: str = Field(description="Unique order ID")
    phone_number: str = Field(description="Customer phone number")
    
    # Order details
    product: str
    quantity: float
    unit: str
    
    # Status
    status: OrderStatus = OrderStatus.PENDING
    
    # Vendors involved
    vendors_sourced: list[str] = Field(default_factory=list)  # vendor_ids
    vendors_called: list[str] = Field(default_factory=list)   # vendor_ids
    vendor_confirmed: Optional[str] = None  # vendor_id of winner
    
    # Outcome
    confirmed_price: Optional[float] = None
    confirmed_eta: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# =============================================================================
# Call Documents
# =============================================================================

class CallOutcomeDocument(BaseModel):
    """Outcome of a vendor call."""
    confirmed: bool = False
    price: Optional[float] = None
    eta: Optional[str] = None
    notes: Optional[str] = None
    transcript: Optional[str] = None


class CallDocument(BaseModel):
    """MongoDB call document schema."""
    call_id: str = Field(description="Vapi call ID")
    order_id: str = Field(description="Associated order ID")
    vendor_id: str = Field(description="Vendor being called")
    vendor_name: str
    vendor_phone: str
    
    # Status
    status: CallStatus = CallStatus.INITIATED
    ended_reason: Optional[str] = None
    
    # Outcome
    outcome: Optional[CallOutcomeDocument] = None
    
    # Timing
    duration_seconds: Optional[int] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# =============================================================================
# Evaluation Documents
# =============================================================================

class EvaluationStatus(str, Enum):
    """Evaluation status states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class VendorCallResult(BaseModel):
    """Result of a single vendor call for evaluation."""
    vendor_id: str
    vendor_name: str
    call_id: Optional[str] = None
    
    # Call outcome
    confirmed: bool = False
    quoted_price: Optional[float] = None
    eta: Optional[str] = None
    
    # Vendor scores (from sourcing)
    quality_score: float = Field(default=50.0, ge=0, le=100)
    reliability_score: float = Field(default=50.0, ge=0, le=100)
    distance_miles: float = Field(default=0.0, ge=0)
    price_per_unit: Optional[float] = None
    unit: Optional[str] = None
    certifications: list[str] = Field(default_factory=list)
    
    # Evaluation scores (calculated)
    final_score: Optional[float] = None
    rank: Optional[int] = None


class EvaluationDocument(BaseModel):
    """MongoDB evaluation document schema."""
    evaluation_id: str = Field(description="Unique evaluation ID")
    order_id: str = Field(description="Associated order ID")
    
    # Status
    status: EvaluationStatus = EvaluationStatus.PENDING
    
    # Input data
    vendor_results: list[VendorCallResult] = Field(default_factory=list)
    
    # Evaluation output
    selected_vendor_id: Optional[str] = None
    selected_vendor_name: Optional[str] = None
    selection_reason: Optional[str] = None
    
    # Scores used
    weights_used: Optional[dict] = None  # {quality, affordability, shipping, reliability}
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# =============================================================================
# Business Profile Documents
# =============================================================================

class BusinessType(str, Enum):
    """Business types from onboarding."""
    RESTAURANT = "restaurant"
    BAKERY = "bakery"
    CAFE = "cafe"
    RETAIL = "retail"
    OTHER = "other"


class BusinessProduct(BaseModel):
    """Product that a business regularly orders."""
    product_id: int
    name: str
    category: str
    unit: str
    estimated_monthly: float = Field(description="Estimated monthly usage")
    

class BusinessLocation(BaseModel):
    """Business location info."""
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "USA"


class BusinessProfile(BaseModel):
    """MongoDB business profile document schema."""
    business_id: str = Field(description="Unique business ID (often phone number)")
    
    # Basic info
    business_name: Optional[str] = None
    business_type: BusinessType = BusinessType.OTHER
    
    # Contact
    phone: Optional[str] = None
    email: Optional[str] = None
    
    # Location
    location: Optional[BusinessLocation] = None
    
    # Products (from onboarding)
    products: list[BusinessProduct] = Field(default_factory=list)
    
    # Preferences (from evaluation agent learning)
    preference_weights: dict = Field(
        default_factory=lambda: {
            "quality": 0.30,
            "affordability": 0.35,
            "shipping": 0.15,
            "reliability": 0.20,
        }
    )
    
    # Onboarding status
    onboarding_complete: bool = False
    menu_uploaded: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
