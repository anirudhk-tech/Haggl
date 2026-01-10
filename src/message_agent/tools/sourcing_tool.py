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

# Hardcoded test phone numbers for vendors [0], [1], [2]
TEST_VENDOR_PHONES = [
    "+15633965540",  # Vendor 0
    "+17203154946",  # Vendor 1
    "+15128508061",  # Vendor 2
]

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
        
        # Extract vendors - take top 3 and assign test phone numbers
        all_vendors = []
        for result in response.results:
            for vendor in result.vendors:
                all_vendors.append(vendor)
        
        # Take only top 3 vendors (indices 0-2)
        top_vendors = all_vendors[:3]
        
        vendors = []
        for i, vendor in enumerate(top_vendors):
            vendors.append({
                "name": vendor.vendor_name,
                "phone": TEST_VENDOR_PHONES[i],  # Assign test phone based on index
                "original_phone": vendor.phone,
                "website": vendor.website,
                "address": vendor.address,
                "distance_miles": vendor.distance_miles,
                "price_per_unit": vendor.pricing.price_per_unit if vendor.pricing else None,
                "unit": vendor.pricing.unit if vendor.pricing else unit,
                "rating": vendor.reviews.rating if vendor.reviews else None,
            })
        
        logger.info(f"Sourced {len(all_vendors)} vendors, using top {len(vendors)} for {product}")
        logger.info(f"Vendors: {[(v['name'], v['phone']) for v in vendors]}")
        
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
