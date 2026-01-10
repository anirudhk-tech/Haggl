"""Business profile storage operations."""

import logging
from datetime import datetime
from typing import Optional

from .database import get_database
from .schemas import BusinessProfile, BusinessProduct, BusinessLocation, BusinessType

logger = logging.getLogger(__name__)

COLLECTION = "businesses"


def save_business_profile(profile: BusinessProfile) -> bool:
    """
    Save or update a business profile.
    
    Args:
        profile: BusinessProfile to save
        
    Returns:
        True if successful
    """
    try:
        db = get_database()
        if db is None:
            logger.warning("MongoDB not available, skipping business save")
            return False
        
        collection = db[COLLECTION]
        
        # Update timestamp
        profile.updated_at = datetime.utcnow()
        
        # Upsert by business_id
        result = collection.update_one(
            {"business_id": profile.business_id},
            {"$set": profile.model_dump()},
            upsert=True,
        )
        
        logger.info(f"Saved business profile: {profile.business_id}")
        return True
        
    except Exception as e:
        logger.exception(f"Failed to save business profile: {e}")
        return False


def get_business_profile(business_id: str) -> Optional[BusinessProfile]:
    """
    Get a business profile by ID.
    
    Args:
        business_id: Business ID (often phone number)
        
    Returns:
        BusinessProfile or None
    """
    try:
        db = get_database()
        if db is None:
            return None
        
        collection = db[COLLECTION]
        doc = collection.find_one({"business_id": business_id})
        
        if doc:
            doc.pop("_id", None)
            return BusinessProfile(**doc)
        
        return None
        
    except Exception as e:
        logger.exception(f"Failed to get business profile: {e}")
        return None


def get_business_by_phone(phone: str) -> Optional[BusinessProfile]:
    """
    Get a business profile by phone number.
    
    Args:
        phone: Phone number (will normalize)
        
    Returns:
        BusinessProfile or None
    """
    # Normalize phone number
    normalized = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not normalized.startswith("+"):
        normalized = f"+{normalized}"
    
    try:
        db = get_database()
        if db is None:
            return None
        
        collection = db[COLLECTION]
        
        # Try both as business_id and phone field
        doc = collection.find_one({
            "$or": [
                {"business_id": normalized},
                {"phone": normalized},
                {"business_id": phone},
                {"phone": phone},
            ]
        })
        
        if doc:
            doc.pop("_id", None)
            return BusinessProfile(**doc)
        
        return None
        
    except Exception as e:
        logger.exception(f"Failed to get business by phone: {e}")
        return None


def create_business_from_onboarding(
    business_id: str,
    business_type: str,
    products: list[dict],
    phone: Optional[str] = None,
    business_name: Optional[str] = None,
    location: Optional[dict] = None,
) -> Optional[BusinessProfile]:
    """
    Create a business profile from onboarding data.
    
    Args:
        business_id: Unique ID (often phone)
        business_type: Type of business
        products: List of product dicts
        phone: Phone number
        business_name: Business name
        location: Location dict
        
    Returns:
        Created BusinessProfile or None
    """
    try:
        # Convert products
        business_products = []
        for p in products:
            business_products.append(BusinessProduct(
                product_id=p.get("id", 0),
                name=p.get("name", ""),
                category=p.get("category", ""),
                unit=p.get("unit", "units"),
                estimated_monthly=p.get("estimatedMonthly", 0),
            ))
        
        # Convert location
        business_location = None
        if location:
            business_location = BusinessLocation(
                city=location.get("city"),
                state=location.get("state"),
                zip_code=location.get("zip_code"),
            )
        
        # Create profile
        profile = BusinessProfile(
            business_id=business_id,
            business_name=business_name,
            business_type=BusinessType(business_type) if business_type else BusinessType.OTHER,
            phone=phone,
            location=business_location,
            products=business_products,
            onboarding_complete=True,
        )
        
        if save_business_profile(profile):
            return profile
        return None
        
    except Exception as e:
        logger.exception(f"Failed to create business from onboarding: {e}")
        return None


def update_business_preferences(business_id: str, weights: dict) -> bool:
    """
    Update business preference weights.
    
    Args:
        business_id: Business ID
        weights: New preference weights dict
        
    Returns:
        True if successful
    """
    try:
        db = get_database()
        if db is None:
            return False
        
        collection = db[COLLECTION]
        result = collection.update_one(
            {"business_id": business_id},
            {
                "$set": {
                    "preference_weights": weights,
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        
        return result.modified_count > 0 or result.matched_count > 0
        
    except Exception as e:
        logger.exception(f"Failed to update business preferences: {e}")
        return False


def get_business_context_for_agent(phone: str) -> dict:
    """
    Get business context formatted for use by agents.
    
    Returns a dict with business info that can be injected into prompts.
    
    Args:
        phone: Customer phone number
        
    Returns:
        Dict with business context (or defaults if not found)
    """
    profile = get_business_by_phone(phone)
    
    if not profile:
        # Return defaults
        return {
            "business_name": "your business",
            "business_type": "business",
            "products": [],
            "location": None,
            "preferences": {
                "quality": 0.30,
                "affordability": 0.35,
                "shipping": 0.15,
                "reliability": 0.20,
            },
        }
    
    return {
        "business_name": profile.business_name or "your business",
        "business_type": profile.business_type.value,
        "products": [
            {
                "name": p.name,
                "category": p.category,
                "unit": p.unit,
                "monthly_usage": p.estimated_monthly,
            }
            for p in profile.products
        ],
        "location": {
            "city": profile.location.city if profile.location else None,
            "state": profile.location.state if profile.location else None,
        } if profile.location else None,
        "preferences": profile.preference_weights,
    }
