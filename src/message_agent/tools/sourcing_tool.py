"""Sourcing tool - finds vendors using the Sourcing Agent."""

import logging
import uuid
from typing import Optional

from sourcing_agent import (
    get_sourcing_agent,
    SourcingRequest,
    IngredientRequest,
    UserLocation,
)

logger = logging.getLogger(__name__)

# Hardcoded test phone number for all vendors
TEST_VENDOR_PHONE = "+15633965540"

# Default location for sourcing
DEFAULT_LOCATION = UserLocation(
    city="Des Moines",
    state="IA",
    country="USA",
)


async def source_vendors(
    product: str,
    quantity: float = 10,
    unit: str = "dozen",
    quality: Optional[str] = None,
    location: Optional[UserLocation] = None,
) -> dict:
    """
    Find vendors for a product using the Sourcing Agent.
    
    Args:
        product: What to source (e.g., "eggs", "flour")
        quantity: How much needed
        unit: Unit of measurement
        quality: Quality requirement (e.g., "organic", "Grade A")
        location: User location for distance calc
        
    Returns:
        dict with vendors list and status
    """
    request_id = f"source-{uuid.uuid4().hex[:8]}"
    
    logger.info(f"Sourcing vendors for {quantity} {unit} of {product}")
    
    # Build the sourcing request
    request = SourcingRequest(
        request_id=request_id,
        ingredients=[
            IngredientRequest(
                name=product,
                quantity=quantity,
                unit=unit,
                quality=quality,
            )
        ],
        location=location or DEFAULT_LOCATION,
        max_results_per_ingredient=5,
    )
    
    try:
        sourcing_agent = get_sourcing_agent()
        response = await sourcing_agent.source_vendors(request)
        
        # Extract vendors and override phone numbers for testing
        vendors = []
        for result in response.results:
            for vendor in result.vendors:
                vendors.append({
                    "name": vendor.vendor_name,
                    "phone": TEST_VENDOR_PHONE,  # Hardcoded for testing
                    "original_phone": vendor.phone,
                    "website": vendor.website,
                    "address": vendor.address,
                    "distance_miles": vendor.distance_miles,
                    "price_per_unit": vendor.pricing.price_per_unit if vendor.pricing else None,
                    "unit": vendor.pricing.unit if vendor.pricing else unit,
                    "rating": vendor.reviews.rating if vendor.reviews else None,
                })
        
        logger.info(f"Found {len(vendors)} vendors for {product}. Vendors: {[vendor['name'] for vendor in vendors]}")
        
        return {
            "success": True,
            "product": product,
            "quantity": quantity,
            "unit": unit,
            "vendors": vendors,
            "total_found": len(vendors),
            "error": None,
        }
        
    except Exception as e:
        logger.exception(f"Failed to source vendors: {e}")
        return {
            "success": False,
            "product": product,
            "vendors": [],
            "total_found": 0,
            "error": str(e),
        }


# OpenAI function schema for source_vendors
SOURCE_VENDORS_FUNCTION = {
    "type": "function",
    "function": {
        "name": "source_vendors",
        "description": "Search for vendors that sell a specific ingredient/product. Use this when the user wants to find suppliers for something like eggs, flour, produce, etc. Returns a list of vendors with contact info and pricing.",
        "parameters": {
            "type": "object",
            "properties": {
                "product": {
                    "type": "string",
                    "description": "The product/ingredient to source (e.g., 'eggs', 'flour', 'milk', 'tomatoes')",
                },
                "quantity": {
                    "type": "number",
                    "description": "How much is needed",
                    "default": 10,
                },
                "unit": {
                    "type": "string",
                    "description": "Unit of measurement (e.g., 'dozen', 'pounds', 'gallons')",
                    "default": "dozen",
                },
                "quality": {
                    "type": "string",
                    "description": "Optional quality requirement (e.g., 'organic', 'Grade A', 'local')",
                },
            },
            "required": ["product"],
        },
    },
}
