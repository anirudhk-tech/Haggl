"""Pydantic schemas for the Evaluation Agent."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class EvaluationParameter(str, Enum):
    """The four evaluation parameters."""
    QUALITY = "quality"
    AFFORDABILITY = "affordability"
    SHIPPING = "shipping"
    RELIABILITY = "reliability"


class FeedbackDirection(str, Enum):
    """Direction of user feedback."""
    UP = "up"
    DOWN = "down"


class PreferenceWeights(BaseModel):
    """Current preference weights for a business."""
    quality: float = Field(default=0.30, ge=0.05, le=0.60)
    affordability: float = Field(default=0.35, ge=0.05, le=0.60)
    shipping: float = Field(default=0.15, ge=0.05, le=0.60)
    reliability: float = Field(default=0.20, ge=0.05, le=0.60)

    def normalize(self) -> "PreferenceWeights":
        """Normalize weights to sum to 1.0."""
        total = self.quality + self.affordability + self.shipping + self.reliability
        return PreferenceWeights(
            quality=self.quality / total,
            affordability=self.affordability / total,
            shipping=self.shipping / total,
            reliability=self.reliability / total,
        )


class VendorScores(BaseModel):
    """Scores for a vendor across all parameters."""
    quality: float = Field(ge=0, le=100)
    affordability: float = Field(ge=0, le=100)
    shipping: float = Field(ge=0, le=100)
    reliability: float = Field(ge=0, le=100)


class VendorData(BaseModel):
    """Vendor data structure matching sourcing agent fields."""
    vendor_id: str
    vendor_name: str
    product: str
    price_per_unit: float
    unit: str = "unit"
    distance_miles: float = 0
    quality_score: float = Field(default=50, ge=0, le=100)
    reliability_score: float = Field(default=50, ge=0, le=100)
    certifications: list[str] = Field(default_factory=list)
    phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None


class VendorEvaluation(BaseModel):
    """Complete evaluation result for a vendor."""
    vendor_id: str
    vendor_name: str
    scores: VendorScores
    embedding_score: float  # Can be negative (cosine similarity range: -1 to 1)
    parameter_score: float = Field(ge=0, le=1)
    final_score: float  # Can vary based on embedding contribution
    rank: Optional[int] = None


class FeedbackRequest(BaseModel):
    """User feedback on preference adjustment."""
    parameter: EvaluationParameter
    direction: FeedbackDirection
    vendor_id: Optional[str] = None  # Optional - for tracking which vendor triggered feedback


class FeedbackRecord(BaseModel):
    """Stored feedback record."""
    business_id: str
    vendor_id: str
    parameter: EvaluationParameter
    direction: FeedbackDirection
    weights_before: PreferenceWeights
    weights_after: PreferenceWeights
    timestamp: str


class BusinessPreferences(BaseModel):
    """Complete preferences for a business."""
    business_id: str
    weights: PreferenceWeights
    voyage_model_id: Optional[str] = None
    total_feedback_count: int = 0
    training_status: str = "pending"


class EvaluationRequest(BaseModel):
    """Request to evaluate vendors."""
    business_id: str
    budget: float = Field(gt=0)
    ingredients: list[str] = Field(default_factory=list)  # Empty = all vendors


class EvaluationResponse(BaseModel):
    """Response from vendor evaluation."""
    selected_vendors: list[VendorEvaluation]
    total_cost: float
    budget: float
    savings: float
    weights_used: PreferenceWeights


class TrainingExample(BaseModel):
    """Training example for Voyage AI fine-tuning."""
    query: str
    positive: str
    negative: str


class ContactMethod(str, Enum):
    """Method to contact the vendor."""
    EMAIL = "email"
    CALL = "call"
    SMS = "sms"


class VendorContactRequest(BaseModel):
    """Request to contact the best vendor for invoice/payment."""
    business_id: str
    business_name: str
    vendor_id: str
    vendor_name: str
    vendor_email: Optional[str] = None
    vendor_phone: Optional[str] = None
    product: str
    quantity: float
    unit: str = "unit"
    agreed_price: Optional[float] = None
    preferred_method: ContactMethod = ContactMethod.EMAIL
    reply_to_email: Optional[str] = None


class VendorContactResponse(BaseModel):
    """Response from contacting a vendor."""
    success: bool
    method_used: ContactMethod
    vendor_id: str
    vendor_name: str
    message_id: Optional[str] = None  # Email ID or Call ID
    call_outcome: Optional[dict] = None  # If call was made
    error: Optional[str] = None
