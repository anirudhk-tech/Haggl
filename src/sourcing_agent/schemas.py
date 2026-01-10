"""Pydantic schemas for the Sourcing Agent."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SourcingState(str, Enum):
    """Sourcing agent state machine states."""
    IDLE = "idle"
    SEARCHING = "searching"
    EXTRACTING = "extracting"
    COMPLETED = "completed"
    FAILED = "failed"


# =============================================================================
# Input Models
# =============================================================================

class IngredientRequest(BaseModel):
    """Input for sourcing an ingredient."""
    name: str = Field(description="Ingredient name (e.g., 'flour', 'eggs')")
    quantity: float = Field(description="Quantity needed")
    unit: str = Field(default="lbs", description="Unit of measurement")
    quality: Optional[str] = Field(default=None, description="Quality requirement (e.g., 'organic', 'Grade A')")


class UserLocation(BaseModel):
    """User location for distance calculations."""
    city: str = Field(description="City name")
    state: str = Field(description="State/Province code (e.g., 'CA')")
    country: str = Field(default="USA")
    zip_code: Optional[str] = Field(default=None)


# =============================================================================
# Vendor Data Models
# =============================================================================

class VendorPricing(BaseModel):
    """Pricing information for a vendor."""
    price_per_unit: Optional[float] = Field(default=None, description="Price per unit")
    unit: Optional[str] = Field(default=None, description="Unit of measurement (lb, kg, dozen, etc.)")
    currency: str = Field(default="USD")
    bulk_discount_available: bool = Field(default=False)


class VendorQuantity(BaseModel):
    """Quantity availability information."""
    available_quantity: Optional[float] = Field(default=None)
    unit: Optional[str] = Field(default=None)
    moq: Optional[float] = Field(default=None, description="Minimum Order Quantity")
    moq_unit: Optional[str] = Field(default=None)


class VendorReview(BaseModel):
    """Vendor review/rating information."""
    rating: Optional[float] = Field(default=None, ge=0, le=5, description="Rating out of 5")
    review_count: Optional[int] = Field(default=None, ge=0)
    review_source: Optional[str] = Field(default=None, description="Source of reviews (Google, Yelp, etc.)")


class ExtractedVendor(BaseModel):
    """Complete extracted vendor information."""
    vendor_name: str = Field(description="Vendor/company name")
    website: Optional[str] = Field(default=None, description="Vendor website URL")
    phone: Optional[str] = Field(default=None, description="Contact phone number")
    email: Optional[str] = Field(default=None, description="Contact email")
    address: Optional[str] = Field(default=None, description="Physical address")
    pricing: Optional[VendorPricing] = Field(default=None)
    quantity: Optional[VendorQuantity] = Field(default=None)
    reviews: Optional[VendorReview] = Field(default=None)
    distance_miles: Optional[float] = Field(default=None, description="Distance from user in miles")
    certifications: list[str] = Field(default_factory=list)
    source_url: str = Field(description="URL where data was extracted from")
    extraction_confidence: float = Field(default=0.5, ge=0, le=1)
    extracted_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# =============================================================================
# Search Result Models
# =============================================================================

class ExaSearchResult(BaseModel):
    """Result from Exa.ai search."""
    url: str
    title: str
    text: Optional[str] = None
    highlights: list[str] = Field(default_factory=list)
    published_date: Optional[str] = None
    score: Optional[float] = None


# =============================================================================
# Request/Response Models
# =============================================================================

class SourcingRequest(BaseModel):
    """Request to source vendors for ingredients."""
    request_id: str = Field(description="Unique request identifier")
    ingredients: list[IngredientRequest] = Field(min_length=1)
    location: UserLocation
    max_results_per_ingredient: int = Field(default=10, ge=1, le=25)


class VendorResult(BaseModel):
    """Result for a single ingredient search."""
    ingredient: str
    vendors: list[ExtractedVendor]
    search_queries: list[str] = Field(default_factory=list)
    total_found: int
    extraction_time_seconds: float = 0


class SourcingResponse(BaseModel):
    """Response from the sourcing agent."""
    request_id: str
    status: SourcingState
    results: list[VendorResult] = Field(default_factory=list)
    total_vendors_found: int = 0
    elapsed_seconds: float = 0
    errors: list[str] = Field(default_factory=list)
